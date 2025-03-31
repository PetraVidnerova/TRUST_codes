
from ollama import Client

HOST = 'http://localhost:11434'
MODEL = 'jean-luc/tiger-gemma-9b-v3:fp16'


class OllamaChat():

    def __init__(self):
        self.client = Client(host=HOST)
        
    def complete(self, prompt):
        response = self.client.chat(model=MODEL, 
                                    messages=[{                                                                                                         
                'content': prompt,                                                                      
                'role': 'user',                                                                                         
            },                                                                                                        
        ])                                                                                                          
                                                                                                            
        return response["message"]["content"]


    