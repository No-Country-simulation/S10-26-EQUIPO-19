from pydantic import BaseModel
from app.schemas.repository import RepositoryAlert

SAAS_COPYLEFT_LICENSES = {"AGPL-3.0", "OSL-3.0"}
COPYLEFT_LICENSES = {"GPL-3.0", "GPL-2.0"}


class RiskAnalysis(BaseModel):
    has_risk: bool
    maintenance_status: str | None
    alerts: list[RepositoryAlert]


def evaluate_repository_risk(
    license: str | None = None,
    health_status: str | None = None,
    is_archived: bool = False,
) -> RiskAnalysis:
    alerts: list[RepositoryAlert] = []

    
    if is_archived:
        maint_status = "Archivado"
        alerts.append(
            RepositoryAlert(
                type="maintenance",
                title="Archivado",
                message="Repositorio archivado: ya no recibe cambios. Considera una alternativa con mantenimiento activo.",
            )
        )
    elif health_status == "Abandonado":
        maint_status = "Abandonado"
        alerts.append(
            RepositoryAlert(
                type="maintenance",
                title="Abandonado",
                message="Proyecto abandonado: lleva más de 180 días sin commits. Considera una alternativa con mantenimiento activo.",
            )
        )
    elif health_status == "En riesgo":
        maint_status = "En riesgo"
        alerts.append(
            RepositoryAlert(
                type="maintenance",
                title="En riesgo",
                message="Mantenimiento en riesgo: lleva más de 90 días sin commits. Revisa la actividad reciente antes de adoptarla.",
            )
        )
    else:
        maint_status = health_status

   
    raw_license = license.strip() if license and license.strip() else None

    if not raw_license:
        alerts.append(
            RepositoryAlert(
                type="license",
                title="Licencia no identificada",
                message="Licencia no identificada: revisa los términos de uso antes de adoptarla.",
            )
        )
    else:
        normalized_license = raw_license.upper()
        if normalized_license in SAAS_COPYLEFT_LICENSES:
            alerts.append(
                RepositoryAlert(
                    type="license",
                    title=f"Licencia {raw_license}",
                    message=f"Licencia {raw_license}: si la ofreces como servicio (SaaS) con cambios, debes publicar el código modificado.",
                )
            )
        elif normalized_license in COPYLEFT_LICENSES:
            alerts.append(
                RepositoryAlert(
                    type="license",
                    title=f"Licencia {raw_license}",
                    message=f"Licencia {raw_license}: si la modificas y la distribuyes, debes compartir el código con la misma licencia.",
                )
            )

    return RiskAnalysis(
        has_risk=len(alerts) > 0,
        maintenance_status=maint_status,
        alerts=alerts,
    )

