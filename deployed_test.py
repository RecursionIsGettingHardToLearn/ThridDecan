from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

from PIL import Image
from io import BytesIO
import numpy as np

app = FastAPI()

# CORS configuration (adjust origins as needed)
origins = ["http://localhost:3000", "https://mi-dominio.com", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# URL de tu servicio de TensorFlow Serving
#tf_serving_url = (
#    "https://modelo-cocina-314745621240.europe-west1.run.app"
#    "/v1/models/modelo_cocina:predict"
#)

tf_serving_url = "https://modelo-tensorflow-cattle.onrender.com/v1/models/modelo_cocina:predict"

# Lista de nombres de clase en orden
class_names = [
    "Ankole",
    "Belted Galloway",
    "Brahman",
    "Desconocido",
    "Frisona",
    "Highland"
]


# Modelo de petición para URLs vía POST
class URLRequest(BaseModel):
    url: str

# Función interna común para llamar a TF Serving
def preprocess_and_predict(arr: np.ndarray):
    payload = {"instances": [arr.tolist()]}
    # Sin usar AsyncClient aquí para simplificar, pero podrías adaptarlo
    resp = httpx.post(
        tf_serving_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30.0
    )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"TF Serving error: {resp.text}"
        )
    data = resp.json()
    preds = data.get("predictions", [])[0]
    mapped = [
        {"class_name": class_names[i], "percentage": round(float(p) * 100, 2)}
        for i, p in enumerate(preds)
    ]
    top = max(mapped, key=lambda x: x["percentage"])
    return {"predictions": mapped, "top_prediction": top}

@app.post("/predict-image")
async def predict_image(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        img = Image.open(BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Imagen inválida o corrupta")
    img = img.resize((224, 224))
    arr = np.array(img, dtype="float32") / 255.0
    return preprocess_and_predict(arr)

@app.post("/predict-url")
async def predict_url(request: URLRequest):
    # Descarga y procesa imagen desde URL (POST)
    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.get(request.url)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Error al obtener la imagen: {resp.text}")
    try:
        img = Image.open(BytesIO(resp.content)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="No se pudo leer la imagen desde la URL")
    img = img.resize((224, 224))
    arr = np.array(img, dtype="float32") / 255.0
    return preprocess_and_predict(arr)

@app.get("/predict-url-get")
async def predict_url_get(url: str = Query(..., description="URL de la imagen a predecir")):
    # Descarga y procesa imagen desde URL (GET con query param)
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Error al obtener la imagen: {resp.text}")
    try:
        img = Image.open(BytesIO(resp.content)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="No se pudo leer la imagen desde la URL")
    img = img.resize((224, 224))
    arr = np.array(img, dtype="float32") / 255.0
    return preprocess_and_predict(arr)

@app.get("/health")
def health():
    return {"status": "ok"}
