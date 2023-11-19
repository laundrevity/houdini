import subprocess
from .i_tool import ITool
from typing import Dict
import json


class DaemonTool(ITool):
    schema = {
        'name': 'daemon_tool',
        'description': 'Start and stop processes in the background, such as a Flask server, latency measurement tool, etc.',
        'parameters': {
            'command_data': {
                'type': 'string',
                'description': 'JSON-encoded string with the command to execute as a background process. It must have a `command` key, such as `python`, an optional `args` key, such as [`flask_app.py`], an `action` key in (`start`, `stop`, and a `process_key` key that we will subsequently use to manage the process.)'
            },
        },
        'required': ['command_data']
    }

    def __init__(self):
        self.processes = {}
    
    def execute(self, command_data: str | Dict):
        try:
            if isinstance(command_data, str):
                command_data = json.loads(command_data)
            action = command_data.get('action')
            if action == 'start':
                return self.start_process(command_data)
            elif action == 'stop':
                return self.stop_process(command_data)
            else:
                return {'error': 'Invalid command action. Use "start" or "stop".'}
        except json.JSONDecodeError:
            return {'error': 'Invalid JSON format for command.'}

    def start_process(self, command_data: Dict):
        command = command_data['command']
        args = command_data.get('args', [])
        process_key = command_data.get('process_key')

        proc = subprocess.Popen(
            [command] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.processes[process_key] = proc
        return {'status': 'started', 'process_key': process_key}
    
    def stop_process(self, command_data: Dict):
        process_key = command_data.get('process_key')
        if process_key in self.processes:
            proc = self.processes[process_key]
            proc.terminate()
            stdout, stderr = proc.communicate()
            del self.processes[process_key]
            return {
                'status': 'stopped',
                'process_key': process_key,
                'stdout': stdout.decode(),
                'stderr': stderr.decode()
            }
        else:
            return {'error': f'No process found with key: {process_key}'}

__all__ = ['DaemonTool']