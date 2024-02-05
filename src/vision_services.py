#vision_services
from google.cloud import vision
from google.cloud.vision_v1 import types
import requests
import json
import os
from .helpers import image_to_base64
from flask import jsonify
import io

def send_image_to_google_vision(image):
    print('SENDING IMG TO GOOGLE_VISION')
    client = vision.ImageAnnotatorClient()
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes = image_bytes.getvalue()
    image = types.Image(content=image_bytes)
    response = client.text_detection(image=image)
    annotations = response.text_annotations
    if annotations:
        return annotations[0].description
    else:
        return 'No se encontró texto'


def send_batch_to_google_vision(batched_requests):
    print('SENDING BATCH TO GOOGLE_VISION')
    client = vision.ImageAnnotatorClient()
    response = client.batch_annotate_images(requests=batched_requests)
    return [resp.text_annotations[0].description if resp.text_annotations else 'No se encontró texto' for resp in
            response.responses]

def send_image_to_vision(question, image):
    base64_image = image_to_base64(image)  # Convertir a base64
    print('SENDING IMAGE TO VISION')
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}", "detail": "auto"}}
                ]
            }
        ],
        "max_tokens": 2500
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        response_json = response.json()
        assistant_response = response_json['choices'][0]['message']['content']
        assistant_response = assistant_response.replace(
            '```json', '').replace('```', '').strip()
        try:
            parsed_response = json.loads(assistant_response)
            return parsed_response
        except json.JSONDecodeError:
            return assistant_response
    else:
        return jsonify({"error": f"Error en la solicitud: {response.status_code}, {response.text}"})