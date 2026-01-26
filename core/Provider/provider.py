from openai import OpenAI
from dotenv import load_dotenv, set_key
from pathlib import Path
import json
import os
import questionary
from rich.console import Console

console = Console()
class Providers:

    def __init__(self, provider_id , provider_name:str , endpoint:str , model:str, stream:bool = False, tools:list = None):
        self.provider_id  = provider_id
        self.provider_name = provider_name
        self.endpoint = endpoint
        self.model = model 
        self.stream = stream
        self.tools = tools 
        self.api_key = self.get_api_key()
    
    
    def get_provider_config(self):
        base_dir = Path(__file__).resolve().parent
        provider_file = base_dir / "providers.json"
        with open(provider_file, "r") as file:
            providers = json.load(file)

        for provider in providers:
            if provider["provider_id"] == self.provider_id:
                return provider
        
        raise ValueError(f"Provider '{self.provider_id} is not found in the providers.json.")

    def get_api_key(self):
        base_dir = Path(__file__).resolve().parent.parent
        env_file = base_dir / ".env"
        provider_config = self.get_provider_config()

        load_dotenv(env_file)

        api_key_name = provider_config["api_key"]
        if api_key_name == "no_api_key" or api_key_name == "no-api-key" or api_key_name == "no_need_of_a_api_key":
            return "no_need_of_a_api_key"
        elif api_key_name.startswith(".env:"):
            api_key = os.getenv(api_key_name[5:])    
            if not api_key:
                raise ValueError("") 
        console.print(api_key)
        

        
        
    def chat(self, chat_completion:list):
        load_dotenv()
        
        provider = self.provider_name.lower()
        if provider == "groq":
            try:
                if not os.getenv("groq_api"):
                    raise ValueError("Groq API key not found in the environment variables.")
                api_key = os.getenv("groq_api")
            except Exception as e:
                console.print(f"Error occured: {e}")
        elif provider == "ollama":
            api_key = "Ollama-key"
        elif provider == "lm studio":
            api_key = "LM-Studio-key"
            
        client = OpenAI(base_url=self.endpoint, api_key=api_key)

        response = client.chat.completions.create(
            model = self.model,
            messages = chat_completion,
            stream = self.stream,
            tools = self.tools 
        )
        return response
    
agent = Providers(provider_id="groq", provider_name="Groq", endpoint="https://api.groq.com/v1", model="so_and_so")

agent.get_api_key()