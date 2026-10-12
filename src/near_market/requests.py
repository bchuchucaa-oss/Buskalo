
def validate_request_texto(texto):
    if texto is None:
        return False
    texto_limpio = str(texto).strip()
    if texto_limpio == "":
        return False
    if texto_limpio.isdigit():
        return False
    if len(texto_limpio) > 200:
        return False
    return True

