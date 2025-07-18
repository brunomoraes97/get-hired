# helpers/sanitizador.py

def sanitizar_dados_para_latex(item, chaves_para_ignorar=set()):
    """
    Navega recursivamente em uma estrutura de dados (dicionários, listas)
    e aplica a sanitização de LaTeX em todas as strings que encontrar,
    exceto naquelas cujas chaves estão no conjunto de ignorados.
    """
    if isinstance(item, dict):
        # Processa um dicionário, respeitando as chaves a serem ignoradas.
        return {
            k: v if k in chaves_para_ignorar 
            else sanitizar_dados_para_latex(v, chaves_para_ignorar) 
            for k, v in item.items()
        }

    elif isinstance(item, list):
        # Processa uma lista, aplicando a sanitização a cada elemento.
        return [sanitizar_dados_para_latex(elem, chaves_para_ignorar) for elem in item]

    elif isinstance(item, str):
        # Sanitiza uma string, substituindo caracteres especiais do LaTeX.
        
        # A barra invertida DEVE ser o primeiro item a ser substituído para evitar erros.
        replacements = {
            '\\': r'\\textbackslash{}',
            '&': r'\\&',
            '%': r'\\%',
            '$': r'\\$',
            '#': r'\\#',
            '_': r'\\_',
            '{': r'\\{',
            '}': r'\\}',
            '~': r'\\textasciitilde{}',
            '^': r'\\textasciicircum{}',
        }
        
        sanitized_item = item
        for char, replacement in replacements.items():
            sanitized_item = sanitized_item.replace(char, replacement)
            
        return sanitized_item

    else:
        # Retorna qualquer outro tipo de dado (int, float, bool, None) como está.
        return item