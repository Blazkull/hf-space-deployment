# 🚀 Despliegue de la API del Chatbot en Hugging Face Spaces

Esta carpeta contiene la implementación del "Cerebro" de tu chatbot como una API dedicada 24/7 con soporte para **Streaming**.

## 🛠️ Configuración del Space

1. Crea un nuevo Space en Hugging Face:
   - **Name:** `chatbot_solicitudes_cul_api`
   - **SDK:** **Docker** (Blank/None)
2. En **Settings -> Variables and secrets**, agrega:
   - `HF_TOKEN`: Tu token de lectura de Hugging Face.
   - (El hardware puede ser el Free tier de CPU/RAM).

## 📥 Cómo subir los cambios

Desde la terminal en esta carpeta (`apps/ai-training/hf-space-deployment`):

```powershell
# 1. Clona tu repositorio (solo la primera vez)
git clone https://huggingface.co/spaces/TU_USUARIO/chatbot_solicitudes_cul_api repo-remoto

# 2. Sincroniza y empuja a producción usando el script automático
.\sync_to_hf.ps1
```

## 🔌 Conexión con el Backend

Una vez que el Space esté en estado **Running**, la URL de tu API será algo como:
`https://TU_USUARIO-chatbot-solicitudes-cul-api.hf.space/generate`

Debes colocar esta URL en el `.env` del backend principal cuando lo construyamos en el Sprint 3.

---
**Nota:** Esta API responde en modo Stream (texto plano) para que el frontend pueda mostrar las palabras a medida que se generan.
