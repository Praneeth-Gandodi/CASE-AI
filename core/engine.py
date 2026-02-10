import json 
from types import SimpleNamespace
from core.Provider.provider import Providers
from rich.console import Console 

console = Console()


class Case:
    def __init__(
        self,
        provider_id:str,
        model:str,
        api_key:str,
        tools:list = None,
        available_functions:dict = None,
        ):
        
        self.provider_id = provider_id
        self.model = model
        self.api_key = api_key
        self.tools = tools
        self.available_functions = available_functions
        
        self.main_agent = Providers(
            provider_id=self.provider_id,
            model=self.model,
            api_key=self.api_key,
            tools=self.tools
        )
        
        
    def gen_ai_response(self, chat_completion:list):
        self.chat_completion = chat_completion
        
        response_delta = self.main_agent.chat(chat_completion=chat_completion)

        tool_call_buffer = {}
        full_content = ''

        for chunk in response_delta:
            delta = chunk.choices[0].delta
            
            if delta.content:
                yield {
                    'role': 'content',
                    'data': delta.content
                }
                full_content += delta.content
                
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    
                    if idx not in tool_call_buffer:
                        tool_call_buffer[idx] = {
                            'id': tc_delta.id,
                            'function': {
                                'name': tc_delta.function.name,
                                'arguments': ""
                            },
                            'type': 'function'
                        }

                    if tc_delta.function.arguments:
                        tool_call_buffer[idx]['function']['arguments'] += tc_delta.function.arguments
                        
        if tool_call_buffer:
            tool_calls_list = list(tool_call_buffer.values())
            
            assistant_tool_call_msg = {
                'role': 'assistant',
                'tool_calls': [],
                'content': full_content or None,
            }
            self.chat_completion.append(assistant_tool_call_msg)
            tc_objects = [
                    SimpleNamespace(
                        id=item['id'],
                        function=SimpleNamespace(name=item['function']['name'], arguments=item['function']['arguments'])
                    )
                    for item in tool_calls_list
                ]
                
            yield from self.tool_calling(tc_objects)       

        elif full_content:
            self.chat_completion.append({
                'role':'assistant',
                'content':full_content
            })
            
        yield {
            'role': 'completion',
            'data': self.chat_completion
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

                yield {
                    'role': 'tool_call_details',
                    'data':{
                        'function_name': function_name,
                        'function_arguments': function_arguments
                    }
                }
                
                try:
                    function_response = function_to_call(**function_arguments)
                except Exception as e:
                    function_response = f"Unable to call the function because of {e}" 

                if isinstance(function_response, (dict, list)):
                    function_response = json.dumps(function_response, indent=2, ensure_ascii=False)
                else:
                    function_response = str(function_response)

                yield{
                    'role':'tool_call_response',
                    'data': function_response
                }
                
                self.chat_completion.append(
                    {
                        'role':'tool',
                        'tool_call_id': tool_call.id,
                        'name': function_name,
                        'content':function_response
                    }
                )
                yield {
                    'role':'completion',
                    'data' : self.chat_completion
                }
            
            else:
                self.chat_completion.append({
                    'role':"tool",
                    'tool_call_id': tool_call.id,
                    'name': function_name,
                    'content':json.dumps({"Error": f"The function '{function_name}' not found."})
                })

                yield {
                    'role':'completion',
                    'data' : self.chat_completion
                }
                
        try:
            yield from self.gen_ai_response(chat_completion=self.chat_completion)
        except Exception as e:
            raise Exception(f"Error:An exception occured while tool calling{e}")


    def chat_summarization(self, chat_completion:list ) -> list:
        
        chat_completion.append({
            'role':'user',
            'content':"Summarize the conversation concisely while preserving:\
                        user's goals and requirements, key facts and decisions made,\
                        technical details and specifications, unresolved questions or next steps,\
                        user preferences and feedback on responses. Use direct statements,\
                        not meta-descriptions. Keep exact numbers, names, and technical terms.\
                        Prioritize actionable context that enables seamless conversation continuation."
        })
        
        response = self.main_agent.non_streaming_chat(chat_completion)

        chat_completion = [{
            "role": "system",
            "content":("""
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
        
        chat_completion.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        }
        )
        
        return chat_completion
    