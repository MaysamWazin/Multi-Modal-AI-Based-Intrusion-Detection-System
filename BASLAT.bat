@echo off
echo ========================================
echo INTELLIGENT IDS - Baslatiliyor...
echo ========================================
echo.

REM Virtual environment aktif et (varsa)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment aktif
) else (
    echo [INFO] Virtual environment bulunamadi, global Python kullaniliyor
)

echo.
echo [INFO] Sistem baslatiliyor...
echo [INFO] Dashboard: http://127.0.0.1:8000/dashboard
echo.
echo Cikmak icin Ctrl+C basin
echo.

python intelligent_ids.py

pause
