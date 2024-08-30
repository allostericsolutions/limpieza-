import streamlit as st
import pandas as pd
import re
from io import BytesIO
import os
from fpdf import FPDF
import tempfile
import numpy as np
from limpieza_texto import limpiar_y_procesar_archivo
from limpieza_email import limpiar_y_validar_correo  # Importar las funciones desde el módulo
from contenido import mostrar_features, mostrar_como_usar  # Importar las nuevas funciones

def generar_pdf_reporte(dataframe, info_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Data Cleanup Report", ln=True, align='C')

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

    pdf.cell(200, 10, txt="Cleaned Data", ln=True, align='C')

    for index, row in dataframe.iterrows():
        pdf.cell(200, 10, txt=row['cleaned_data'], ln=True, align='C')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)

    return tmpfile.name

def limpiar_y_validar(dato):
    dato_limpio = re.sub(r'\D', '', dato).strip()
    if len(dato_limpio) == 10:
        return dato_limpio
    return None

def process_chunk(chunk, output, tipo):
    fondos_planos = chunk.values.flatten().astype(str).tolist()
    for line in fondos_planos:
        process_line(line, output, tipo)

def process_line(line, output, tipo):
    datos = re.split(r'[,\s]+', line.strip())
    for dato in datos:
        if tipo == 'emails':
            cleaned_dato = limpiar_y_validar_correo(dato)
        else:
            cleaned_dato = limpiar_y_validar(dato)
        if cleaned_dato is not None:
            output.add(cleaned_dato)

def procesar_archivos(uploaded_files, tipo='telefonos'):
    chunk_size = 10000  # Tamaño de los chunks
    output = set()  # Usamos un set para eliminar duplicados automáticamente
    total_items = 0
    invalid_items = 0

    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split('.')[-1]

        try:
            if file_extension == "csv":
                uploaded_file.seek(0)
                for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size, header=None, error_bad_lines=False, quoting=3):  # quoting=3 para ignorar comillas
                    process_chunk(chunk, output, tipo)

            elif file_extension == "txt":
                uploaded_file.seek(0)
                # Leer archivo línea por línea
                for line in uploaded_file:
                    try:
                        process_line(line.decode('utf-8'), output, tipo)
                    except Exception as e:
                        continue  # Ignorar líneas problemáticas

            elif file_extension in ["xls", "xlsx"]:
                reader = pd.read_excel(uploaded_file, None)
                for sheet_name, sheet in reader.items():
                    num_chunks = max(1, len(sheet) // chunk_size)
                    for chunk in np.array_split(sheet, num_chunks):
                        process_chunk(chunk, output, tipo)
        except Exception as e:
            continue  # Ignorar cualquier otro error inesperado

    return output, invalid_items, total_items

def download_txt(df):
    buffer = BytesIO()
    buffer.write('\n'.join(df['cleaned_data']).encode('utf-8'))
    buffer.seek(0)
    return buffer

def generar_reporte_telefonos(total_items, n_validos, invalid_items, output):
    n_duplicados_eliminados = max(0, total_items - n_validos - invalid_items)
    reporte = {
        'Total numbers found in the file(s)': total_items,
        'Total valid numbers processed (exactly 10 digits)': n_validos,
        'Total invalid numbers': total_items - n_validos,
        'Total duplicate numbers removed': n_duplicados_eliminados
    }
    return reporte

def generar_reporte_correos(total_items, n_validos, invalid_items, output):
    n_duplicados_eliminados = max(0, total_items - n_validos - invalid_items)
    reporte = {
        'Total emails found in the file(s)': total_items,
        'Total valid emails processed': n_validos,
        'Total invalid emails': total_items - n_validos,
        'Total duplicate emails removed': n_duplicados_eliminados
    }
    return reporte

def main():
    st.title("Dr. Cleaner")

    # Mover el logo y el contacto a la barra lateral
    st.sidebar.image("https://i.imgur.com/LzPcPIk.png", caption='Allosteric Solutions', use_column_width=True)
    st.sidebar.markdown("[Visit our website](https://www.allostericsolutions.com)")
    st.sidebar.markdown("Contact: [franciscocuriel@allostericsolutions.com](mailto:franciscocuriel@allostericsolutions.com)")

    # Mostrar "Features" y "How to Use" importados del archivo contenido.py
    mostrar_features()
    mostrar_como_usar()

    # Selección del tipo de análisis
    options = st.radio("Select Data Type:", ('Phone Numbers', 'Emails'))

    uploaded_files = st.file_uploader("Drop Your Junk Here", type=["csv", "xls", "xlsx", "txt"], accept_multiple_files=True)

    if uploaded_files:
        tipo = 'emails' if options == 'Emails' else 'telefonos'
        output, invalid_items, total_items = procesar_archivos(uploaded_files, tipo)

        df = pd.DataFrame({'cleaned_data': list(output)})
        st.write("Cleaned Data:")
        st.dataframe(df)

        formato_salida = st.selectbox("Choose Your Fancy Output!", ["CSV", "Excel", "PDF", "TXT"])

        if formato_salida == "CSV":
            buffer = BytesIO()
            df.to_csv(buffer, index=False, header=False)  # Exportar a CSV sin encabezado
            buffer.seek(0)
            st.download_button(
                label="Grab your things here",
                data=buffer.getvalue(),
                file_name='cleaned_data.csv',
                mime='text/csv'
            )
        elif formato_salida == "Excel":
            buffer = BytesIO()
            df.to_excel(buffer, index=False, header=False)  # Exportar a Excel sin encabezado
            buffer.seek(0)
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
        elif formato_salida == "TXT":
            buffer = download_txt(df)
            st.download_button(
                label="Download Cleaned TXT",
                data=buffer.getvalue(),
                file_name='cleaned_data.txt',
                mime='text/plain'
            )

        n_validos = len(output)
        total_invalid_items = total_items - n_validos

        # Generar reporte específico basado en tipo de análisis
        if tipo == 'emails':
            reporte = generar_reporte_correos(total_items, n_validos, invalid_items, output)
        else:
            reporte = generar_reporte_telefonos(total_items, n_validos, invalid_items, output)

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
