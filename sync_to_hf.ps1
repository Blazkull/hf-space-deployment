# Sincronización con Hugging Face Space (Git)

# Instrucciones:
# 1. Abre PowerShell en esta carpeta: `apps/ai-training/hf-space-deployment`
# 2. Si no has clonado el repositorio, ejecuta: 
#    git clone https://huggingface.co/spaces/Jeacosta37/CHATBOT_AI_SOLICITUDES repo-remoto
# 3. Luego ejecuta este script: .\sync_to_hf.ps1

if (Test-Path .\repo-remoto\.git) {
    Write-Host "Copiando archivos al repositorio remoto..." -ForegroundColor Cyan
    Copy-Item .\app.py .\repo-remoto\ -Force
    Copy-Item .\Dockerfile .\repo-remoto\ -Force
    Copy-Item .\requirements.txt .\repo-remoto\ -Force
    
    cd repo-remoto
    Write-Host "Enviando cambios a Hugging Face..." -ForegroundColor Green
    git add .
    git commit -m "Update: Implementación de API Streaming con FastAPI"
    git push
    cd ..
    Write-Host "¡Sincronización Completada!" -ForegroundColor Yellow
} else {
    Write-Error "No se encontró la carpeta 'repo-remoto' con un repositorio Git válido. Por favor clona tu Space primero."
}
