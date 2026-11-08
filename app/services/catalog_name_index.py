"""Índice de nombres del catálogo para validar herramientas mencionadas.

Se carga una vez y se refresca por TTL. No llama a Gemini: solo consulta la
tabla de repositorios ya sincronizada.
"""

import logging
import re
import time
import unicodedata

from app.database import get_supabase_client

logger = logging.getLogger(__name__)

_SELECTED_COLUMNS = "id,name,full_name,category_id,url"
_MAX_REPOSITORIES = 1000


def _normalize(value: str) -> str:
    text = unicodedata.normalize("NFKD", (value or "").lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "", text)


def _entry_from_row(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "name": row.get("name") or "",
        "full_name": row.get("full_name") or "",
        "category_id": row.get("category_id"),
        "url": row.get("url") or "",
    }


class CatalogNameIndex:

    TTL_SECONDS = 6 * 60 * 60

    def __init__(self, supabase=None, ttl_seconds: int | None = None):
        self._supabase = supabase
        self._ttl_seconds = self.TTL_SECONDS if ttl_seconds is None else ttl_seconds
        self._entries_by_key: dict[str, dict] = {}
        self._loaded = False
        self._loaded_at = 0.0

    @property
    def supabase(self):
        if self._supabase is None:
            self._supabase = get_supabase_client()

        return self._supabase

    def _is_stale(self) -> bool:
        return (
            not self._loaded
            or (time.monotonic() - self._loaded_at) > self._ttl_seconds
        )

    def _refresh(self) -> None:
        client = self.supabase
        entries: dict[str, dict] = {}

        if client is not None:
            response = (
                client.table("repositories")
                .select(_SELECTED_COLUMNS)
                .limit(_MAX_REPOSITORIES)
                .execute()
            )

            for row in response.data or []:
                entry = _entry_from_row(row)
                keys = {_normalize(entry["name"])}

                if entry["full_name"]:
                    keys.add(_normalize(entry["full_name"]))
                    keys.add(_normalize(entry["full_name"].split("/")[-1]))

                for key in keys:
                    if key:
                        entries.setdefault(key, entry)

        self._entries_by_key = entries
        self._loaded = True
        self._loaded_at = time.monotonic()

        logger.info("Catalog name index loaded: %s keys", len(entries))

    def _prefix_match(self, key: str) -> dict | None:
        if len(key) < 5:
            return None

        matches: dict[int, dict] = {}

        for entry_key, entry in self._entries_by_key.items():
            if len(entry_key) < 5:
                continue

            if entry_key.startswith(key) or key.startswith(entry_key):
                matches[entry.get("id")] = entry

        if len(matches) == 1:
            return next(iter(matches.values()))

        return None

    def _lookup_in_database(self, candidate: str) -> dict | None:
        client = self.supabase

        if client is None:
            return None

        safe = re.sub(r"[^0-9A-Za-z ._+-]", "", candidate or "").strip()

        if not safe:
            return None

        try:
            response = (
                client.table("repositories")
                .select(_SELECTED_COLUMNS)
                .ilike("name", f"%{safe}%")
                .limit(10)
                .execute()
            )
        except Exception:
            logger.exception("Failed to look up tool name in the catalog")
            return None

        wanted_key = _normalize(candidate)

        for row in response.data or []:
            entry = _entry_from_row(row)

            if _normalize(entry["name"]) == wanted_key:
                return entry

        return None

    def lookup(self, candidate: str) -> dict | None:
        """Repositorio del catálogo que corresponde al nombre, o None."""
        key = _normalize(candidate)

        if len(key) < 2:
            return None

        if self._is_stale():
            self._refresh()

        entry = self._entries_by_key.get(key)

        if entry is not None:
            return entry

        entry = self._prefix_match(key)

        if entry is not None:
            return entry

        return self._lookup_in_database(candidate)

    def alternatives(self, repository: dict, limit: int = 3) -> list[dict]:
        """Herramientas del catálogo en la misma categoría que el repositorio."""
        if not repository or not repository.get("category_id"):
            return []

        client = self.supabase

        if client is None:
            return []

        try:
            response = (
                client.table("repositories")
                .select(_SELECTED_COLUMNS)
                .eq("category_id", repository["category_id"])
                .neq("id", repository.get("id"))
                .eq("archived", False)
                .order("health_score", desc=True)
                .limit(limit)
                .execute()
            )
        except Exception:
            logger.exception("Failed to load catalog alternatives")
            return []

        return response.data or []
