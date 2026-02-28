from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer, StoppingCriteria, StoppingCriteriaList
import torch
from threading import Thread
import os

app = FastAPI(title="Chatbot Solicitudes CUL AI API", version="3.0.0")

# =========================================
# 1. CONFIGURACION DEL MODELO
# =========================================
MODEL_ID = "Jeacosta37/chatbot_solicitudes_cul"
HF_TOKEN = os.getenv("HF_TOKEN", "").strip() or None

# System Prompt v2 (CUL = Corporacion Universitaria Latinoamericana)
SYSTEM_PROMPT = (
    "Eres el Asistente Virtual de Gestion Academica de la Corporacion Universitaria "
    "Latinoamericana (CUL), ubicada en Barranquilla, Colombia. Tu mision es guiar a "
    "los estudiantes en procesos academicos como Reintegros, Homologaciones, Supletorios, "
    "Habilitaciones, Retiro de Asignaturas, Certificados, Cambio de Programa, Validaciones, "
    "Reembolsos y Congelamiento de semestre. Responde SIEMPRE en espanol formal y amable. "
    "NUNCA respondas preguntas fuera de tu dominio academico."
)

print(f"Cargando modelo {MODEL_ID}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=HF_TOKEN,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    print("Modelo cargado exitosamente!")
except Exception as e:
    print(f"Error cargando el modelo: {e}")
    model = None


# =========================================
# 2. STOPPING CRITERIA
# =========================================
class StopOnToken(StoppingCriteria):
    def __init__(self, stop_token_id):
        self.stop_token_id = stop_token_id
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        return input_ids[0][-1] == self.stop_token_id


# =========================================
# 3. SCHEMAS
# =========================================
class ChatRequest(BaseModel):
    inputs: str
    max_new_tokens: int = 512
    temperature: float = 0.2
    top_p: float = 0.9


# =========================================
# 4. ENDPOINTS
# =========================================
@app.get("/")
def health_check():
    status = "ready" if model else "loading_or_error"
    return {"status": status, "model": MODEL_ID, "version": "3.0.0"}


@app.post("/generate")
async def generate_text(request: ChatRequest):
    if not model:
        raise HTTPException(status_code=503, detail="Modelo cargando o con error.")

    # Template ChatML v2 (alineado con 02_train_colab.py)
    sys_tag = "<" + "|system|" + ">"
    usr_tag = "<" + "|user|" + ">"
    ast_tag = "<" + "|assistant|" + ">"
    eos = "<" + "/s" + ">"

    prompt = (
        f"{sys_tag}\n{SYSTEM_PROMPT}{eos}\n"
        f"{usr_tag}\n{request.inputs}{eos}\n"
        f"{ast_tag}\n"
    )

    inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    stopping_criteria = StoppingCriteriaList([StopOnToken(tokenizer.eos_token_id)])

    generation_kwargs = dict(
        inputs,
        streamer=streamer,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        do_sample=True,
        repetition_penalty=1.1,
        stopping_criteria=stopping_criteria
    )

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    def stream_generator():
        for new_text in streamer:
            yield new_text

    return StreamingResponse(stream_generator(), media_type="text/plain")
