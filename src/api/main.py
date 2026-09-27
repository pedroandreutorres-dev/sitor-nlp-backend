import os
import time
import json
import torch
import numpy as np
import torch.nn.functional as F
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from lime.lime_text import LimeTextExplainer

from src.api.schemas import TicketInput, TicketResponse

# --- CONFIGURACIÓN DE ENTORNOS Y RUTAS ---
UMBRAL_PASIVIDAD = 0.85
# Rutas relativas asumiendo que uvicorn se ejecuta desde la raíz del proyecto
DIR_TOKENIZER = Path("src/models/roberta_corporativo")
DIR_MODELO = DIR_TOKENIZER / "roberta_corporativo_final"
RUTA_MAPPING = DIR_TOKENIZER / "label_mapping.json"

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Variables globales en RAM
model = None
tokenizer = None
id2label = None
lime_explainer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Carga bloqueante de pesos y tokenizador en memoria RAM durante el inicio del servidor.
    Esencial para que el Event Loop no se bloquee luego en cada request.
    """
    global model, tokenizer, id2label, lime_explainer
    
    print("Cargando tokenizador...")
    tokenizer = AutoTokenizer.from_pretrained(str(DIR_TOKENIZER))
    
    print("Cargando modelo...")
    model = AutoModelForSequenceClassification.from_pretrained(str(DIR_MODELO)).to(device)
    model.eval()  
    
    print("Cargando diccionario de clases...")
    with open(RUTA_MAPPING, 'r', encoding='utf-8') as f:
        raw_id2label = json.load(f)
    id2label = {int(k): v for k, v in raw_id2label.items()}
    
    print("Instanciando motor LIME...")
    # Acortamos los nombres de clase para que no colapsen el SVG de LIME
    short_class_names = []
    for i in range(len(id2label)):
        c_name = id2label[i]
        if c_name == "OUT_OF_SCOPE":
            short_class_names.append("OOS")
        else:
            parts = c_name.split('_')
            if len(parts) == 3:
                q = parts[0][:8] + ".." if len(parts[0]) > 10 else parts[0]
                short_class_names.append(f"{q}_{parts[1]}_{parts[2][:3]}")
            else:
                short_class_names.append(c_name[:15])
                
    lime_explainer = LimeTextExplainer(class_names=short_class_names)
    
    print("🚀 FastAPI listo para recibir tráfico.")
    yield
    
    # Garbage collection en apagado
    model = None
    tokenizer = None
    id2label = None
    lime_explainer = None

app = FastAPI(title="SITOR API", version="1.0.0", lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Interceptor de fallos en el contrato Pydantic."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Estructura JSON inválida"}
    )

@app.post("/api/v1/predict", response_model=TicketResponse)
def predict_ticket(payload: TicketInput):
    """
    Endpoint Core: Evalúa un ticket y decide si ejecutar Override o Passivity.
    """
    start_time = time.perf_counter()
    
    inputs = tokenizer(
        payload.raw_text,
        truncation=True,
        max_length=256,
        padding="max_length",
        return_tensors="pt"
    ).to(device)
    
    with torch.no_grad():
        logits = model(**inputs).logits
    
    probabilities = F.softmax(logits, dim=1)
    max_prob = torch.max(probabilities).item()
    predicted_class_id = torch.argmax(probabilities).item()
    
    latency = (time.perf_counter() - start_time) * 1000.0
    
    if max_prob >= UMBRAL_PASIVIDAD:
        macro_label = id2label.get(predicted_class_id, "")
        
        if macro_label == "OUT_OF_SCOPE":
            # Abstención por regla de negocio: SITOR no redirige a la papelera.
            verdict = "HUMAN_ROUTING_MAINTAINED"
            sitor_queue, sitor_type, sitor_priority = payload.human_queue, payload.human_type, payload.human_priority
        else:
            parts = macro_label.split('_')
            
            if len(parts) == 3:
                sitor_queue = parts[0]
                sitor_type = parts[1]
                sitor_priority = parts[2]
                
                # Auditoría de concordancia humano vs máquina
                if (sitor_queue.strip().lower() == payload.human_queue.strip().lower() and 
                    sitor_type.strip().lower() == payload.human_type.strip().lower() and 
                    sitor_priority.strip().lower() == payload.human_priority.strip().lower()):
                    verdict = "VERIFIED_MAINTAINED"
                else:
                    verdict = "OVERRIDE_APPROVED"
            else:
                # Fallback estructural
                verdict = "HUMAN_ROUTING_MAINTAINED"
                sitor_queue, sitor_type, sitor_priority = payload.human_queue, payload.human_type, payload.human_priority
    else:
        # Passivity threshold no superado
        verdict = "HUMAN_ROUTING_MAINTAINED"
        sitor_queue, sitor_type, sitor_priority = payload.human_queue, payload.human_type, payload.human_priority

    return TicketResponse(
        ticket_id=payload.ticket_id,
        verdict=verdict,
        softmax_confidence=max_prob,
        latency_ms=latency,
        sitor_queue=sitor_queue,
        sitor_type=sitor_type,
        sitor_priority=sitor_priority
    )

def _predict_proba_lime(texts):
    """Función de inferencia en batch exigida por el framework LIME."""
    inputs = tokenizer(
        texts,
        truncation=True,
        max_length=256,
        padding="max_length",
        return_tensors="pt"
    ).to(device)
    
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=1)
        
    return probs.cpu().numpy()

@app.post("/api/v1/explain")
def explain_ticket(payload: TicketInput):
    """
    Endpoint XAI: Retorna la explicación LIME computada en servidor 
    para no sobrecargar la RAM del frontend Streamlit.
    """
    # 1. Inferir clase dominante primero
    inputs = tokenizer(payload.raw_text, return_tensors="pt", truncation=True, max_length=256).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
        predicted_class_id = torch.argmax(logits, dim=1).item()
    
    # 2. Generar perturbaciones LIME (Limitamos num_features y num_samples para rendimiento en Demo)
    exp = lime_explainer.explain_instance(
        payload.raw_text, 
        _predict_proba_lime, 
        num_features=10, 
        num_samples=30, 
        labels=[predicted_class_id]
    )
    
    # 3. Empaquetar como HTML con CSS inyectado para modo oscuro
    raw_html = exp.as_html(labels=[predicted_class_id])
    html_out = f"""
    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; color: #0f172a; font-family: sans-serif;">
        {raw_html}
    </div>
    """
    
    return JSONResponse(content={
        "ticket_id": payload.ticket_id,
        "lime_html_string": html_out,
        "predicted_class": id2label.get(predicted_class_id)
    })
