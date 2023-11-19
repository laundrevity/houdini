from tools.i_tool import ITool
from termcolor import colored
from openai import OpenAI
from loguru import logger
from typing import Dict
import importlib
import datetime
import json
import sys
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
        
        self.tool_instances: Dict[str, ITool] = {}
        self.tools = self.load_tools()
        self.total_tokens = 0
        self.setup_logging()
        logger.info(f"{self.tools=}")

    def setup_logging(self, log_level="INFO"):
        # Configure Loguru to log to stdout
        logger.remove()
        logger.add(sys.stdout, level=log_level)

        # Configure Loguru to log to a file
        # # Set the log file name based on the current timestamp
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file_name = f"app_log_{current_time}.log"
        logger.add(log_file_name, level=log_level)


    def load_tools(self):
        tools_dir = 'tools'
        tools_json = []
        self.tool_instances = {}

        for filename in os.listdir(tools_dir):
            if filename.endswith('py') and filename not in ['__init__.py', 'i_tool.py']:
                module_name = filename[:-3] # Strip off .py
                tool_module = importlib.import_module(f"{tools_dir}.{module_name}")
                tool_class = getattr(tool_module, tool_module.__all__[0]) # Assume each mnodule defines __all__
                tool_schema = tool_class.schema

                # Construct JSON conforming to OpenAI specification for functions
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

                # Instantiate and store the tool class instance for persist behavior across calls
                self.tool_instances[module_name] = tool_class()
        
        return tools_json

    def execute_tool(self, tool_name: str, tool_args):
        # Find the tool in the list of tools by name
        tool_instance = self.tool_instances.get(tool_name)

        # If the tool instance is not found, raise an exception
        if tool_instance is None:
            raise ValueError(f"Tool '{tool_name}' not found or not instantiated")
        
        # Execute the tool using the stored instance
        result = tool_instance.execute(**tool_args)
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
            try:
                tool_result = self.execute_tool(tool_name, tool_args)
            except Exception as e:
                tool_result = f"Error executing {tool_name}({tool_args}): {e}"
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
            logger.info(f'Assistant: {assistant_response_message.content.strip()}')

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
                logger.info('Later dude')
                break

            self.messages.append({'role': 'user', 'content': user_input})
