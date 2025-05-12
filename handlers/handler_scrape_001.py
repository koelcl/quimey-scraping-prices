from datetime import datetime, timezone
from xml.etree.ElementTree import tostring
from .utils import limpiar_precio_arauco

def handler_scrape_001(main_element_lxml, task_details):
    extracted_data_list = []
    if main_element_lxml is None:
        print(f"[{task_details['id']}] (handler_scrape_001) Elemento principal no encontrado con XPath: {task_details['xpath']}")
        return extracted_data_list

    # Obtener solo filas válidas de distribuidores que contienen un precio
    filas_xpath = ".//div[contains(@class, 'distributors--row')][.//div[contains(@class, 'col-sm-3')]/p[contains(@class, 'js-price')]]"
    filas = main_element_lxml.xpath(filas_xpath)

    if len(filas) < 3:
        print(f"[{task_details['id']}] (handler_scrape_001) Menos de 3 distribuidores encontrados ({len(filas)}).")
        return extracted_data_list

    # Solo tomamos el tercer distribuidor real
    fila_lxml = filas[2]
    precio_xpath = "normalize-space(.//div[contains(@class, 'col-sm-3')]/p[@class='fw-bold js-price'])"

    nombre = 'Arauco'
    precio_bruto = fila_lxml.xpath(precio_xpath)

    precio_limpio = limpiar_precio_arauco(precio_bruto)

    if nombre and precio_limpio:
        data_item = {
            "task_id": task_details["id"],
            "product_name_task": task_details["name"],
            "source_url": task_details["url"],
            "scraped_at": datetime.now(timezone.utc),
            "distributor_name": nombre,
            "board_price": precio_limpio,
        }
        extracted_data_list.append(data_item)
    else:
        print(f"  [{task_details['id']}] (handler_scrape_001) No se pudo extraer nombre o precio del tercer distribuidor. Nombre: '{nombre}', Precio crudo: '{precio_bruto}'")

    return extracted_data_list
