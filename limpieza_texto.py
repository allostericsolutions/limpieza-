import pandas as pd
import re
import numpy as np

def limpiar_y_validar(dato):
    dato_limpio = re.sub(r'\D', '', dato).strip()
    if len(dato_limpio) == 10:
        return dato_limpio
    return None

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
                continue  # Intentar con la siguiente codificación

    elif file_extension in ["xls", "xlsx"]:
        uploaded_file.seek(0)
        reader = pd.read_excel(uploaded_file, None)
        for sheet_name, sheet in reader.items():
            num_chunks = max(1, len(sheet) // chunk_size)
            for chunk_num, chunk in enumerate(np.array_split(sheet, num_chunks)):
                total_numbers += chunk.size
                invalid_numbers_less_than_10, invalid_numbers_greater_than_10 = procesar_chunk(
                    chunk, output, invalid_numbers_less_than_10, invalid_numbers_greater_than_10
                )

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
                continue  # Intentar con la siguiente codificación

    else:
        raise ValueError("Invalid file format. Please upload a CSV, Excel, or Text file.")

    return {
        "cleaned_numbers": list(output),
        "total_numbers": total_numbers,
        "invalid_numbers_less_than_10": invalid_numbers_less_than_10,
        "invalid_numbers_greater_than_10": invalid_numbers_greater_than_10
    }
