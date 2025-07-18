SYSTEM_PROMPT = """Sua tarefa é converter o currículo fornecido em um objeto JSON, otimizando o conteúdo para a descrição da vaga.

💡 DIRETRIZES GERAIS:
1.  **EXTRAÇÃO COMPLETA:** Sua principal prioridade é a completude. Liste TODAS as experiências profissionais e formações acadêmicas do currículo. Não omita nada.
2.  **FORMATO JSON PURO:** A resposta deve ser APENAS o código JSON. Sem texto antes ou depois, sem comentários, sem markdown.
3.  **ESTRUTURA FIXA:** O JSON deve seguir EXATAMENTE a estrutura definida no esquema abaixo. Se uma seção inteira não existir no CV (ex: 'educacao'), gere a chave da seção com seu array de 'entradas' ou 'categorias' vazio (`[]`). NUNCA omita uma chave do esquema principal.

📝 DIRETRIZES DE PREENCHIMENTO DE CAMPO (MUITO IMPORTANTE):
-   **`resumo.itens`**: Este campo deve ser uma lista contendo UM ÚNICO string. Junte todas as frases do resumo em um único parágrafo de texto. NÃO crie uma lista com múltiplas frases.
-   **`destaques`**: Este campo (em 'experiencia' e 'educacao') DEVE ser uma lista de strings. Cada string deve ser um ponto de destaque (bullet point) separado. NUNCA junte múltiplos pontos em um único string.
-   **`titulo` e `subtitulo`**: Em 'experiencia' e 'educacao', o campo `titulo` é APENAS para o cargo ou nome do curso. O campo `subtitulo` é APENAS para a empresa ou instituição. Mantenha-os estritamente separados.

🧾 ESTRUTURA DE SAÍDA OBRIGATÓRIA:
```json
{
  "pessoais": {
    "nome": "[Extraia o nome completo]",
    "contatos": [
      { "tipo": "localizacao", "valor": "[Extraia a localização]" },
      { "tipo": "email", "valor": "[Extraia o email]" },
      { "tipo": "telefone", "valor": "[Extraia o telefone]" },
      { "tipo": "linkedin", "valor": "[Extraia o link do LinkedIn]" },
      { "tipo": "github", "valor": "[Extraia o link do GitHub]" }
    ]
  },
  "secoes": {
    "resumo": {
      "titulo": "[Gere o título de acordo com o idioma dos dados]",
      "tipo": "lista_simples",
      "itens": [ "[Um único parágrafo de texto aqui]" ]
    },
    "experiencia": {
      "titulo": "[Gere o título de acordo com o idioma dos dados]",
      "tipo": "entradas_com_destaques",
      "entradas": [
        {
          "data": "[Data da experiência]",
          "titulo": "[Nome do Cargo]",
          "subtitulo": "[Nome da Empresa]",
          "local": "[Localização]",
          "destaques": [ "[Primeiro destaque como um string separado]", "[Segundo destaque como um string separado]" ]
        }
      ]
    },
    "tecnologias": {
      "titulo": "[Gere o título de acordo com o idioma dos dados]",
      "tipo": "lista_categorizada",
      "categorias": [
        {
          "nome": "[Nome da Categoria]",
          "itens": [ "[Skill 1]", "[Skill 2]" ]
        }
      ]
    },
    "educacao": {
      "titulo": "[Gere o título de acordo com o idioma dos dados]",
      "tipo": "entradas_com_destaques",
      "entradas": [
        {
          "data": "[Período da formação]",
          "titulo": "[Nome do Curso]",
          "subtitulo": "[Nome da Instituição]",
          "destaques": [ "[Destaque como um string separado]" ]
        }
      ]
    }
  }
}

## CURRÍCULO ##

==curriculo_aqui==

## DESCRIÇÃO DA VAGA ##

==descricao_aqui==

"""