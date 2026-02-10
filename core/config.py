from pathlib import Path
from tomlkit import document, table
import os 
import json

home_dir = Path.home()

config_dir = home_dir / ".case"
provider_json_path = config_dir / "provider.json" 
env_file_path = config_dir / ".env"
settings_toml_path = config_dir / "settings.toml"


def create_files(file_name:str ):
    global provider_json_path
    global env_file_path
    global settings_toml_path
    
    provider_list = provider_list = [
        {
            "provider_id": "openai",
            "provider_name": "OpenAI",
            "endpoint": "https://api.openai.com/v1",
            "api_compatibility": "openai",
            "api_key": ".env:openai_api",
            "models": [
                {
                    "model_name": "GPT-5.3 Codex",
                    "model_id": "gpt-5.3-codex"
                },
                {
                    "model_name": "GPT-5.2",
                    "model_id": "gpt-5.2"
                },
                {
                    "model_name": "o3-pro",
                    "model_id": "o3-pro"
                },
                {
                    "model_name": "GPT-5 Mini",
                    "model_id": "gpt-5-mini"
                }
            ]
        },
        {
            "provider_id": "google",
            "provider_name": "Google Gemini",
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "api_compatibility": "openai",
            "api_key": ".env:google_api",
            "models": [
                {
                    "model_name": "Gemini 3 Pro",
                    "model_id": "gemini-3-pro"
                },
                {
                    "model_name": "Gemini 3 Flash",
                    "model_id": "gemini-3-flash"
                },
                {
                    "model_name": "Gemini 2.5 Pro",
                    "model_id": "gemini-2.5-pro"
                }
            ]
        },
        {
            "provider_id": "groq",
            "provider_name": "Groq",
            "endpoint": "https://api.groq.com/openai/v1",
            "api_compatibility": "openai",
            "api_key": ".env:groq_api",
            "models": [
                {
                    "model_name": "GPT OSS 120B",
                    "model_id": "openai/gpt-oss-120b"
                },
                {
                    "model_name": "Llama 3.3 70B",
                    "model_id": "llama-3.3-70b-versatile"
                },
                {
                    "model_name": "Llama 3.1 8B",
                    "model_id": "llama-3.1-8b-instant"
                },
                {
                    "model_name": "GPT OSS 20B",
                    "model_id": "openai/gpt-oss-20b"
                }
            ]
        },
        {
            "provider_id": "ollama",
            "provider_name": "Ollama",
            "endpoint": "http://127.0.0.1:11434/v1",
            "api_compatibility": "openai",
            "api_key": "no_need_of_a_api_key",
            "models": []
        },
        {
            "provider_id": "lm studio",
            "provider_name": "LM Studio",
            "endpoint": "http://127.0.0.1:1234/v1",
            "api_compatibility": "openai",
            "api_key": "no_need_of_a_api_key",
            "models": []
        }
    ]

    
    doc = document()
    provider = table()
    provider.add("provider_id", "")
    provider.add("model_id", "")
    doc.add("provider", provider)

    general = table()
    general.add("theme", "github-dark")
    doc.add("general", general)

    
    if file_name == "provider":
        Path.touch(provider_json_path, exist_ok=True)
        with open(provider_json_path, "w") as file:
            json.dump(provider_list, file, indent=4)
    elif file_name == ".env":
        Path.touch(env_file_path, exist_ok=True)
    elif file_name == "settings":
        Path.touch(settings_toml_path, exist_ok=True)
        with open(settings_toml_path, "w", encoding="utf-8") as file:
            file.write(doc.as_string())

def verify_config():
    global env_file_path
    global settings_toml_path
    
    Path.mkdir(config_dir, parents= True, exist_ok=True)

    if not os.path.exists(provider_json_path):
        create_files("provider")
    if not os.path.exists(env_file_path):
        create_files(".env")
    if not os.path.exists(settings_toml_path):
        create_files("settings")
    




verify_config()
