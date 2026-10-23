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

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Respuesta generada por el asistente basada en RAG")
    sources: list[ChatSource] = Field(default=[], description="Repositorios citados como fuente de la recomendación")
    suggested_questions: list[str] = Field(default=[], description="Preguntas sugeridas de seguimiento", examples=[["¿Cómo integrar Chroma con LangChain?"]])