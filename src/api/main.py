import os
import time
import torch
import torch.nn.functional as F
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from src.api.schemas import TicketInput, TicketResponse

# Carga de hiperparámetros desde el entorno
load_dotenv()
UMBRAL_PASIVIDAD = float(os.getenv("UMBRAL_PASIVIDAD", 0.85))
MODEL_PATH = os.getenv("MODEL_PATH", "models/produccion_roberta/")

# Referencias globales en RAM
model = None
tokenizer = None
id2label = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Carga de pesos y tokenizador en memoria RAM.
    Operación bloqueante de I/O en disco durante la inicialización.
    """
    global model, tokenizer, id2label
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()  
    
    # Extracción y casteo estricto del diccionario de clases a enteros
    raw_id2label = model.config.id2label
    id2label = {int(k): v for k, v in raw_id2label.items()}
    
    yield
    
    model = None
    tokenizer = None
    id2label = None

app = FastAPI(title="API Inferencia SITOR", lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Interceptor para gestionar fallos de Pydantic y devolver HTTP 422."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Error de validación en la estructura de entrada de Pydantic."}
    )

@app.post("/api/v1/predict", response_model=TicketResponse)
def predict_ticket(payload: TicketInput):
    """Endpoint principal de inferencia unitaria REST."""
    start_time = time.perf_counter()
    
    inputs = tokenizer(
        payload.raw_text,
        truncation=True,
        max_length=256,
        padding="max_length",
        return_tensors="pt"
    )
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    
    probabilities = F.softmax(logits, dim=1)
    max_prob = torch.max(probabilities).item()
    predicted_class_id = torch.argmax(probabilities).item()
    
    latency = (time.perf_counter() - start_time) * 1000.0
    
    if max_prob >= UMBRAL_PASIVIDAD:
        macro_label = id2label.get(predicted_class_id, "")
        parts = macro_label.split('_')
        
        if len(parts) == 3:
            sitor_queue = parts[0]
            sitor_type = parts[1]
            sitor_priority = parts[2]
            
            # Auditoría de Redundancia: Si la máquina predice lo mismo que el humano, no es Override.
            if (sitor_queue.strip().lower() == payload.human_queue.strip().lower() and 
                sitor_type.strip().lower() == payload.human_type.strip().lower() and 
                sitor_priority.strip().lower() == payload.human_priority.strip().lower()):
                verdict = "VERIFIED_MAINTAINED"
            else:
                verdict = "OVERRIDE_APPROVED"
        else:
            verdict = "HUMAN_ROUTING_MAINTAINED"
            sitor_queue = payload.human_queue
            sitor_type = payload.human_type
            sitor_priority = payload.human_priority
    else:
        verdict = "HUMAN_ROUTING_MAINTAINED"
        sitor_queue = payload.human_queue
        sitor_type = payload.human_type
        sitor_priority = payload.human_priority

    return TicketResponse(
        ticket_id=payload.ticket_id,
        verdict=verdict,
        softmax_confidence=max_prob,
        latency_ms=latency,
        sitor_queue=sitor_queue,
        sitor_type=sitor_type,
        sitor_priority=sitor_priority
    )