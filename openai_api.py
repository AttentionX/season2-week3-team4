import os
import openai
import tiktoken
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Key 세팅하기
openai.api_key = os.environ.get('OPENAI_KEY')

model = "gpt-3.5-turbo"
system_message = "You are a helpful assistant"
query = "Explain self-attention"

class OpenAI_API:
    def __init__(self, model=model, system_message=system_message):
        self.model = model
        self.system_message = system_message

    def chatgpt(self, query):
        messages = [
            {"role":"system", "content":self.system_message},
            {"role":"user", "content":query}
        ]

        functions = [
            {
            "name": "get_word_rank",
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "the next word to guess",
                    },
                },
                
            },
        }    
        ]
    
        response = openai.ChatCompletion.create(model=self.model, messages=messages,
                                               # functions=functions
                                            ).choices[0].message.content
        return response
    
    @staticmethod
    def get_embedding(query):
        query = query.replace("\n", " ")
        return openai.Embedding.create(input = [query], model="text-embedding-ada-002")['data'][0]['embedding']
    
    def token_count(self, text):
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = len(encoding.encode(text))
        return num_tokens
