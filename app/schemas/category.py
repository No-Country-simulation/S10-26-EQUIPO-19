from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    name: str = Field(..., description="Nombre único de la categoría", examples=["Bases de Datos Vectoriales"])

class CategoryResponse(CategoryBase):
    id: int = Field(..., description="Identificador único de la categoría", examples=[1])
    repositories_count: int | None = Field(default=0, description="Cantidad de repositorios asociados", examples=[5])

    class Config:
        from_attributes = True