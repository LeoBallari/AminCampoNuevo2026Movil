# 1. Limpieza absoluta de variables de entornos virtuales previos
Remove-Item Env:\VIRTUAL_ENV -ErrorAction SilentlyContinue
$env:Path = ($env:Path -split ';' | Where-Object { $_ -notmatch 'venv' }) -join ';'

# 2. Asegurar que estamos en la raíz y luego ir a frontend_nuevo
cd C:\Python\AminCampoNuevo2026Movil
cd frontend_nuevo

# 3. Activar el entorno virtual nuevo
..\venv_nuevo\Scripts\activate

# 4. Forzar la ruta de Java 21 al principio del Path
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-21.0.6.7-hotspot"
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path

# 5. Limpiar la pantalla y verificar
Clear-Host
Write-Host "=============================================" -ForegroundColor Green
Write-Host " ENTORNO NUEVO ACTIVADO (Flet 0.85 + JDK 21)" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
python --version
java -version
if (Get-Command flet -ErrorAction SilentlyContinue) { flet --version } else { Write-Host "Flet: No instalado aún" }
Write-Host "=============================================" -ForegroundColor Green