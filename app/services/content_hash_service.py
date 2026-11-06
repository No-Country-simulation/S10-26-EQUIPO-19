import hashlib


class ContentHashService:

    @staticmethod
    def generate(content: str) -> str:
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def has_changed(
        current_hash: str | None,
        new_hash: str,
    ) -> bool:
        return current_hash != new_hash
