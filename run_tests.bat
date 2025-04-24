@echo off
REM Activar el entorno virtual si existe
if exist "venv" (
    echo Activando entorno virtual...
    call venv\Scripts\activate
)
REM Instalar dependencias de pruebas
echo Instalando dependencias de pruebas...
pip install -r tests/requirements-test.txt
REM Ejecutar pruebas con cobertura
echo Ejecutando pruebas con cobertura...
pytest --cov=app tests/ -v
REM Generar informe HTML de cobertura
echo Generando informe de cobertura...
coverage html
echo Pruebas completadas. Puede ver el informe de cobertura en htmlcov\index.html
cmd /k