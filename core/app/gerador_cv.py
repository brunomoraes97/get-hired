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
        """Adiciona uma seção de lista simples."""
        if not isinstance(itens, list): return
        conteudo = ""
        for i, item in enumerate(itens):
            conteudo += fr"\begin{{onecolentry}}{{{item}}}\end{{onecolentry}}"
            if i < len(itens) - 1:
                conteudo += "\n\\vspace{0.2cm}\n"
        self.secoes.append((titulo, conteudo))

    def adicionar_secao_lista_categorizada(self, titulo, categorias):
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

    def adicionar_secao_entradas_com_destaques(self, titulo, entradas):
        """Adiciona uma seção de entradas com destaques (layout da coluna esquerda aprimorado)."""
        if not isinstance(entradas, list): return
        conteudo = ""
        for i, entrada in enumerate(entradas):
            if not isinstance(entrada, dict): continue

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

    def gerar_latex(self):
            """Monta e retorna a string completa do documento LaTeX."""
            preambulo = self._gerar_preambulo()
            if preambulo is None:
                return None
            
            cabecalho = self._gerar_cabecalho()
            partes = [preambulo, r"\begin{document}", cabecalho]
            
            # CORREÇÃO: A função agora simplesmente percorre as seções
            # que já foram formatadas e salvas em self.secoes.
            for titulo, conteudo in self.secoes:
                partes.append(fr"\section{{{titulo}}}")
                partes.append(conteudo)

            partes.append(r"\end{document}")
            return "\n".join(partes)

    def salvar_tex(self, nome_arquivo="cv_gerado.tex"):
        codigo_latex = self.gerar_latex()
        if codigo_latex is None:
            print("❌ Falha ao gerar código LaTeX. Arquivo .tex não será salvo.")
            return
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(codigo_latex)
        print(f"✅ Arquivo '{nome_arquivo}' salvo com sucesso!")

    def gerar_pdf(self, nome_arquivo_saida="cv_gerado.pdf"):
        print(f"\n⚙️  Gerando PDF como '{nome_arquivo_saida}'...")
        codigo_latex = self.gerar_latex()
        if codigo_latex is None:
            print("❌ Falha ao gerar código LaTeX. Geração de PDF cancelada.")
            return
        files_payload = {'filecontents[]': (None, codigo_latex),'filename[]': (None, 'document.tex'),'engine': (None, 'pdflatex'),'return': (None, 'pdf')}
        try:
            print("📡 Conectando à API e compilando...")
            response = requests.post("https://texlive.net/cgi-bin/latexcgi", files=files_payload, timeout=90)
            response.raise_for_status()
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                with open(nome_arquivo_saida, 'wb') as f:
                    f.write(response.content)
                print(f"🎉 PDF '{nome_arquivo_saida}' gerado com sucesso!")
                return response.content
            else:
                print("❌ Erro na compilação LaTeX. Log da API:")
                print(response.content.decode('utf-8', errors='ignore'))
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")

    def download(self,dados=None):
        """Função principal que orquestra a geração do CV."""
        global dados_brutos
        print("Iniciando gerador de CV a partir de 'dados_cv.json'...")
        path = os.path.join(project_root, 'input', 'dados_cv.json')

        if dados == None:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    dados_brutos = json.load(f)
            except FileNotFoundError:
                print(f"\nERRO: Arquivo '{path}' não encontrado.")
                return
            except json.JSONDecodeError as e:
                print(f"\nERRO ao ler o arquivo JSON: {e}")
                return
        else:
            dados_brutos = dados

        print("Sanitizando dados para o LaTeX...")
        dados = sanitizar_dados_para_latex(dados_brutos, chaves_para_ignorar={'itens'})
        
        dados_pessoais = dados.get('pessoais', {})
        self.nome=dados_pessoais.get('nome', 'Nome não encontrado')
        self.contatos=dados_pessoais.get('contatos', [])

        print("Processando seções do currículo...")
        for nome_secao, dados_secao in dados_brutos.get('secoes', {}).items():
            if not isinstance(dados_secao, dict):
                print(f"  - Aviso: Seção '{nome_secao}' está mal formatada. Pulando.")
                continue

            tipo_secao = dados_secao.get('tipo')
            titulo_sanitizado = dados.get('secoes', {}).get(nome_secao, {}).get('titulo', f"secao_{nome_secao}")

            if tipo_secao == 'lista_simples':
                self.adicionar_secao_lista_simples(titulo_sanitizado, dados_secao.get('itens', []))
            elif tipo_secao == 'lista_categorizada':
                self.adicionar_secao_lista_categorizada(titulo_sanitizado, dados.get('secoes', {}).get(nome_secao, {}).get('categorias', []))
            elif tipo_secao == 'entradas_com_destaques':
                self.adicionar_secao_entradas_com_destaques(titulo_sanitizado, dados.get('secoes', {}).get(nome_secao, {}).get('entradas', []))
            else:
                print(f"  - Aviso: Seção '{nome_secao}' com tipo '{tipo_secao}' não reconhecida. Pulando.")

        output_dir = os.path.join(project_root, 'output')
        os.makedirs(output_dir, exist_ok=True)
        nome_base_arquivo = f"cv_{dados_pessoais.get('nome', 'sem_nome').lower().replace(' ', '_')}"
        caminho_final = os.path.join(output_dir, nome_base_arquivo)
        
        self.salvar_tex(f"{caminho_final}.tex")
        pdf = self.gerar_pdf(f"{caminho_final}.pdf")
        
        return pdf

        #print("\nProcesso finalizado!")

if __name__ == "__main__":
    GeradorCV().main()