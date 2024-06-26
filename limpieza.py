import streamlit as st
import pandas as pd
import re
from io import StringIO
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
    st.title("CSV Data Cleaning")

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
        1. **Upload your CSV file**: The file should contain phone numbers that need to be cleaned.
        2. **Download the cleaned CSV file**: After processing, download the cleaned file with valid phone numbers.
        3. **Enjoy the Magic**: Sit back and relax while our app works its magic. It's like having a personal assistant who loves cleaning up phone numbers!
        """)

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv", "xls", "xlsx"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file, header=None)
        else:
            data = pd.read_excel(uploaded_file, header=None)

        output = []
        for col in data.columns:
            data[col] = data[col].apply(lambda x: limpiar_dato(str(x)))
            for value in data[col].to_list():
                if value is not None and value not in output:
                    output.append(value)

        df = pd.DataFrame()
        df["cleaned_numbers"] = output

        # Mostrar el DataFrame en la aplicación Streamlit
        st.write("Cleaned Data:")
        st.dataframe(df)

        # Opción de formato de salida (Excel o PDF)
        formato_salida = st.selectbox("Select output format", ["Excel", "PDF"])

        if formato_salida == "Excel":
            # Guarda el DataFrame en un archivo Excel
            cleaned_file = df.to_excel('cleaned_numbers.xlsx', index=False)
            st.download_button(
                label="Download Cleaned Excel",
                data=cleaned_file,
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
