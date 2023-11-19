from .i_tool import ITool
import subprocess
import json
from typing import Dict, Any

class WiresharkTool(ITool):
    schema = {
        'name': 'wireshark_tool',
        'description': 'Tool to start and stop capturing packets and to analyze captured packets using Wireshark.',
        'parameters': {
            'action': {
                'type': 'string',
                'description': 'Action to take. Valid options are start_capture, stop_capture, and analyze_capture'
            },
            'interface': {
                'type': 'string',
                'description': 'The interface on which to capture packets'
            },
            'capture_file': {
                'type': 'string',
                'description': 'The file path to save the captured packets'
            }
        },
        'required': ['action']
    }

    def __init__(self):
        self.capture_process = None

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        # Dispatch to the appropriate method based on the action argument
        if action == "start_capture":
            return self.start_capture(**kwargs)
        elif action == "stop_capture":
            return self.stop_capture(**kwargs)
        elif action == "analyze_capture":
            return self.analyze_capture(**kwargs)
        else:
            return {"error": f"Unknown action {action}"}

    def start_capture(self, interface: str, capture_file: str) -> Dict[str, Any]:
        # Start packet capture using tshark on a specified interface
        self.capture_process = subprocess.Popen(
            ["tshark", "-i", interface, "-w", capture_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return {"status": "Capture started", "interface": interface, "capture_file": capture_file}

    def stop_capture(self) -> Dict[str, Any]:
        # Stop the packet capture if it's running
        if self.capture_process:
            self.capture_process.terminate()
            stdout, stderr = self.capture_process.communicate()
            return {"status": "Capture stopped", "output": stdout.decode('utf-8'), "errors": stderr.decode('utf-8')}
        return {"status": "No capture to stop"}

    def analyze_capture(self, capture_file: str, filters: str = "") -> Dict[str, Any]:
        # Analyze a capture file using tshark with optional filters
        completed_process = subprocess.run(
            ["tshark", "-r", capture_file, "-Y", filters],
            capture_output=True
        )
        packets = completed_process.stdout.decode('utf-8')
        return {"status": "Analysis complete", "packets": packets}

__all__ = ['WiresharkTool']