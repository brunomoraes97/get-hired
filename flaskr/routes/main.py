# app/routes.py

from flask import Blueprint, request, send_file, jsonify, render_template
# Supondo que seus módulos estejam em 'core' como no exemplo
from core.app.gerador_cv import GeradorCV
from core.helpers.sanitizador import sanitizar_dados_para_latex
from io import BytesIO
import requests
import os # Adicionado para criar o caminho do output
import json
from ai.llm_io import LLM


routes = Blueprint("routes", __name__)

from flask import Blueprint, request, send_file, jsonify, render_template, redirect, url_for

routes = Blueprint("routes", __name__)

@routes.route("/")
def index_redirect():
    return redirect(url_for('routes.index', lang_code='en'))

@routes.route('/<lang_code>')
def index(lang_code):
    supported_languages = ['en', 'pt', 'es', 'ru']
    if lang_code not in supported_languages:
        return redirect(url_for('routes.index', lang_code='en')) # Default to English if unsupported
    return render_template(f'index_{lang_code}.html')

@routes.route('/generate', methods=["POST"])
def transform_json():
    print("LOG: transform_json - Iniciando requisição.")
    dados_entrada = request.get_json()
    if not dados_entrada:
        print("LOG: transform_json - Erro: JSON ausente ou malformado.")
        return jsonify({"erro": "Corpo da requisição JSON ausente ou malformado."}), 400
    
    cv_text = dados_entrada.get("cv").replace("&", "and")
    vaga_text = dados_entrada.get("job_description").replace("&", "and")
    print("PASSOU AQUI 1")
    print(f"LOG: transform_json - CV text length: {len(cv_text) if cv_text else 0}, Vaga text length: {len(vaga_text) if vaga_text else 0}")

    if not cv_text or not vaga_text:
        return jsonify({"erro": "As chaves 'cv' e 'job_description' são obrigatórias."}), 400

    llm = LLM()
    print("LOG: transform_json - Chamando LLM.run()...")
    dados_brutos = llm.run(cv_text, vaga_text)
    print(f"LOG: transform_json - LLM.run() retornou dados brutos (tipo: {type(dados_brutos)}).")

    # A função download() em GeradorCV já lida com a sanitização e a geração do PDF
    print("LOG: transform_json - Chamando GeradorCV().download()...")
    pdf_content = GeradorCV().download(dados_brutos)
    print(f"LOG: transform_json - GeradorCV().download() retornou PDF (tamanho: {len(pdf_content) if pdf_content else 0}).")

    if not pdf_content:
        print("LOG: transform_json - Erro: PDF não gerado.")
        return jsonify({"erro": "Erro ao gerar PDF"}), 500

    print("LOG: transform_json - Enviando PDF como resposta.")
    return send_file(
        BytesIO(pdf_content),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"cv_otimizado.pdf"
    )
