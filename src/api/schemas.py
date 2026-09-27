from pydantic import BaseModel, Field

class TicketInput(BaseModel):
    ticket_id: str = Field(..., description="Identificador único del ticket")
    raw_text: str = Field(..., description="Cuerpo del texto original del ticket")
    human_queue: str = Field(..., description="Cola de enrutamiento seleccionada por el nivel 1")
    human_type: str = Field(..., description="Tipo de operación seleccionada por el nivel 1")
    human_priority: str = Field(..., description="Prioridad asignada por el nivel 1")

class TicketResponse(BaseModel):
    ticket_id: str
    verdict: str
    softmax_confidence: float
    latency_ms: float
    sitor_queue: str
    sitor_type: str
    sitor_priority: str
