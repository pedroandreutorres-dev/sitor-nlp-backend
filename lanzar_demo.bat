@echo off
echo ========================================================
echo        SITOR - STARTUP SCRIPT (MICROSERVICIOS)
echo ========================================================
echo.

echo [1/2] Levantando el Motor de Inferencia (FastAPI)...
echo Abriendo en una nueva ventana aislada...
start "SITOR Backend (FastAPI)" cmd /k "call .venv\Scripts\activate && uvicorn src.api.main:app --host 127.0.0.1 --port 8000"

echo.
echo Esperando 8 segundos para que PyTorch y LIME carguen los pesos en RAM...
timeout /t 8 /nobreak >nul

echo.
echo [2/2] Levantando el Cuadro de Mando QA (Streamlit)...
start "SITOR Frontend (Streamlit)" cmd /k "call .venv\Scripts\activate && streamlit run src/frontend/app.py"

echo.
echo Despliegue completado con exito.
echo El navegador deberia abrirse automaticamente.
echo Puedes cerrar esta ventana de control.
pause
