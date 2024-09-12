import pandas as pd
import re
import numpy as np

# Función modificada para incluir depuración
def limpiar_y_validar(dato):
    print(f"Original: {dato}")  # Depuración: Mostrar el dato original

    # Detectar y normalizar la excepción específica
    if re.match(r'^\(\d{1,3}\) ', dato):
        print("Excepción detectada: Patrón (NNN) ")  # Depuración: Excepción detectada
        dato = re.sub(r'^\((\d{1,3})\) ', r'\1', dato)
        print(f"Después de aplicar excepción: {dato}")  # Depuración: Después de aplicar excepción

    dato_limpio = re.sub(r'\D', '', dato).strip()
    print(f"Limpieza General: {dato_limpio}")  # Depuración: Después de limpieza general
    
    if len(dato_limpio) == 10:
        print(f"Válido: {dato_limpio}")  # Depuración: Número válido
        return dato_limpio
    print("Inválido")  # Depuración: Número inválido
    return None

# El resto del código se mantiene igual, incluidos otros funciones que procesan los chunks y el archivo

def procesar_chunk(chunk, output, invalid_numbers_less_than_10, invalid_numbers_greater_than_10):
    fondos_planos = chunk.values.flatten().astype(str).tolist()
    for line in fondos_planos:
        numbers = re.split(r'[,\s]+', line)
        for number in numbers:
            cleaned_number = limpiar_y_validar(number)
            if cleaned_number:
                output.add(cleaned_number)
            else:
                num_digits = len(re.sub(r'\D', '', number))
                if num_digits < 10:
                    invalid_numbers_less_than_10 += 1
                elif num_digits > 10:
                    invalid_numbers_greater_than_10 += 1
    return invalid_numbers_less_than_10, invalid_numbers_greater_than_10

def limpiar_y_procesar_archivo(uploaded_file, file_extension, chunk_size=10000):
    total_numbers = 0
    invalid_numbers_less_than_10 = 0
    invalid_numbers_greater_than_10 = 0
    output = set()

    if file_extension == "csv":
        codificaciones = ['utf-8', 'latin1', 'cp1252']
        for encoding in codificaciones:
            try:
                uploaded_file.seek(0)
                reader = pd.read_csv(uploaded_file, chunksize=chunk_size, header=None, encoding=encoding)
                for chunk_num, chunk in enumerate(reader):
                    total_numbers += chunk.size
                    invalid_numbers_less_than_10, invalid_numbers_greater_than_10 = procesar_chunk(
                        chunk, output, invalid_numbers_less_than_10, invalid_numbers_greater_than_10
                    )
                break  # Salir del bucle si la codificación tiene éxito
            except UnicodeDecodeError:
                continue

    elif file_extension in ["xls", "xlsx"]:
        codificaciones = ['utf-8', 'latin1', 'cp1252']
        for encoding in codificaciones:
            try:
                uploaded_file.seek(0)
                engine = 'openpyxl' if file_extension == "xlsx" else 'xlrd'
                reader = pd.read_excel(uploaded_file, None, engine=engine)
                for sheet_name, sheet in reader.items():
                    num_chunks = max(1, len(sheet) // chunk_size)
                    for chunk_num, chunk in enumerate(np.array_split(sheet, num_chunks)):
                        total_numbers += chunk.size
                        invalid_numbers_less_than_10, invalid_numbers_greater_than_10 = procesar_chunk(
                            chunk, output, invalid_numbers_less_than_10, invalid_numbers_greater_than_10
                        )
                break  # Salir del bucle si la codificación tiene éxito
            except UnicodeDecodeError:
                continue

    elif file_extension == "txt":
        codificaciones = ['utf-8', 'latin1', 'cp1252']
        for encoding in codificaciones:
            try:
                uploaded_file.seek(0)
                total_lines = sum(1 for _ in uploaded_file)
                uploaded_file.seek(0)
                for i, line in enumerate(uploaded_file):
                    cleaned_line = line.decode(encoding).strip()
                    numbers = re.split(r'[,\s]+', cleaned_line)
                    for number in numbers:
                        total_numbers += 1
                        cleaned_number = limpiar_y_validar(number)
                        if cleaned_number:
                            output.add(cleaned_number)
                        else:
                            num_digits = len(re.sub(r'\D', '', number))
                            if num_digits < 10:
                                invalid_numbers_less_than_10 += 1
                            elif num_digits > 10:
                                invalid_numbers_greater_than_10 += 1
                break  # Salir del bucle si la codificación tiene éxito
            except UnicodeDecodeError:
                continue

    else:
        raise ValueError("Invalid file format. Please upload a CSV, Excel, or Text file.")

    return {
        "cleaned_numbers": list(output),
        "total_numbers": total_numbers,
        "invalid_numbers_less_than_10": invalid_numbers_less_than_10,
        "invalid_numbers_greater_than_10": invalid_numbers_greater_than_10
    }
