import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from ai.llm_io import LLM

import sys

# Adiciona o diretório 'core' ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

# Load variables from .env if present
load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configurações de terceiros
    app.config['SUPABASE_URL'] = os.environ.get('SUPABASE_URL', '')
    app.config['SUPABASE_KEY'] = os.environ.get('SUPABASE_KEY', '')
    app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', 'change-me')

    # Importa e registra as rotas
    from flaskr.routes.main import routes
    from flaskr.routes.auth import routes_auth
    app.register_blueprint(routes)
    app.register_blueprint(routes_auth)

    return app