# handlers/utils.py
import re

def limpiar_precio_arauco(texto_precio):
    """
    Limpia un string de precio eliminando símbolos monetarios, puntos, y espacios.
    Específico para el formato de Arauco, pero podría generalizarse o tener variantes.
    """
    if texto_precio:
        limpio = re.sub(r'[$.]|&nbsp;', '', texto_precio)
        limpio = re.sub(r'\s+', '', limpio)
        return int(limpio.strip())
    return None

# Puedes añadir más funciones de utilidad aquí, por ejemplo:
# def limpiar_precio_general(texto_precio):
#     # Lógica de limpieza más genérica
#     pass