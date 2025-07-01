# main.py
from fastapi import FastAPI, File, UploadFile,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import cv2
import tempfile
import uvicorn  
from zipfile import ZipFile
import base64
import openai
import io
from starlette.responses import JSONResponse
import os
from dotenv import load_dotenv
load_dotenv(override=True)  
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("No se encontró la variable OPENAI_API_KEY en el entorno")
app = FastAPI()


print('la clave openai es:', os.getenv("OPENAI_API_KEY"))
# --- Configuración de CORS ---
origins = [
    "http://localhost",
    "http://localhost:8000",
    # agrega aquí los orígenes permitidos de tu frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # o ["*"] para permitir todos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/extract_frames")
async def extract_frames(video_file: UploadFile = File(...)):
    # Guardar el vídeo en un archivo temporal
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    contents = await video_file.read()
    temp.write(contents)
    temp.flush()

    cap = cv2.VideoCapture(temp.name)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = int(total_frames / fps)

    # Preparar ZIP en memoria
    zip_buf = io.BytesIO()
    with ZipFile(zip_buf, "w") as zipf:
        for sec in range(duration):
            cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
            success, frame = cap.read()
            if not success:
                continue
            # Codificar a JPEG en memoria
            ret, jpg = cv2.imencode(".jpg", frame)
            if ret:
                zipf.writestr(f"frame_{sec:02d}.jpg", jpg.tobytes())

    cap.release()
    zip_buf.seek(0)

    # Devolver ZIP como respuesta   
    return StreamingResponse(
        zip_buf,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": 'attachment; filename="frames.zip"'}
    )


@app.post("/recognize_object")
async def recognize_object(image_file: UploadFile = File(...)):
    # 1) Leer bytes de la imagen
    img_bytes = await image_file.read()
    if not img_bytes:
        raise HTTPException(status_code=400, detail="No se recibió ningún archivo")

    # 2) Codificar en Base64 y montar Data URI
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    data_uri = f"data:{image_file.content_type};base64,{img_b64}"

    # 3) Construir mensaje con parte de texto e imagen
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "¿Qué objeto principal ves en esta imagen?"},
                {"type": "image_url", "image_url": {"url": data_uri}}
            ]
        }
    ]

    # 4) Llamada a OpenAI (modelo multimodal como gpt-4o o gpt-4-vision)
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o",           # o "gpt-4-vision-preview", según tu disponibilidad
            messages=messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error llamando a OpenAI: {e}")

    # 5) Extraer y devolver la respuesta
    resultado = resp.choices[0].message.content.strip()
    return JSONResponse({"recognized_object": resultado})


print('hello')
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
