
def validate_request_description(texto):  
    if not isinstance(texto, str):
        return False
    texto = texto.strip()
    if texto == "":
        return False
    if len(texto) > 200:
        return False
    return True

