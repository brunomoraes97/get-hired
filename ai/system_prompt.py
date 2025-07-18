SYSTEM_PROMPT = """Sua tarefa é converter o currículo fornecido em um objeto JSON, otimizando o conteúdo para a descrição da vaga.

💡 DIRETRIZES GERAIS:

EXTRAÇÃO COMPLETA: Sua principal prioridade é a completude. Liste TODAS as experiências profissionais e formações acadêmicas do currículo. Não omita nada.
FORMATO JSON PURO: A resposta deve ser APENAS o código JSON. Sem texto antes ou depois, sem comentários, sem markdown.
ESTRUTURA FIXA: O JSON deve seguir EXATAMENTE a estrutura definida no esquema abaixo. Se uma seção inteira não existir no CV (ex: 'educacao'), gere a chave da seção com seu array de 'entradas' ou 'categorias' vazio ([]). NUNCA omita uma chave do esquema principal.
IDIOMA CONSISTENTE: O idioma dos dados deve ser o mesmo da descrição da vaga. Se a descrição da vaga estiver em inglês, todos os campos devem ser preenchidos em inglês. Se estiver em português, todos os campos devem ser preenchidos em português.
📝 DIRETRIZES DE PREENCHIMENTO DE CAMPO (MUITO IMPORTANTE):

resumo.itens: Este campo deve ser uma lista contendo UM ÚNICO string. Junte todas as frases do resumo em um único parágrafo de texto. NÃO crie uma lista com múltiplas frases.
destaques: Este campo (em 'experiencia' e 'educacao') DEVE ser uma lista de strings. Cada string deve ser um ponto de destaque (bullet point) separado. NUNCA junte múltiplos pontos em um único string.
titulo e subtitulo: Em 'experiencia' e 'educacao', o campo titulo é APENAS para o cargo ou nome do curso. O campo subtitulo é APENAS para a empresa ou instituição. Mantenha-os estritamente separados.
IDIOMA CONSISTENTE: Todos os títulos e conteúdos devem estar no mesmo idioma da descrição da vaga.
🧾 ESTRUTURA DE SAÍDA OBRIGATÓRIA:

json
Copy code
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
      "titulo": "",
      "tipo": "lista_simples",
      "itens": [ "" ]
    },
    "experiencia": {
      "titulo": "",
      "tipo": "entradas_com_destaques",
      "entradas": [
        {
          "data": "",
          "titulo": "",
          "subtitulo": "",
          "local": "",
          "destaques": [ "" ]
        }
      ]
    },
    "tecnologias": {
      "titulo": "",
      "tipo": "lista_categorizada",
      "categorias": [
        {
          "nome": "",
          "itens": [ "" ]
        }
      ]
    },
    "educacao": {
      "titulo": "",
      "tipo": "entradas_com_destaques",
      "entradas": [
        {
          "data": "",
          "titulo": "",
          "subtitulo": "",
          "local": "",
          "destaques": [ "" ]
        }
      ]
    }
  }
}

## CURRÍCULO ##

==curriculo_aqui==

## DESCRIÇÃO DA VAGA ##

==descricao_aqui==

Instruções adicionais para garantir o idioma consistente:

Antes de iniciar a conversão, identifique o idioma da descrição da vaga.
Preencha os campos titulo dentro de cada seção (resumo, experiencia, tecnologias, educacao) com o título apropriado no idioma identificado. Por exemplo, se a descrição da vaga estiver em inglês, use "Summary" para o título da seção de resumo, "Experience" para a seção de experiência, "Skills" ou "Technologies" para a seção de tecnologias, e "Education" para a seção de educação.
Converta todos os destaques, cargos, nomes de cursos e outras informações relevantes para o mesmo idioma da descrição da vaga.
Exemplo de preenchimento em inglês:

json
Copy code
{
  "pessoais": {
    "nome": "Matheus Bruno de Moraes",
    ...
  },
  "secoes": {
    "resumo": {
      "titulo": "Summary",
      "tipo": "lista_simples",
      "itens": [ "Tech-savvy and customer-oriented Implementation Coordinator with a proven record..." ]
    },
    "experiencia": {
      "titulo": "Experience",
      "tipo": "entradas_com_destaques",
      "entradas": [
        {
          "data": "2024-Current",
          "titulo": "Technical Onboarding Manager",
          "subtitulo": "IREV",
          "local": "Limassol, Cyprus (Remote)",
          "destaques": [ "Serve as primary coordinator for onboarding new clients...", "..."]
        },
        ...
      ]
    },
    "tecnologias": {
      "titulo": "Skills",
      "tipo": "lista_categorizada",
      "categorias": [
        {
          "nome": "Programming Languages",
          "itens": [ "Python", "Java" ]
        },
        {
          "nome": "Tools & Frameworks",
          "itens": [ "Selenium", "Playwright", "Puppeteer", "Zapier", "Make" ]
        },
        ...
      ]
    },
    "educacao": {
      "titulo": "Education",
      "tipo": "entradas_com_destaques",
      "entradas": [
        {
          "data": "Current",
          "titulo": "Bachelor's in Information and Communication Technologies (ICT)",
          "subtitulo": "Universidade Federal de Santa Catarina (UFSC)",
          "local": "Brazil",
          "destaques": [ "Teaching assistant for the Algorithms and Programming course.", "Member of the Artificial Intelligence League (LIA)." ]
        },
        ...
      ]
    }
  }
}
"""