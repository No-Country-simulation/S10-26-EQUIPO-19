import json
import logging
import asyncio

from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class EvidenceEvaluator:

    VALID_STATUSES = {"verified", "not_verified", "contradicted"}
    BATCH_SIZE = 3
    MAX_RETRIES = 0

    def __init__(self, llm: LLMService):
        self.llm = llm

    async def evaluate(
            self,
            requirements: dict,
            semantic_results: list[dict],
        ) -> dict[int, list[dict]]:

            mandatory = requirements.get("mandatory_requirements") or {}

            requirements_to_evaluate = [
                {
                    "category": category,
                    "requirement": requirement,
                }
                for category in ("technologies", "functionality")
                for requirement in (mandatory.get(category) or [])
            ]

            if not requirements_to_evaluate or not semantic_results:
                return {}

            repositories = {}
            original_chunks = {}

            for result in semantic_results:
                repository_id = result.get("repository_id")
                source_text = str(result.get("source_text") or "").strip()

                if repository_id is None or not source_text:
                    continue

                chunk_index = result.get("chunk_index")

                repositories.setdefault(repository_id, []).append({
                    "chunk_index": chunk_index,
                    "content": source_text,
                })

                original_chunks.setdefault(repository_id, {})[
                    chunk_index
                ] = source_text

            if not repositories:
                return {}

            all_evaluations = self._empty_evaluations(
                repositories,
                requirements_to_evaluate,
            )

            repository_items = list(repositories.items())

            for start in range(0, len(repository_items), self.BATCH_SIZE):

                batch = repository_items[
                    start:start + self.BATCH_SIZE
                ]

                batch_repositories = dict(batch)

                batch_original_chunks = {
                    repository_id: original_chunks[repository_id]
                    for repository_id, _ in batch
                }

                payload = {
                    "requirements": requirements_to_evaluate,
                    "repositories": [
                        {
                            "repository_id": repository_id,
                            "chunks": chunks,
                        }
                        for repository_id, chunks in batch
                    ],
                }

                context = f"""
    Eres un evaluador técnico especializado en verificar requisitos
    utilizando documentación de proyectos Open Source.

    Evalúa cada repositorio de forma independiente.

    REGLAS OBLIGATORIAS:

    1. verified: solo si existe evidencia explícita de cumplimiento.
    2. contradicted: solo si existe evidencia explícita de incumplimiento.
    3. not_verified: si no existe evidencia suficiente.
    4. La ausencia de información NO significa contradicción.
    5. No infieras funcionalidades.
    6. Las citas deben ser textuales y exactas.
    7. El chunk_index debe corresponder al fragmento original.
    8. Devuelve TODOS los requisitos para TODOS los repositorios.
    9. No mezcles evidencias entre repositorios.

    REQUISITOS Y REPOSITORIOS:

    {json.dumps(payload, ensure_ascii=False)}

    Devuelve exclusivamente JSON válido con esta estructura:

    {{
        "evaluations": [
            {{
                "repository_id": 1,
                "requirements": [
                    {{
                        "category": "functionality",
                        "requirement": "autenticación",
                        "status": "verified",
                        "evidence": "Cita textual exacta",
                        "chunk_index": 0,
                        "reason": "Explicación breve"
                    }}
                ]
            }}
        ]
    }}
    """

                try:
                    logger.info(
                        "Evaluating evidence batch: %s repositories",
                        len(batch),
                    )

                    response = await self.llm.generate_json_response(context)
                    data = json.loads(response)

                    validated = self._validate_evaluations(
                        data,
                        batch_repositories,
                        batch_original_chunks,
                        requirements_to_evaluate,
                    )

                    all_evaluations.update(validated)

                except Exception:
                    logger.exception(
                        "Evidence evaluation failed for batch starting at %s",
                        start,
                    )

            return all_evaluations

    @staticmethod
    def _empty_evaluations(
        repositories: dict,
        requirements: list[dict],
    ) -> dict[int, list[dict]]:

        return {
            repository_id: [
                {
                    "category": item["category"],
                    "requirement": item["requirement"],
                    "status": "not_verified",
                    "evidence": None,
                    "chunk_index": None,
                    "reason": "No se encontró evidencia suficiente.",
                }
                for item in requirements
            ]
            for repository_id in repositories
        }

    def _validate_evaluations(
        self,
        data: dict,
        repositories: dict,
        original_chunks: dict,
        requirements: list[dict],
    ) -> dict[int, list[dict]]:

        validated = self._empty_evaluations(
            repositories,
            requirements,
        )

        evaluations = data.get("evaluations")

        if not isinstance(evaluations, list):
            raise ValueError("Missing or invalid 'evaluations' field")

        valid_requirements = {
            (item["category"], item["requirement"])
            for item in requirements
        }

        for repository in evaluations:

            if not isinstance(repository, dict):
                continue

            repository_id = repository.get("repository_id")

            if repository_id not in validated:
                continue

            repository_requirements = repository.get("requirements")

            if not isinstance(repository_requirements, list):
                continue

            for item in repository_requirements:

                if not isinstance(item, dict):
                    continue

                category = item.get("category")
                requirement = item.get("requirement")
                status = item.get("status")

                if (category, requirement) not in valid_requirements:
                    continue

                if status not in self.VALID_STATUSES:
                    continue

                evidence = item.get("evidence")
                chunk_index = item.get("chunk_index")
                reason = item.get("reason")

                if status == "not_verified":
                    evidence = None
                    chunk_index = None

                elif status in {"verified", "contradicted"}:

                    if not isinstance(evidence, str) or not evidence.strip():
                        continue

                    if chunk_index not in original_chunks.get(repository_id, {}):
                        continue

                    original_text = original_chunks[repository_id][chunk_index]

                    if evidence.strip() not in original_text:
                        continue

                validated_item = {
                    "category": category,
                    "requirement": requirement,
                    "status": status,
                    "evidence": evidence,
                    "chunk_index": chunk_index,
                    "reason": str(reason or ""),
                }

                for index, existing in enumerate(validated[repository_id]):
                    if (
                        existing["category"] == category
                        and existing["requirement"] == requirement
                    ):
                        validated[repository_id][index] = validated_item
                        break

        return validated
