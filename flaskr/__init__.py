import os
from flask import Flask
from flask_cors import CORS
from ai.llm_io import LLM

import sys

# Adiciona o diretório 'core' ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Importa e registra as rotas
    from flaskr.routes.main import routes
    app.register_blueprint(routes)

    return app