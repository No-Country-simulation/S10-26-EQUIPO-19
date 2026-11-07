
import re


class ReadmeProcessor:

    CODE_BLOCK_PATTERN = re.compile(
        r"(```.*?```|~~~.*?~~~)",
        re.DOTALL
    )

    BADGE_PATTERN = re.compile(
        r"\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)"
    )

    IMAGE_PATTERN = re.compile(
        r"!\[([^\]]*)\]\(([^)]*)\)"
    )

    COMMENT_PATTERN = re.compile(
        r"<!--.*?-->",
        re.DOTALL
    )

    DECORATIVE_PATTERNS = (
        "shields.io",
        "badge",
        "logo.svg",
    )

    def process(self, content: str) -> str:
        if not content:
            return ""

        # Proteger bloques de código
        content, code_blocks = self._extract_code_blocks(content)

        # Eliminar comentarios HTML
        content = self.COMMENT_PATTERN.sub("", content)

        # Eliminar badges
        content = self.BADGE_PATTERN.sub("", content)

        # Procesar imágenes
        content = self.IMAGE_PATTERN.sub(
            self._process_image,
            content
        )

        # Normalizar líneas
        content = "\n".join(
            line.rstrip() for line in content.splitlines()
        )

        # Reducir líneas vacías consecutivas
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Restaurar bloques de código
        content = self._restore_code_blocks(
            content,
            code_blocks
        )

        return content.strip()

    def _extract_code_blocks(self, content: str):
        code_blocks = []

        def replace(match):
            placeholder = f"CODEBLOCKPLACEHOLDER{len(code_blocks)}"
            code_blocks.append(match.group(0))
            return placeholder

        content = self.CODE_BLOCK_PATTERN.sub(
            replace,
            content
        )

        return content, code_blocks

    @staticmethod
    def _restore_code_blocks(content: str, code_blocks: list[str]) -> str:
        for index, block in enumerate(code_blocks):
            placeholder = f"CODEBLOCKPLACEHOLDER{index}"
            content = content.replace(placeholder, block)

        return content

    def _process_image(self, match: re.Match) -> str:
        alt_text = match.group(1).strip()
        image_url = match.group(2).strip().lower()

        if any(
            pattern in image_url
            for pattern in self.DECORATIVE_PATTERNS
        ):
            return ""

        return alt_text
