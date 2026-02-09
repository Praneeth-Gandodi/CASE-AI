import os
import subprocess
import questionary
from rich.console import Console 
from rich.panel import Panel
from questionary import Style

console = Console()


modern_purple = Style([
    ('qmark', 'fg:#c554eb bold'),                   
    ('question', 'fg:#ffffff bold'),
    ('answer', 'fg:#c554eb bold'),
    ('pointer', 'fg:#c554eb bold'),
    ('highlighted', 'fg:#c554eb bold'),    
    ('selected', 'fg:#888888'),
    ('separator', 'fg:#444444'),
    ('instruction', 'fg:#666666'),
])


def info_printing(text:str):
    console.print(f"[cyan bold]{text}[/cyan bold]")

def warning_printing(text:str):
    console.print(f"[yellow3 bold]⚠️ {text}[/yellow3 bold]")

def success_printing(text:str):
    console.print(f"[spring_green2 bold]{text}[/spring_green2 bold]")
    
            
def non_empty_input(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value 
        
        warning_printing("Input cannot be empty. Please try again.")
        
def case_ascii_art():
    ascii_art = """
    
 ▄████████    ▄████████    ▄████████    ▄████████       ▄████████  ▄█        ▄█ 
███    ███   ███    ███   ███    ███   ███    ███      ███    ███ ███       ███ 
███    █▀    ███    ███   ███    █▀    ███    █▀       ███    █▀  ███       ███▌
███          ███    ███   ███         ▄███▄▄▄          ███        ███       ███▌
███        ▀███████████ ▀███████████ ▀▀███▀▀▀          ███        ███       ███▌
███    █▄    ███    ███          ███   ███    █▄       ███    █▄  ███       ███ 
███    ███   ███    ███    ▄█    ███   ███    ███      ███    ███ ███▌    ▄ ███ 
████████▀    ███    █▀   ▄████████▀    ██████████      ████████▀  █████▄▄██ █▀  
                                                                  ▀                                                                                                                                                                      
    """

    console.print(f"[plum2]{ascii_art}[/plum2]")     

def clear_the_terminal():
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True)
    
def prompt_api_key(provider_name:str):
    api_key = questionary.password(
        f"Enter Api key for the provider '{provider_name}' :",
        qmark="●",
        style=Style([
            ('qmark', 'fg:#c554eb bold'),
            ("answer", 'fg:#bf5ad6 bold' )
            ])
        ).ask()
    return api_key


def startup_details(provider_name , model_name):
    console.print(Panel(
        f"● Current Provider: [bold aquamarine1]{provider_name}[/bold aquamarine1]\n"
        f"● Current Model:    [bold aquamarine1]{model_name}[/bold aquamarine1]\n"
        f"● Use [bold violet]/model[/bold violet] to switch provider and model.\n"
        f"● Use [bold violet]/help[/bold violet] for commands.",
        border_style="cyan",
        expand=False
    ))



    # console.print(Panel(
    #     f"● Current Provider: [aquamarine1]{provider_name}[/aquamarine1]\
    #     \n● Current Model: [aquamarine1]{model_name}[/aquamarine1]\
    #     \n● Use [violet]/model[/violet] to switch provider and model.\
    #     \n● Use [violet]/help[/violet] for commands.",
    #     expand=False                ))

    