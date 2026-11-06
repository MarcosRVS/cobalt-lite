@echo off
title Subir Cobalt Lite a GitHub
cd /d "%~dp0"

echo ========================================================
echo          SUBIENDO PROYECTO A GITHUB (MarcosRVS)
echo ========================================================
echo.
echo Si es la primera vez, se abrira una ventana o navegador
echo para autorizar tu cuenta de GitHub (Sign in with your browser).
echo.

git push -u origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo   TODO LISTO: Subido correctamente a GitHub!
    echo ========================================================
) else (
    echo [!] Hubo un detalle al subir. Revisa el mensaje arriba.
)
echo.
pause
