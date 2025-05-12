from datetime import datetime, timezone
from xml.etree.ElementTree import tostring
from .utils import limpiar_precio_arauco

def handler_scrape_003(main_element_lxml, task_details):
    extracted_data_list = []
    if main_element_lxml is None:
        print(f"[{task_details['id']}] (handler_scrape_003) Elemento principal no encontrado con XPath: {task_details['xpath']}")
        return extracted_data_list
    
    precio_xpath = "//span[@class='old-price']//span[@class='price']/text()"
    precio = main_element_lxml.xpath(precio_xpath)

    if len(precio) < 1:
        print(f"[{task_details['id']}] (handler_scrape_003) No se ha encontrado el precio normal del producto.")
        return extracted_data_list

    nombre = 'Construplaza'
    precio_bruto = precio[0]
    precio_limpio = limpiar_precio_arauco(precio_bruto)
    precio_caja_100_unidades = precio_limpio*100

    if nombre and precio_limpio:
        data_item = {
            "task_id": task_details["id"],
            "product_name_task": task_details["name"],
            "source_url": task_details["url"],
            "scraped_at": datetime.now(timezone.utc),
            "distributor_name": nombre,
            "board_price": precio_caja_100_unidades,
            "product_detail": "100 und"
        }
        extracted_data_list.append(data_item)
    else:
        print(f"  [{task_details['id']}] (handler_scrape_003) No se pudo extraer el precio del producto.") 

    return extracted_data_list
