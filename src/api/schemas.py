from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

# --- CONTRATO DE ENTRADA (Payload inyectado por el CRM) ---
class TicketInput(BaseModel):
    
    ticket_id: str = Field(..., description="ID único del ticket")
    raw_text: str = Field(..., description="Cuerpo del texto libre")
    
    # Tripleta original (Cortafuegos de Pasividad)
    human_queue: str
    human_type: str
    human_priority: str
    
    # Metadatos Opcionales
    created_at: Optional[str] = None
    agent_id: Optional[str] = None

    # Validador exclusivo para texto (mayor densidad exigida)
    @field_validator('raw_text')
    @classmethod
    def validate_raw_text(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 10:
            raise ValueError("El texto libre no puede ser espacio en blanco ni tener menos de 10 caracteres reales.")
        return cleaned

    # Validador masivo anti-vacíos para la trazabilidad y la tripleta espejo
    @field_validator('ticket_id', 'human_queue', 'human_type', 'human_priority')
    @classmethod
    def validate_vital_strings(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 1:
            raise ValueError("Las variables de trazabilidad y tipificación no pueden estar vacías ni contener solo espacios.")
        return cleaned


# --- CONTRATO DE SALIDA (Payload devuelto por SITOR) ---
class TicketResponse(BaseModel):
    
    ticket_id: str
    
    # Restricción categórica de decisión
    verdict: Literal["OVERRIDE_APPROVED", "HUMAN_ROUTING_MAINTAINED", "VERIFIED_MAINTAINED"]
    
    # Fronteras Matemáticas y Físicas Estrictas
    softmax_confidence: float = Field(..., ge=0.0, le=1.0, description="Probabilidad pura entre 0 y 1")
    latency_ms: float = Field(..., ge=0.0, description="Tiempo de inferencia positivo")
    
    # Tripleta Resolutiva Final
    sitor_queue: str
    sitor_type: str
    sitor_priority: str