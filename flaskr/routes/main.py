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

@routes.route("/")
def index():
    return render_template("index.html")

@routes.route('/generate', methods=["POST"])
def transform_json():
    dados_entrada = request.get_json()
    if not dados_entrada:
        return jsonify({"erro": "Corpo da requisição JSON ausente ou malformado."}), 400
    
    cv = dados_entrada.get("cv")
    vaga = dados_entrada.get("job_description")

    if not cv or not vaga:
        return jsonify({"erro": "As chaves 'texto_cv' e 'texto_vaga' são obrigatórias."}), 400

    llm = LLM()

    dados_brutos = llm.run(cv,vaga)
    pdf = GeradorCV().download(dados_brutos)

    return send_file(
        BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"cv_{"resume".lower().replace(' ', '_')}.pdf"
    )

"""
    if not dados_brutos:
        return jsonify({"erro": "JSON ausente ou malformado na requisição"}), 400

    # MUDANÇA 2: Sanitizar tudo para maior segurança
    dados = sanitizar_dados_para_latex(dados_brutos, chaves_para_ignorar={'itens'})
    
    dados_pessoais = dados.get('pessoais', {})
    cv = GeradorCV(
        nome=dados_pessoais.get('nome', 'Nome não encontrado'),
        contatos=dados_pessoais.get('contatos', [])
    )

    print("Processando seções do currículo...")

    for nome_secao, dados_secao in dados_brutos.get('secoes', {}).items():
        if not isinstance(dados_secao, dict):
            print(f"  - Aviso: Seção '{nome_secao}' está mal formatada. Pulando.")
            continue

        tipo_secao = dados_secao.get('tipo')
        titulo_sanitizado = dados.get('secoes', {}).get(nome_secao, {}).get('titulo', f"secao_{nome_secao}")

        if tipo_secao == 'lista_simples':
            cv.adicionar_secao_lista_simples(titulo_sanitizado, dados_secao.get('itens', []))
        elif tipo_secao == 'lista_categorizada':
            cv.adicionar_secao_lista_categorizada(titulo_sanitizado, dados.get('secoes', {}).get(nome_secao, {}).get('categorias', []))
        elif tipo_secao == 'entradas_com_destaques':
            cv.adicionar_secao_entradas_com_destaques(titulo_sanitizado, dados.get('secoes', {}).get(nome_secao, {}).get('entradas', []))
        else:
            print(f"  - Aviso: Seção '{nome_secao}' com tipo '{tipo_secao}' não reconhecida. Pulando.")

    pdf = cv.gerar_pdf()"""
