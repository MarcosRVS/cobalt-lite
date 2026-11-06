@echo off
title Cobalt Lite - Servidor Local
cd /d "%~dp0"

echo ========================================================
echo          INICIANDO COBALT LITE (MODO LOCAL)
echo ========================================================
echo.
echo  Abriendo el navegador en http://localhost:5000 ...
echo  Presiona Ctrl + C en esta ventana cuando quieras cerrar la app.
echo.

start "" http://localhost:5000
python app.py

pause
