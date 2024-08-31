import streamlit as st
import pandas as pd
import re
from io import BytesIO
import os
from fpdf import FPDF
import tempfile
import numpy as np

# Funciones existentes para la limpieza y manejo de números de teléfono
def limpiar_y_validar(dato):
    dato_limpio = re.sub(r'\D', '', dato).strip()
    if len(dato_limpio) == 10:
        return dato_limpio
    return None

def generar_pdf_reporte(dataframe, info_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Phone Number Cleanup Report", ln=True, align='C')
    for i, (desc, count) in dataframe.iterrows():
        pdf.cell(200, 10, txt=f"{desc}: {count}", ln=True, align='L')
    pdf.add_page()
    pdf.cell(200, 10, txt="Analysis Information", ln=True, align='C')
    for info in info_df['Analysis']:
        pdf.cell(200, 10, txt=info, ln=True, align='L')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
    return tmpfile.name

def generar_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Cleaned Phone Numbers", ln=True, align='C')
    for index, row in dataframe.iterrows():
        pdf.cell(200, 10, txt=row['cleaned_data'], ln=True, align='C')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
    return tmpfile.name

# Nueva función para correos electrónicos
def validar_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def limpiar_y_validar_correo(dato):
    dato = dato.strip().lower()  # Convertir a minúsculas
    if validar_email(dato):
        return dato
    return None

# Variables globales para mantener seguimiento de los totales
total_items = 0
invalid_items = 0

# Procesamiento de archivos masivos
def procesar_archivos(uploaded_files, tipo='telefonos'):
    global total_items, invalid_items

    chunk_size = 10000  # Tamaño de los chunks
    output = set()  # Usamos un set para eliminar duplicados automáticamente
    total_items = 0
    invalid_items = 0
    
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split('.')[-1]

        try:
            if file_extension == "csv":
                uploaded_file.seek(0)
                # **Aquí se agrega on_bad_lines='skip' para omitir las líneas con errores**
                reader = pd.read_csv(uploaded_file, chunksize=chunk_size, header=None, on_bad_lines='skip')
                for chunk in reader:
                    process_chunk(chunk, output, tipo)
                    
            elif file_extension == "txt":
                uploaded_file.seek(0)
                # Leer archivo línea por línea
                for line in uploaded_file:
                    process_line(line.decode('utf-8'), output, tipo)
                
            elif file_extension in ["xls", "xlsx"]:
                reader = pd.read_excel(uploaded_file, sheet_name=None)
                for sheet_name, sheet in reader.items():
                    num_chunks = max(1, len(sheet) // chunk_size)
                    for chunk in np.array_split(sheet, num_chunks):
                        process_chunk(chunk, output, tipo)
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")
    
    return output, invalid_items, total_items

def process_chunk(chunk, output, tipo):
    global total_items, invalid_items
    fondos_planos = chunk.values.flatten().astype(str).tolist()
    for line in fondos_planos:
        process_line(line, output, tipo)

def process_line(line, output, tipo):
    global total_items, invalid_items
    datos = re.split(r'[,\s]+', line.strip())
    for dato in datos:
        total_items += 1
        if tipo == 'emails':
            cleaned_dato = limpiar_y_validar_correo(dato)
        elif tipo == 'codigos_postales':
            cleaned_dato = limpiar_codigo_postal(dato) # LLamando a la función de limpieza
        else:
            cleaned_dato = limpiar_y_validar(dato)
        if cleaned_dato is not None:
            output.add(cleaned_dato)
        else:
            invalid_items += 1

def download_excel(df):
    MAX_ROWS = 1048576  # Máximo número de filas permitido por hoja en Excel
    buffer = BytesIO()
    try:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            for i in range(0, len(df), MAX_ROWS):
                df.iloc[i:i + MAX_ROWS].to_excel(writer, sheet_name=f'Sheet{i//MAX_ROWS + 1}', index=False, header=False) 
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error exporting to Excel: {e}")
        return None

def download_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False, header=False)  # Asegúrate de que header=False está aquí
    buffer.seek(0)
    return buffer

def main():
    st.title("Dr. Cleaner")

    with st.sidebar:
        st.image("https://i.imgur.com/LzPcPIk.png", caption='Allosteric Solutions', width=360)
        st.markdown("[Visit our website](https://www.allostericsolutions.com)")
        st.markdown("Contact: [franciscocuriel@allostericsolutions.com](mailto:franciscocuriel@allostericsolutions.com)")

        with st.expander("Features"):
            st.markdown("""
            1. Removes duplicate numbers and emails
            2. Filters out invalid phone numbers and emails
            3. Eliminates non-numeric characters in phone numbers
            4. **Makes your lists sparkle**
            """)

    options = st.radio(
        "Select Data Type:",
        ('Phone Numbers', 'Emails', 'Postal Codes'))  # Agrega 'Postal Codes'

    uploaded_files = st.file_uploader("Drop Your Junk Here", type=["csv", "xls", "xlsx", "txt"], accept_multiple_files=True)
    
    if uploaded_files:
        tipo = 'emails' if options == 'Emails' else 'telefonos'
        if options == 'Postal Codes':
            tipo = 'codigos_postales'
        output, invalid_items, total_items = procesar_archivos(uploaded_files, tipo)

        df = pd.DataFrame({'cleaned_data': list(output)})
        st.write("Cleaned Data:")
        st.dataframe(df)

        formato_salida = st.selectbox("Choose Your Fancy Output!", ["CSV", "Excel", "PDF"])
        
        if formato_salida == "CSV":
            buffer = download_csv(df)
            st.download_button(
                label="Grab your things here",
                data=buffer.getvalue(),
                file_name='cleaned_data.csv',
                mime='text/csv'
            )
        elif formato_salida == "Excel":
            buffer = download_excel(df)
            if buffer:
                st.download_button(
                    label="Grab your things here",
                    data=buffer.getvalue(),
                    file_name='cleaned_data.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        elif formato_salida == "PDF":
            pdf_file_path = generar_pdf(df)
            with open(pdf_file_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Cleaned PDF",
                    data=pdf_file,
                    file_name='cleaned_data.pdf',
                    mime='application/pdf'
                )
            os.remove(pdf_file_path)

        reporte = {
            'Total items found in the file': total_items,
            'Total valid items processed': len(output),
            'Total invalid items': invalid_items,
            'Total duplicate items removed': total_items - len(output) - invalid_items
        }

        reporte_df = pd.DataFrame(list(reporte.items()), columns=['Description', 'Count'])
        info_df = pd.DataFrame({
            'Analysis': ['Analyzed by Allosteric Solutions', 'www.allostericsolutions.com', 'franciscocuriel@allostericsolutions.com']
        })

        st.write("Report Summary (you're welcome):")
        st.dataframe(reporte_df)

        formato_reporte = st.selectbox("Select report format", ["Excel", "PDF"])

        if formato_reporte == "Excel":
            reporte_file = 'report.xlsx'
            try:
                with pd.ExcelWriter(reporte_file, engine='xlsxwriter') as writer:
                    reporte_df.to_excel(writer, sheet_name='Summary', index=False)
                    info_df.to_excel(writer, sheet_name='Analysis Info', index=False)
                with open(reporte_file, "rb") as report_file:
                    st.download_button(
                        label="Retrieve Your Report Here",
                        data=report_file,
                        file_name='report.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
            except Exception as e:
                st.error(f"Error exporting report to Excel: {e}")
        elif formato_reporte == "PDF":
            pdf_report_file_path = generar_pdf_reporte(reporte_df, info_df)
            with open(pdf_report_file_path, "rb") as pdf_report_file:
                st.download_button(
                    label="Download Report (PDF)",
                    data=pdf_report_file,
                    file_name='report.pdf',
                    mime='application/pdf'
                )
            os.remove(pdf_report_file_path)

if __name__ == "__main__":
    main()
