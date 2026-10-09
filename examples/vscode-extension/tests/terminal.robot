*** Settings ***
Documentation       Runs a command in the integrated terminal and reads its output.

Resource            resources/vscode.resource
Resource            resources/terminal.resource

Suite Setup         Open Example VS Code
Suite Teardown      Close VS Code


*** Test Cases ***
Command Output In The Terminal
    # The result 42 shows that the command ran: the typed command line contains only 40 and 2.
    Run In Terminal    echo $((40 + 2))
    Terminal Should Show    42
    Take Screenshot    filename=terminal
