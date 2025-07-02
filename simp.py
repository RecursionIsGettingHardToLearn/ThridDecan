import os
import cv2
from skimage.metrics import structural_similarity as ssim

# Ruta principal
carpeta = r'C:\Users\Administrador\Downloads\imagen de vacas frisona - Google Search\vaca frisona identica - Google Search'
extensiones = ('.jpg', '.jpeg', '.png', '.webp')
umbral_similitud = 0.97  # entre 0.0 (muy diferentes) y 1.0 (idénticas)

archivos = []
duplicados = []

# Recolectar todas las rutas de imágenes
for carpeta_actual, _, archivos_encontrados in os.walk(carpeta):
    for archivo in archivos_encontrados:
        if archivo.lower().endswith(extensiones):
            archivos.append(os.path.join(carpeta_actual, archivo))

# Comparar cada imagen con las siguientes
for i in range(len(archivos)):
    img1 = cv2.imread(archivos[i])
    if img1 is None:
        continue
    img1 = cv2.resize(img1, (224, 224))
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

    for j in range(i + 1, len(archivos)):
        img2 = cv2.imread(archivos[j])
        if img2 is None:
            continue
        img2 = cv2.resize(img2, (224, 224))
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        score, _ = ssim(img1_gray, img2_gray, full=True)
        if score >= umbral_similitud:
            os.remove(archivos[j])
            duplicados.append(archivos[j])
            print(f"🗑️ Eliminado por SSIM ({score:.3f}): {archivos[j]}")

print(f"\n✅ Total duplicados visuales eliminados por SSIM: {len(duplicados)}")
