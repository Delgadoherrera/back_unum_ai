
from PIL import Image
from .image_processing import mejorar_imagen_para_codigo_de_barras
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path
import os

def leer_codigos_barra(imagen):
    codigos = decode(imagen)
    resultados = []
    for codigo in codigos:
        tipo_codigo = codigo.type
        valor_codigo = codigo.data.decode('utf-8')
        resultados.append({'code': tipo_codigo, 'value': valor_codigo})
    return resultados


def procesar_archivo(archivo, page_num=None):
    extension = os.path.splitext(archivo)[1].lower()
    resultados = []

    if extension in ['.jpg', '.jpeg', '.png']:
        imagen = Image.open(archivo)
        imagen_mejorada = mejorar_imagen_para_codigo_de_barras(imagen)
        codigos = leer_codigos_barra(imagen_mejorada)
        for codigo in codigos:
            resultados.append(codigo)

    elif extension in ['.tiff', '.tif']:
        try:
            with Image.open(archivo) as img:
                total_paginas = img.n_frames
                paginas_a_procesar = range(total_paginas)

                if page_num is not None:
                    if str(page_num).upper() == 'U':
                        paginas_a_procesar = [total_paginas - 1]
                    elif str(page_num).upper() == 'P':
                        paginas_a_procesar = [0]
                    elif str(page_num).upper() == 'T':
                        paginas_a_procesar = range(total_paginas)
                    else:
                        try:
                            page_num = int(page_num) - 1
                            if page_num < 0 or page_num >= total_paginas:
                                return resultados, f"El número de página {page_num+1} está fuera del rango válido (1 - {total_paginas})."
                            paginas_a_procesar = [page_num]
                        except ValueError:
                            return resultados, "Número de página no válido"

                for i in paginas_a_procesar:
                    img.seek(i)
                    imagen_mejorada = mejorar_imagen_para_codigo_de_barras(img)
                    codigos = leer_codigos_barra(imagen_mejorada)
                    for codigo in codigos:
                        resultados.append({'codigo': codigo, 'pagina': i+1})
        finally:
            # Eliminar el archivo temporal si existe (ajustar según la lógica de tu aplicación)
            if os.path.exists(archivo):
                os.remove(archivo)

    elif extension == '.pdf':
        try:
            paginas = convert_from_path(archivo)
            total_paginas = len(paginas)

            if page_num is None:
                return resultados, "El valor 'page_num' no está especificado correctamente."
            else:
                try:
                    if str(page_num).upper() == 'U':
                        page_num = total_paginas  # Buscar en la última página
                    elif str(page_num).upper() == 'P' or str(page_num).upper() == 'p':
                        page_num = 1  # Buscar en la primera página

                    elif str(page_num).upper() == 'T':
                        # Escanear todas las páginas
                        for num_pagina, pagina in enumerate(paginas, start=1):
                            imagen_mejorada = mejorar_imagen_para_codigo_de_barras(pagina)
                            codigos = leer_codigos_barra(imagen_mejorada)
                            for codigo in codigos:
                                codigo['pagina'] = num_pagina
                                resultados.append(codigo)
                        return resultados, None
                    else:
                        page_num = int(page_num)  # Ahora page_num es un número que representa la página deseada

                    if page_num < 1 or page_num > total_paginas:
                        return resultados, f"El número de página {page_num} está fuera del rango válido (1 - {total_paginas})."

                    pagina = paginas[page_num - 1]
                    imagen_mejorada = mejorar_imagen_para_codigo_de_barras(pagina)
                    codigos = leer_codigos_barra(imagen_mejorada)
                    for codigo in codigos:
                        codigo['pagina'] = page_num
                        resultados.append(codigo)

                except ValueError:
                    return resultados, "Número de página no válido"
        finally:
            # Eliminar el archivo temporal si existe
            if os.path.exists(archivo):
                os.remove(archivo)

    return resultados, None