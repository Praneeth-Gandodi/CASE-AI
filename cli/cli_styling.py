from rich.console import Console 

console = Console()

def info_printing(text:str):
    console.print(f"[cyan bold]{text}[/cyan bold]")

def warning_printing(text:str):
    console.print(f"[yellow3 bold]⚠️ {text}[/yellow3 bold]")
        
def non_empty_input(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value 
        
        warning_printing("Input cannot be empty. Please try again.")
        
        