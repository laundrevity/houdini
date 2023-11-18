from agent import Agent
import json
import sys

def main():
    if len(sys.argv) < 2:
        print(f'Usage: python {sys.argv[0]} <PROMPT>')
        exit()
    
    agent = Agent()
    agent.messages.append({'role': 'user', 'content': sys.argv[1]})
    agent.loop()

if __name__ == '__main__':
    main()
