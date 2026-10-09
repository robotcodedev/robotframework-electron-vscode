*** Settings ***
Documentation       Runs a Python script with the Python extension, an extension that the extension
...                 under test depends on: once installed when VS Code starts, once into the running VS Code.
...
...                 The tests need network access for the Marketplace and a Python interpreter on the PATH.
...                 Leave them out with `--exclude network`.

Resource            resources/vscode.resource
Resource            resources/command_palette.resource
Resource            resources/editor.resource
Resource            resources/terminal.resource

Test Tags           network
Test Teardown       Close VS Code


*** Variables ***
# The interpreter in the status bar, which the Python extension shows once it is ready.
${PYTHON_INTERPRETER}       [id="ms-python.vscode-python-envs.python.interpreterDisplay"]


*** Test Cases ***
Installed At The Start
    Open Example VS Code    extensions=${{ ["ms-python.python"] }}
    Run Hello World
    Take Screenshot    filename=python-run

Installed While Running
    Open Example VS Code
    Install VS Code Extension    ms-python.python
    Run Hello World


*** Keywords ***
Run Hello World
    Open File    hello.py
    Wait For Elements State    ${PYTHON_INTERPRETER}    visible    timeout=60s
    Run Command    Python: Run Python File in Terminal
    Terminal Should Show    Hello World
