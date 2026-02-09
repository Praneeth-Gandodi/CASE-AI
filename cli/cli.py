import os 
import tomlkit 
import sys
import pathlib
from markrender import MarkdownRenderer
from openai import APIStatusError
from core.engine import Case
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
    startup_details,
    console, 
)

class Terminal_interface:
    def __init__(self):
        self.settings = Settings()
        self.renderer = MarkdownRenderer(theme='monokai')
        self.chat_completeion = [
            {
                "role": "system",
                "content": ("""
                You are a friendly, approachable, and helpful AI assistant.
                You respond clearly, accurately, and politely to all user questions.
                Your tone is warm, conversational, and respectful, without being overly casual or robotic.
                You explain things in a simple, easy-to-understand way and adjust your level of detail based on the user’s question.
                You stay patient, supportive, and non-judgmental at all times.
                If a request is unclear, you ask a brief clarifying question before answering.
                If you do not know something or cannot help with a request, you say so honestly and suggest a helpful alternative when possible.
                Your goal is to make the user feel comfortable, understood, and satisfied with each interaction.
                            """)
                }
        ]
        
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
                for model in provider['models']:
                    if model['model_id'] == model_id:
                        model_name = model['model_name']    
                break
        
        
        api_key = self.get_api(provider_id=provider_id)  
              
        return provider_name, provider_id, model_id, api_key, model_name                   
    
    def get_api(self, provider_id):

        provider_json = self.settings.get_provider_json()
        
        for provider in provider_json:
            if provider['provider_id'] == provider_id:
                provider_name = provider['provider_name']    
                break
        try:    
            api_key = self.settings.manage_api_key(provider_id=provider_id)
            return api_key
        except ApiKeyNotFound as e:
            api_key = prompt_api_key(provider_name=provider_name)
            if self.settings.manage_api_key(provider_id=provider_id, api_key=api_key, mode='set'):
                success_printing("Api Key is set successfully.")

                return api_key
            
    def change_model_or_provider(self):
        setttings_toml = self.settings.get_settings_toml()    
        provider_id , model_id = model_settings()
        
        setttings_toml['provider']['provider_id'] = provider_id
        setttings_toml['provider']['model_id'] = model_id
        
        self.settings.get_settings_toml(updated_settings=setttings_toml, mode='w')

        api_key = self.get_api(provider_id=provider_id)
        return provider_id, model_id, api_key
    
    def create_update_provider(self, provider_id, model_id, api_key, tools:list = None, available_functions:dict = None):
        self.agent = Case(provider_id=provider_id, model=model_id, api_key=api_key, tools=tools, available_functions=available_functions)
        
    def validate_prompt(self, prompt):
        prompt = prompt.strip()
        if prompt in ['/model', '/provider']:
            provider_id, model_id, api_key = self.change_model_or_provider()
            self.create_update_provider(provider_id=provider_id, model_id=model_id, api_key=api_key)
            
            return None
        elif prompt.lower() == "/exit":
            sys.exit()
        elif prompt.lower() == "/clear":
            clear_the_terminal()
        elif prompt.lower() == "/summarize":
            self.chat_completion = self.agent.chat_summarization(chat_completion=self.chat_completeion)
        else:
            return prompt

    def ask_user(self):
        print()
        prompt = console.input("[magenta2]❯ [/magenta2]") 
        prompt = self.validate_prompt(prompt=prompt)
        if prompt is None:
            prompt = self.ask_user()
        return prompt
        
        
    def cli(self):

        provider_name , provider_id , model_id, api_key, model_name = self.startup_configuration()
        clear_the_terminal()
        case_ascii_art()
        startup_details(provider_name=provider_name, model_name=model_name)

        tools = None

        self.create_update_provider(provider_id=provider_id, model_id=model_id, api_key=api_key, tools=tools)
        

        
        while True:
            print()
            prompt = self.ask_user()   
            print()
            self.chat_completeion.append({
                "role":'user',
                'content':prompt
            })
            
            try:
                reply_object = self.agent.gen_ai_response(chat_completion=self.chat_completeion)

                final_text = ""
                console.print("[grey100]✺ [/grey100]", end = "")
                for chunk in reply_object:
                    if chunk['role'] == 'content':
                        self.renderer.render(chunk["data"])
                        final_text += chunk['data']
                self.renderer.finalize()
            except APIStatusError as e:
                console.print("Api Key is not Valid..........")
            except Exception as e:
                continue
            
            except KeyboardInterrupt:
                console.print("Keyboard Interruption detected exitting.")

            self.chat_completeion.append({
                'role':'assistant',
                'content':final_text
            })
    
tui = Terminal_interface()    
tui.cli()