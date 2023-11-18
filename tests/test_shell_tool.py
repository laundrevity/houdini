from tools.shell_tool import ShellTool


def test_pwd_output():
    shell_tool = ShellTool()
    result = shell_tool.execute({"command": "pwd"})
    assert result['stdout'].strip() == '/app'
