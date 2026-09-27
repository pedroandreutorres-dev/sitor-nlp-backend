import streamlit as st
import pandas as pd
import requests
import json
import time
import os
import shutil
from pathlib import Path

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SITOR | Control Tower", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# Estilos CSS Corporativos (Clon de sitor1.png y sitor2.png)
st.markdown('''
<style>
    /* Fondo principal y tipografía base */
    .stApp { background-color: #0b0e14; color: #a0aabf; font-family: 'JetBrains Mono', 'Courier New', monospace; }
    
    /* Cabecera y Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: #0b0e14; border-bottom: 1px solid #1e293b; }
    .stTabs [data-baseweb="tab"] { color: #64748b; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #10b981 !important; border-bottom: 2px solid #10b981 !important; }
    
    /* KPIs Top Row */
    .kpi-container { background-color: #0f172a; border: 1px solid #1e293b; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    .kpi-label { color: #475569; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
    .kpi-value { color: #f8fafc; font-size: 2rem; font-weight: bold; }
    .kpi-sub { color: #10b981; font-size: 0.75rem; }
    
    /* Grid de Logs (Tab 1) */
    .log-row { background-color: #0b0e14; padding: 15px 0; border-bottom: 1px solid #1e293b; display: flex; align-items: stretch; font-size: 0.85rem;}
    .col-ticket { flex: 3; padding-right: 20px; }
    .col-human { flex: 2; padding-right: 20px; }
    .col-sitor { flex: 2; padding-right: 20px; }
    .col-conf { flex: 1; text-align: right; }
    
    /* Textos y Badges */
    .text-excerpt { color: #64748b; margin-top: 8px; line-height: 1.4; font-family: sans-serif; font-size: 0.8rem; }
    .text-red-strike { color: #ef4444; text-decoration: line-through; display: block; font-family: monospace; }
    .text-green { color: #10b981; display: block; font-weight: bold; font-family: monospace; }
    .text-gray { color: #64748b; display: block; font-family: monospace; }
    .badge-override { background-color: #064e3b; color: #34d399; padding: 2px 6px; border-radius: 2px; font-size: 0.7rem; font-weight: bold; border: 1px solid #059669; }
    .badge-maintained { background-color: #1e293b; color: #94a3b8; padding: 2px 6px; border-radius: 2px; font-size: 0.7rem; font-weight: bold; border: 1px solid #334155; }
    .conf-huge-green { color: #10b981; font-size: 1.5rem; font-weight: bold; }
    .conf-huge-gray { color: #64748b; font-size: 1.5rem; font-weight: bold; }
    .header-title { font-weight: bold; color: #475569; font-size: 0.7rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; }
    
    /* Cajas estilo JSON / Payload */
    .payload-box { background-color: #0f172a; border: 1px solid #1e293b; padding: 10px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #e2e8f0; height: 350px; overflow-y: auto; }
</style>
''', unsafe_allow_html=True)

API_URL_PREDICT = "http://localhost:8000/api/v1/predict"
API_URL_EXPLAIN = "http://localhost:8000/api/v1/explain"

# Rutas absolutas a prueba de fallos (Bulletproof absolute paths)
_current_dir = Path(__file__).resolve().parent
_project_root = _current_dir.parent.parent
DIR_INBOX = _project_root / "data" / "inbox"
DIR_OUTBOX = _project_root / "data" / "outbox"
DIR_OUTBOX.mkdir(parents=True, exist_ok=True)

st.markdown('<div style="display:flex; align-items:center; gap: 15px; margin-bottom: 20px;"><h2 style="color:white; margin:0;">🛡️ SITOR</h2><span style="color:#64748b; font-size:0.9rem;">Autonomous Ticket Interception · Control Tower</span></div>', unsafe_allow_html=True)

# Inicialización de contadores de sesión para KPIs dinámicos
if 'total_procesados' not in st.session_state:
    st.session_state.total_procesados = 0
if 'total_overrides' not in st.session_state:
    st.session_state.total_overrides = 0
if 'processing_batch' not in st.session_state:
    st.session_state.processing_batch = False
if 'log_history' not in st.session_state:
    st.session_state.log_history = []

tab1, tab2 = st.tabs(["Live Observability READ-ONLY", "API Sandbox INTERACTIVE"])

# --- PESTAÑA 1: LIVE OBSERVABILITY ---
with tab1:
    # Contenedores para actualización en vivo (sin st.rerun)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    ph_kpi1 = kpi_col1.empty()
    ph_kpi2 = kpi_col2.empty()
    ph_kpi3 = kpi_col3.empty()
    ph_kpi4 = kpi_col4.empty()
    
    def render_kpis():
        intercepted = st.session_state.total_overrides
        auto_rate = (intercepted / st.session_state.total_procesados * 100) if st.session_state.total_procesados > 0 else 0.0
        time_liberated_hrs = (intercepted * 120) / 3600
        
        ph_kpi1.markdown(f'<div class="kpi-container"><div class="kpi-label">TICKETS INTERCEPTED (SESSION)</div><div class="kpi-value">{intercepted}</div><div class="kpi-sub" style="color:#64748b;">Out of {st.session_state.total_procesados} processed</div></div>', unsafe_allow_html=True)
        ph_kpi2.markdown(f'<div class="kpi-container"><div class="kpi-label">CURRENT AUTOMATION RATE</div><div class="kpi-value">{auto_rate:.1f}%</div><div class="kpi-sub" style="color:#64748b;">Live session avg</div></div>', unsafe_allow_html=True)
        ph_kpi3.markdown(f'<div class="kpi-container"><div class="kpi-label">BACK-OFFICE TIME LIBERATED</div><div class="kpi-value" style="color:#10b981;">{time_liberated_hrs:.2f} hrs</div><div class="kpi-sub" style="color:#64748b;">120 s AHT delta × volume</div></div>', unsafe_allow_html=True)
        ph_kpi4.markdown('<div class="kpi-container"><div class="kpi-label">AI PASSIVITY THRESHOLD</div><div class="kpi-value">0.85</div><div class="kpi-sub" style="color:#64748b;">Softmax min · global config</div></div>', unsafe_allow_html=True)

    archivos_inbox = list(DIR_INBOX.glob("*.json"))
    
    # Auto-arranque si hay archivos pendientes
    if archivos_inbox and not st.session_state.processing_batch:
        st.session_state.processing_batch = True
        st.rerun()

    st.markdown('<hr style="border-color:#1e293b; margin: 10px 0;">', unsafe_allow_html=True)
    
    st.markdown('''
    <div style="display: flex; justify-content: space-between;">
        <div class="col-ticket header-title">TICKET / EXCERPT</div>
        <div class="col-human header-title">HUMAN ROUTING × ERROR</div>
        <div class="col-sitor header-title">SITOR OVERRIDE ✓ CORRECTED</div>
        <div class="col-conf header-title">CONFIDENCE</div>
    </div>
    ''', unsafe_allow_html=True)
    
    ph_logs = st.empty()
    
    def render_logs():
        html_content = ""
        for ticket in reversed(st.session_state.log_history):
            conf_pct = ticket.get('softmax_confidence', 0) * 100
            verdict = ticket.get('verdict')
            if verdict == "OVERRIDE_APPROVED":
                html_content += f'''
                <div class="log-row">
                    <div class="col-ticket">
                        <strong style="color: #f8fafc;">● {ticket.get('ticket_id')}</strong> <span style="color:#475569; font-size:0.7rem;">JUST NOW</span><br>
                        <span class="badge-override">OVERRIDE</span>
                        <div class="text-excerpt">{ticket.get('raw_excerpt')}</div>
                    </div>
                    <div class="col-human">
                        <span class="text-gray" style="font-size:0.7rem;">HUMAN ROUTING</span>
                        <span class="text-red-strike">{ticket.get('h_queue')}</span>
                        <span class="text-red-strike">{ticket.get('h_type')}</span>
                        <span class="text-red-strike">{ticket.get('h_priority')}</span>
                    </div>
                    <div class="col-sitor">
                        <span class="text-green" style="font-size:0.7rem;">SITOR OVERRIDE</span>
                        <span class="text-green">→ {ticket.get('sitor_queue')}</span>
                        <span class="text-green">{ticket.get('sitor_type')}</span>
                        <span class="text-green">{ticket.get('sitor_priority')}</span>
                    </div>
                    <div class="col-conf">
                        <div class="conf-huge-green">{conf_pct:.1f}%</div>
                        <div class="text-green" style="font-size: 0.7rem;">↑ OVER THRESHOLD</div>
                    </div>
                </div>
                '''
            else:
                reason_text = "⊙ Verified by SITOR (Match)" if conf_pct >= 85 else "⊙ Confidence below passivity floor"
                conf_badge = "✓ VERIFIED" if conf_pct >= 85 else "↓ BELOW 0.85"
                html_content += f'''
                <div class="log-row">
                    <div class="col-ticket">
                        <strong style="color: #64748b;">● {ticket.get('ticket_id')}</strong> <span style="color:#475569; font-size:0.7rem;">JUST NOW</span><br>
                        <span class="badge-maintained">HUMAN_ROUTING_MAINTAINED</span>
                        <div class="text-excerpt">{ticket.get('raw_excerpt')}</div>
                    </div>
                    <div class="col-human">
                        <span class="text-gray" style="font-size:0.7rem;">ROUTING DECISION</span>
                        <span class="text-gray">{ticket.get('h_queue')}</span>
                        <span class="text-gray">{ticket.get('h_type')} · {ticket.get('h_priority')}</span>
                        <span class="text-gray" style="font-size:0.7rem; margin-top:5px;">{reason_text}</span>
                    </div>
                    <div class="col-sitor">
                        <span class="badge-maintained" style="background:transparent;">NO CHANGE</span>
                    </div>
                    <div class="col-conf">
                        <div class="conf-huge-gray">{conf_pct:.1f}%</div>
                        <div class="text-gray" style="font-size: 0.7rem;">{conf_badge}</div>
                    </div>
                </div>
                '''
        ph_logs.markdown(html_content, unsafe_allow_html=True)
        
    # Inicial render
    render_kpis()
    render_logs()

    # Event Loop Spooling
    if st.session_state.processing_batch and archivos_inbox:
        archivo_actual = archivos_inbox[0]
        try:
            with open(archivo_actual, 'r', encoding='utf-8') as f:
                lote = json.load(f)
                
            for item in lote:
                raw_tripleta = item.get('target_tripleta') or 'Customer Service_Service Request_P3 - Low'
                tripleta = raw_tripleta.split('_')
                h_queue = tripleta[0] if len(tripleta) > 0 else "UNKNOWN"
                h_type = tripleta[1] if len(tripleta) > 1 else "UNKNOWN"
                h_priority = tripleta[2] if len(tripleta) > 2 else "UNKNOWN"
                texto_raw = item.get('body', item.get('full_text', ''))
                
                payload = {
                    "ticket_id": item.get('ticket_id', 'UNKNOWN'),
                    "raw_text": texto_raw,
                    "human_queue": h_queue,
                    "human_type": h_type,
                    "human_priority": h_priority
                }
                
                try:
                    resp = requests.post(API_URL_PREDICT, json=payload, timeout=2)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.total_procesados += 1
                        if data.get('verdict') == "OVERRIDE_APPROVED":
                            st.session_state.total_overrides += 1
                            
                        st.session_state.log_history.append({
                            'ticket_id': payload['ticket_id'],
                            'raw_excerpt': texto_raw[:120] + "..." if len(texto_raw) > 120 else texto_raw,
                            'h_queue': h_queue,
                            'h_type': h_type,
                            'h_priority': h_priority,
                            'verdict': data.get('verdict'),
                            'softmax_confidence': data.get('softmax_confidence'),
                            'sitor_queue': data.get('sitor_queue'),
                            'sitor_type': data.get('sitor_type'),
                            'sitor_priority': data.get('sitor_priority')
                        })
                        if len(st.session_state.log_history) > 10:
                            st.session_state.log_history.pop(0)
                        
                        # Actualizar interfaz EN VIVO
                        render_kpis()
                        render_logs()
                        
                except Exception as e:
                    st.error(f"API Error: {e}")
                    st.session_state.processing_batch = False
                    st.stop()
                    
                time.sleep(0.1) # Pausa dramática para simular procesamiento en vivo sin agotar CPU visualmente
                
            shutil.move(str(archivo_actual), str(DIR_OUTBOX / archivo_actual.name))
            st.session_state.processing_batch = False
            st.rerun()
            
        except Exception as e:
            st.error(f"JSON Error: {e}")
            st.session_state.processing_batch = False

# --- PESTAÑA 2: API SANDBOX ---
with tab2:
    st.markdown('<div style="margin-bottom:20px;"></div>', unsafe_allow_html=True)
    
    # Grid principal 50/50
    col_req, col_res = st.columns(2)
    
    with col_req:
        st.markdown('<div class="header-title">● REQUEST PAYLOAD</div>', unsafe_allow_html=True)
        
        # Interfaz Humana
        txt_body = st.text_area("Cuerpo del Ticket (raw_text)", height=100, value="URGENT — SAP SM50 ABAP dump since 06:00 CET. All batch jobs blocked. Payroll run failing for 240 employees. Need immediate escalation.")
        
        # Extraer tripletas reales del modelo para los selectores
        # Ruta relativa limpia al diccionario de entrenamiento
        mapping_path = _project_root / "src" / "models" / "roberta_corporativo" / "label_mapping.json"
        
        colas, tipos, prioridades = ["UNKNOWN"], ["UNKNOWN"], ["UNKNOWN"]
        if mapping_path.exists():
            with open(mapping_path, "r", encoding="utf-8") as f:
                mapping = json.load(f)
            c_set, t_set, p_set = set(), set(), set()
            for v in mapping.values():
                if v == "OUT_OF_SCOPE":
                    continue
                parts = v.split('_')
                if len(parts) == 3:
                    c_set.add(parts[0])
                    t_set.add(parts[1])
                    p_set.add(parts[2])
            colas = sorted(list(c_set))
            tipos = sorted(list(t_set))
            prioridades = sorted(list(p_set))
            
        c1, c2, c3 = st.columns(3)
        h_q = c1.selectbox("human_queue", colas)
        h_t = c2.selectbox("human_type", tipos)
        h_p = c3.selectbox("human_priority", prioridades)
        
        # Construimos JSON
        req_json = {
            "ticket_id": "TKT-8951",
            "raw_text": txt_body,
            "human_queue": h_q,
            "human_type": h_t,
            "human_priority": h_p
        }
        
        st.markdown('<div class="payload-box">' + json.dumps(req_json, indent=4) + '</div>', unsafe_allow_html=True)
        
        # Botones
        col_b1, col_b2 = st.columns([3, 1])
        with col_b1:
            btn_predict = st.button("▶ POST /API/V1/PREDICT", type="primary", use_container_width=True)
        with col_b2:
            btn_lime = st.button("🔍 XAI (LIME)", use_container_width=True)

    with col_res:
        st.markdown('<div class="header-title">● SERVER RESPONSE</div>', unsafe_allow_html=True)
        
        if btn_predict:
            start_req = time.time()
            try:
                resp = requests.post(API_URL_PREDICT, json=req_json, timeout=5)
                req_latency = (time.time() - start_req) * 1000
                if resp.status_code == 200:
                    resp_data = resp.json()
                    st.markdown('<div class="payload-box" style="border-color:#10b981;">' + json.dumps(resp_data, indent=4) + '</div>', unsafe_allow_html=True)
                    st.session_state.last_resp = resp_data
                    st.session_state.last_lat = req_latency
                else:
                    st.markdown('<div class="payload-box" style="border-color:#ef4444;">' + resp.text + '</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
        elif btn_lime:
            try:
                with st.spinner("Computando interpretabilidad LIME en servidor..."):
                    resp = requests.post(API_URL_EXPLAIN, json=req_json, timeout=45)
                    if resp.status_code == 200:
                        st.session_state.lime_html = resp.json().get('lime_html_string')
                        st.markdown('<div class="payload-box" style="border-color:#3b82f6;">LIME HTML recibido correctamente. Scroll abajo para verlo.</div>', unsafe_allow_html=True)
                    else:
                        st.error(resp.text)
            except Exception as e:
                st.error(f"Timeout LIME: {e}")
        else:
            st.markdown('<div class="payload-box" style="display:flex; align-items:center; justify-content:center; color:#475569;">Run a request to see the response</div>', unsafe_allow_html=True)
            
    st.markdown('<hr style="border-color:#1e293b; margin: 20px 0;">', unsafe_allow_html=True)
    
    # Métricas Inferiores
    if 'last_resp' in st.session_state:
        d = st.session_state.last_resp
        cm1, cm2, cm3 = st.columns(3)
        with cm1:
            st.markdown(f'<div class="kpi-container"><div class="kpi-label">INFERENCE VERDICT</div><div class="kpi-value" style="font-size:1.5rem; color:{"#10b981" if d.get("verdict") == "OVERRIDE_APPROVED" else "#64748b"};">{d.get("verdict")}</div></div>', unsafe_allow_html=True)
        with cm2:
            st.markdown(f'<div class="kpi-container"><div class="kpi-label">SOFTMAX CONFIDENCE</div><div class="kpi-value" style="font-size:1.5rem;">{d.get("softmax_confidence", 0)*100:.2f}%</div></div>', unsafe_allow_html=True)
        with cm3:
            st.markdown(f'<div class="kpi-container"><div class="kpi-label">SERVER LATENCY</div><div class="kpi-value" style="font-size:1.5rem;">{st.session_state.get("last_lat", 0):.1f} ms</div></div>', unsafe_allow_html=True)
            
        # Refuerzo visual del cambio
        if d.get("verdict") == "OVERRIDE_APPROVED":
            st.markdown(f'''
            <div class="log-row" style="margin-top: 10px; border: 1px solid #10b981; border-radius: 4px; padding: 15px;">
                <div class="col-human">
                    <span class="text-gray" style="font-size:0.7rem;">ORIGINAL (ERROR HUMANO)</span>
                    <span class="text-red-strike">{req_json['human_queue']}</span>
                    <span class="text-red-strike">{req_json['human_type']}</span>
                    <span class="text-red-strike">{req_json['human_priority']}</span>
                </div>
                <div class="col-sitor">
                    <span class="text-green" style="font-size:0.7rem;">NUEVO ENRUTAMIENTO (SITOR)</span>
                    <span class="text-green">→ {d.get("sitor_queue")}</span>
                    <span class="text-green">{d.get("sitor_type")}</span>
                    <span class="text-green">{d.get("sitor_priority")}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        elif d.get("verdict") == "VERIFIED_MAINTAINED":
            st.markdown('<div style="margin-top: 10px; color:#10b981; font-family:monospace;">✓ SITOR coincide con la decisión humana. No se requieren cambios.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="margin-top: 10px; color:#64748b; font-family:monospace;">↓ Confianza insuficiente (< 0.85). Se mantiene la decisión humana por seguridad.</div>', unsafe_allow_html=True)
            
    # Visor LIME Condicional
    if 'lime_html' in st.session_state and st.session_state.lime_html and btn_lime:
        st.markdown('<div class="header-title">🔍 LIME EXPLANATION RENDER</div>', unsafe_allow_html=True)
        import streamlit.components.v1 as components
        components.html(st.session_state.lime_html, height=400, scrolling=True)