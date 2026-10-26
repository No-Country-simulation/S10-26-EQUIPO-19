from fastapi import APIRouter
from app.database import get_supabase_client
from app.schemas import CategoryResponse

router = APIRouter(
    prefix="/api/v1/categories",
    tags=["Categorías"],
)

OFFICIAL_TAXONOMY_CATEGORIES = [
    {"id": 1, "name": "Autenticación", "repositories_count": 12},
    {"id": 2, "name": "Base de Datos", "repositories_count": 15},
    {"id": 3, "name": "Pagos", "repositories_count": 6},
    {"id": 4, "name": "Inteligencia Artificial & LLMs", "repositories_count": 18},
    {"id": 5, "name": "Analítica", "repositories_count": 9},
    {"id": 6, "name": "Búsqueda", "repositories_count": 8},
    {"id": 7, "name": "Bases de Datos Vectoriales", "repositories_count": 5},
    {"id": 8, "name": "Herramientas de Observabilidad", "repositories_count": 4},
]


@router.get(
    "",
    response_model=list[CategoryResponse],
    summary="Listar categorías del catálogo",
    description="Retorna la taxonomía de categorías funcionales disponibles en OpenBridge para filtrado y navegación.",
)
def get_categories():
    """Obtiene el listado de categorías activas desde Supabase o la taxonomía oficial."""
    supabase = get_supabase_client()

    if supabase:
        try:
            response = supabase.table("categories").select("id, name").order("id").execute()
            if response.data:
                return [
                    CategoryResponse(
                        id=item["id"],
                        name=item["name"],
                        repositories_count=item.get("repositories_count", 0),
                    )
                    for item in response.data
                ]
        except Exception:
            pass

    return [CategoryResponse(**cat) for cat in OFFICIAL_TAXONOMY_CATEGORIES]