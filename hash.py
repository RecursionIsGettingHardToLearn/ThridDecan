import os
import hashlib

# Ruta principal
carpeta_principal = r'C:\Users\Administrador\Downloads\mie'  # ← Ajusta si es necesario

# Extensiones válidas de imágenes
extensiones_validas = ('.jpg', '.jpeg', '.png', '.webp')

# Función para calcular el hash de un archivo
def calcular_hash(ruta, bloque=65536):
    hasher = hashlib.md5()
    with open(ruta, 'rb') as archivo:
        while bloque_lectura := archivo.read(bloque):
            hasher.update(bloque_lectura)
    return hasher.hexdigest()

# Recorremos cada subcarpeta dentro de la ruta principal
total_eliminados = 0

for carpeta_actual, _, archivos in os.walk(carpeta_principal):
    archivos_unicos = {}
    duplicados_encontrados = []

    for archivo in archivos:
        if archivo.lower().endswith(extensiones_validas):
            ruta_completa = os.path.join(carpeta_actual, archivo)
            hash_archivo = calcular_hash(ruta_completa)

            if hash_archivo in archivos_unicos:
                # Es un duplicado dentro de esta subcarpeta
                os.remove(ruta_completa)
                duplicados_encontrados.append(ruta_completa)
                print(f"🗑️ Eliminado duplicado en {carpeta_actual}: {archivo}")
                total_eliminados += 1
            else:
                archivos_unicos[hash_archivo] = ruta_completa

print(f"\n✅ Proceso terminado. Total de duplicados eliminados: {total_eliminados}")
