*** Settings ***
Documentation       Runs a Python script with the Python extension, an extension that the extension
...                 under test depends on: once installed when VS Code starts, once into the running VS Code.
...
...                 The tests need network access for the Marketplace and a Python interpreter on the PATH.
...                 Leave them out with `--exclude network`.

Resource            resources/vscode.resource
Resource            resources/editor.resource
Resource            resources/python.resource
Resource            resources/terminal.resource

Test Tags           network
Test Teardown       Close VS Code


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
    Run Python File
    Terminal Should Show    Hello World
