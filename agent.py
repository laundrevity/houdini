from termcolor import colored
from openai import OpenAI
from typing import Dict
import importlib
import json
import os


class Agent:
    MODEL = 'gpt-4-1106-preview'

    def __init__(self):
        self.client = OpenAI()
        self.messages = [
            {
                'role': 'system',
                'content': open('system.txt').read()
            }
        ]
        self.tools = self.load_tool_definitions()
        print(f"{self.tools=}")
        self.total_tokens = 0

    @staticmethod
    def generate_tools_json():
        tools_dir = 'tools'
        tools_json = []

        for filename in os.listdir(tools_dir):
            if filename.endswith('py') and filename not in ['__init__.py']:
                module_name = filename[:-3] # Strip off .py
                tool_module = importlib.import_module(f"{tools_dir}.{module_name}")
                tool_class = getattr(tool_module, tool_module.__all__[0]) # Assume each mnodule defines __all__
                tool_schema = tool_class.schema

                tool_schema['parameters'] = {
                    'type': 'object',
                    'properties': tool_schema['parameters']
                }

                tools_json.append(
                    {
                        'type': 'function',
                        'function': tool_schema
                    }
                )

        with open('tools.json', 'w') as f:
            json.dump(tools_json, f, indent=4)

    def load_tool_definitions(self):
        self.generate_tools_json()
        with open('tools.json', 'r') as f:
            return json.load(f)

    def execute_tool(self, tool_name: str, tool_args):
        # Find the tool in the list of tools by name
        tool = next((t for t in self.tools if t['function']['name'] == tool_name), None)

        # If the tool is not found, raise an exception
        if tool is None:
            raise ValueError(f"Tool {tool_name} not found")
        
        # Assume each tool's module is named after the tool and contains a class with the same name
        module_name = tool_name
        tool_class_name = self.snake_to_pascal(module_name)

        # Dynamically import the module and class
        tool_module = importlib.import_module(f"tools.{module_name}")
        tool_class = getattr(tool_module, tool_class_name)

        # Create an instance of the tool class and execute it
        tool_instance = tool_class()
        result = tool_instance.execute(**tool_args)
        # print(f'execute_tool result: {result}')
        return result

    @staticmethod
    def snake_to_pascal(snake_case):
        words = snake_case.split('_')
        pascal_case = ''.join(word.capitalize() for word in words)
        return pascal_case

    def handle_tool_call(self, tool_call, messages):
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        if input(colored(f'{tool_name}({tool_args})? (y/n) ', 'blue', attrs=['bold'])).lower() == 'y':
            tool_result = self.execute_tool(tool_name, tool_args)
        else:
            tool_result = f"User declined to execute tool: {tool_name}({tool_args})"

        messages.append({
            'tool_call_id': tool_call.id,
            'role': 'tool',
            'name': tool_name,
            'content': json.dumps({'result': tool_result})
        })

    def process_response(self, response, messages):
        assistant_response_message = response.choices[0].message
        messages.append(assistant_response_message)
        self.total_tokens += response.usage.total_tokens
        tool_calls = assistant_response_message.tool_calls

        if tool_calls:
            for tool_call in tool_calls:
                self.handle_tool_call(tool_call, messages)

            return self.client.chat.completions.create(
                model=self.MODEL,
                messages=messages,
                tools=self.tools,
                tool_choice='auto'
            )
        
        else:
            print(f'Assistant: {assistant_response_message.content.strip()}')

    def loop(self):
        while True:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=self.messages,
                tools=self.tools,
                tool_choice='auto'
            )
            while response:
                response = self.process_response(response, self.messages)

            user_input = input(f'[{self.total_tokens}] > ')
            if user_input.lower() in ['exit', 'quit', 'q']:
                print('Later dude')
                break

            self.messages.append({'role': 'user', 'content': user_input})
