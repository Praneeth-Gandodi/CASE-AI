import os 
import tomlkit 
import pathlib
from core.engine import CASE
from core.settings import Settings
from core.exception import ApiKeyNotFound
from .cli_settings import model_settings
from .cli_styling import (
    info_printing,
    warning_printing, 
    success_printing,
    case_ascii_art,
    clear_the_terminal,
    prompt_api_key,
    console
)

class Terminal_interface:
    def __init__(self):
        self.settings = Settings()
        
    def startup_configuration(self):
        provider_json = self.settings.get_provider_json()
        settings_toml = self.settings.get_settings_toml()
        
        
        if not settings_toml['provider']['provider_id'] or not settings_toml['provider']['model_id']:
            provider_id , model_id = model_settings()
            settings_toml['provider']['provider_id'] = provider_id
            settings_toml['provider']['model_id'] = model_id
            
            self.settings.get_settings_toml(updated_settings=settings_toml, mode= "w")
        else:
            provider_id = settings_toml['provider']['provider_id']
            model_id = settings_toml['provider']['model_id']
            
        for provider in provider_json:
            if provider['provider_id'] == provider_id:
                provider_name = provider['provider_name']    
                break
            
        try:    
            api_key = self.settings.manage_api_key(provider_id=provider_id)
        except ApiKeyNotFound as e:
            api_key = prompt_api_key(provider_name=provider_name)
            if self.settings.manage_api_key(provider_id=provider_id, api_key=api_key, mode='set'):
                success_printing("Api Key is set successfully.")
        
        return provider_name, provider_id, model_id, api_key                   
        
    def cli(self):

        provider_name , provider_id , model_id, api_key = self.startup_configuration()
        clear_the_terminal()
        case_ascii_art()
        tools = None
        agent = CASE(provider_id=provider_id, model=model_id, api_key=api_key, tools=tools)
        chat_completeion = [
            {
                "role": "system",
                "content": "You are a highly intelligent, precise, and helpful AI that explains clearly, reasons step-by-step, and checks all facts before answering."
                }
        ]
        
        while True:
            prompt = console.input("❯ ")
            chat_completeion.append({
                "role":'user',
                'content':prompt
            })
            reply_object = agent.generate_ai_response(chat_completion=chat_completeion)
            for chunk in reply_object:
                console.print(chunk['content'])
        

        
        
    
    
tui = Terminal_interface()    
tui.cli()