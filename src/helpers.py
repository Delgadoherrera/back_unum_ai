import base64
import io

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff', 'tif', 'pdf'}

def image_to_base64(image):
    # Convertir la imagen a modo 'RGB' si no lo está
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convertir la imagen a un objeto de bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    # Codificar los bytes a base64
    base64_image = base64.b64encode(img_byte_arr).decode('utf-8')
    return base64_image


def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
