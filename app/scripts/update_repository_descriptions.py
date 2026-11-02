
import csv
from pathlib import Path

from app.database import get_supabase_client


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "descripciones_es.csv"

BATCH_SIZE = 100


def read_csv():
    """Lee las descripciones del CSV."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {CSV_PATH}"
        )

    with CSV_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def update_descriptions(supabase, rows):
    """Actualiza exclusivamente description_es."""

    updated = 0
    not_found = []
    errors = []

    for row in rows:
        full_name = row["full_name"].strip()
        description_es = row["description_es"].strip()

        if not full_name:
            errors.append("Registro sin full_name")
            continue

        if not description_es:
            errors.append(
                f"Descripción vacía para {full_name}"
            )
            continue

        try:
            response = (
                supabase.table("repositories")
                .update({
                    "description_es": description_es
                })
                .eq("full_name", full_name)
                .execute()
            )

            if response.data:
                updated += 1
            else:
                not_found.append(full_name)

        except Exception as e:
            errors.append(f"{full_name}: {e}")

    return updated, not_found, errors


def main():
    print("Iniciando actualización de descripciones...\n")

    supabase = get_supabase_client()

    if not supabase:
        raise RuntimeError(
            "No se pudo conectar con Supabase."
        )

    rows = read_csv()

    print(f"Registros encontrados en CSV: {len(rows)}")

    updated, not_found, errors = update_descriptions(
        supabase,
        rows
    )

    print("\n========== RESULTADO ==========")
    print(f"Actualizados: {updated}")
    print(f"No encontrados: {len(not_found)}")
    print(f"Errores: {len(errors)}")

    if not_found:
        print("\nRepositorios no encontrados:")
        for name in not_found:
            print(f" - {name}")

    if errors:
        print("\nErrores:")
        for error in errors:
            print(f" - {error}")

    print("\nProceso finalizado.")


if __name__ == "__main__":
    main()
