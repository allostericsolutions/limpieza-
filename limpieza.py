import streamlit as st
import pandas as pd
import re
from io import StringIO

def limpiar_dato(dato):
    try:
        # Eliminar caracteres no numéricos
        dato_limpio = re.sub(r'\D', '', dato)

        # Verificar si el dato limpio tiene 10 dígitos
        if len(dato_limpio) == 10:
            return dato_limpio
        else:
            return None
    except:
        return None

def main():
    st.title("CSV Data Cleaning")

    # Mostrar la imagen de la empresa con tamaño ajustado
    st.image("https://i.imgur.com/LzPcPIk.png", caption='Allosteric Solutions', width=100)

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

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        # Leer el archivo CSV cargado
        data = pd.read_csv(uploaded_file, header=None)

        output = []
        for col in data.columns:
            data[col] = data[col].apply(lambda x: limpiar_dato(x))
            for value in data[col].to_list():
                if value not in output:
                    if value is not None:
                        output.append(value)

        df = pd.DataFrame()
        df["cleaned_numbers"] = output

        # Mostrar el DataFrame en la aplicación Streamlit
        st.write("Cleaned Data:")
        st.dataframe(df)

        # Descargar el archivo CSV limpio
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Cleaned CSV",
            data=csv,
            file_name='cleaned_numbers.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()
