@echo off
echo ==================================================
echo   Iniciando el Servidor de Analisis Estadistico
echo ==================================================
echo.

:: Cambiar al directorio donde se encuentra este script
cd /d "%~dp0"

:: Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] No se encontro el entorno virtual en la carpeta 'venv'.
    echo Por favor, asegurese de crearlo e instalar las dependencias.
    pause
    exit /b 1
)

echo [1/2] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [2/2] Levantando servidor con Streamlit...
echo.
streamlit run app.py

pause
