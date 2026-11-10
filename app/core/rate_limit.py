import os
import time
from collections import defaultdict
from typing import Optional
from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    """Rate limiter en memoria con ventana deslizante por IP y tope global.

    Diseñado para proteger endpoints sensibles (como el asistente RAG o proxies externos)
    contra abuso, rotación de IPs (N4-01) y DoS por consumo no controlado (OWASP API4:2023).
    """

    def __init__(
        self,
        requests_limit: int = 10,
        window_seconds: int = 60,
        global_limit: Optional[int] = None,
        max_tracked_ips: int = 1000,
    ):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        # Tope global en la ventana para mitigar ataques con rotación de IP (N4-01)
        self.global_limit = global_limit or (requests_limit * 5)
        self.max_tracked_ips = max_tracked_ips
        self.requests: dict[str, list[float]] = defaultdict(list)
        self.global_requests: list[float] = []

    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP real del cliente evitando spoofing de cabeceras (H4)."""
        is_production = (
            os.getenv("ENVIRONMENT", "development").lower() == "production"
            or os.getenv("RENDER", "").lower() == "true"
        )

        # Solo confiar en cabeceras de proxy cuando corre detrás de Cloudflare/Render en producción
        if is_production:
            cf_ip = request.headers.get("cf-connecting-ip")
            if cf_ip:
                return cf_ip.strip()

            forwarded = request.headers.get("x-forwarded-for")
            if forwarded:
                # Tomar la última IP agregada por el proxy más cercano
                ips = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
                if ips:
                    return ips[-1]

        # En conexiones directas o desarrollo local, confiar únicamente en la conexión TCP real (client.host)
        if request.client and request.client.host:
            return request.client.host

        return "unknown"

    def _cleanup_expired_ips(self, window_start: float) -> None:
        """Limpia IPs cuyos contadores de rate limit ya vencieron (pasó más de 1 minuto)."""
        expired_ips = [
            ip
            for ip, ts_list in self.requests.items()
            if not ts_list or ts_list[-1] <= window_start
        ]
        for ip in expired_ips:
            del self.requests[ip]

        # Si aun así se supera el máximo de IPs rastreadas, desalojar la más antigua
        while len(self.requests) >= self.max_tracked_ips:
            oldest_ip = next(iter(self.requests))
            del self.requests[oldest_ip]

    def __call__(self, request: Request) -> None:
        client_ip = self._get_client_ip(request)
        now = time.time()
        window_start = now - self.window_seconds

        # 1. Filtrar y verificar el límite global por ventana (mitiga rotación de IPs - N4-01)
        self.global_requests = [t for t in self.global_requests if t > window_start]
        if len(self.global_requests) >= self.global_limit:
            oldest_global_ts = self.global_requests[0]
            retry_after = max(1, int(self.window_seconds - (now - oldest_global_ts)))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Límite global de solicitudes excedido ({self.global_limit} req/{self.window_seconds}s). "
                    f"Reintente en {retry_after} segundos."
                ),
                headers={"Retry-After": str(retry_after)},
            )

        # 2. Limpiar contadores viejos si se acumulan demasiadas IPs distintas
        if len(self.requests) >= self.max_tracked_ips:
            self._cleanup_expired_ips(window_start)

        # 3. Filtrar y verificar el límite individual por IP
        timestamps = [t for t in self.requests[client_ip] if t > window_start]
        if timestamps:
            self.requests[client_ip] = timestamps
        else:
            self.requests.pop(client_ip, None)

        if len(timestamps) >= self.requests_limit:
            oldest_ts = timestamps[0]
            retry_after = max(1, int(self.window_seconds - (now - oldest_ts)))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Límite de solicitudes excedido ({self.requests_limit} req/{self.window_seconds}s). Reintente en {retry_after} segundos.",
                headers={"Retry-After": str(retry_after)},
            )

        self.requests[client_ip].append(now)
        self.global_requests.append(now)


# Limitador para el Asistente RAG (10 req/min por IP, 30 req/min globales)
assistant_rate_limiter = InMemoryRateLimiter(
    requests_limit=10, window_seconds=60, global_limit=30
)

# Limitador para endpoints de GitHub (20 req/min por IP, 60 req/min globales -> máx 3600/h < 5000/h de cuota GitHub)
github_rate_limiter = InMemoryRateLimiter(
    requests_limit=20, window_seconds=60, global_limit=60
)

# Limitador general para el catálogo de repositorios (60 req/min por IP, 300 req/min globales - H4)
repositories_rate_limiter = InMemoryRateLimiter(
    requests_limit=60, window_seconds=60, global_limit=300
)
