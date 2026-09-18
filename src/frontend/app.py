import streamlit as st
import pandas as pd
import requests
import json
import time

# 1. Parámetros globales de la interfaz
st.set_page_config(page_title="SITOR Control Tower", layout="wide")
API_URL = "http://localhost:8000/api/v1/predict"

# 2. Inicialización de la memoria de sesión (Persistencia entre recargas)
if 'log_history' not in st.session_state:
    st.session_state.log_history = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'streaming_active' not in st.session_state:
    st.session_state.streaming_active = False
if 'connection_error' not in st.session_state:
    st.session_state.connection_error = None
if 'kpi_overrides' not in st.session_state:
    st.session_state.kpi_overrides = 0
if 'kpi_maintained' not in st.session_state:
    st.session_state.kpi_maintained = 0

def process_next_ticket(df):
    """
    Extracción de la siguiente fila del dataset, empaquetado y consumo REST.
    """
    row = df.iloc[st.session_state.current_index]
    
    # Mapeo de columnas al contrato Pydantic exigido
    payload = {
        "ticket_id": str(row.get("ticket_id", f"TKT-AUTO-{st.session_state.current_index}")),
        "raw_text": str(row.get("interaction_content", "Texto vacío de prueba debido a columna no encontrada.")),
        "human_queue": str(row.get("Assignment_Group", "UNKNOWN")),
        "human_type": str(row.get("Interaction_Type", "UNKNOWN")),
        "human_priority": str(row.get("Priority", "UNKNOWN"))
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=3)
        if response.status_code == 200:
            data = response.json()
            
            # Inyección de metadatos locales para el frontend (el backend no los devuelve para ahorrar ancho de banda)
            data['raw_excerpt'] = payload['raw_text'][:70] + "..." if len(payload['raw_text']) > 70 else payload['raw_text']
            data['h_queue'] = payload['human_queue']
            data['h_type'] = payload['human_type']
            data['h_priority'] = payload['human_priority']
            
            st.session_state.log_history.insert(0, data)
            
            if data.get('verdict') == "OVERRIDE_APPROVED":
                st.session_state.kpi_overrides += 1
            else:
                st.session_state.kpi_maintained += 1
                
            if len(st.session_state.log_history) > 10:
                st.session_state.log_history.pop()
            st.session_state.connection_error = None
        else:
            st.session_state.streaming_active = False
            st.session_state.connection_error = f"Error HTTP {response.status_code}"
            return
    except requests.exceptions.RequestException:
        st.session_state.streaming_active = False
        st.session_state.connection_error = "Conexión rechazada. Servidor inalcanzable."
        return 
        
    st.session_state.current_index += 1

# 3. Construcción del Layout
st.title("SITOR | Autonomous Ticket Interception")

# Inyección de CSS para clonar el aspecto del Mockup en Figma
st.markdown("""
<style>
.log-row { display: flex; justify-content: space-between; border-bottom: 1px solid #2B2B2B; padding: 15px 0; font-family: 'Courier New', Courier, monospace; }
.col-ticket { width: 30%; padding-right: 15px; }
.col-human { width: 25%; }
.col-sitor { width: 25%; }
.col-conf { width: 20%; text-align: right; }
.badge-override { background-color: #003300; color: #00FF00; padding: 2px 6px; font-size: 0.75em; border-radius: 3px; font-weight: bold; border: 1px solid #00FF00; }
.badge-maintained { background-color: #222222; color: #888888; padding: 2px 6px; font-size: 0.75em; border-radius: 3px; font-weight: bold; border: 1px solid #555555; }
.text-red-strike { color: #FF4444; text-decoration: line-through; display: block; font-size: 0.85em; margin-bottom: 2px; }
.text-green { color: #00FF00; display: block; font-size: 0.85em; font-weight: bold; margin-bottom: 2px; }
.text-gray { color: #888888; display: block; font-size: 0.85em; margin-bottom: 2px; }
.text-excerpt { color: #AAAAAA; font-size: 0.8em; margin-top: 8px; line-height: 1.3; }
.conf-huge-green { font-size: 1.8em; font-weight: bold; color: #00FF00; }
.conf-huge-gray { font-size: 1.8em; font-weight: bold; color: #888888; }
.header-title { color: #555555; font-size: 0.7em; letter-spacing: 1px; margin-bottom: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Live Observability [READ-ONLY]", "API Sandbox [INTERACTIVE]"])

# --- PESTAÑA 1: OBSERVABILIDAD DE FLUJOS (NOC) ---
with tab1:
    # Integración de los 4 KPIs exactos del Mockup
    total_processed = st.session_state.current_index
    tasa_automatizacion = (st.session_state.kpi_overrides / total_processed * 100) if total_processed > 0 else 0.0
    horas_liberadas = st.session_state.kpi_overrides * (3.0 / 60.0) # Simulando 3 minutos de AHT por ticket
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    col_kpi1.metric("Tickets Interceptados", f"{st.session_state.kpi_overrides}")
    col_kpi2.metric("Tasa Automatización", f"{tasa_automatizacion:.1f} %")
    col_kpi3.metric("Umbral de Seguridad", "0.75", delta="Softmax Limit", delta_color="off")
    col_kpi4.metric("Horas L2 Liberadas", f"{horas_liberadas:.1f} hrs")
    
    st.divider()

    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv("data/resultados/predicciones_holdout_roberta.csv")
            return df.fillna("UNKNOWN")
        except FileNotFoundError:
            return pd.DataFrame()
            
    df_raw = load_data()
    
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        if st.button("Iniciar / Detener Streaming"):
            st.session_state.streaming_active = not st.session_state.streaming_active
            st.session_state.connection_error = None 
            
    with col_ctrl2:
        st.write(f"Registro en proceso: {st.session_state.current_index} / {len(df_raw)}")

    if st.session_state.connection_error:
        st.error(st.session_state.connection_error)

    # Contenedor estático visual
    log_container = st.container()
    with log_container:
        # Cabeceras del Grid
        st.markdown('''
        <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #333; padding-bottom: 5px;">
            <div class="col-ticket header-title">TICKET / EXCERPT</div>
            <div class="col-human header-title">HUMAN ROUTING (ERROR)</div>
            <div class="col-sitor header-title">SITOR OVERRIDE / CORRECTED</div>
            <div class="col-conf header-title">CONFIDENCE</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Iteración de registros
        for ticket in st.session_state.log_history:
            conf_pct = ticket.get('softmax_confidence', 0) * 100
            verdict = ticket.get('verdict')
            
            if verdict == "OVERRIDE_APPROVED":
                html_block = f'''
                <div class="log-row">
                    <div class="col-ticket">
                        <strong style="color: #00FF00; font-size: 1.1em;">{ticket.get('ticket_id')}</strong><br>
                        <span class="badge-override">OVERRIDE</span>
                        <div class="text-excerpt">{ticket.get('raw_excerpt')}</div>
                    </div>
                    <div class="col-human">
                        <span class="text-red-strike">{ticket.get('h_queue')}</span>
                        <span class="text-red-strike">{ticket.get('h_type')}</span>
                        <span class="text-red-strike">{ticket.get('h_priority')}</span>
                    </div>
                    <div class="col-sitor">
                        <span class="text-green">&#8594; {ticket.get('sitor_queue')}</span>
                        <span class="text-green">{ticket.get('sitor_type')}</span>
                        <span class="text-green">{ticket.get('sitor_priority')}</span>
                    </div>
                    <div class="col-conf">
                        <div class="conf-huge-green">{conf_pct:.1f}%</div>
                        <div class="text-gray" style="font-size: 0.7em;">&#8593; OVER THRESHOLD</div>
                    </div>
                </div>
                '''
            elif verdict == "VERIFIED_MAINTAINED":
                html_block = f'''
                <div class="log-row">
                    <div class="col-ticket">
                        <strong style="color: #00FF00; font-size: 1.1em;">{ticket.get('ticket_id')}</strong><br>
                        <span class="badge-override" style="background-color: #003333; color: #00FFFF; border-color: #00FFFF;">VERIFIED</span>
                        <div class="text-excerpt">{ticket.get('raw_excerpt')}</div>
                    </div>
                    <div class="col-human">
                        <span class="text-gray" style="color: #00FFFF;">{ticket.get('h_queue')}</span>
                        <span class="text-gray" style="color: #00FFFF;">{ticket.get('h_type')}</span>
                        <span class="text-gray" style="color: #00FFFF;">{ticket.get('h_priority')}</span>
                    </div>
                    <div class="col-sitor">
                        <span class="text-gray" style="font-size: 0.8em; padding: 2px 5px; border: 1px solid #333; border-radius: 3px;">NO CHANGE (AGREEMENT)</span>
                    </div>
                    <div class="col-conf">
                        <div class="conf-huge-green" style="color: #00FFFF;">{conf_pct:.1f}%</div>
                        <div class="text-gray" style="font-size: 0.7em;">&#10003; AI & HUMAN MATCH</div>
                    </div>
                </div>
                '''
            else:
                html_block = f'''
                <div class="log-row">
                    <div class="col-ticket">
                        <strong style="color: #888888; font-size: 1.1em;">{ticket.get('ticket_id')}</strong><br>
                        <span class="badge-maintained">HUMAN_ROUTING_MAINTAINED</span>
                        <div class="text-excerpt">{ticket.get('raw_excerpt')}</div>
                    </div>
                    <div class="col-human">
                        <span class="text-gray">{ticket.get('h_queue')}</span>
                        <span class="text-gray">{ticket.get('h_type')}</span>
                        <span class="text-gray">{ticket.get('h_priority')}</span>
                    </div>
                    <div class="col-sitor">
                        <span class="text-gray" style="font-size: 0.8em; padding: 2px 5px; border: 1px solid #333; border-radius: 3px;">NO CHANGE (PASSIVITY)</span>
                    </div>
                    <div class="col-conf">
                        <div class="conf-huge-gray">{conf_pct:.1f}%</div>
                        <div class="text-gray" style="font-size: 0.7em;">&#8595; BELOW 0.75 - PASSIVITY</div>
                    </div>
                </div>
                '''
            st.markdown(html_block, unsafe_allow_html=True)
            
    # Gestión controlada del Event Loop del Framework
    if st.session_state.streaming_active:
        if st.session_state.current_index < len(df_raw):
            process_next_ticket(df_raw)
            # Doble comprobación: si la petición falló, streaming_active pasó a False dentro de la función
            if st.session_state.streaming_active:
                time.sleep(1.5) 
                st.rerun()
        else:
            # Apagado orgánico: Fin del Dataset
            st.session_state.streaming_active = False

# --- PESTAÑA 2: CONSOLA DE AUDITORÍA REST ---
with tab2:
    st.markdown("### Consola de Inyección (API Sandbox)")
    
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        default_payload = {
            "ticket_id": "TKT-TEST-001",
            "raw_text": "El sistema SAP no permite facturar desde esta mañana. Da un dump ABAP continuo.",
            "human_queue": "GENERAL_IT",
            "human_type": "Service Request",
            "human_priority": "P3 - Low"
        }
        json_input = st.text_area("Payload del Webhook (Estructura JSON)", value=json.dumps(default_payload, indent=4), height=250)
        btn_post = st.button("Ejecutar POST /predict", type="primary")
        
    with col_der:
        if btn_post:
            try:
                parsed_payload = json.loads(json_input)
                
                start_req = time.time()
                response = requests.post(API_URL, json=parsed_payload, timeout=5)
                req_latency = (time.time() - start_req) * 1000
                
                if response.status_code == 200:
                    resp_data = response.json()
                    st.success(f"HTTP 200 OK | Round-Trip Network: {req_latency:.1f} ms")
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("Veredicto SITOR", resp_data.get("verdict"))
                    col_m2.metric("Softmax Math", f"{resp_data.get('softmax_confidence', 0):.3f}")
                    col_m3.metric("Backend CPU Latency", f"{resp_data.get('latency_ms', 0):.1f} ms")
                    
                    st.json(resp_data)
                    
                elif response.status_code == 422:
                    st.error("HTTP 422 Unprocessable Entity - Contrato violado")
                    st.json(response.json())
                else:
                    st.error(f"HTTP {response.status_code} - Fallo interno")
                    st.text(response.text)
                    
            except json.JSONDecodeError:
                st.error("Error: La sintaxis no es JSON válido.")
            except requests.exceptions.ConnectionError:
                st.error("Conexión rechazada.")