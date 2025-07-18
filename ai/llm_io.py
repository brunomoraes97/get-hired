from maritalk import count_tokens
from dotenv import load_dotenv
import openai
load_dotenv()
import os
import json
from ai.system_prompt import SYSTEM_PROMPT
from ai.tests.fixtures.curriculo import CURRICULO
from ai.tests.fixtures.descricao import DESCRICAO
import re

class LLM:
    def __init__(self):
        self.api_key = os.getenv("MARITACA_APIKEY")
        self.base_url = os.getenv("MARITACA_URL")
        self.model=os.getenv("MARITACA_MODEL")

    def prompt(self, question: str):
       
        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        response = client.chat.completions.create(
        model=self.model,
        messages=[
            {
                "role": "user",
                "content": question
            }
        ],
        max_tokens=8000,
        temperature=0.3
        )
        return response.choices[0].message.content
    
    def gera_json(self,answer):
        try:
            output = self.extract_json(answer)
            return output
        except Exception as e:
            return e
    
    def extract_json(self,text):
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Nenhum JSON válido encontrado na resposta.")
    
    def test(self):
        question = SYSTEM_PROMPT \
            .replace("==curriculo_aqui==", CURRICULO) \
            .replace("==descricao_aqui==", DESCRICAO)
      
        answer = self.prompt(question)
        output = self.gera_json(answer)
        return output
    
    def run(self, cv, job_description):
        question = SYSTEM_PROMPT \
            .replace("==curriculo_aqui==", cv) \
            .replace("==descricao_aqui==", job_description)
        

        print("--- PROMPT FINAL ENVIADO PARA A API ---")
        print(question)
        print("---------------------------------------")
        answer = self.prompt(question)
        output = self.gera_json(answer)
        print(output)
        return output


if __name__ == "__main__":
    
    question = SYSTEM_PROMPT \
                .replace("==curriculo_aqui==", CURRICULO) \
                .replace("==descricao_aqui==", DESCRICAO)
      
    llm = LLM()
    answer = llm.prompt(question)
    output = llm.gera_json(answer)
    print(output)

    ########## MARITACA AI ##############
    #input_tokens = count_tokens(question, model="deepseek-chat")
    #output_tokens = count_tokens(answer, model="sabia-3")
    #total_tokens = f"O total de tokens usados foi: {int(input_tokens) + int(output_tokens)}. Entrada: {input_tokens}, Saída: {output_tokens}"
    #print(total_tokens)
    ########## MARITACA AI ##############