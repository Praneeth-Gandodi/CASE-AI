from openai import OpenAI
from openai import APIConnectionError, AuthenticationError, RateLimitError
from core.exception import CASEError, ProviderNotFound 
from pathlib import Path
import json
class Providers:

    def __init__(self, provider_id:str ,api_key:str, model:str, stream:bool = False, tools:list = None):
        self.provider_id  = provider_id
        self.model = model 
        self.stream = stream
        self.tools = tools 
        self.api_key = api_key
        self.endpoint = self.get_endpoint()
        self.client = OpenAI(base_url=self.endpoint, api_key=self.api_key)

    def get_endpoint(self):
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / "providers.json"
        with open(file_path, 'r') as file:
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
            response = self.client.chat.completions.create(
                model = self.model,
                messages = chat_completion,
                stream = self.stream,
                tools = self.tools 
            )
            return response
        except AuthenticationError as e:
            raise AuthenticationError("API key is invalid or expired.") 
        except APIConnectionError as e: 
            raise APIConnectionError(f"Failed to conenct to the provider at {self.provider_name}")
        except RateLimitError as e:
            raise RateLimitError("Rate limit exceeded. Please wait and try again.")
        except CASEError as e:
            raise CASEError(f"An Unexpected error occured with the providder {e}.")
    
    def generate_image(self):
        pass        
            
        
 


