#__init__.py
from flask import Flask, request, jsonify
import os
from PIL import Image
from pdfminer.high_level import extract_text
from base64 import b64encode
from pdf2image import convert_from_path
from dotenv import load_dotenv
from .vectors_chains import create_vector_store, create_conversation_chain, handle_user_input
from .vision_services import send_image_to_vision, send_batch_to_google_vision
from .image_processing import batch_images, convert_pdf_to_images, process_image_file
from .text_processing import extract_text_from_pdf
from werkzeug.utils import secure_filename
from .helpers import allowed_file
from .barcodes import procesar_archivo
import tempfile
from flask_cors import CORS  # Importa CORS


credentials_path = os.path.abspath("the-byway-410420-9ab864cb800b.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
app = Flask(__name__)
CORS(app)  # Habilita CORS para toda la aplicación

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env.dev')
load_dotenv(dotenv_path)

UPLOAD_FOLDER = 'temps'

if not os.path.exists(UPLOAD_FOLDER):
    try:
        # Intentar crear la carpeta 'temps' si no existe
        os.makedirs(UPLOAD_FOLDER)
    except OSError as e:
        # Manejar cualquier error que pueda ocurrir durante la creación de la carpeta
        print(f"Error al crear la carpeta 'temps': {e}")


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

@app.route("/")
def hello_world():
    return jsonify(statusCode="200", statusMessage="OK")

@app.route('/ia/api/assets/answer', methods=['POST'])
def process_file():
    question = request.form['question']
    file = request.files['file']
    chunk_size = int(request.form.get('chunk_size', 3000))  # Valor predeterminado de 3000 si no se proporciona
    chunk_overlap = int(request.form.get('chunk_overlap', 1000))  # Valor predeterminado de 1000 si no se proporciona
    temperature = float(request.form.get('temperature', 0.3))

    if not file:
        return jsonify({"error": "No se proporcionó archivo"}), 400

    file_extension = file.filename.split('.')[-1].lower()

    # Guardar el archivo temporalmente
    temp_file_path = 'tempfile.' + file_extension
    file.save(temp_file_path)

    if file_extension in ['jpeg', 'jpg', 'png']:
        image = Image.open(temp_file_path)
        # Envía directamente la imagen a send_image_to_vision
        response = send_image_to_vision(question, image)
        # Eliminar el archivo temporal
        os.remove(temp_file_path)
        return jsonify(response)

    elif file_extension in ['tif', 'tiff']:
        return process_image_file(temp_file_path, question, chunk_size, chunk_overlap)

    elif file_extension == 'pdf':
        extracted_text = extract_text_from_pdf(temp_file_path)

        # Verificar si el texto extraído es menor a 30 caracteres
        if len(extracted_text) < 30:
            images = convert_pdf_to_images(temp_file_path)
            batched_requests = batch_images(images)
            extracted_texts = send_batch_to_google_vision(batched_requests)
            extracted_text = ' '.join(extracted_texts)

        os.remove(temp_file_path)

        if not extracted_text:
            return jsonify({"error": "No se pudo extraer texto del archivo"}), 400

        vector_store = create_vector_store(extracted_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        conversation_chain = create_conversation_chain(vector_store,temperature=temperature)
        response = handle_user_input(question, conversation_chain, max_tokens=1500)
        return jsonify({"response": response})

    else:
        os.remove(temp_file_path)
        return jsonify({"error": "Formato de archivo no soportado"}), 400



@app.route('/ia/api/assets/barcode', methods=['POST'])
def upload_file():
    """Endpoint para subir archivos y procesarlos."""
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400

    pages = request.form.get('pages')

    # Manejar casos especiales para 'U', 'P' y 'T'
    if pages.upper() in ['U', 'P', 'T']:
        page_num = pages.upper()
    else:
        try:
            page_num = int(pages)  # Ahora pages es un número que representa la página deseada
        except ValueError:
            return jsonify(error="Número de página no válido"), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            resultados, error = procesar_archivo(filepath, page_num)
            if error:
                return jsonify(error=error), 400

            # Opcional: elimina el archivo después de procesarlo
            if app.config.get('REMOVE_UPLOADED_FILES', False):
                os.remove(filepath)

            if resultados:
                return jsonify(result=resultados)
            else:
                return jsonify(result=[]), 404  # No se encontraron resultados
        except Exception as e:
            return jsonify(error=str(e)), 500
    else:
        return jsonify(error="File type not allowed"), 400