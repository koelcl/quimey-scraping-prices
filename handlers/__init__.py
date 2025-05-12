# handlers/__init__.py

# Importa los handlers específicos de sus respectivos archivos
from .scrape_001 import handler_scrape_001
from .scrape_002 import handler_scrape_002
from .scrape_003 import handler_scrape_003
from .scrape_004 import handler_scrape_004
# Si tienes más handlers, impórtalos aquí:
# from .handler_scrape_002 import handler_scrape_002
# ... etc.

# Crea el diccionario TASK_HANDLERS que el script principal utilizará
TASK_HANDLERS = {
    'SCRAPE-001': handler_scrape_001, #Melamina Blanca
    'SCRAPE-002': handler_scrape_002, #Tapacanto PVC blanco
    'SCRAPE-003': handler_scrape_003, #Tornillo aglomerado 25mm
    'SCRAPE-004': handler_scrape_003, #Tornillo aglomerado 15mm
    'SCRAPE-005': handler_scrape_003, #Tornillo aglomerado 45mm
    'SCRAPE-006': handler_scrape_004, #Bisagra Cierre Suave 35mm
    'SCRAPE-007': handler_scrape_004, #Bisagra Cierre Estandar 35mm
}

# Opcionalmente, para evitar errores si un handler no está importado pero se lista arriba:
# Limpiar TASK_HANDLERS para solo incluir los que realmente se importaron.
# _all_handlers = {k: v for k, v in TASK_HANDLERS.items() if v is not None}
# TASK_HANDLERS = _all_handlers

# Para facilitar la importación, puedes definir __all__
__all__ = ['TASK_HANDLERS']