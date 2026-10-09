*** Settings ***
Documentation       Runs Python files with the Python extension.

Library             VSCode


*** Variables ***
# The interpreter in the status bar, which the Python extension shows once it has chosen one.
${PYTHON_INTERPRETER}           [id="ms-python.vscode-python-envs.python.interpreterDisplay"]
# The run button that the Python extension shows above a Python file in the editor.
${RUN_PYTHON_FILE_BUTTON}       .editor-group-container.active .editor-actions [aria-label="Run Python File"]


*** Keywords ***
Run Python File
    [Documentation]    Runs the Python file in the active editor with the run button above the editor.
    ...
    ...    The keyword waits until the Python extension has chosen an interpreter, and then
    ...    until VS Code has stopped redrawing the run button, which it does several times
    ...    while the extension starts. Run earlier, the extension reports an invalid
    ...    interpreter, and a click on a button that is just being replaced can fail.
    Wait For Elements State    ${PYTHON_INTERPRETER}    visible    timeout=60s
    Wait Until Run Button Is Settled
    Click    ${RUN_PYTHON_FILE_BUTTON}

Wait Until Run Button Is Settled
    [Documentation]    Waits until the run button has stayed the same element for two seconds.
    VAR    ${settled}
    ...    () => {
    ...    const button = document.querySelector('${RUN_PYTHON_FILE_BUTTON}');
    ...    const state = window.robotRunButton ??= { element: null, since: 0 };
    ...    if (button !== state.element) { state.element = button; state.since = Date.now(); }
    ...    return button !== null && Date.now() - state.since >= 2000;
    ...    }
    ...    separator=\n
    Wait For Function    ${settled}    timeout=60s
