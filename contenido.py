import streamlit as st

def mostrar_features():
    with st.expander("Features"):
        st.markdown("""
        1. Removes duplicate numbers
        2. Filters out numbers with more or less than 10 digits
        3. Eliminates non-numeric characters
        4. **Makes your phone number list sparkle**: Because who doesn't love a clean and shiny phone number list?
        """)

def mostrar_como_usar():
    with st.expander("How to Use"):
        st.markdown("""
        1. **Upload your file:** You can upload multiple files in the following formats:
            * **CSV (.csv)**
            * **Excel (.xls, .xlsx)**
            * **Text (.txt)** (Make sure each phone number is on a separate line)
        2. **Download the cleaned file:** After processing, you can download your cleaned phone number list in either:
            * **Excel (.xlsx)**
            * **PDF (.pdf)**
            * **CSV (.csv)**
        3. **Enjoy the Magic**: Sit back and relax while our app works its magic. It's like having a personal assistant who loves cleaning up phone numbers!
        """)
