import json 
import questionary
from pathlib import Path
from questionary import Choice
from dotenv import load_dotenv, set_key
from core.config import provider_json_path, env_file_path
from .cli_styling import (info_printing,
                          non_empty_input,
                          warning_printing,
                          modern_purple,
                          console)



def input_provider_details():
    
    info_printing("\n🛈 Make sure the API provider or model supports the OpenAI JSON format.")
    print()
    info_printing("Please provide the details of the provider ")
    
    provider_name = non_empty_input("Enter provider name: ")
    endpoints = non_empty_input("Enter the endpoint of the provider: ")
    api_key = input("Enter api key of the provider(If no api key leave blank): ").strip()
    print()
    info_printing("Are these details correct ")
    console.print(f"[dark_slate_gray1]Provider name:[/dark_slate_gray1][grey100] {provider_name}[/grey100]\n[dark_slate_gray1]endpoint:[/dark_slate_gray1] [grey100]{endpoints}[/grey100]\n[dark_slate_gray1]Api key:[/dark_slate_gray1] {api_key}")
    choice_ = questionary.confirm(
        "Confirm?",
        default=True,
        style=modern_purple
    ).ask()
    
    if choice_ == False:
        return input_provider_details()
    
    if api_key:
        api_key_name = provider_name + "_api"
        key_to_save = ".env:" + api_key_name
    else:
        key_to_save = "no_need_of_a_api_key"
        
    custom_provider_details = {   
        "provider_id": provider_name.lower(),
        "provider_name": provider_name,
        "endpoint": endpoints,
        "api_key": key_to_save,
        "models":[]
    }
    
    if api_key:
        load_dotenv() 
        set_key(dotenv_path=env_file_path, key_to_set=api_key_name, value_to_set=api_key )
        
    return custom_provider_details

def add_models(provider_list, provider_choice, providers_by_id):
    info_printing("🛈 Please provide the model details ")
    
    model_name = non_empty_input("Enter the name of the model: ")
    model_id = non_empty_input(f"Enter the id for the model: ")

    provider = providers_by_id.get(provider_choice)

    provider.setdefault("models", [])
    
    if any(m["model_id"] == model_id for m in provider["models"]):
        info_printing(f"The model '{model_name}' already exists.")
        return 
    
    provider["models"].append({
        "model_name": model_name,
        "model_id": model_id
    })
    

def get_provider_list(provider_list=None, mode:str = "r"):
    if mode == "r": 
        with open(provider_json_path, 'r') as file:
            provider_list = json.load(file)
        return provider_list    
    else:
        with open(provider_json_path, 'w') as file:
            json.dump(provider_list, file , indent=4)
    
def get_provider():
    provider_list = get_provider_list()

    provider_ids = []
    for provider in provider_list:
        provider = dict(provider)
        provider_ids.append(Choice(provider['provider_name'], value=provider['provider_id']))

    provider_ids.append(Choice("Custom Provider", value="custom"))
    
    provider_choice = questionary.select(
        "Select a provider ",
        qmark='●',
        choices=provider_ids,
        style=modern_purple,
        use_jk_keys=True,
        use_shortcuts=True,        
    ).ask()
    return provider_choice

def get_model(provider_choice):
    provider_list = get_provider_list()
    providers_by_id = {p["provider_id"]: p for p in provider_list}
    
    models = providers_by_id.get(provider_choice, {}).get("models", [])
    
    if not models:
        add_models(provider_list, provider_choice, providers_by_id)
        get_provider_list(provider_list, mode="w")
        models = providers_by_id.get(provider_choice, {}).get("models", [])
    
    model_tuple = []
    for model in models:
        model_tuple.append(Choice(model['model_name'], value=model['model_id']))

    model_tuple.append(Choice("Add a new model", value="add_model"))
    model_tuple.append(Choice("Back", value="back"))
    model_choice = questionary.select(
        "Select or Add a new model ",
        qmark='●',
        choices=model_tuple,
        style=modern_purple,
        use_jk_keys=True,
        use_shortcuts=True
    ).ask()

    if model_choice == "add_model":
        add_models(provider_list, provider_choice, providers_by_id)
        get_provider_list(provider_list, mode="w")
        return get_model(provider_choice)
    elif model_choice == "back":
        return None 
        
    return model_choice
    
    
def model_settings():
    
    provider_choice = get_provider()

    if provider_choice == "custom":
        provider_list = get_provider_list()
        custom_provider_details = input_provider_details()        
        provider_list.append(custom_provider_details)
        
        get_provider_list(provider_list, "w")
        
        provider_choice = custom_provider_details["provider_id"]
        console.print(provider_choice)
    
    model_choice = get_model(provider_choice)
    if model_choice is None:
        return model_settings()
    
    provider_list = get_provider_list()        
    providers_by_id = {p["provider_id"]: p for p in provider_list}
    model_name = None
      
    for model in providers_by_id[provider_choice]["models"]:
        if model["model_id"] == model_choice:
            model_name = model["model_name"]
            break
        
    return provider_choice, model_choice, model_name
        

