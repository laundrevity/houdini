from termcolor import colored
from .i_tool import ITool
from typing import Dict
import subprocess
import datetime
import json

class ShellTool(ITool):
    # Define the schema according to the OpenAI tool specification
    schema = {
        'name': 'shell_tool',
        'description': 'Execute arbitrary shell commands and return the output',
        'parameters': {
            'command_json': {
                'type': 'string',
                'description': 'JSON-encoded string representing the command to execute, including any arguments. Note that any arguments MUST be provided in a separate, optional `args` keyword. So, for example, if we wanted to list all files we could use the command_json: `{"command": "ls", "args": ["-ltrah"].} Note also that redirection `<` should be used as a separate argument, e.g. command_json: `{"command": "cat", "args": ["foo", ">", "foo.txt"]}`'
            }
        },
        'required': ['command_json']
    }
    LOG_FILE = 'shell_audit_log.txt'

    def log_command(self, command, args, result):
        """Record command execution details to the audit log."""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'command': command,
            'args': args,
            'stdout': result['stdout'],
            'stderr': result['stderr'],
            'returncode': result['returncode']
        }
        # Open the log file in append mode and write the log entry
        with open(self.LOG_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    

    def execute(self, command_json: Dict | str):
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
        redirect_out = None

        if '>' in args: # detect redirection
            redirect_index = args.index('>')
            redirect_out = args[redirect_index + 1] # get output file
            args = args[:redirect_index] # remove '>' and the filename symbols
        
        # Execute the command and return its output or error message
        result = {'stdout': '', 'stderr': '', 'returncode': 0}
        try:
            if redirect_out:
                with open(redirect_out, 'w') as fp:
                    subprocess.run([command] + args, stdout=fp, check=True)
                result['stdout'] = f'Redirected to file: {redirect_out}'
            else:
                self.capture_process = subprocess.Popen(
                    [command] + args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                result['stdout'], result['std'] = self.capture_process.communicate()

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

        finally:
            # Log the command execution details whether successful or not
            self.log_command(command, args, result)

        if result['stdout'].strip():
            print(colored(result['stdout'], 'green'))
        else:
            print(colored('Error occurred', 'red'))
            if result['stderr'].strip():
                print(colored(result['stderr'], 'yellow'))

        return result

# Ensure that the tool can be discovered by the tool generator script
__all__ = ['ShellTool']
