import yaml
import os

# --- ESTRUTURA ESPERADA ---
# Define as chaves obrigatórias para cada tipo de entrada para uma validação mais detalhada.
CHAVES_OBRIGATORIAS = {
    "experiencia": {"data", "cargo", "empresa", "local", "destaques"},
    "educacao": {"data", "curso", "instituicao", "destaques"},
    "publicacoes": {"data", "titulo", "autores", "doi", "doi_url"},
    "projetos": {"titulo", "link", "destaques"},
}

def validar_estrutura(dados):
    """
    Valida a estrutura dos dados carregados do YAML.
    Retorna uma lista de erros encontrados.
    """
    erros = []

    # 1. Validação de chaves principais
    if not isinstance(dados, dict):
        return ["O arquivo YAML não representa um dicionário (chave: valor)."]
        
    if 'pessoais' not in dados:
        erros.append("A chave principal 'pessoais' não foi encontrada.")
    if 'secoes' not in dados:
        erros.append("A chave principal 'secoes' não foi encontrada.")

    # 2. Validação da seção 'pessoais'
    if 'pessoais' in dados:
        pessoais = dados['pessoais']
        if not isinstance(pessoais, dict):
            erros.append("'pessoais' deveria ser um dicionário.")
        else:
            if 'nome' not in pessoais:
                erros.append("A chave 'nome' está faltando em 'pessoais'.")
            if 'contatos' not in pessoais:
                erros.append("A chave 'contatos' está faltando em 'pessoais'.")
            elif not isinstance(pessoais.get('contatos'), list):
                 erros.append("'contatos' deveria ser uma lista.")
            else:
                for i, contato in enumerate(pessoais['contatos']):
                    if not isinstance(contato, dict) or 'tipo' not in contato or 'valor' not in contato:
                        erros.append(f"O item {i+1} na lista 'contatos' está mal formatado. Precisa ser um dicionário com as chaves 'tipo' e 'valor'.")

    # 3. Validação da seção 'secoes'
    if 'secoes' in dados:
        secoes = dados['secoes']
        if not isinstance(secoes, dict):
            erros.append("'secoes' deveria ser um dicionário.")
        else:
            for nome_secao, conteudo_secao in secoes.items():
                if not isinstance(conteudo_secao, dict) or 'titulo' not in conteudo_secao:
                    erros.append(f"A seção '{nome_secao}' está mal formatada. Precisa ser um dicionário com a chave 'titulo'.")
                    continue
                
                # Valida se a seção tem 'entradas' ou 'itens'
                tem_entradas = 'entradas' in conteudo_secao
                tem_itens = 'itens' in conteudo_secao

                if not tem_entradas and not tem_itens:
                    erros.append(f"A seção '{nome_secao}' precisa ter ou 'entradas' ou 'itens'.")
                    continue

                if tem_entradas and not isinstance(conteudo_secao['entradas'], list):
                    erros.append(f"A chave 'entradas' na seção '{nome_secao}' deveria ser uma lista.")
                
                if tem_itens and not isinstance(conteudo_secao['itens'], list):
                    erros.append(f"A chave 'itens' na seção '{nome_secao}' deveria ser uma lista.")

                # Validação detalhada das entradas, se aplicável
                if tem_entradas and nome_secao in CHAVES_OBRIGATORIAS:
                    chaves_necessarias = CHAVES_OBRIGATORIAS[nome_secao]
                    for i, entrada in enumerate(conteudo_secao['entradas']):
                         if not isinstance(entrada, dict) or not chaves_necessarias.issubset(entrada.keys()):
                             chaves_faltando = chaves_necessarias - entrada.keys()
                             erros.append(f"A entrada {i+1} da seção '{nome_secao}' está incompleta. Faltando chaves: {chaves_faltando}")


    return erros


def main():
    """
    Função principal que executa a validação completa do arquivo YAML.
    """
    try:
        # --- CÓDIGO NOVO PARA CONSTRUIR O CAMINHO ---
        # Pega o caminho absoluto do script que está sendo executado (validate_yaml.py)
        script_path = os.path.abspath(__file__)
        # Pega o diretório onde o script está (a pasta 'helpers')
        script_dir = os.path.dirname(script_path)
        # Sobe um nível para encontrar a raiz do projeto (a pasta 'resume')
        project_root = os.path.dirname(script_dir)
        # Monta o caminho completo e correto para o arquivo de dados
        caminho_arquivo = os.path.join(project_root, 'input', 'dados_cv.yaml')
        # ---------------------------------------------

        print(f"--- Iniciando validação de '{caminho_arquivo}' ---")

        # 1. Verifica se o arquivo existe
        if not os.path.exists(caminho_arquivo):
            print(f"❌ ERRO FATAL: Arquivo '{caminho_arquivo}' não foi encontrado pelo caminho construído.")
            return

        # 2. Verifica a sintaxe do YAML
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = yaml.safe_load(f)
        print("✅ Sintaxe do YAML está correta.")

    except yaml.YAMLError as e:
        print(f"❌ ERRO FATAL: O arquivo '{caminho_arquivo}' possui um erro de sintaxe YAML:")
        print(e)
        return
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return


    # 3. Verifica a estrutura dos dados
    print("Verificando a estrutura e os itens obrigatórios...")
    erros_estrutura = validar_estrutura(dados)

    if not erros_estrutura:
        print("\n🎉 SUCESSO! A estrutura do arquivo YAML está correta e todos os itens necessários foram encontrados.")
    else:
        print("\n❌ ATENÇÃO! Foram encontrados os seguintes problemas de estrutura:")
        for i, erro in enumerate(erros_estrutura):
            print(f"   {i+1}. {erro}")
        print("\nPor favor, corrija os itens acima no seu arquivo 'dados_cv.yaml'.")


if __name__ == "__main__":
    main()