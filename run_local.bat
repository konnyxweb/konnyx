@echo off
title Konnyx — Sitio Web ^& Catalogos Digitales
echo ==================================================================
echo   Iniciando Konnyx Web ^& Catalogos Digitales...
echo   Home:               http://localhost:5000/
echo   Diseno Grafico:     http://localhost:5000/diseno-grafico
echo   Desarrollo Web:     http://localhost:5000/desarrollo-web
echo   Catalogo Digital:   http://localhost:5000/catalogo
echo   Admin Catalogos:    http://localhost:5000/admin
echo ==================================================================
echo.
if exist "env\Scripts\python.exe" (
    "env\Scripts\python.exe" app.py
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        py -3 app.py
    ) else (
        python app.py
    )
)
pause
