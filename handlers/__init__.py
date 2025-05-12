# handlers/__init__.py

# Importa los handlers específicos de sus respectivos archivos
from .handler_scrape_001 import handler_scrape_001
# Si tienes más handlers, impórtalos aquí:
# from .handler_scrape_002 import handler_scrape_002
# ... etc.

# Crea el diccionario TASK_HANDLERS que el script principal utilizará
TASK_HANDLERS = {
    'SCRAPE-001': handler_scrape_001,
    # 'SCRAPE-002': handler_scrape_002, # Añade otros handlers aquí
}

# Opcionalmente, para evitar errores si un handler no está importado pero se lista arriba:
# Limpiar TASK_HANDLERS para solo incluir los que realmente se importaron.
# _all_handlers = {k: v for k, v in TASK_HANDLERS.items() if v is not None}
# TASK_HANDLERS = _all_handlers

# Para facilitar la importación, puedes definir __all__
__all__ = ['TASK_HANDLERS']