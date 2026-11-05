import time
from collections import defaultdict
from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    """Rate limiter en memoria con ventana deslizante por IP de cliente.

    Diseñado para proteger endpoints sensibles (como el asistente RAG o proxies externos)
    contra abuso y DoS por consumo no controlado (OWASP API4:2023).
    """

    def __init__(self, requests_limit: int = 10, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP real del cliente evitando spoofing de cabeceras (H4)."""
        # Cloudflare en producción garantiza 'cf-connecting-ip' (no falsificable por el cliente)
        cf_ip = request.headers.get("cf-connecting-ip")
        if cf_ip:
            return cf_ip.strip()

        # En conexiones directas o desarrollo local, confiar en la conexión TCP real (client.host)
        # para evitar que un atacante saltee el limitador inyectando X-Forwarded-For falsos
        if request.client and request.client.host:
            return request.client.host

        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # Tomar la última IP agregada por el proxy más cercano
            ips = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
            if ips:
                return ips[-1]

        return "unknown"

    def __call__(self, request: Request) -> None:
        client_ip = self._get_client_ip(request)
        now = time.time()
        window_start = now - self.window_seconds

        # Filtrar timestamps que están dentro de la ventana actual
        timestamps = [t for t in self.requests[client_ip] if t > window_start]
        self.requests[client_ip] = timestamps

        if len(timestamps) >= self.requests_limit:
            oldest_ts = timestamps[0]
            retry_after = max(1, int(self.window_seconds - (now - oldest_ts)))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Límite de solicitudes excedido ({self.requests_limit} req/{self.window_seconds}s). Reintente en {retry_after} segundos.",
                headers={"Retry-After": str(retry_after)},
            )

        self.requests[client_ip].append(now)


# Limitador para el Asistente RAG (10 peticiones por minuto por IP)
assistant_rate_limiter = InMemoryRateLimiter(requests_limit=10, window_seconds=60)

# Limitador para endpoints de GitHub (20 peticiones por minuto por IP)
github_rate_limiter = InMemoryRateLimiter(requests_limit=20, window_seconds=60)

# Limitador general para el catálogo de repositorios (60 peticiones por minuto por IP - H4)
repositories_rate_limiter = InMemoryRateLimiter(requests_limit=60, window_seconds=60)
