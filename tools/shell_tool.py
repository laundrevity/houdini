from termcolor import colored
import subprocess
import json

class ShellTool:
    # Define the schema according to the OpenAI tool specification
    schema = {
        'name': 'shell_tool',
        'description': 'Execute arbitrary shell commands and return the output',
        'parameters': {
            'command_json': {
                'type': 'string',
                'description': 'JSON-encoded string representing the command to execute, including any arguments. Note that any arguments MUST be provided in a separate, optional `args` keyword. So, for example, if we wanted to list all files we could use the command_json: `{"command": "ls", "args": ["-ltrah"]}'
            }
        },
        'required': ['command_json']
    }

    def execute(self, command_json):
        # Check if command_json is already a dict and use it directly if so
        if isinstance(command_json, str):
            try:
                command_data = json.loads(command_json)
            except json.JSONDecodeError:
                return 'Invalid JSON format for command.'
        elif isinstance(command_json, dict):
            command_data = command_json
        else:
            return 'Command JSON must be a string or a dictionary.'

        # Extract the command and arguments
        command = command_data.get('command')
        args = command_data.get('args', [])

        # Execute the command and return its output or error message
        result = {'stdout': '', 'stderr': '', 'returncode': 0}
        try:
            completed_process = subprocess.run(
                [command] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            result['stdout'] = completed_process.stdout
            result['stderr'] = completed_process.stderr

        except subprocess.CalledProcessError as e:
            result['stdout'] = e.stdout
            result['stderr'] = e.stderr
            result['returncode'] = e.returncode

        except FileNotFoundError:
            result['stderr'] = f"Command not found: {command}"
            result['returncode'] = 127

        except Exception as e:
            result['stderr'] = str(e)
            result['returncode'] = 1

        if result['stdout'].strip():
            print(colored(result['stdout'], 'green'))
        else:
            print(colored('Error occurred', 'red'))
            if result['stderr'].strip():
                print(colored(result['stderr'], 'yellow'))

        return result

# Ensure that the tool can be discovered by the tool generator script
__all__ = ['ShellTool']
