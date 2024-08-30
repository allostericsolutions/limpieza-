import pandas as pd
import re
import numpy as np

def limpiar_y_validar(dato):
    # Eliminar todos los caracteres no numéricos
    dato_limpio = re.sub(r'\D', '', dato).strip()
    
    # Contar número de dígitos en la celda original
    total_digitos = len(re.sub(r'\D', '', dato))
    
    # Verificar si la celda tiene más de 11 dígitos
    if total_digitos > 11:
        # Considerar cada segmento separado por espacios como un número individual
        numeros_separados = re.split(r'\s+', dato)
        resultados_separados = []
        for num in numeros_separados:
            numero_limpio = re.sub(r'\D', '', num)
            if len(numero_limpio) == 10:
                resultados_separados.append(numero_limpio)
        return resultados_separados if resultados_separados else None
    else:
        # Regla general: Normalizar el número
        if len(dato_limpio) == 10:
            return [dato_limpio]
        return None

def procesar_chunk(chunk, output, invalid_numbers_less_than_10, invalid_numbers_greater_than_10):
    fondos_planos = chunk.values.flatten().astype(str).tolist()
    for line in fondos_planos:
        total_digitos_en_linea = sum(len(re.sub(r'\D', '', number)) for number in re.split(r'\s+', line))
        numbers = re.split(r'[,\s]+', line)
        for number in numbers:
            resultados = limpiar_y_validar(number)
            if resultados:
                for cleaned_number in resultados:
                    output.add(cleaned_number)
            else:
                num_digits = len(re.sub(r'\D', '', number))
                if num_digits < 10:
                    invalid_numbers_less_than_10 += 1
                elif num_digits > 10 and total_digitos_en_linea <= 11:
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
                if file_extension == "xlsx":
                    reader = pd.read_excel(uploaded_file, engine='openpyxl', None) 
                else:
                    reader = pd.read_excel(uploaded_file, engine='xlrd', None)
                for sheet_name, sheet in reader.items():
                    num_chunks = max(1, len(sheet) // chunk_size)
                    for chunk_num, chunk in enumerate(np.array_split(sheet, num_chunks)):
                        total_numbers += chunk.size
                        invalid_numbers_less_than_10, invalid_numbers_greater_than_10 = procesar_chunk(
                            chunk, output, invalid_numbers_less_than_10, invalid_numbers_greater_than_10
                        )
                break
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
                        resultados = limpiar_y_validar(number)
                        if resultados:
                            for cleaned_number in resultados:
                                output.add(cleaned_number)
                        else:
                            num_digits = len(re.sub(r'\D', '', number))
                            if num_digits < 10:
                                invalid_numbers_less_than_10 += 1
                            elif num_digits > 10 and total_digitos_en_linea <= 11:
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
