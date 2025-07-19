from maritalk import count_tokens
from dotenv import load_dotenv
import openai
load_dotenv()
import os
from ai.system_prompt import SYSTEM_PROMPT, USER_MESSAGE
from ai.tests.fixtures.curriculo import CURRICULO
from ai.tests.fixtures.descricao import DESCRICAO
from ai.schemas import CV
import google.generativeai as genai

class LLM:
    def __init__(self):

        """self.api_key = os.getenv("OLLAMA_APIKEY")
        self.base_url = os.getenv("OLLAMA_URL")
        self.model=os.getenv("OLLAMA_MODEL")"""

        self.api_key=os.getenv("GEMINI_APIKEY")
        self.model=os.getenv("GEMINI_MODEL")

    def prompt(self, question: str):
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }
        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=SYSTEM_PROMPT,
            generation_config=generation_config
        )
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(question)
        return response.text

    """def prompt(self, question: str):
        print(self.model)
        self.model=os.getenv("OLLAMA_MODEL")
        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        response = client.chat.completions.parse(
            model="qwen3:4b",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=8000,
            temperature=0.3,
            response_format=CV
        )
        return response.choices[0].message.content"""


    """self.api_key = os.getenv("MARITACA_APIKEY")
       self.base_url = os.getenv("MARITACA_URL")
       self.model=os.getenv("MARITACA_MODEL")"""

    def test(self):
        question = SYSTEM_PROMPT \
            .replace("==curriculo_aqui==", CURRICULO) \
            .replace("==descricao_aqui==", DESCRICAO)
      
        output = self.prompt(question)
        return output
    
    def run(self, cv, job_description):
        question = USER_MESSAGE \
            .replace("==curriculo_aqui==", cv) \
            .replace("==descricao_aqui==", job_description)
        
        print("--- PROMPT FINAL ENVIADO PARA A API ---")
        print(question)
        print("---------------------------------------")
        output = self.prompt(question)
        print("PASSOU AQUI 4")
        print(f"ANSWER É: {output}")
        print("PASSOU AQUI 5 -> gerou output. OUTPUT É ANSWER EM JSON")
        print(output)
        return output

if __name__ == "__main__":
    
    question = SYSTEM_PROMPT \
                .replace("==curriculo_aqui==", CURRICULO) \
                .replace("==descricao_aqui==", DESCRICAO)
      
    llm = LLM()
    output = llm.prompt(question)
    print(output)

    ########## MARITACA AI ##############
    #input_tokens = count_tokens(question, model="deepseek-chat")
    #output_tokens = count_tokens(answer, model="sabia-3")
    #total_tokens = f"O total de tokens usados foi: {int(input_tokens) + int(output_tokens)}. Entrada: {input_tokens}, Saída: {output_tokens}"
    #print(total_tokens)
    ########## MARITACA AI #############