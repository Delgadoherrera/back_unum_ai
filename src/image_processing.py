#image_processing
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from base64 import b64encode
import io
from google.cloud.vision_v1 import types
import base64
from pdf2image import convert_from_path
from .vision_services import send_batch_to_google_vision, send_image_to_google_vision
from .vectors_chains import create_conversation_chain, handle_user_input, create_vector_store
from flask import jsonify
import os
import cv2
import numpy as np

def tiff_to_pdf(image, pdf_path):
    """
    Convierte un objeto Image TIFF a un archivo PDF.
    """
    # Crear un lienzo PDF con el mismo tamaño que la imagen TIFF
    c = canvas.Canvas(pdf_path, pagesize=image.size)

    # Recorrer cada página del TIFF
    try:
        while True:
            width, height = image.size
            c.drawImage(ImageReader(image), 0, 0, width, height)
            c.showPage()  # Finaliza la página actual y comienza una nueva
            image.seek(image.tell() + 1)
    except EOFError:
        pass  # Fin del archivo TIFF

    c.save()


def batch_images(images):
    batched_requests = []
    for image in images:
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()
        batched_requests.append(types.AnnotateImageRequest(
            image=types.Image(content=image_bytes),
            features=[types.Feature(type=types.Feature.Type.TEXT_DETECTION)]
        ))
    return batched_requests

def convert_pdf_to_images(pdf_path):
    print('CONVERTING PDF TO IMAGES')
    return convert_from_path(pdf_path)

def process_image_file(file_path, question, chunk_size, chunk_overlap):
    try:
        image = Image.open(file_path)
        images = []
        try:
            while True:
                images.append(image.copy())
                image.seek(image.tell() + 1)
        except EOFError:
            pass  # Fin de la secuencia de imágenes TIFF

        batched_requests = batch_images(images)
        extracted_texts = send_batch_to_google_vision(batched_requests)
        extracted_text = ' '.join(extracted_texts)

        # Verificar si el texto extraído es menor a 30 caracteres
        if len(extracted_text) < 30:
            print('MENOS DE 30 CARACTERES ENCONTRADOS')
            extracted_text = ' '.join([send_image_to_google_vision(img) for img in images])

        os.remove(file_path)

        if not extracted_text:
            return jsonify({"error": "No se pudo extraer texto del archivo"}), 400

        vector_store = create_vector_store(extracted_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        conversation_chain = create_conversation_chain(vector_store)
        response = handle_user_input(question, conversation_chain, max_tokens=1500)
        return jsonify({"response": response})

    except IOError:
        os.remove(file_path)
        return jsonify({"error": "No se pudo procesar el archivo"}), 400
    
def mejorar_imagen_para_codigo_de_barras(imagen_pil):
    # Convertir imagen PIL a array NumPy (eliminando canal alfa si existe)
    imagen_np = np.array(imagen_pil.convert('RGB'))  # Convertir a RGB
    # Convertir a escala de grises directamente
    imagen_gris = cv2.cvtColor(imagen_np, cv2.COLOR_RGB2GRAY)
    # Ajustar contraste con CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    imagen_contraste = clahe.apply(imagen_gris)
    # Binarización con umbralización de Otsu
    _, imagen_binaria = cv2.threshold(imagen_contraste, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Suavizado con un filtro Gaussiano (opcional)
    imagen_suavizada = cv2.GaussianBlur(imagen_binaria, (3, 3), 0)
    # Convertir de vuelta a formato PIL para procesamiento posterior
    imagen_mejorada_pil = Image.fromarray(imagen_suavizada)
    return imagen_mejorada_pil
