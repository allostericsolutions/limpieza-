import streamlit as st
import pandas as pd
import re
from io import BytesIO
import os
from fpdf import FPDF
import tempfile
import numpy as np
from limpieza_texto import limpiar_y_procesar_archivo
from limpieza_email import limpiar_y_validar_correo  # Importar la función desde el módulo
from contenido import mostrar_features, mostrar_como_usar  # Importar las nuevas funciones

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

    pdf.cell(200, 10, txt="Cleaned Data", ln=True, align='C')

    for index, row in dataframe.iterrows():
        pdf.cell(200, 10, txt=row['cleaned_data'], ln=True, align='C')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)

    return tmpfile.name

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
            
def main():
    st.title("Dr. Cleaner")

    # Mover el logo y el contacto a la barra lateral
    st.sidebar.image("https://i.imgur.com/LzPcPIk.png", caption='Allosteric Solutions', use_column_width=True)
    st.sidebar.markdown("[Visit our website](https://www.allostericsolutions.com)")
    st.sidebar.markdown("Contact: [franciscocuriel@allostericsolutions.com](mailto:franciscocuriel@allostericsolutions.com)")

    # Mostrar "Features" y "How to Use" importados del archivo contenido.py
    mostrar_features()
    mostrar_como_usar()

    options = st.radio(
        "Select Data Type:",
        ('Phone Numbers', 'Emails'))

    uploaded_files = st.file_uploader("Drop Your Junk Here", type=["csv", "xls", "xlsx", "txt"], accept_multiple_files=True)

    if uploaded_files:
        tipo = 'emails' if options == 'Emails' else 'telefonos'
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
