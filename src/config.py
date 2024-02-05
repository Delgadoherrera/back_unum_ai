#config.py
import os

# Ruta al archivo JSON de credenciales de Google Cloud
credentials_path = os.path.abspath("the-byway-410420-9ab864cb800b.json")

# Configura la variable de entorno GOOGLE_APPLICATION_CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env.dev')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
