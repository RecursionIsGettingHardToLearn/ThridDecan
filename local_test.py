from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
import cv2

# 1) Inicializa FastAPI\app = FastAPI()

# 2) Habilita CORS para todos los orígenes (ajusta según tus necesidades)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Carga tu modelo SavedModel (ajusta la ruta si es necesario)
model = tf.keras.models.load_model("/modelo_cocina/1")

# 4) Función de preprocesado idéntica a la usada en entrenamiento
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    # Decodifica la imagen desde bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # RGB, resize y normalización
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224)).astype(np.float32) / 255.0
    return np.expand_dims(img, axis=0)

# 5) Endpoint para predicción
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # Leer el contenido del archivo subido
    contents = await file.read()
    try:
        x = preprocess_image(contents)
    except Exception:
        raise HTTPException(status_code=400, detail="Imagen inválida o corrupta")
    # Realiza la predicción
    preds = model.predict(x)[0]
    class_idx = int(np.argmax(preds))
    confidence = float(preds[class_idx])
    return {"class": class_idx, "confidence": confidence}

# 6) Instrucciones para correr:
# Guardar este archivo como main.py y ejecutar:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Luego prueba con curl o Postman:
# curl -X POST "http://localhost:8000/predict/" -F "file=@/ruta/a/tu/imagen.jpg"
