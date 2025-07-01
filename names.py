import os

def listar_subcarpetas(ruta):
    """
    Retorna una lista con los nombres de las carpetas
    (solo primer nivel) que hay en la ruta indicada.
    """
    try:
        return [
            nombre for nombre in os.listdir(ruta)
            if os.path.isdir(os.path.join(ruta, nombre))
        ]
    except FileNotFoundError:
        print(f"La ruta {ruta!r} no existe.")
        return []
    except PermissionError:
        print(f"No tienes permiso para acceder a {ruta!r}.")
        return []

if __name__ == "__main__":
    directorio = r"C:\Users\USUARIO\Documents\topicos_projects\modelo de vacas\https_www_kaggle.com_datasets_lukex9442_indian-bovine-breeds\Indian_bovine_breeds"
    carpetas = listar_subcarpetas(directorio)
    print("Subcarpetas encontradas:")
    for c in carpetas:
        print(f" - {c}")
