import os 
import json 
from core.Provider.provider import Providers
from rich.console import Console 

console = Console()

## Main class, for generating ai responses
class CASE:
    def __init__(
        self,
        provider_name:str,
        model:str,
        endpoint:str,
        tools:list = None,
        available_functions:dict = None,
        ):
        
        self.provider_name = provider_name
        self.model = model
        self.endpoint = endpoint
        self.tools = tools
        self.available_functions = available_functions
        
        
        self.provider_ = Providers(
            provider_name=self.provider_name,
            model=self.model,
            endpoint=self.endpoint,
            stream=False,
            tools = self.tools
        )
      
    def generate_ai_response(self, chat_completion:list):
        self.chat_completion = chat_completion
        
        response = self.provider_.chat(chat_completion=self.chat_completion)
        
        if response.choices[0].message.tool_calls:
            yield from self.tool_calling(response.choices[0].message.tool_calls)

        else:
            yield {
                "content": response.choices[0].message.content
                }


        
    def tool_calling(self, tool_calls:list):
        self.tool_calls = tool_calls
        
        for tool_call in self.tool_calls:
            function_name = tool_call.function.name
            
            if function_name in self.available_functions:
                function_to_call = self.available_functions[function_name]
                if tool_call.function.arguments:
                    try:
                        parsed = json.loads(tool_call.function.arguments)
                        function_arguments = parsed if isinstance(parsed, dict) else {}
                    except:
                        function_arguments = {}
                
                try:
                    function_response = function_to_call(**function_arguments)
                except Exception as e:
                    function_response = f"Error: An error occured {e}"
                
                if isinstance(function_response, (dict, list)):
                    function_response = json.dumps(function_response, indent=2, ensure_ascii=False)
                else:
                    function_response = str(function_response)
                    
                yield {
                    "tool_call_response": function_response
                }
                self.chat_completion.append(
                    {
                        "role":"tool",
                        "tool_call_id": tool_call.id,
                        "name":function_name,
                        "content":function_response
                    }
                )
                
            else:
                self.chat_completion.append(
                    {
                        "role":"tool",
                        "tool_call_id": tool_call.id,
                        "name":function_name,
                        "content": json.dumps({"Error": f"The function '{function_name}' not found."})                    
                    }
                )
                
        try:
            response = self.provider_.chat(chat_completion = self.chat_completion)
        except Exception as e:
            raise Exception(f"An Error occured: {e}")
        
        if response.choices[0].message.tool_calls:
            yield from self.tool_calling(response.choices[0].message.tool_calls)
            
        else:
            yield {
                "content": response.choices[0].message.content
            }
                 
    def chat_summarize(self, chat_completion:list, custom_summarization_prompt:str = None) -> list:
        
        if custom_summarization_prompt:
            summarization_prompt = custom_summarization_prompt
        else:
            summarization_prompt = {
                            "role": "user",
                            "content": "Summarize our previous conversation in few concise sentences. Focus only on the factual information discussed. Do not add roleplay elements, character references, or fictional context."
                        }
        
        chat_completion.append(summarization_prompt)

        response = self.provider_.chat(chat_completion=chat_completion)

        chat_completion = [{
            "role": "system",
            "content":"You are a helpful, intelligent AI assistant.\
                        Provide accurate, clear, and concise responses.\
                        Adapt your tone and level of detail to the user’s needs.\
                        Do not guess or fabricate information; say when you are unsure.\
                        Ask clarifying questions only when necessary."
        }
        ]
        
        chat_completion.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        }
        )
        return chat_completion
        

