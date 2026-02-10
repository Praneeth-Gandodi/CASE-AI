from openai import OpenAI
from openai import APIConnectionError, AuthenticationError, RateLimitError, APIStatusError
from core.exception import CASEError, ProviderNotFound 
from core.config import provider_json_path
import json

class Providers:

    def __init__(self, provider_id:str ,api_key:str, model:str, tools:list = None):
        self.provider_id  = provider_id
        self.model = model 
        self.tools = tools 
        self.api_key = api_key
        self.endpoint = self.get_endpoint()
        self.client = OpenAI(base_url=self.endpoint, api_key=self.api_key)

    def get_endpoint(self):
        with open(provider_json_path, 'r') as file:
            providers_json = json.load(file)
            
            endpoint = None
            for provider in providers_json:
                if provider['provider_id'] == self.provider_id:
                    endpoint = provider["endpoint"]
                    return endpoint
            if not endpoint:
                raise ProviderNotFound("The provider you are trying to access is not in the providers json.")
                
    def chat(self, chat_completion:list):
        try:
            response_delta = self.client.chat.completions.create(
                model = self.model,
                messages = chat_completion,
                stream = True,
                tools = self.tools 
            )
            for response in response_delta:
                yield response
        except AuthenticationError as e:
            raise  
        except APIConnectionError as e: 
            raise 
        except RateLimitError as e:
            raise 
        except APIStatusError as e:
            raise 
        except CASEError as e:
            raise         
        
    def non_streaming_chat(self, chat_completion:list ):
        
        try:
            response = self.client.chat.completions.create(
            model = self.model,
            messages = chat_completion,
            stream = False,
            tools = self.tools 
            )

            return response
        
        except AuthenticationError as e:
            raise 
        except APIConnectionError as e: 
            raise 
        except RateLimitError as e:
            raise 
        except CASEError as e:
            raise 
    
    def generate_image(self):
        pass        
            

        
