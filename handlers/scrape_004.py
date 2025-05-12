from datetime import datetime, timezone
from xml.etree.ElementTree import tostring
from .utils import limpiar_precio_arauco

def handler_scrape_004(main_element_lxml, task_details):
    extracted_data_list = []
    if main_element_lxml is None:
        print(f"[{task_details['id']}] (handler_scrape_004) Elemento principal no encontrado con XPath: {task_details['xpath']}")
        return extracted_data_list
    
    precio_xpath = "//div[@class='prices']//span[@class='value']/text()"
    precio = main_element_lxml.xpath(precio_xpath)

    if len(precio) < 1:
        print(f"[{task_details['id']}] (handler_scrape_004) No se ha encontrado el precio normal del producto.")
        return extracted_data_list

    nombre = 'DVP'
    precio_bruto = precio[0]
    precio_limpio = limpiar_precio_arauco(precio_bruto)

    if nombre and precio_limpio:
        data_item = {
            "task_id": task_details["id"],
            "product_name_task": task_details["name"],
            "source_url": task_details["url"],
            "scraped_at": datetime.now(timezone.utc),
            "distributor_name": nombre,
            "board_price": precio_limpio,
            "product_detail": "Bisagra Recta 110° 35mm con 4 Tornillos Cierre Suave"
        }
        extracted_data_list.append(data_item)
    else:
        print(f"  [{task_details['id']}] (handler_scrape_004) No se pudo extraer el precio del producto.") 

    return extracted_data_list
