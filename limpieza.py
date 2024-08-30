import streamlit as st
import pandas as pd
import re
from io import BytesIO
import os
from fpdf import FPDF
import tempfile
import numpy as np
from limpieza_texto import limpiar_y_procesar_archivo  # Importar la función desde el módulo

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
        pdf.cell(200, 10, txt=row['cleaned_numbers'], ln=True, align='C')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)

    return tmpfile.name

def main():
    st.title("Dr. Cleaner")

    st.image("https://i.imgur.com/LzPcPIk.png", caption='Allosteric Solutions', width=360)

    st.markdown("[Visit our website](https://www.allostericsolutions.com)")
    st.markdown("Contact: [franciscocuriel@allostericsolutions.com](mailto:franciscocuriel@allostericsolutions.com)")

    with st.expander("Features"):
        st.markdown("""
        1. Removes duplicate numbers
        2. Filters out numbers with more or less than 10 digits
        3. Eliminates non-numeric characters
        4. **Makes your phone number list sparkle**: Because who doesn't love a clean and shiny phone number list?
        """)

    with st.expander("How to Use"):
        st.markdown("""
        1. **Upload your file:**  You can upload your phone number list in the following formats:
            * **CSV (.csv)**
            * **Excel (.xls, .xlsx)**
            * **Text (.txt)** (Make sure each phone number is on a separate line)
        2. **Download the cleaned file:**  After processing, you can download your cleaned phone number list in either:
            * **Excel (.xlsx)**
            * **PDF (.pdf)**
            * **CSV (.csv)**
        3. **Enjoy the Magic**: Sit back and relax while our app works its magic. It's like having a personal assistant who loves cleaning up phone numbers!
        """)

    uploaded_file = st.file_uploader("Drop Your Junk Here", type=["csv", "xls", "xlsx", "txt"])

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1]

        # Llamar la función de limpieza y procesamiento
        resultado = limpiar_y_procesar_archivo(uploaded_file, file_extension)

        df = pd.DataFrame()
        df["cleaned_numbers"] = resultado["cleaned_numbers"]

        st.write("Cleaned Data:")
        st.dataframe(df)

        formato_salida = st.selectbox("Choose Your Fancy Output!", ["Excel", "PDF", "CSV"])

        if formato_salida == "Excel":
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="Grab your things here",
                data=buffer.getvalue(),
                file_name='cleaned_numbers.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        elif formato_salida == "PDF":
            pdf_file_path = generar_pdf(df)
            with open(pdf_file_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Cleaned PDF",
                    data=pdf_file,
                    file_name='cleaned_numbers.pdf',
                    mime='application/pdf'
                )
            os.remove(pdf_file_path)

        elif formato_salida == "CSV":
            buffer = BytesIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="Download Cleaned CSV",
                data=buffer.getvalue(),
                file_name='cleaned_numbers.csv',
                mime='text/csv'
            )

        n_validos = len(resultado["cleaned_numbers"])
        n_duplicados_eliminados = resultado["total_numbers"] - (
            n_validos + resultado["invalid_numbers_less_than_10"] + resultado["invalid_numbers_greater_than_10"]
        )

        reporte = {
            'Total numbers found in the file': resultado["total_numbers"],
            'Total valid numbers processed (exactly 10 digits)': n_validos,
            'Total disqualified numbers (less than 10 digits)': resultado["invalid_numbers_less_than_10"],
            'Total disqualified numbers (more than 10 digits)': resultado["invalid_numbers_greater_than_10"],
            'Total duplicate numbers removed': n_duplicados_eliminados
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
            with pd.ExcelWriter(reporte_file) as writer:
                reporte_df.to_excel(writer, sheet_name='Summary', index=False)
                info_df.to_excel(writer, sheet_name='Analysis Info', index=False)

            with open(reporte_file, "rb") as report_file:
                st.download_button(
                    label="Retrieve Your Report Here, Hurry Up man!",
                    data=report_file,
                    file_name='report.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

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
