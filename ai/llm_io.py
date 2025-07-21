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
from core.app.preambulo_template import preamble

class LLM:
    def __init__(self):

        """self.api_key = os.getenv("OLLAMA_APIKEY")
        self.base_url = os.getenv("OLLAMA_URL")
        self.model=os.getenv("OLLAMA_MODEL")"""

        self.api_key=os.getenv("GEMINI_APIKEY")
        self.model=os.getenv("GEMINI_MODEL")

    def prompt(self, cv: str, job_description: str):
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
        response = model.generate_content(
            [
                f"System prompt: {SYSTEM_PROMPT}",
                f"Preamble template: {preamble}",
                f"CV:\n{cv}",
                f"Job Description:\n{job_description}",
                f"Language:\nSame language as the job description",
            ],
            generation_config=generation_config
        )
        return response.text

    def generate_field(self, field_name: str, instructions: str) -> str:
        """Generate resume text for a specific field using natural language instructions."""
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        system_prompt = (
            f"You are a professional resume writer. Generate the {field_name} "
            f"using the user's notes. Return only the plain text or bullet list."
        )
        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt,
            generation_config=generation_config,
        )
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(instructions)
        return response.text.strip()

    def generate_cover_letter(self, cv: str, job_description: str) -> str:
        """Generate a cover letter based on the resume and job description."""
        genai.configure(api_key=self.api_key)
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        system_prompt = (
            "You are an expert career coach. Write a concise cover letter "
            "for the provided job description using information from the resume."
            "Do not use empty placeholders such as [Your Name] and [Date]"
            "Populate placeholders according to the information from the resume"
        )
        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt,
            generation_config=generation_config,
        )
        chat_session = model.start_chat(history=[])
        prompt = f"RESUME:\n{cv}\nJOB DESCRIPTION:\n{job_description}"
        response = chat_session.send_message(prompt)
        return response.text.strip()

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
        output = self.prompt(cv, job_description)
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