from fastapi import APIRouter
from app.database import get_supabase_client
from app.schemas import CategoryResponse

router = APIRouter(
    prefix="/api/v1/categories",
    tags=["Categorías"],
)

OFFICIAL_TAXONOMY_CATEGORIES = [
    {"id": 1, "name": "Autenticación", "repositories_count": 0},
    {"id": 2, "name": "Base de Datos y Backend", "repositories_count": 0},
    {"id": 3, "name": "Pagos y Comercio", "repositories_count": 0},
    {"id": 4, "name": "IA y LLM", "repositories_count": 0},
    {"id": 5, "name": "Geolocalización y Logística", "repositories_count": 0},
    {"id": 6, "name": "Analítica", "repositories_count": 0},
    {"id": 7, "name": "Notificaciones y Comunicación", "repositories_count": 0},
    {"id": 8, "name": "Herramientas de Negocio", "repositories_count": 0},
    {"id": 9, "name": "Seguridad y Secretos", "repositories_count": 0},
    {"id": 10, "name": "Búsqueda", "repositories_count": 0},
    {"id": 11, "name": "Observabilidad y Monitoreo", "repositories_count": 0},
    {"id": 12, "name": "Despliegue (PaaS)", "repositories_count": 0},
    {"id": 13, "name": "Video y Tiempo Real", "repositories_count": 0},
    {"id": 14, "name": "IoT y Series de Tiempo", "repositories_count": 0},
    {"id": 15, "name": "Búsqueda Vectorial", "repositories_count": 0},
    {"id": 16, "name": "Almacenamiento de Archivos", "repositories_count": 0},
    {"id": 17, "name": "Mensajería y Colas", "repositories_count": 0},
    {"id": 18, "name": "Automatización y Workflows", "repositories_count": 0},
    {"id": 19, "name": "CMS y Contenido", "repositories_count": 0},
    {"id": 20, "name": "Feature Flags", "repositories_count": 0},
    {"id": 21, "name": "API Gateway y Proxy", "repositories_count": 0},
    {"id": 22, "name": "Herramientas para APIs", "repositories_count": 0},
    {"id": 23, "name": "Paneles Internos y Low-code", "repositories_count": 0},
    {"id": 24, "name": "UI y Componentes", "repositories_count": 0},
    {"id": 25, "name": "Educación (LMS)", "repositories_count": 0},
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
            response = (
                supabase.table("categories")
                .select("id, name, repositories(count)")
                .order("id")
                .execute()
            )
            if response.data:
                return [
                    CategoryResponse(
                        id=item["id"],
                        name=item["name"],
                        repositories_count=(
                            item["repositories"][0]["count"]
                            if item.get("repositories")
                            else 0
                        ),
                    )
                    for item in response.data
                ]
        except Exception:
            pass

    return [CategoryResponse(**cat) for cat in OFFICIAL_TAXONOMY_CATEGORIES]