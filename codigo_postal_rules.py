import re

def limpiar_codigo_postal(codigo):
    """
    Limpia y valida un código postal.

    Args:
        codigo (str): Código postal a limpiar.

    Returns:
        str: Código postal limpio, o None si el código es inválido.
    """
    codigo_limpio = re.sub(r'\D', '', codigo).strip()
    if len(codigo_limpio) == 5:
        return codigo_limpio
    elif len(codigo_limpio) == 4:
        return '0' + codigo_limpio
    return None  # Código inválido (menos de 4 o más de 5 dígitos)
