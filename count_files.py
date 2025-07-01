#!/usr/bin/env python3
# count_files.py

import os
import sys

# Ajusta aquí tu ruta de directorio:
BASE_DIR = r"C:\Users\USUARIO\Desktop\drivers"

def count_files(path):
    """Cuenta recursivamente archivos en el directorio dado."""
    total = 0
    for root, dirs, files in os.walk(path):
        total += len(files)
    return total

def main(base_dir):
    if not os.path.isdir(base_dir):
        print(f"Error: '{base_dir}' no es un directorio válido.")
        sys.exit(1)

    # Listamos solo los subdirectorios inmediatos
    for entry in os.listdir(base_dir):
        entry_path = os.path.join(base_dir, entry)
        if os.path.isdir(entry_path):
            num = count_files(entry_path)
            print(f"{entry}: {num} archivo{'s' if num != 1 else ''}")

if __name__ == "__main__":
    main(BASE_DIR)
