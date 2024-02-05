import os
from src import app
from dotenv import load_dotenv

FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT')
FLASK_DEBUG = os.getenv('FLASK_DEBUG')
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_env_prod = os.path.join(directorio_actual, '.env.prod')
ruta_env_dev = os.path.join(directorio_actual, '.env.dev')
load_dotenv(ruta_env_prod)




if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host='0.0.0.0', port=FLASK_RUN_PORT)
