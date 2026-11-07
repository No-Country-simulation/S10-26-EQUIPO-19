import logging

logger = logging.getLogger(__name__)

class ContextBuilder:

    def __init__(self, max_repositories: int = 5, max_content_length: int = 1500):
        self.max_repositories = max_repositories
        self.max_content_length = max_content_length

    def build(
        self,
        query: str,
        requirements: dict,
        repositories: list[dict],
        semantic_results: list[dict] | None = None,
        integration_context: list[dict] | None = None,
    ) -> str:

        semantic_results = semantic_results or []

        integration_context = integration_context or []

        logger.info(
            "Integration context details: %s",
            [
                {
                    "id": integration.get("id"),
                    "integration_code": integration.get("integration_code"),
                    "purpose": integration.get("purpose"),
                    "repositories": [
                        repository.get("full_name")
                        for repository in integration.get("repositories", [])
                    ],
                }
                for integration in integration_context
            ],
        )

        semantic_by_repository = {}

        for result in semantic_results:
            repository_id = result.get("repository_id")

            if repository_id is None:
                continue

            semantic_by_repository.setdefault(repository_id, []).append(result)

        # Solo conservar repositorios con evidencia semántica.
        repositories_with_evidence = [
            repository
            for repository in repositories
            if repository.get("repository_id") in semantic_by_repository
        ]

        allowed_repositories = {
            repository.get("full_name")
            for repository in repositories_with_evidence
            if repository.get("full_name")
        }

        architecture_repositories = {
            repository.get("full_name")
            for integration in integration_context
            for repository in integration.get("repositories", [])
            if repository.get("full_name")
        }

        context = [
            "Eres un asistente técnico especializado en herramientas Open Source.",
            "Usa solo los datos de este contexto, pero nunca le digas al usuario que existe "
            "un contexto, una lista o información proporcionada: háblale de forma directa.",
            "No inventes características, integraciones ni compatibilidades.",
            "Si la información no es suficiente, indícalo explícitamente.",
            "Una similitud semántica alta no demuestra por sí sola que un repositorio "
            "implemente una funcionalidad.",
            "",
            f"CONSULTA DEL USUARIO:\n{query}",
            "",
            "REQUISITOS DETECTADOS:",
            str(requirements),
            "",
            "REPOSITORIOS CON EVIDENCIA SEMÁNTICA:",
            "CATÁLOGO PARA RECOMENDAR:",
            *[
                f"- {repository}"
                for repository in sorted(allowed_repositories)
            ],
            "CATÁLOGO PARA LA ARQUITECTURA:",
            *[
                f"- {repository}"
                for repository in sorted(architecture_repositories)
            ],
        ]

        if not repositories_with_evidence:
            context.append(
                "No se encontraron repositorios con fragmentos semánticos relevantes."
            )

        for index, repository in enumerate(
            repositories_with_evidence[:self.max_repositories],
            start=1,
        ):
            repository_id = repository.get("repository_id")

            repository_context = (
                f"\n{index}. {repository.get('full_name', 'Repositorio desconocido')}\n"
                f"ID: {repository_id}\n"
                f"Licencia: {repository.get('license')}\n"
                f"Estado de mantenimiento: {repository.get('health_status')}\n"
            )

            for key, value in repository.get("criteria_scores", {}).items():
                repository_context += f"{key}: {value}/100\n"

            semantic_chunks = semantic_by_repository[repository_id]

            repository_context += "\nFRAGMENTOS RELEVANTES DEL README:\n"

            for chunk in semantic_chunks:
                content = str(chunk.get("source_text") or "")
                content = content[:self.max_content_length]

                repository_context += f"- {content}\n"

            context.append(repository_context)

        context.append("\nINTEGRACIONES ASOCIADAS A LOS CASOS DE NEGOCIO:")

        if not integration_context:
            context.append(
                "No se encontraron integraciones asociadas a los casos de negocio."
            )

        for integration in integration_context:
            integration_text = (
                f"\nIntegration ID: {integration.get('id')}\n"
                f"Código: {integration.get('integration_code')}\n"
                f"Propósito: {integration.get('purpose')}\n"
                f"Tipo: {integration.get('integration_type')}\n"
                f"Dificultad: {integration.get('difficulty')}\n"
                f"Estado: {integration.get('status')}\n"
                f"Casos de negocio asociados: {integration.get('business_case_ids', [])}\n"
                "Repositorios asociados:\n"
            )

            for repository in integration.get("repositories", []):
                integration_text += (
                    f"- ID: {repository.get('repository_id')} "
                    f"| Repositorio: {repository.get('full_name')} "
                    f"| Rol: {repository.get('role')} "
                    f"| Lenguaje: {repository.get('language')}\n"
                )

            context.append(integration_text)

        context.append(
            "\nINSTRUCCIONES DE RESPUESTA:\n"
            "- Explica qué evidencia respalda la relevancia de cada repositorio.\n"
            "- Compara las alternativas cuando corresponda.\n"
            "- Menciona limitaciones o requisitos que no se cumplen.\n"
            "- No menciones puntajes de compatibilidad, criterios de ranking ni porcentajes "
            "de evaluación en la respuesta al usuario.\n"
            "- No presentes una integración como verificada si no hay evidencia explícita.\n"
            "- No recomiendes un repositorio únicamente por su lenguaje o popularidad.\n"
            "- Si los fragmentos no demuestran la funcionalidad solicitada, dilo claramente.\n"
            "- Utiliza una integración únicamente si su propósito es directamente "
            "pertinente para el dominio de negocio de la consulta.\n"
            "- No consideres que una integración es relevante solamente porque "
            "comparte una funcionalidad técnica con la necesidad del usuario.\n"
            "- No presentes como recomendada o verificada una integración cuyo "
            "contexto de negocio corresponda a un dominio diferente.\n"
            "- Para las recomendaciones textuales, utilizá exclusivamente "
            "repositorios incluidos en CATÁLOGO PARA RECOMENDAR.\n"
            "- Para la arquitectura, podés seleccionar repositorios incluidos en "
            "CATÁLOGO PARA LA ARQUITECTURA, siempre que aporten "
            "directamente a los requisitos del usuario.\n"
            "- No presentes automáticamente todos los repositorios de las integraciones "
            "como recomendaciones.\n"
            "- Utiliza los datos de licencia y estado de mantenimiento "
            "incluidos en cada repositorio.\n"
            "- Cuando recomiendes un repositorio, informa su licencia "
            "y estado de mantenimiento si esos datos están disponibles.\n"
            "- No afirmes que faltan datos de licencia o mantenimiento "
            "si están presentes en el contexto.\n"
        )

        return "\n".join(context)