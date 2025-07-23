# app/routes.py

from flask import (
    Blueprint,
    request,
    send_file,
    jsonify,
    render_template,
    redirect,
    url_for,
    current_app,
)
from core.app.gerador_cv import GeradorCV
from core.helpers.sanitizador import sanitizar_dados_para_latex
from io import BytesIO
import json
import os
import re
import zipfile
import jwt
from ai.llm_io import LLM
from flaskr.auth_utils import token_required
from flaskr.routes.auth import get_supabase
import logging


routes = Blueprint("routes", __name__)

@routes.route("/")
def index_redirect():
    return redirect(url_for('routes.home', lang_code='en'))


@routes.route('/home/<lang_code>')
def home(lang_code):
    supported_languages = ['en', 'pt', 'es', 'ru']
    if lang_code not in supported_languages:
        return redirect(url_for('routes.home', lang_code='en'))
    return render_template(f'home_{lang_code}.html')

@routes.route('/<lang_code>')
def index(lang_code):
    supported_languages = ['en', 'pt', 'es', 'ru']
    if lang_code not in supported_languages:
        return redirect(url_for('routes.index', lang_code='en')) # Default to English if unsupported
    return render_template(f'index_{lang_code}.html')

@routes.route('/generate', methods=["POST"])
@token_required
def transform_json():

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='logs',level=logging.INFO)
    logger.info('Started')


    dados_entrada = request.get_json()

    if not dados_entrada:
        logging.log(0,"LOG: transform_json - Erro: JSON ausente ou malformado.")
        return jsonify({"erro": "Corpo da requisição JSON ausente ou malformado."}), 400

    cv_text = dados_entrada.get("cv", "").replace("&", "and")
    vaga_text = dados_entrada.get("job_description", "").replace("&", "and")
    cover_letter_flag = dados_entrada.get("cover_letter", False)
    llm = LLM()
    print("PASSOU AQUI 1")
    print(f"LOG: transform_json - CV text length: {len(cv_text) if cv_text else 0}, Vaga text length: {len(vaga_text) if vaga_text else 0}")

    if not cv_text or not vaga_text:
        return jsonify({"erro": "As chaves 'cv' e 'job_description' são obrigatórias."}), 400

    print("LOG: transform_json - Chamando LLM.run()...")
    tex_code = llm.run(cv_text, vaga_text)
    print(f"LOG: transform_json - LLM.run() retornou dados brutos (tipo: {type(tex_code)}).")


        #### LIMPEZA
    def limpeza(tex_code):
        # LOG: transform_json - LLM.run() retornou dados brutos (tipo: ...).
        print("LOG: transform_json - Limpando LaTeX...")

        # Corrige escape duplicado de barras
        tex_code = tex_code.strip().strip('"').strip("'")
        if tex_code.startswith('\\\\documentclass') or '\\\\' in tex_code:
            tex_code = re.sub(r'\\\\', r'\\', tex_code)

        # Confirma se é LaTeX válido
        if not (tex_code.lstrip().startswith(r'\documentclass') and tex_code.strip().endswith(r'\end{document}')):
            print("LOG: transform_json - Erro: LaTeX inválido detectado.")
            return jsonify({"erro": "O código LaTeX retornado não é válido."}), 500

        return tex_code
    ##### AQUI!!!!!
    tex_code_limpo = limpeza(tex_code)
    pdf_file = GeradorCV().generate_from_tex(tex_code_limpo)

    # A função download() em GeradorCV já lida com a sanitização e a geração do PDF
    """print("LOG: transform_json - Chamando GeradorCV().download()...")
    pdf_content = GeradorCV().download(dados_brutos)
    print(f"LOG: transform_json - GeradorCV().download() retornou PDF (tamanho: {len(pdf_content) if pdf_content else 0}).")"""
    counter = 0
    while 'error_messages' in pdf_file and counter < 3:
        counter += 1
        new_tex_code = LLM().reprompt(pdf_file)
        pdf_file = GeradorCV().generate_from_tex(limpeza(new_tex_code))

    if 'error_messages' in pdf_file and counter >= 3:
        print("LOG: transform_json - Erro: PDF não gerado.")
        return jsonify({"erro": "Erro ao gerar PDF"}), 500

    if cover_letter_flag:
        print("LOG: transform_json - Gerando cover letter...")
        cover_letter_text = llm.generate_cover_letter(cv_text, vaga_text)
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            zf.writestr('cv_otimizado.pdf', pdf_file)
            zf.writestr('cover_letter.txt', cover_letter_text)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='cv_e_carta.zip'
        )

    print("LOG: transform_json - Enviando PDF como resposta.")
    return send_file(
        BytesIO(pdf_file),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="cv_otimizado.pdf"
    )


@routes.route('/resume-builder')
def resume_builder_redirect():
    """Redirects to the English resume builder."""
    return redirect(url_for('routes.resume_builder', lang_code='en'))


@routes.route('/resume-builder/<lang_code>')
def resume_builder(lang_code):
    """Display resume builder page in the requested language."""
    supported = ['en', 'pt', 'es', 'ru']
    if lang_code not in supported:
        return redirect(url_for('routes.resume_builder', lang_code='en'))
    return render_template(f'resume_builder_{lang_code}.html')


@routes.route('/create-resume', methods=['POST'])
@token_required
def create_resume():
    """Generate a resume PDF from form data."""
    data = request.get_json()
    if not data:
        return jsonify({'erro': 'Invalid data'}), 400

    cv_data = {
        'pessoais': {
            'nome': data.get('name', ''),
            'contatos': [
                {'tipo': 'localizacao', 'valor': data.get('location', '')},
                {'tipo': 'email', 'valor': data.get('email', '')},
                {'tipo': 'telefone', 'valor': data.get('phone', '')},
                {'tipo': 'linkedin', 'valor': data.get('linkedin', '')},
                {'tipo': 'github', 'valor': data.get('github', '')},
                {'tipo': 'site', 'valor': data.get('website', '')},
            ]
        },
        'secoes': []
    }

    # Save base resume data for LaTeX generation
    token = request.cookies.get('token')
    email = None
    if token:
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            email = payload.get('sub')
        except jwt.PyJWTError:
            email = None

    if email:
        try:
            supabase = get_supabase()
            supabase.table('latex_data').insert({
                'user_email': email,
                'resume_json': cv_data
            }).execute()
        except Exception:
            pass


    summary_text = data.get('summary', '')
    if summary_text:
        cv_data['secoes'].append({
            'titulo': 'Summary',
            'type': 'lista_simples',
            'itens': [summary_text]
        })

    skills_raw = data.get('skills', '')
    if isinstance(skills_raw, list):
        skills = skills_raw
    else:
        skills = [s.strip() for s in skills_raw.split(',') if s.strip()]
    if skills:
        cv_data['secoes'].append({
            'titulo': 'Skills',
            'type': 'lista_simples',
            'itens': skills
        })

    experiences = data.get('experiences', [])
    if experiences:
        entries = []
        for exp in experiences:
            desc = exp.get('description', '')
            highlights = [d.strip() for d in desc.split('\n') if d.strip()] if desc else []
            entries.append({
                'data': exp.get('period', ''),
                'titulo': exp.get('title', ''),
                'subtitulo': exp.get('company', ''),
                'local': exp.get('location', ''),
                'destaques': highlights
            })
        cv_data['secoes'].append({
            'titulo': 'Experience',
            'type': 'entradas_com_destaques',
            'entradas': entries
        })

    education = data.get('education', [])
    if education:
        entries = []
        for ed in education:
            desc = ed.get('description', '')
            highlights = [d.strip() for d in desc.split('\n') if d.strip()] if desc else []
            entries.append({
                'data': ed.get('period', ''),
                'titulo': ed.get('degree', ''),
                'subtitulo': ed.get('institution', ''),
                'local': ed.get('field_of_study', ''),
                'destaques': highlights
            })
        cv_data['secoes'].append({
            'titulo': 'Education',
            'type': 'entradas_com_destaques',
            'entradas': entries
        })

    languages = data.get('languages', [])
    if languages:
        cv_data['secoes'].append({
            'titulo': 'Languages',
            'type': 'lista_simples',
            'itens': languages
        })

    pdf_content = GeradorCV().download(cv_data)
    if not pdf_content:
        return jsonify({'erro': 'Erro ao gerar PDF'}), 500

    return send_file(
        BytesIO(pdf_content),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='resume.pdf'
    )


@routes.route('/generate-field', methods=['POST'])
@token_required
def generate_field_route():
    """Generate text for a single resume field using LLM."""
    data = request.get_json()
    if not data or 'field_name' not in data or 'instructions' not in data:
        return jsonify({'erro': 'Invalid data'}), 400

    llm = LLM()
    try:
        text = llm.generate_field(data['field_name'], data['instructions'])
    except Exception:
        return jsonify({'erro': 'Generation failed'}), 500

    return jsonify({'text': text})
