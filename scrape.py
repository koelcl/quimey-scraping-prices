# main_scraper.py
import requests
from lxml import html # Necesario para parsear el HTML antes de pasarlo al handler
import redis
import pymongo
import json
# import re # Ya no es necesario aquí si la limpieza está en utils
from datetime import datetime, timezone # Necesario si usas datetime fuera de los handlers
import os
import traceback
from dotenv import load_dotenv # Para cargar el archivo .env

# Cargar variables de entorno desde .env
load_dotenv()

# --- Importar Handlers ---
# Esto importará el diccionario TASK_HANDLERS desde handlers/__init__.py
from handlers import TASK_HANDLERS
# Alternativamente, si utils.py tuviera funciones que el main necesita:
# from handlers.utils import alguna_funcion_util_para_main

# --- CONFIGURACIÓN (leyendo desde el entorno) ---
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_TASKS_KEY = os.getenv('REDIS_TASKS_KEY_NAME', 'scrape_tasks_config') # Usando la variable del .env si se define

MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING', "mongodb://localhost:27017/")
MONGO_DATABASE_NAME = os.getenv('MONGO_DATABASE_NAME', "scraping_db")
MONGO_COLLECTION_NAME = os.getenv('MONGO_COLLECTION_NAME', "scraped_prices")

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', # Fecha hipotética: Mayo 2025
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
}

# --- CLIENTES DE BASES DE DATOS ---
redis_client = None
mongo_client = None

# (El código de conexión a Redis y MongoDB permanece igual)
try:
    redis_client_params = {
        'host': REDIS_HOST, 'port': REDIS_PORT, 'db': REDIS_DB, 'decode_responses': True
    }
    if REDIS_PASSWORD:
        redis_client_params['password'] = REDIS_PASSWORD
    
    redis_client = redis.Redis(**redis_client_params)
    redis_client.ping()
    print(f"Conectado a Redis ({REDIS_HOST}:{REDIS_PORT}) exitosamente.")
except redis.exceptions.AuthenticationError:
    print(f"Error de autenticación con Redis ({REDIS_HOST}:{REDIS_PORT}): Contraseña incorrecta o requerida y no provista.")
    exit()
except redis.exceptions.ConnectionError as e:
    print(f"Error al conectar con Redis ({REDIS_HOST}:{REDIS_PORT}): {e}")
    exit()

try:
    mongo_client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
    mongo_db = mongo_client[MONGO_DATABASE_NAME]
    mongo_collection = mongo_db[MONGO_COLLECTION_NAME]
    mongo_client.admin.command('ping')
    print(f"Conectado a MongoDB ({MONGO_DATABASE_NAME}/{MONGO_COLLECTION_NAME}) exitosamente.")
except pymongo.errors.ConnectionFailure as e:
    print(f"Error al conectar con MongoDB: {e}")
    exit()


# --- YA NO SE DEFINEN HANDLERS AQUÍ ---
# La función limpiar_precio_arauco() también se movió a handlers/utils.py
# El diccionario TASK_HANDLERS se importa desde handlers/__init__.py


# --- FUNCIÓN PRINCIPAL DE SCRAPING (el resto del main permanece similar) ---
def main():
    print(f"Proceso de scraping iniciado a las {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}")

    try:
        tasks_json_array_string = redis_client.get(REDIS_TASKS_KEY)
    except redis.exceptions.RedisError as e:
        print(f"Error al obtener la clave '{REDIS_TASKS_KEY}' de Redis: {e}")
        return
        
    if not tasks_json_array_string:
        print(f"No se encontró datos en la clave de Redis '{REDIS_TASKS_KEY}' o está vacía.")
        return

    try:
        list_of_task_objects = json.loads(tasks_json_array_string)
        if not isinstance(list_of_task_objects, list):
            print(f"El contenido de la clave '{REDIS_TASKS_KEY}' no es un array JSON. Tipo encontrado: {type(list_of_task_objects)}")
            return
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el array JSON de la clave '{REDIS_TASKS_KEY}': {e}")
        return

    if not list_of_task_objects:
        print(f"El array JSON de tareas en '{REDIS_TASKS_KEY}' está vacío.")
        return

    print(f"Se obtuvieron {len(list_of_task_objects)} tareas de la clave '{REDIS_TASKS_KEY}' en Redis.")

    for task in list_of_task_objects:
        if not isinstance(task, dict):
            print(f"Elemento en el array JSON no es un objeto (diccionario), saltando: {task}")
            continue
        try:
            task_id = task.get("id")
            task_name = task.get("name")
            task_url = task.get("url")
            task_xpath_general = task.get("xpath")

            if not all([task_id, task_name, task_url, task_xpath_general]):
                print(f"Tarea incompleta, faltan campos requeridos (id, name, url, xpath), saltando: {task}")
                continue

            print(f"\n--- Procesando Tarea ID: {task_id} | Nombre: {task_name} | URL: {task_url} ---")

            try:
                response = requests.get(task_url, headers=REQUEST_HEADERS, timeout=30)
                response.raise_for_status()
                print(f"[{task_id}] Página obtenida exitosamente (Status: {response.status_code}).")
            except requests.exceptions.RequestException as e:
                print(f"[{task_id}] Error al obtener la URL {task_url}: {e}")
                continue

            try:
                doc_lxml = html.fromstring(response.content) # Parseo del HTML
                main_elements_lxml = doc_lxml.xpath(task_xpath_general)
                if not main_elements_lxml:
                    print(f"[{task_id}] No se encontró el elemento principal con XPath: {task_xpath_general}")
                    main_element_to_pass = None
                else:
                    main_element_to_pass = main_elements_lxml[0]
            except Exception as e:
                print(f"[{task_id}] Error al parsear HTML o aplicar XPath general: {e}")
                traceback.print_exc()
                continue

            # Aquí se usa el TASK_HANDLERS importado
            handler_function = TASK_HANDLERS.get(task_id)
            if not handler_function:
                print(f"[{task_id}] No se encontró un manejador para este ID de tarea. Saltando.")
                continue
            
            try:
                extracted_results = handler_function(main_element_to_pass, task)
            except Exception as e:
                print(f"[{task_id}] Error crítico dentro del manejador específico '{task_id}': {e}")
                traceback.print_exc()
                continue
            
            if extracted_results:
                if not isinstance(extracted_results, list):
                    if isinstance(extracted_results, dict):
                        extracted_results = [extracted_results]
                    else:
                        print(f"[{task_id}] El manejador devolvió datos en un formato no esperado (no es lista ni dict). Tipo: {type(extracted_results)}")
                        continue

                if len(extracted_results) > 0:
                    try:
                        for result in extracted_results:
                            task_id = result.get("task_id")
                            board_price = result.get("board_price")
                            scraped_at = result.get("scraped_at", datetime.now(timezone.utc))
                            
                            if not task_id or board_price is None:
                                print(f"[{task_id}] Registro sin 'task_id' o 'board_price', saltando.")
                                continue

                            update_result = mongo_collection.update_one(
                                {"task_id": task_id},
                                {
                                    "$set": {
                                        "product_name_task": result.get("product_name_task"),
                                        "source_url": result.get("source_url"),
                                        "distributor_name": result.get("distributor_name"),
                                        "current_price": board_price,
                                        "updated_at": datetime.now(timezone.utc)
                                    },
                                    "$push": {
                                        "history": {
                                            "price": board_price,
                                            "scraped_at": scraped_at
                                        }
                                    }
                                },
                                upsert=True
                            )
                            if update_result.upserted_id:
                                print(f"[{task_id}] Documento creado con nuevo ID: {update_result.upserted_id}")
                            else:
                                print(f"[{task_id}] Documento existente actualizado.")

                    except pymongo.errors.BulkWriteError as bwe:
                        successful_inserts = len(extracted_results) - len(bwe.details.get('writeErrors',[]))
                        print(f"[{task_id}] Errores durante la inserción múltiple en MongoDB. {successful_inserts} exitosos, {len(bwe.details.get('writeErrors',[]))} fallaron.")
                    except pymongo.errors.PyMongoError as e:
                         print(f"[{task_id}] Error al insertar registros en MongoDB: {e}")
            else:
                print(f"[{task_id}] No se extrajeron datos para esta tarea o el manejador devolvió vacío.")

        except Exception as e:
            print(f"Error inesperado procesando una tarea ({task if isinstance(task, dict) else type(task)}): {e}") # Ajuste en log
            traceback.print_exc()

    print(f"\nProceso de scraping finalizado a las {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}")

if __name__ == '__main__':
    if not REDIS_PASSWORD and REDIS_HOST not in ['localhost', '127.0.0.1']:
        print("ADVERTENCIA: REDIS_PASSWORD no está configurada y el host de Redis no es local. Asegúrate de que Redis no requiera contraseña o configúrala.")

    main()
    if mongo_client:
         mongo_client.close()
         print("Conexión a MongoDB cerrada.")
    if redis_client:
        redis_client.close()
        print("Conexión a Redis cerrada.")