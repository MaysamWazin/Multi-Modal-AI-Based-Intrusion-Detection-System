@echo off
echo ========================================
echo LIVE AGENT - Canli Trafik Dinleme
echo ========================================
echo.
echo [UYARI] Admin yetkisi gerekebilir!
echo.

REM Virtual environment aktif et
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment aktif
)

echo.
echo [INFO] Canli trafik dinleniyor...
echo [INFO] Ana sistem calisiyor olmali: python intelligent_ids.py
echo.

python agent\live_agent_flow.py

pause
