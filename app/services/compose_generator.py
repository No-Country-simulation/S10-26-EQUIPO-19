import json
import re
from typing import Dict, Any, List, Set
import yaml


def sanitize_service_name(name: str) -> str:
    
    name = name.lower()
    name = re.sub(r'[^a-z0-9-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name or "service"


class ComposeGeneratorService:
    def __init__(self, data_file_path: str = "app/data/docker_data.json"):
        self.data_file_path = data_file_path
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.repositories: Dict[str, Any] = data.get("repositories", {})
        except FileNotFoundError:
            self.repositories = {}

    def _get_primary_source(self, repo_info: dict) -> str:
        sources = repo_info.get("source", [])
        return sources[0] if sources else "https://github.com"

    def _process_ports(self, repo_info: dict) -> List[str]:
        ports_list = []
        raw_ports = repo_info.get("ports", [])
        for p in raw_ports:
            if isinstance(p, dict):
                container_port = p.get("container")
                range_end = p.get("range_end")
                if container_port:
                    if range_end:
                        ports_list.append(f"{container_port}-{range_end}:{container_port}-{range_end}")
                    else:
                        ports_list.append(f"{container_port}:{container_port}")
            elif isinstance(p, (str, int)):
                ports_list.append(f"{p}:{p}")
        return ports_list

    def generate(self, request_repos: List[str]) -> Dict[str, Any]:
        services_map: Dict[str, dict] = {}
        services_response: List[dict] = []
        skipped_response: List[dict] = []
        warnings: List[str] = []
        used_ports: Dict[str, str] = {}
        has_secrets = False
        processed_catalog_deps: Set[str] = set()

        queue: List[str] = list(request_repos)

        for repo_name in queue:
            repo_info = self.repositories.get(repo_name)

            if not repo_info:
                if repo_name in request_repos:
                    skipped_response.append({
                        "full_name": repo_name,
                        "reason": "El repositorio no se encuentra registrado en el inventario Docker."
                    })
                continue

            kind = repo_info.get("kind", "")
            image = repo_info.get("image")
            review = repo_info.get("review")

           
            if review and repo_name in request_repos:
                warnings.append(f"Nota de revisión para '{repo_name}': {review}")

          
            if kind == "stack":
                if repo_name in request_repos:
                    source_url = self._get_primary_source(repo_info)
                    reason = f"Es un stack multicontenedor complejo. Se recomienda usar su compose oficial: {source_url}"
                    skipped_response.append({"full_name": repo_name, "reason": reason})
                continue

            elif kind == "library":
                if repo_name in request_repos:
                    skipped_response.append({
                        "full_name": repo_name,
                        "reason": "Es una librería ejecutable en código fuente y se instala como dependencia, no como un servicio en Docker Compose."
                    })
                continue

            elif kind in ["cli", "kubernetes", "desktop", "no_official_image"]:
                if repo_name in request_repos:
                    reasons = {
                        "cli": "Es una herramienta de línea de comandos (CLI) y no un servicio web continuo.",
                        "kubernetes": "Está diseñado para desplegarse en Kubernetes (vía manifiestos/Helm/CLI), no con Docker Compose.",
                        "desktop": "Es una aplicación de escritorio local y no se despliega en Docker.",
                        "no_official_image": "No posee una imagen oficial o preconstruida en los registros estándar."
                    }
                    skipped_response.append({"full_name": repo_name, "reason": reasons[kind]})
                continue

            elif kind != "service" or not image:
                if repo_name in request_repos:
                    skipped_response.append({
                        "full_name": repo_name,
                        "reason": "El repositorio no tiene una configuración válida de servicio de Docker."
                    })
                continue

            if ":latest" in image or ":" not in image:
                if repo_name in request_repos:
                    skipped_response.append({
                        "full_name": repo_name,
                        "reason": "La imagen Docker debe incluir una versión fija explícita y no la etiqueta 'latest'."
                    })
                continue

            service_name = sanitize_service_name(repo_name.split("/")[-1])
            ports = self._process_ports(repo_info)
            env_vars = dict(repo_info.get("environment", {}))
            command = repo_info.get("command")

            for v in env_vars.values():
                if v == "<secreto>":
                    has_secrets = True

            for p in ports:
                host_port = p.split(":")[0]
                if host_port in used_ports and used_ports[host_port] != service_name:
                    warnings.append(
                        f"Conflicto de puerto detectado: El puerto {host_port} ya está asignado al servicio '{used_ports[host_port]}' y también es requerido por '{service_name}'."
                    )
                else:
                    used_ports[host_port] = service_name

        
            depends_on_list: List[str] = []
            depends_on_data = repo_info.get("depends_on", {})
            catalog_deps = depends_on_data.get("catalog", [])

            for dep_repo in catalog_deps:
                dep_service_name = sanitize_service_name(dep_repo.split("/")[-1])
                depends_on_list.append(dep_service_name)
                if dep_repo not in processed_catalog_deps and dep_repo not in request_repos:
                    processed_catalog_deps.add(dep_repo)
                    queue.append(dep_repo)

            external_deps = depends_on_data.get("external", [])
            for ext in external_deps:
                ext_name = ext.lower()
                if "redis" in ext_name and "valkey-io/valkey" in self.repositories:
                    valkey_service_name = sanitize_service_name("valkey")
                    if valkey_service_name not in depends_on_list:
                        depends_on_list.append(valkey_service_name)
                    if "valkey-io/valkey" not in processed_catalog_deps and "valkey-io/valkey" not in request_repos:
                        processed_catalog_deps.add("valkey-io/valkey")
                        queue.append("valkey-io/valkey")
                else:
                    warnings.append(
                        f"El servicio '{service_name}' requiere la dependencia externa '{ext}' que está fuera del catálogo principal. Verifique la imagen oficial correspondiente."
                    )

            service_spec: Dict[str, Any] = {"image": image}
            if command:
                service_spec["command"] = command
            if ports:
                service_spec["ports"] = ports
            if env_vars:
                service_spec["environment"] = env_vars
            if depends_on_list:
                service_spec["depends_on"] = depends_on_list

            services_map[service_name] = service_spec

            if repo_name in request_repos:
                services_response.append({
                    "full_name": repo_name,
                    "service": service_name,
                    "image": image,
                    "ports": ports
                })

        if has_secrets:
            warnings.append(
                "Algunas variables de entorno contienen contraseñas o claves sensibles marcadas como '<secreto>'. Reemplácelas antes de ejecutar el contenedor."
            )

       
        compose_dict = {
            "services": services_map
        }

        yaml_content = yaml.safe_dump(compose_dict, sort_keys=False, default_flow_style=False)

        return {
            "filename": "docker-compose.yml",
            "content": yaml_content,
            "services": services_response,
            "skipped": skipped_response,
            "warnings": warnings
        }

    