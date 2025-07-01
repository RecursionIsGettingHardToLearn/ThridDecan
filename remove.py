import os
import tensorflow as tf

# Directorio base donde se encuentran las carpetas de clases
BASE_DIR = 'C:/Users/Administrador/Downloads/mie'  # Ajusta la ruta a tu directorio
VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}

# Lista para almacenar los archivos corruptos
bad_paths = []

# Recorre todas las carpetas y subcarpetas en el directorio BASE_DIR
for root, _, files in os.walk(BASE_DIR):
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        # Verifica si el archivo es una imagen válida
        if ext in VALID_EXTS:
            path = os.path.join(root, f)
            try:
                # Intenta leer la imagen
                raw = tf.io.read_file(path)
                img = tf.image.decode_image(raw, channels=3)
                _ = img.shape  # Forzar la decodificación completa
            except Exception:
                # Si hay un error al decodificar la imagen, se agrega a la lista de archivos corruptos
                bad_paths.append(path)

# Elimina los archivos corruptos
for path in bad_paths:
    try:
        os.remove(path)
        print(f"🗑️ Eliminado: {path}")
    except OSError as e:
        print(f"⚠️ No se pudo eliminar {path}: {e}")

# Resumen de archivos eliminados
print(f"Se eliminaron {len(bad_paths)} archivos corruptos de las carpetas.")
