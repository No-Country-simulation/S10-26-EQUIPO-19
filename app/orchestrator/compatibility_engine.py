class CompatibilityEngine:

    WEIGHTS = {
        "language": 15,
        "license": 10,
        "health_score": 10,
        "semantic_similarity": 20,
    }

    def evaluate(
        self,
        repository: dict,
        requirements: dict,
        semantic_similarity: float | None = None,
    ) -> dict:

        scores = {}
        applicable_weight = 0
        mandatory_failures = []

        def add_score(criterion: str, score: float):
            nonlocal applicable_weight

            weight = self.WEIGHTS[criterion]
            scores[criterion] = round(score, 2)
            applicable_weight += weight

        mandatory = requirements.get("mandatory_requirements") or {}

        # Lenguaje
        requested_language = mandatory.get("language")

        if requested_language:
            repository_language = repository.get("language") or ""

            language_score = (
                100
                if repository_language.lower() == requested_language.lower()
                else 0
            )

            add_score("language", language_score)

            if language_score < 100:
                mandatory_failures.append("language")

        # Licencia
        requested_license = requirements.get("license")

        if requested_license:
            repository_license = repository.get("license") or ""

            license_score = (
                100
                if repository_license.lower() == requested_license.lower()
                else 0
            )

            add_score("license", license_score)

        # Salud del proyecto
        health_score = repository.get("health_score")

        if health_score is not None:
            normalized_health = max(0, min(float(health_score), 100))
            add_score("health_score", normalized_health)

        # Similitud semántica
        if semantic_similarity is not None:
            normalized_similarity = max(
                0,
                min(float(semantic_similarity), 1),
            )

            add_score(
                "semantic_similarity",
                normalized_similarity * 100,
            )

        if applicable_weight:
            compatibility_score = sum(
                scores[criterion] * self.WEIGHTS[criterion]
                for criterion in scores
            ) / applicable_weight
        else:
            compatibility_score = 0

        return {
            "repository_id": repository.get("id"),
            "full_name": repository.get("full_name"),
            "compatibility_score": round(compatibility_score, 2),
            "criteria_scores": scores,
            "applicable_weight": applicable_weight,
            "is_compatible": not mandatory_failures,
            "mandatory_failures": mandatory_failures,
            "requirement_evaluations": [],
        }

    def rank(
        self,
        repositories: list[dict],
        requirements: dict,
        similarities: dict[int, float] | None = None,
    ) -> list[dict]:

        similarities = similarities or {}

        results = []

        for repository in repositories:
            repository_id = repository.get("id")

            result = self.evaluate(
                repository=repository,
                requirements=requirements,
                semantic_similarity=similarities.get(repository_id),
            )

            results.append(result)

        return sorted(
            results,
            key=lambda item: (
                item["is_compatible"],
                item["compatibility_score"],
            ),
            reverse=True,
        )
