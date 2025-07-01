import os
import uuid

def rename_all_jpg_files(directory):
    """
    Renombra todos los archivos .jpg en el directorio especificado
    a nombres aleatorios basados en UUID4, manteniendo la extensión .jpg.
    """
    count = 0
    for filename in os.listdir(directory):
        if not filename.lower().endswith('.jpg'):
            continue

        old_path = os.path.join(directory, filename)
        new_name = f"{uuid.uuid4().hex}.jpg"
        new_path = os.path.join(directory, new_name)

        try:
            os.rename(old_path, new_path)
            print(f"{filename} → {new_name}")
            count += 1
        except Exception as e:
            print(f"Error renombrando {filename}: {e}")

    print(f"Total de archivos renombrados: {count}")

if __name__ == "__main__":
    # Ajusta esta ruta a tu carpeta con .jpg
    DIRECTORY = r"C:\Users\USUARIO\Desktop\trash\fat"
    rename_all_jpg_files(DIRECTORY)
