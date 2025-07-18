# app/gerador_cv.py

# --- Bloco de Configuração de Caminhos e Importações ---
import os
import sys

# Pega o caminho absoluto do script atual (gerador_cv.py)
script_path = os.path.abspath(__file__)
# Pega o diretório do script (a pasta 'app')
script_dir = os.path.dirname(script_path)
# Sobe um nível para encontrar a raiz do projeto (a pasta 'resume')
project_root = os.path.dirname(script_dir)
# Adiciona a raiz do projeto ao path do Python para encontrar 'helpers'
sys.path.append(project_root)
# ---------------------------------------------

import json
import requests
from helpers.sanitizador import sanitizar_dados_para_latex

# Variável global para ser usada pelas funções
dados_brutos = {}

class GeradorCV:
    """
    Gera um currículo em LaTeX de forma programática, lendo os dados de um arquivo JSON.
    """

    def __init__(self):
        self.secoes = []

    def _gerar_preambulo(self):
        """Lê o preâmbulo de um arquivo externo usando um caminho robusto."""
        preambulo_path = os.path.join(script_dir, 'preambulo_template.tex')
        try:
            with open(preambulo_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            preambulo_formatado = template_content.replace("%%NOME_DA_PESSOA%%", self.nome)
            return preambulo_formatado
        except FileNotFoundError:
            print(f"❌ ERRO FATAL: Arquivo de template '{preambulo_path}' não encontrado.")
            return None

    def _gerar_cabecalho(self):
        """Gera o cabeçalho em duas linhas de forma simples e robusta, sem macros complexas."""
        
        # Separa os contatos em duas listas para as duas linhas
        contatos_principais = []
        links_sociais = []

        for contato in self.contatos:
            tipo = contato.get('tipo', 'texto')
            if tipo in ["linkedin", "github", "site"]:
                links_sociais.append(contato)
            else:
                contatos_principais.append(contato)
        
        def formatar_lista(lista):
            items_latex = []
            for contato in lista:
                tipo = contato.get('tipo', 'texto')
                valor = contato.get('valor', '')
                item_formatado = ""
                # A lógica de formatação de cada item continua a mesma
                if tipo == "localizacao": item_formatado = fr"\mbox{{{valor}}}"
                elif tipo == "email": item_formatado = fr"\mbox{{\href{{mailto:{valor}}}{{{valor}}}}}"
                elif tipo == "telefone": item_formatado = fr"\mbox{{\href{{tel:{valor.replace(' ', '').replace('-', '')}}}{{{valor}}}}}"
                elif tipo == "site":
                    url = valor if valor.startswith("http") else "https://" + valor
                    texto_display = valor.replace("https://", "").replace("http://", "")
                    item_formatado = fr"\mbox{{\href{{{url}}}{{{texto_display}}}}}"
                elif tipo == "linkedin":
                    url = f"{valor}"
                    texto_display = f"{valor}"
                    item_formatado = fr"\mbox{{\href{{{url}}}{{{"LinkedIn"}}}}}"
                elif tipo == "github":
                    url = f"{valor}"
                    texto_display = f"{valor}"
                    item_formatado = fr"\mbox{{\href{{{url}}}{{{"Github"}}}}}"
                else: item_formatado = fr"\mbox{{{valor}}}"
                items_latex.append(item_formatado)
            
            # --- A MUDANÇA PRINCIPAL ESTÁ AQUI ---
            # Usa um separador simples e robusto com espaçamento padrão do LaTeX
            separador = r" \enskip|\enskip " 
            return separador.join(items_latex)

        contatos_principais_str = formatar_lista(contatos_principais)
        links_sociais_str = formatar_lista(links_sociais)
        
        # Retorna um bloco LaTeX muito mais simples, sem \newcommand ou \sbox
        return fr"""
\begin{{header}}
    {{\fontsize{{25pt}}{{25pt}}\selectfont {self.nome}}}

    \vspace{{0pt}}

    \normalsize
    {contatos_principais_str} \\
    {links_sociais_str}
\end{{header}}

\vspace{{5pt - 0.1cm}}
"""

    def adicionar_secao_lista_simples(self, titulo, itens):
        print(f"LOG: GeradorCV.adicionar_secao_lista_simples - Adicionando seção '{titulo}' com {len(itens)} itens.")
        """Adiciona uma seção de lista simples."""
        if not isinstance(itens, list): 
            print(f"LOG: GeradorCV.adicionar_secao_lista_simples - Itens não é uma lista para '{titulo}'.")
            return
        conteudo = ""
        for i, item in enumerate(itens):
            conteudo += fr"\begin{{onecolentry}}{{{item}}}\end{{onecolentry}}"
            if i < len(itens) - 1:
                conteudo += "\n\\vspace{0.2cm}\n"
        self.secoes.append((titulo, conteudo))
        print(f"LOG: GeradorCV.adicionar_secao_lista_simples - Seção '{titulo}' adicionada.")

    def adicionar_secao_lista_categorizada(self, titulo, categorias):
        print(f"LOG: GeradorCV.adicionar_secao_lista_categorizada - Adicionando seção '{titulo}' com {len(categorias)} categorias.")
        """Adiciona uma seção de categorias, formatando cada uma como um item separado."""
        conteudo = ""
        for i, categoria in enumerate(categorias):
            if isinstance(categoria, dict) and 'nome' in categoria and 'itens' in categoria:
                nome_categoria = categoria['nome'] # O sanitizador já tratou o '&'
                itens_str = ", ".join(categoria['itens'])
                linha_formatada = fr"\textbf{{{nome_categoria}:}} {itens_str}"
                
                conteudo += fr"\begin{{onecolentry}}{{{linha_formatada}}}\end{{onecolentry}}"
                if i < len(categorias) - 1:
                    conteudo += "\n\\vspace{0.1cm}\n"
        self.secoes.append((titulo, conteudo))
        print(f"LOG: GeradorCV.adicionar_secao_lista_categorizada - Seção '{titulo}' adicionada.")

    def adicionar_secao_entradas_com_destaques(self, titulo, entradas):
        print(f"LOG: GeradorCV.adicionar_secao_entradas_com_destaques - Adicionando seção '{titulo}' com {len(entradas)} entradas.")
        """Adiciona uma seção de entradas com destaques (layout da coluna esquerda aprimorado)."""
        if not isinstance(entradas, list): 
            print(f"LOG: GeradorCV.adicionar_secao_entradas_com_destaques - Entradas não é uma lista para '{titulo}'.")
            return
        conteudo = ""
        for i, entrada in enumerate(entradas):
            print(f"LOG: GeradorCV.adicionar_secao_entradas_com_destaques - Processando entrada {i+1}.")
            if not isinstance(entrada, dict): 
                print(f"LOG: GeradorCV.adicionar_secao_entradas_com_destaques - Entrada {i+1} não é um dicionário. Pulando.")
                continue

            # Constrói a coluna da esquerda com quebra de linha para clareza
            titulo_principal = entrada.get("titulo", "")
            subtitulo_e_local = []
            if entrada.get("subtitulo"):
                subtitulo_e_local.append(entrada.get("subtitulo"))
            if entrada.get("local"):
                subtitulo_e_local.append(entrada.get("local"))
            
            coluna_esquerda = fr'\textbf{{{titulo_principal}}}'
            if subtitulo_e_local:
                coluna_esquerda += fr' \\ {", ".join(subtitulo_e_local)}'

            coluna_direita = fr'{entrada.get("data", "")}'
            conteudo_entrada = fr"""
\begin{{onecolentry}}
    \setcolumnwidth{{\fill, 4.5cm}}
    \begin{{paracol}}{{2}}
        {coluna_esquerda}
        \switchcolumn
        \raggedleft {coluna_direita}
    \end{{paracol}}
\end{{onecolentry}}"""
            if entrada.get("destaques"):
                destaques_latex = '\n'.join([fr'                \item {d}' for d in entrada["destaques"]])
                conteudo_entrada += fr"""
\vspace{{0.10cm}}
\begin{{onecolentry}}
    \begin{{highlights}}
{destaques_latex}
    \end{{highlights}}
\end{{onecolentry}}
"""
            conteudo += conteudo_entrada
            if i < len(entradas) - 1:
                conteudo += "\n\\vspace{0.2cm}\n"
        self.secoes.append((titulo, conteudo))
        print(f"LOG: GeradorCV.adicionar_secao_entradas_com_destaques - Seção '{titulo}' adicionada.")

    def gerar_latex(self):
        print("LOG: GeradorCV.gerar_latex - Iniciando geração de LaTeX.")
        """Monta e retorna a string completa do documento LaTeX."""
        preambulo = self._gerar_preambulo()
        if preambulo is None:
            print("LOG: GeradorCV.gerar_latex - ERRO: Preâmbulo não gerado.")
            return None
        
        cabecalho = self._gerar_cabecalho()
        partes = [preambulo, r"\begin{document}", cabecalho]
        
        print(f"LOG: GeradorCV.gerar_latex - Processando {len(self.secoes)} seções.")
        for titulo, conteudo in self.secoes:
            print(f"LOG: GeradorCV.gerar_latex - Adicionando seção LaTeX: {titulo}.")
            partes.append(fr"\section{{{titulo}}}")
            partes.append(conteudo)

        partes.append(r"\end{document}")
        latex_final = "\n".join(partes)
        print(f"LOG: GeradorCV.gerar_latex - LaTeX final gerado (tamanho: {len(latex_final)}).")
        return latex_final

    def salvar_tex(self, nome_arquivo="cv_gerado.tex"):
        print(f"LOG: GeradorCV.salvar_tex - Tentando salvar {nome_arquivo}.")
        codigo_latex = self.gerar_latex()
        if codigo_latex is None:
            print("LOG: GeradorCV.salvar_tex - Falha ao gerar código LaTeX. Arquivo .tex não será salvo.")
            return
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(codigo_latex)
            print(f"LOG: GeradorCV.salvar_tex - Arquivo '{nome_arquivo}' salvo com sucesso!")
        except Exception as e:
            print(f"LOG: GeradorCV.salvar_tex - ERRO ao salvar '{nome_arquivo}': {e}")

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
            # Esta parte é para testes locais, não deve ocorrer em produção.
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
        
        print(f"LOG: GeradorCV.download - Dados brutos recebidos (tipo: {type(dados_brutos)}).")

        # 1. Sanitiza uma cópia dos dados para o conteúdo do LaTeX.
        print("LOG: GeradorCV.download - Sanitizando dados para o LaTeX...")
        chaves_a_ignorar = {'tipo', 'itens'}
        dados_sanitizados = sanitizar_dados_para_latex(dados_brutos, chaves_para_ignorar=chaves_a_ignorar)
        print(f"LOG: GeradorCV.download - Dados sanitizados com sucesso.")
        
        # 2. Configura informações pessoais a partir dos dados sanitizados.
        dados_pessoais_sanitizados = dados_sanitizados.get('pessoais', {})
        self.nome = dados_pessoais_sanitizados.get('nome', 'Nome não encontrado')
        self.contatos = dados_pessoais_sanitizados.get('contatos', [])
        print(f"LOG: GeradorCV.download - Nome: {self.nome}, Contatos: {len(self.contatos)}.")

        # 3. Processa as seções com a LÓGICA CORRIGIDA.
        print("LOG: GeradorCV.download - Processando seções do currículo...")
        
        # USA DADOS BRUTOS PARA O CONTROLE DO LOOP
        for nome_secao, dados_secao_brutos in dados_brutos.get('secoes', {}).items():
            
            # Pega o tipo da seção dos dados BRUTOS, que não foi alterado.
            tipo_secao = dados_secao_brutos.get('tipo')
            print(f"LOG: GeradorCV.download - Processando seção: '{nome_secao}' (tipo lido: '{tipo_secao}').")

            # Pega a seção correspondente dos dados SANITIZADOS para obter o conteúdo seguro.
            dados_secao_sanitizados = dados_sanitizados.get('secoes', {}).get(nome_secao, {})
            if not dados_secao_sanitizados:
                print(f"LOG: GeradorCV.download - Aviso: Seção '{nome_secao}' não encontrada nos dados sanitizados. Pulando.")
                continue

            titulo_sanitizado = dados_secao_sanitizados.get('titulo', nome_secao)

            # O 'if/elif' agora funcionará perfeitamente.
            if tipo_secao == 'lista_simples':
                # 'itens' não são sanitizados por regra, então pegamos da fonte original.
                self.adicionar_secao_lista_simples(titulo_sanitizado, dados_secao_brutos.get('itens', []))

            elif tipo_secao == 'lista_categorizada':
                # Conteúdo vem dos dados sanitizados.
                self.adicionar_secao_lista_categorizada(titulo_sanitizado, dados_secao_sanitizados.get('categorias', []))
                
            elif tipo_secao == 'entradas_com_destaques':
                # Conteúdo vem dos dados sanitizados.
                self.adicionar_secao_entradas_com_destaques(titulo_sanitizado, dados_secao_sanitizados.get('entradas', []))
                
            else:
                print(f"LOG: GeradorCV.download - Aviso: Seção '{nome_secao}' com tipo '{tipo_secao}' não reconhecida. Pulando.")

        # 4. Geração dos arquivos (sem alteração).
        output_dir = os.path.join(project_root, 'output')
        os.makedirs(output_dir, exist_ok=True)
        nome_base_arquivo = f"cv_{self.nome.lower().replace(' ', '_')}"
        caminho_final = os.path.join(output_dir, nome_base_arquivo)
        
        print(f"LOG: GeradorCV.download - Salvando .tex em {caminho_final}.tex")
        self.salvar_tex(f"{caminho_final}.tex")
        print(f"LOG: GeradorCV.download - Gerando PDF em {caminho_final}.pdf")
        pdf = self.gerar_pdf(f"{caminho_final}.pdf")
        
        print("LOG: GeradorCV.download - Retornando PDF.")
        return pdf

if __name__ == "__main__":
    GeradorCV().main()