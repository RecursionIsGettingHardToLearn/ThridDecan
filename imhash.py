import os
from PIL import Image
import imagehash

# Ruta donde buscar duplicados visuales
carpeta = r'C:\Users\Administrador\Downloads\new'

# Extensiones válidas
extensiones = ('.jpg', '.jpeg', '.png', '.webp')

# Umbral de similitud (0 = idénticas, ≤ 5 = casi iguales)
umbral = 0

# Guardar hashes visuales
hashes = {}
duplicados = []

for carpeta_actual, _, archivos in os.walk(carpeta):
    for archivo in archivos:
        if archivo.lower().endswith(extensiones):
            ruta = os.path.join(carpeta_actual, archivo)
            try:
                img = Image.open(ruta)
                hash_img = imagehash.phash(img)

                duplicado = False
                for hash_existente, ruta_existente in hashes.items():
                    if abs(hash_img - hash_existente) <= umbral:
                        os.remove(ruta)
                        duplicados.append((ruta, ruta_existente))
                        print("🗑️ Eliminado:", ruta)
                        print("   ↪️ Se parecía a:", ruta_existente)
                        duplicado = True
                        break

                if not duplicado:
                    hashes[hash_img] = ruta

            except Exception as e:
                print(f"⚠️ Error procesando {archivo}: {e}")

print(f"\n✅ Proceso completado. Total duplicados visuales eliminados: {len(duplicados)}")
