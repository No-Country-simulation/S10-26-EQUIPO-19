from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Rol del emisor: 'user' o 'assistant'", examples=["user"])
    content: str = Field(..., description="Mensaje de la conversación", examples=["Hola, busco una base vectorial"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pregunta o consulta del usuario", examples=["¿Qué base vectorial me recomiendan para Python?"])
    conversation_history: list[ChatMessage] = Field(default=[], description="Historial previo de la conversación para mantener contexto")


class ChatSource(BaseModel):
    repository_id: int = Field(..., description="ID del repositorio referenciado", examples=[102])
    name: str = Field(..., description="Nombre del repositorio", examples=["chroma"])
    full_name: str = Field(..., description="Owner y repo", examples=["chroma-core/chroma"])
    url: str = Field(..., description="URL al repositorio", examples=["https://github.com/chroma-core/chroma"])
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Puntaje de similitud semántica (0 a 1)", examples=[0.94])


class ArchitectureComponent(BaseModel):
    key: str = Field(..., description="Identificador del nodo dentro de la respuesta", examples=["vectores"])
    repository_id: int = Field(..., description="ID del repositorio en el catálogo", examples=[102])
    full_name: str = Field(..., description="Owner y repo", examples=["chroma-core/chroma"])
    role: str = Field(..., description="Función del componente en la arquitectura")
    license: str | None = Field(default=None, description="Licencia del repositorio", examples=["Apache-2.0"])
    health_status: str | None = Field(default=None, description="Estado de mantenimiento", examples=["Activo"])
    justification: str = Field(..., description="Justificación técnica de la elección")


class ArchitectureConnection(BaseModel):
    from_node: str = Field(..., alias="from", serialization_alias="from", description="Nodo origen", examples=["docs"])
    to_node: str = Field(..., alias="to", serialization_alias="to", description="Nodo destino", examples=["vectores"])
    label: str = Field(..., description="Descripción de la conexión")
    verified: bool = Field(..., description="Indica si corresponde a una idea aprobada del catálogo")
    integration_code: str | None = Field(default=None, description="Código de la idea si es verificada", examples=["INT-047"])

    model_config = {"populate_by_name": True}


class ArchitectureProposal(BaseModel):
    components: list[ArchitectureComponent] = Field(default=[], description="Componentes de la arquitectura propuesta")
    connections: list[ArchitectureConnection] = Field(default=[], description="Conexiones entre los componentes")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Respuesta generada por el asistente basada en RAG")
    sources: list[ChatSource] = Field(default=[], description="Repositorios citados como fuente de la recomendación")
    suggested_questions: list[str] = Field(default=[], description="Preguntas sugeridas de seguimiento", examples=[["¿Cómo integrar Chroma con LangChain?"]])
    architecture: ArchitectureProposal | None = Field(default=None, description="Arquitectura estructurada para el visualizador")