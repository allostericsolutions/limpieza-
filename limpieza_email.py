import re

def validar_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def limpiar_y_validar_correo(dato):
    dato = dato.strip().lower()  # Convertir a minúsculas
    if validar_email(dato):
        return dato
    return None
