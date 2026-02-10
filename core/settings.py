import json
import tomlkit 
import os
from dotenv import load_dotenv , set_key
from pathlib import Path
from tomlkit import parse
from core.exception import ApiKeyNotFound
from core.config import config_dir, provider_json_path, env_file_path, settings_toml_path

class Settings:
    def __init__(self):
        self.base_dir = config_dir
        self.settings_toml_path = settings_toml_path
        self.providers_path = provider_json_path
        self.env_file_path = env_file_path
        
    def get_settings_toml(self, updated_settings = None, mode:str = 'r'):
        try:
            if mode == "r":
                with open(self.settings_toml_path, mode, encoding="utf-8") as file:
                    settings_content = file.read()
                settings_content = parse(settings_content)
                return settings_content
            else:
                with open(self.settings_toml_path, mode) as file:
                    file.write(tomlkit.dumps(updated_settings))
                return True
        except FileNotFoundError as e:
            raise FileNotFoundError(f"The settings.toml file not found.") from e 
        except FileExistsError as e:
            raise FileExistsError(f"The settings.toml does not exists.") from e
    
    def get_provider_json(self, mode:str = 'r', updated_providers_json:str = None):
        try:
            if mode == 'r':
                with open(self.providers_path, 'r')  as file:
                    providers_json = json.load(file)                
                    return providers_json
            else:
                with open(self.providers_path, 'w') as file:
                    json.dump(updated_providers_json)
                    return True
        except FileNotFoundError as e:
            raise FileNotFoundError(f"The 'providers.json' file not found.") from e
        except FileExistsError as e:
            raise FileExistsError(f"The 'provider.json' does not exists.") from e
        
            
    def manage_api_key(self, provider_id:str, api_key:str = None, mode:str = 'get'):
        
        api_key_path = self.env_file_path
        load_dotenv(api_key_path)
        
        providers_json = self.get_provider_json()
        for provider in providers_json:
            if provider['provider_id'] == provider_id:
                api_key_name = provider['api_key']   
                break
            
        if api_key_name == "no_need_of_a_api_key":
            return api_key_name
        else:
            api_key_name  = api_key_name[5:]
        
        if mode == "set":
            set_key(dotenv_path=api_key_path, key_to_set=api_key_name, value_to_set=api_key)
            return True   
             
        if not os.getenv(api_key_name):
            raise ApiKeyNotFound(f"Api key is not set for the provider '{provider_id}'.")
        else:
            api_key = os.getenv(api_key_name)
            return api_key
                
        
        

