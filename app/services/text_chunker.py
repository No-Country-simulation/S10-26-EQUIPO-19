
import re
import tiktoken


class TextChunker:

    def __init__(
        self,
        max_tokens: int = 500,
        overlap: int = 75,
        min_tokens: int = 50,
    ):
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        if overlap < 0 or overlap >= max_tokens:
            raise ValueError("overlap must be between 0 and max_tokens")

        if min_tokens < 0 or min_tokens > max_tokens:
            raise ValueError("min_tokens must be between 0 and max_tokens")

        self.max_tokens = max_tokens
        self.overlap = overlap
        self.min_tokens = min_tokens

        self.encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))

    def chunk(self, content: str) -> list[dict]:
        if not content or not content.strip():
            return []

        sections = self._extract_sections(content)

        chunks = []

        for section in sections:
            section_chunks = self._chunk_section(section)

            for item in section_chunks:
                item["chunk_index"] = len(chunks)
                chunks.append(item)

        return chunks

    def _extract_sections(self, content: str) -> list[dict]:
        sections = []

        heading_stack = []
        current_lines = []
        current_path = []

        def save_section():
            body = "\n".join(current_lines).strip()

            if body:
                sections.append({
                    "section": current_path[-1]["title"]
                    if current_path else "Introduction",
                    "section_path": [
                        item["title"] for item in current_path
                    ],
                    "content": body,
                })

        for line in content.splitlines():
            match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)

            if match:
                save_section()

                level = len(match.group(1))
                title = match.group(2).strip()

                heading_stack = [
                    item for item in heading_stack
                    if item["level"] < level
                ]

                heading_stack.append({
                    "level": level,
                    "title": title,
                })

                current_path = list(heading_stack)
                current_lines = []

            else:
                current_lines.append(line)

        save_section()

        return sections

    @staticmethod
    def _split_blocks(content: str) -> list[str]:
        blocks = []
        current = []
        inside_code = False
        fence = None

        for line in content.splitlines():
            stripped = line.strip()

            fence_match = re.match(r"^(```+|~~~+)", stripped)

            if fence_match:
                marker = fence_match.group(1)

                if not inside_code:
                    inside_code = True
                    fence = marker[0]

                elif marker[0] == fence:
                    inside_code = False
                    fence = None

            if not stripped and not inside_code:
                if current:
                    blocks.append("\n".join(current))
                    current = []

                continue

            current.append(line)

        if current:
            blocks.append("\n".join(current))

        return blocks

    def _chunk_section(self, section: dict) -> list[dict]:
        heading = "\n".join(
            f"{'#' * (index + 1)} {title}"
            for index, title in enumerate(section["section_path"])
        )

        prefix = heading + "\n\n" if heading else ""

        prefix_tokens = self.count_tokens(prefix)
        available_tokens = self.max_tokens - prefix_tokens

        if available_tokens <= 0:
            raise ValueError(
                "Section heading exceeds max_tokens"
            )

        blocks = self._split_blocks(section["content"])

        result = []
        current_tokens = []

        def save_chunk():
            nonlocal current_tokens

            if not current_tokens:
                return

            body = self.encoder.decode(current_tokens)
            text = prefix + body

            result.append({
                "content": text,
                "section": section["section"],
                "section_path": section["section_path"],
                "token_count": self.count_tokens(text),
            })

            current_tokens = current_tokens[-self.overlap:] if self.overlap else []

        for block in blocks:
            block_tokens = self.encoder.encode(block)

            if len(block_tokens) > available_tokens:
                if current_tokens:
                    save_chunk()

                # Dividir bloques demasiado grandes
                step = max(1, available_tokens - self.overlap)

                for start in range(0, len(block_tokens), step):
                    piece = block_tokens[start:start + available_tokens]

                    result.append({
                        "content": prefix + self.encoder.decode(piece),
                        "section": section["section"],
                        "section_path": section["section_path"],
                        "token_count": self.count_tokens(
                            prefix + self.encoder.decode(piece)
                        ),
                    })

                current_tokens = []
                continue

            if len(current_tokens) + len(block_tokens) > available_tokens:
                save_chunk()

            if current_tokens:
                current_tokens.extend(
                    self.encoder.encode("\n\n")
                )

            current_tokens.extend(block_tokens)

        if current_tokens:
            save_chunk()

        # Evitar fragmentos finales demasiado pequeños
        if len(result) > 1:
            last = result[-1]

            if last["token_count"] < self.min_tokens:
                previous = result[-2]
                combined = previous["content"] + "\n\n" + last["content"]

                if self.count_tokens(combined) <= self.max_tokens:
                    previous["content"] = combined
                    previous["token_count"] = self.count_tokens(combined)
                    result.pop()

        return result
