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
    ) -> str:

        semantic_results = semantic_results or []

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

        context = [
            "Eres un asistente técnico especializado en herramientas Open Source.",
            "Responde utilizando exclusivamente la información proporcionada.",
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
                f"Compatibilidad: {repository.get('compatibility_score', 0)}/100\n"
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

        context.append(
            "\nINSTRUCCIONES DE RESPUESTA:\n"
            "- Explica qué evidencia respalda la relevancia de cada repositorio.\n"
            "- Compara las alternativas cuando corresponda.\n"
            "- Menciona limitaciones o requisitos que no se cumplen.\n"
            "- Utiliza los puntajes de compatibilidad como referencia secundaria.\n"
            "- No presentes una integración como verificada si no hay evidencia explícita.\n"
            "- No recomiendes un repositorio únicamente por su lenguaje o popularidad.\n"
            "- Si los fragmentos no demuestran la funcionalidad solicitada, dilo claramente."
        )

        return "\n".join(context)
