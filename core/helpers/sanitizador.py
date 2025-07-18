 # helpers/sanitizador.py

def sanitizar_dados_para_latex(item, chaves_para_ignorar=set()):
    """
    Navega recursivamente em uma estrutura de dados (dicionários, listas)
    e aplica a sanitização de LaTeX em todas as strings que encontrar,
    exceto naquelas cujas chaves estão na lista de ignorados.
    """
    if isinstance(item, dict):
        # Se for um dicionário, chama a função para cada valor
        # A chave 'itens' (usada em tecnologias) será ignorada para não quebrar comandos como \textbf{}
        return {k: v if k in chaves_para_ignorar else sanitizar_dados_para_latex(v, chaves_para_ignorar) for k, v in item.items()}
    elif isinstance(item, list):
        # Se for uma lista, chama a função para cada elemento
        return [sanitizar_dados_para_latex(elem, chaves_para_ignorar) for elem in item]
    elif isinstance(item, str):
        # Se for uma string, aplica a sanitização dos caracteres especiais do LaTeX
        replacements = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
        }
        for char, replacement in replacements.items():
            item = item.replace(char, replacement)
        return item
    else:
        # Se for outro tipo (número, etc.), retorna como está
        return item