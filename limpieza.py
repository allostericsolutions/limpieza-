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
    st.title("Limpieza de Datos CSV")

    # Mostrar la imagen de la empresa
    st.image("https://i.imgur.com/Mns8Z85.png", caption='Allosteric Solutions', use_column_width=True)

    # Compartir la página empresarial y el correo
    st.markdown("[Visita nuestra página web](https://www.allostericsolutions.com)")
    st.markdown("Contacto: [franciscocuriel@allostericsolutions.com](mailto:franciscocuriel@allostericsolutions.com)")

    uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

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
        df["limpios"] = output

        # Mostrar el DataFrame en la aplicación Streamlit
        st.write("Datos Limpiados:")
        st.dataframe(df)

        # Descargar el archivo CSV limpio
        csv = df.to_csv(index=False)
        st.download_button(
            label="Descargar CSV limpio",
            data=csv,
            file_name='limpios.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()
