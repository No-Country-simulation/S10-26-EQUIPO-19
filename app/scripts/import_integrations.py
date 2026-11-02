
import csv
import json
from pathlib import Path

from app.database import get_supabase_client


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

BATCH_SIZE = 100


def read_csv(filename: str) -> list[dict]:
    """Lee un CSV y devuelve sus registros."""
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el CSV: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def parse_json_list(value: str | None):
    """Convierte una cadena JSON en una lista Python."""
    if not value:
        return None

    result = json.loads(value)

    if not isinstance(result, list):
        raise ValueError(f"Se esperaba una lista JSON: {value}")

    return result


def get_all_rows(supabase, table: str) -> list[dict]:
    """Obtiene todos los registros de una tabla, usando paginación."""
    results = []
    offset = 0

    while True:
        response = (
            supabase.table(table)
            .select("*")
            .range(offset, offset + 999)
            .execute()
        )

        batch = response.data or []
        results.extend(batch)

        if len(batch) < 1000:
            break

        offset += 1000

    return results


def upsert_batches(
    supabase,
    table: str,
    records: list[dict],
    conflict_column: str,
):
    """Inserta o actualiza registros por lotes."""
    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]

        supabase.table(table).upsert(
            batch,
            on_conflict=conflict_column,
        ).execute()


def import_business_cases(supabase):
    """Importa los casos de negocio conservando sus IDs del CSV."""
    rows = read_csv("casos_de_negocio.csv")

    records = [
        {
            "id": int(row["id"]),
            "name": row["name"].strip(),
            "description": row.get("description") or None,
        }
        for row in rows
    ]

    upsert_batches(
        supabase,
        "business_cases",
        records,
        "id",
    )

    print(f"Casos de negocio procesados: {len(records)}")


def import_integrations(supabase):
    """Importa las ideas de integración."""
    rows = read_csv("ideas_de_integracion.csv")

    records = []

    for row in rows:
        records.append({
            "code": row["code"].strip(),
            "purpose": row.get("purpose") or None,
            "integration_type": row.get("integration_type") or None,
            "triggers_or_webhooks": (
                row.get("triggers_or_webhooks") or None
            ),
            "example_snippet": (
                row.get("example_snippet") or None
            ),
            "compatible_stack": parse_json_list(
                row.get("compatible_stack")
            ),
            "difficulty": row.get("difficulty") or None,
            "documentation_url": (
                row.get("documentation_url") or None
            ),
            "how_it_connects": (
                row.get("how_it_connects") or None
            ),
            "main_steps": parse_json_list(
                row.get("main_steps")
            ),
            "status": row.get("status") or None,
        })

    upsert_batches(
        supabase,
        "integrations",
        records,
        "code",
    )

    print(f"Integraciones procesadas: {len(records)}")


def import_integration_repositories(supabase):
    """Relaciona integraciones con repositorios."""
    rows = read_csv("ideas_repositorios.csv")

    integrations = get_all_rows(supabase, "integrations")
    repositories = get_all_rows(supabase, "repositories")

    integration_map = {
        item["code"]: item["id"]
        for item in integrations
    }

    repository_map = {
        item["full_name"]: item["id"]
        for item in repositories
        if item.get("full_name")
    }

    records = []
    errors = []

    for row in rows:
        code = row["integration_code"].strip()
        full_name = row["repository_full_name"].strip()

        integration_id = integration_map.get(code)
        repository_id = repository_map.get(full_name)

        if integration_id is None:
            errors.append(f"Integración inexistente: {code}")
            continue

        if repository_id is None:
            errors.append(f"Repositorio inexistente: {full_name}")
            continue

        records.append({
            "integration_id": integration_id,
            "repository_id": repository_id,
            "role": row.get("role") or None,
        })

    if errors:
        raise ValueError(
            "Errores al resolver repositorios:\n"
            + "\n".join(errors)
        )

    upsert_batches(
        supabase,
        "integration_repositories",
        records,
        "integration_id,repository_id",
    )

    print(f"Relaciones con repositorios procesadas: {len(records)}")


def import_integration_business_cases(supabase):
    """Relaciona integraciones con casos de negocio."""
    rows = read_csv("ideas_casos_de_negocio.csv")

    integrations = get_all_rows(supabase, "integrations")
    business_cases = get_all_rows(supabase, "business_cases")

    integration_map = {
        item["code"]: item["id"]
        for item in integrations
    }

    business_case_map = {
        item["id"]: item["id"]
        for item in business_cases
    }

    records = []
    errors = []

    for row in rows:
        code = row["integration_code"].strip()
        business_case_id = int(row["business_case_id"])

        integration_id = integration_map.get(code)

        if integration_id is None:
            errors.append(f"Integración inexistente: {code}")
            continue

        if business_case_id not in business_case_map:
            errors.append(
                f"Caso de negocio inexistente: {business_case_id}"
            )
            continue

        records.append({
            "integration_id": integration_id,
            "business_case_id": business_case_id,
        })

    if errors:
        raise ValueError(
            "Errores al resolver casos de negocio:\n"
            + "\n".join(errors)
        )

    upsert_batches(
        supabase,
        "integration_business_cases",
        records,
        "integration_id,business_case_id",
    )

    print(f"Relaciones con casos procesadas: {len(records)}")


def main():
    supabase = get_supabase_client()

    if not supabase:
        raise RuntimeError("No se pudo conectar con Supabase.")

    print("Iniciando importación de integraciones...\n")

    import_business_cases(supabase)
    import_integrations(supabase)
    import_integration_repositories(supabase)
    import_integration_business_cases(supabase)

    print("\nImportación finalizada correctamente.")


if __name__ == "__main__":
    main()
