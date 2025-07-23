import os
import sys
# --------------------------------------------- #
# Pega o caminho absoluto do script atual (gerador_cv.py)
script_path = os.path.abspath(__file__)
# Pega o diretório do script (a pasta 'app')
script_dir = os.path.dirname(script_path)
# Sobe um nível para encontrar a raiz do projeto (a pasta 'resume')
project_root = os.path.dirname(script_dir)
# Adiciona a raiz do projeto ao path do Python para encontrar 'helpers'
sys.path.append(project_root)
# --------------------------------------------- #

import json
import requests
from helpers.sanitizador import sanitizar_dados_para_latex
from ai.llm_io import LLM

# Variável global para ser usada pelas funções
dados_brutos = {}

class GeradorCV:
    """
    Gera um currículo em LaTeX de forma programática, lendo os dados de um arquivo JSON.
    """

    def __init__(self):
        pass

    def compile_tex(self, tex_code):
        files_payload = {
            'filecontents[]': (None, tex_code),
            'filename[]': (None, 'document.tex'),
            'engine': (None, 'pdflatex'),
            'return': (None, 'pdf')
            }
        
        response = requests.post(
            "https://texlive.net/cgi-bin/latexcgi",
            files=files_payload,
            timeout=90)
        response.raise_for_status()

        if 'application/pdf' in response.headers.get('Content-Type', ''):
            return response.content
        elif 'application/pdf' not in response.headers.get('Content-Type', ''):

            errors = {}
            errors["payload"] = files_payload
            errors["error_messages"] = response.text
            errors["instruction"] = "fix errors and return the complete and fixed tex code: only tex code and nothing else"
            logs = json.dumps(errors)

            return logs

    def generate_from_tex(self, tex_code: str):

        compilation_result = self.compile_tex(tex_code)
        return compilation_result

    def gerar_pdf(self, nome_arquivo_saida="cv_gerado.pdf"):
        print(f"LOG: GeradorCV.gerar_pdf - Iniciando geração de PDF para '{nome_arquivo_saida}'...")
        codigo_latex = self.gerar_latex()
        if codigo_latex is None:
            print("LOG: GeradorCV.gerar_pdf - Falha ao gerar código LaTeX. Geração de PDF cancelada.")
            return None
        files_payload = {'filecontents[]': (None, codigo_latex),'filename[]': (None, 'document.tex'),'engine': (None, 'pdflatex'),'return': (None, 'pdf')}
        try:
            print("LOG: GeradorCV.gerar_pdf - Conectando à API de compilação LaTeX...")
            response = requests.post("https://texlive.net/cgi-bin/latexcgi", files=files_payload, timeout=90)
            response.raise_for_status()
            print(f"LOG: GeradorCV.gerar_pdf - Resposta da API recebida (Status: {response.status_code}, Content-Type: {response.headers.get('Content-Type')}).")
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                print(f"LOG: GeradorCV.gerar_pdf - PDF gerado com sucesso pela API.")
                return response.content
            else:
                print("LOG: GeradorCV.gerar_pdf - Erro na compilação LaTeX. Log da API:")
                print(response.content.decode('utf-8', errors='ignore'))
                return None
        except requests.exceptions.RequestException as e:
            print(f"LOG: GeradorCV.gerar_pdf - ERRO de conexão ou API: {e}")
            return None

    def download(self, dados=None):
        """Função principal que orquestra a geração do CV."""
        print("LOG: GeradorCV.download - Iniciando...")
        if dados is None:
            # Testes locais
            print("LOG: GeradorCV.download - Dados não fornecidos, usando arquivo local.")
            path = os.path.join(project_root, 'input', 'dados_cv.json')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    dados_brutos = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"LOG: GeradorCV.download - ERRO ao carregar dados locais: {e}")
                return None
        else:
            dados_brutos = dados

        # Garante que os dados brutos sejam um dicionário, não uma string JSON.
        if isinstance(dados_brutos, str):
            print("LOG: GeradorCV.download - Dados brutos são uma string. Decodificando JSON...")
            try:
                dados_brutos = json.loads(dados_brutos)
            except json.JSONDecodeError as e:
                print(f"LOG: GeradorCV.download - ERRO FATAL: Falha ao decodificar o JSON. {e}")
                return None

        print(f"LOG: GeradorCV.download - Dados brutos processados (tipo: {type(dados_brutos)}).")

        # 1. Sanitiza uma cópia dos dados para o conteúdo do LaTeX.
        print("LOG: GeradorCV.download - Sanitizando dados para o LaTeX...")
        chaves_a_ignorar = {'tipo', 'itens'}
        dados_sanitizados = sanitizar_dados_para_latex(dados_brutos, chaves_para_ignorar=chaves_a_ignorar)
        print(f"LOG: GeradorCV.download - Dados sanitizados com sucesso.")
        
        # 2. Configura informações pessoais a partir dos dados sanitizados.
        # Esta parte já é segura e lida com a ausência da chave 'pessoais'.
        dados_pessoais_sanitizados = dados_sanitizados.get('pessoais', {})
        self.nome = dados_pessoais_sanitizados.get('nome', 'Nome não encontrado')
        self.contatos = dados_pessoais_sanitizados.get('contatos', [])
        print(f"LOG: GeradorCV.download - Nome: {self.nome}, Contatos: {len(self.contatos)}.")

        # [REMOVIDO] - Bloco de código duplicado foi retirado daqui.
        
        # 3. Processa as seções do currículo.
        print("LOG: GeradorCV.download - Processando seções do currículo...")
        
        # [CORRIGIDO] - Processa 'secoes' como uma LISTA, que é o formato correto.
        # Itera sobre cada dicionário de seção na lista 'secoes'.
        secoes_brutas = dados_brutos.get('secoes', [])
        secoes_sanitizadas = dados_sanitizados.get('secoes', [])

        for i, secao_bruta in enumerate(secoes_brutas):
            tipo_secao = secao_bruta.get('type')
            
            # Garante que a seção correspondente exista nos dados sanitizados
            if i >= len(secoes_sanitizadas):
                print(f"LOG: GeradorCV.download - Aviso: Seção de índice {i} não encontrada nos dados sanitizados. Pulando.")
                continue
                
            secao_sanitizada = secoes_sanitizadas[i]
            titulo_sanitizado = secao_sanitizada.get('titulo', f'Seção {i+1}')

            print(f"LOG: GeradorCV.download - Processando seção: '{titulo_sanitizado}' (tipo: '{tipo_secao}').")

            if tipo_secao == 'lista_simples':
                self.adicionar_secao_lista_simples(titulo_sanitizado, secao_bruta.get('itens', []))
            elif tipo_secao == 'lista_categorizada':
                self.adicionar_secao_lista_categorizada(titulo_sanitizado, secao_sanitizada.get('categorias', []))
            elif tipo_secao == 'entradas_com_destaques':
                self.adicionar_secao_entradas_com_destaques(titulo_sanitizado, secao_sanitizada.get('entradas', []))
            else:
                print(f"LOG: GeradorCV.download - Aviso: Seção '{titulo_sanitizado}' com tipo '{tipo_secao}' não reconhecida. Pulando.")

        # 4. Geração dos arquivos.
        output_dir = os.path.join(project_root, 'output')
        os.makedirs(output_dir, exist_ok=True)
        nome_base_arquivo = f"cv_{self.nome.lower().replace(' ', '_')}"
        caminho_final = os.path.join(output_dir, nome_base_arquivo)
        
        print(f"LOG: GeradorCV.download - Salvando .tex em {caminho_final}.tex")
        self.salvar_tex(f"{caminho_final}.tex")
        
        print(f"LOG: GeradorCV.download - Gerando PDF...")
        pdf = self.gerar_pdf() # gerar_pdf já usa o latex gerado, não precisa de argumento
        
        print("LOG: GeradorCV.download - Finalizado.")
        return pdf


if __name__ == "__main__":
    GeradorCV().main()