import streamlit as st
import pandas as pd
import re
from io import StringIO, BytesIO
import os
from fpdf import FPDF
import tempfile

def limpiar_dato(dato):
    try:
        # Eliminar caracteres no numéricos
        dato_limpio = re.sub(r'\D', '', dato)

        # Verificar si el dato limpio tiene exactamente 10 dígitos
        if len(dato_limpio) == 10:
            return dato_limpio
        else:
            return None
    except:
        return None

def generar_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Encabezado
    pdf.cell(200, 10, txt="Cleaned Phone Numbers", ln=True, align='C')

    # Datos
    for index, row in dataframe.iterrows():
        pdf.cell(200, 10, txt=row['cleaned_numbers'], ln=True, align='C')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)

    return tmpfile.name

def main():
    st.title("Dr. Cleaner")

    # Mostrar la imagen de la empresa con tamaño ajustado
    st.image("https://i.imgur.com/LzPcPIk.png", caption='Allosteric Solutions', width=200)

    # Compartir la página empresarial y el correo
    st.markdown("[Visit our website](https://www.allostericsolutions.com)")
    st.markdown("Contact: [franciscocuriel@allostericsolutions.com](mailto:franciscocuriel@allostericsolutions.com)")

    # Sección desplegable para "Features"
    with st.expander("Features"):
        st.markdown("""
        1. Removes duplicate numbers
        2. Filters out numbers with more or less than 10 digits
        3. Eliminates non-numeric characters
        4. **Makes your phone number list sparkle**: Because who doesn't love a clean and shiny phone number list?
        """)

    # Sección desplegable para "How to Use"
    with st.expander("How to Use"):
        st.markdown("""
        1. **Upload your file:**  You can upload your phone number list in the following formats:
            * **CSV (.csv)**
            * **Excel (.xls, .xlsx)**
            * **Text (.txt)** (Make sure each phone number is on a separate line)
        2. **Download the cleaned file:**  After processing, you can download your cleaned phone number list in either:
            * **Excel (.xlsx)**
            * **PDF (.pdf)**
        3. **Enjoy the Magic**: Sit back and relax while our app works its magic. It's like having a personal assistant who loves cleaning up phone numbers!
        """)

    uploaded_file = st.file_uploader("Upload your file", type=["csv", "xls", "xlsx", "txt"])

    if uploaded_file is not None:
        # Usar un set para evitar duplicados
        output = set()

        # Procesar archivo CSV
        if uploaded_file.name.endswith(".csv"):
            chunk_size = 10000
            for chunk in pd.read_csv(uploaded_file, header=None, chunksize=chunk_size):
                for line in chunk.iloc[:, 0]:
                    numbers = re.split(r'[,\s]+', str(line))
                    for number in numbers:
                        cleaned_number = limpiar_dato(number)
                        if cleaned_number is not None:
                            output.add(cleaned_number)

        # Procesar archivo Excel
        elif uploaded_file.name.endswith((".xls", ".xlsx")):
            chunk_size = 10000
            for chunk in pd.read_excel(uploaded_file, header=None, chunksize=chunk_size):
                for line in chunk.iloc[:, 0]:
                    numbers = re.split(r'[,\s]+', str(line))
                    for number in numbers:
                        cleaned_number = limpiar_dato(number)
                        if cleaned_number is not None:
                            output.add(cleaned_number)

        # Procesar archivo de texto
        elif uploaded_file.name.endswith(".txt"):
            for line in uploaded_file:
                line = line.decode("utf-8").strip()
                numbers = re.split(r'[,\s]+', line)
                for number in numbers:
                    cleaned_number = limpiar_dato(number)
                    if cleaned_number is not None:
                        output.add(cleaned_number)

        else:
            st.error("Invalid file format. Please upload a CSV, Excel, or Text file.")
            return

        df = pd.DataFrame(list(output), columns=["cleaned_numbers"])

        # Mostrar el DataFrame en la aplicación Streamlit
        st.write("Cleaned Data:")
        st.dataframe(df)

        # Opción de formato de salida (Excel o PDF)
        formato_salida = st.selectbox("Select output format", ["Excel", "PDF"])

        if formato_salida == "Excel":
            # Guarda el DataFrame en un objeto en memoria como un archivo temporal
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)  # Vuelve al principio del buffer

            # Descarga el archivo Excel como un byte string
            st.download_button(
                label="Download Cleaned Excel",
                data=buffer.getvalue(),
                file_name='cleaned_numbers.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )

        elif formato_salida == "PDF":
            pdf_file_path = generar_pdf(df)
            with open(pdf_file_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Cleaned PDF",
                    data=pdf_file,
                    file_name='cleaned_numbers.pdf',
                    mime='application/pdf',
                )
            os.remove(pdf_file_path)

if __name__ == "__main__":
    main()
