import pandas as pd
import re
import numpy as np

def limpiar_y_validar(dato):
    # Elimine todos los caracteres no numéricos
    dato_limpio = re.sub(r'\D', '', dato).strip()

    # Cuente el número total de dígitos en la celda original
    total_digitos = len(dato_limpio)
    
    # Si hay más de 11 dígitos, considere cada segmento separado por espacios como un número individual
    if total_digitos > 11:
        numeros_separados = re.split(r'\s+', dato)
        resultados_separados = []
        for num in numeros_separados:
            numero_limpio = re.sub(r'\D', '', num)
            if len(numero_limpio) == 10:
                resultados_separados.append(numero_limpio)
        return resultados_separados if resultados_separados else None
    else:
        # Regla general: normalizar el número
        if len(dato_limpio) == 10:
            return [dato_limpio]
        return None

def procesar_chunk(chunk, output, invalid_numbers_less_than_10, invalid_numbers_greater_than_10):
    fondos_planos = chunk.values.flatten().astype(str).tolist()
    for line in fondos_planos:
        line_digitos = re.sub(r'\D', '', line)
        if len(line_digitos) > 11:
            numbers = re.split(r'\s+', line)
        else:
            numbers = [line]
        for number in numbers:
            resultados = limpiar_y_validar(number)
            if resultados:
                for cleaned_number in resultados:
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

    if file_extension in ["csv", "txt"]:
        codificaciones = ['utf-8', 'latin1', 'cp1252']
        for encoding in codificaciones:
            try:
                uploaded_file.seek(0)
                if file_extension == "csv":
                    reader = pd.read_csv(uploaded_file, chunksize=chunk_size, header=None, encoding=encoding)
                elif file_extension == "txt":
                    reader = (line.decode(encoding).strip() for line in uploaded_file)
                for chunk_num, chunk in enumerate(reader):
                    total_numbers += chunk.size if file_extension == "csv" else 1
                    chunk_df = pd.DataFrame([chunk]) if file_extension == "txt" else chunk
                    invalid_numbers_less_than_10, invalid_numbers_greater_than_10 = procesar_chunk(
                        chunk_df, output, invalid_numbers_less_than_10, invalid_numbers_greater_than_10)
                break
            except UnicodeDecodeError:
                continue

    elif file_extension in ["xls", "xlsx"]:
        engine = 'openpyxl' if file_extension == "xlsx" else 'xlrd'
        reader = pd.read_excel(uploaded_file, engine=engine, sheet_name=None)
        for sheet_name, sheet in reader.items():
            num_chunks = max(1, len(sheet) // chunk_size)
            chunks = np.array_split(sheet, num_chunks)
            for chunk in chunks:
                total_numbers += len(chunk)
                invalid_numbers_less_than_10, invalid_numbers_greater_than_10 = procesar_chunk(
                    chunk, output, invalid_numbers_less_than_10, invalid_numbers_greater_than_10)

    else:
        raise ValueError("Invalid file format. Please upload a CSV, Excel, or Text file.")

    return {
        "cleaned_numbers": list(output),
        "total_numbers": total_numbers,
        "invalid_numbers_less_than_10": invalid_numbers_less_than_10,
        "invalid_numbers_greater_than_10": invalid_numbers_greater_than_10
    }
