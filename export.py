import os

# Directory containing the files
directory = "."

file_list = [
    'Dockerfile',
    'docker-compose.yml',
    'conftest.py',
    'requirements.txt',
    'main.py',
    'conftest.py',
    'agent.py',
    'tools/shell_tool.py',
    'tools/wireshark_tool.py',
    'tests/test_shell_tool.py'
]

# Function to create the representation of the project structure
def create_project_structure(directory):
    structure = []
    for root, dirs, files in os.walk(directory):
        # Skip .git, __pycache__, and pricer directories
        dirs_to_exclude = ['.git', '__pycache__', '.pytest_cache']
        for d in dirs_to_exclude:
            if d in dirs:
                dirs.remove(d)

        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            structure.append(f"{subindent}{f}")
    return '\n'.join(structure)

def get_file_content(path):
    return open(path).read()

# Write the file contents and structure to a text file
output_file_path = os.path.join(directory, 'out.txt')
with open(output_file_path, 'w') as output_file:
    # Write project structure
    output_file.write("Project Structure:\n")
    output_file.write(create_project_structure(directory))
    output_file.write("\n\n")

    # Write contents of each file
    for file_name in file_list:
        file_path = os.path.join(directory, file_name)
        output_file.write(f"Contents of {file_name}:\n```\n")
        output_file.write(get_file_content(file_path))
        output_file.write("\n```\n\n")
