*** Settings ***
Documentation       Runs Python files with the Python extension.

Library             VSCode


*** Variables ***
# The interpreter in the status bar, which the Python extension shows once it has chosen one.
${PYTHON_INTERPRETER}           [id="ms-python.vscode-python-envs.python.interpreterDisplay"]
# The progress in the status bar while the Python extension still discovers interpreters.
${PYTHON_DISCOVERY}             [id="status.progress"][aria-label*="Discovering Python Interpreters"]
# The run button that the Python extension shows above a Python file in the editor.
${RUN_PYTHON_FILE_BUTTON}       .editor-group-container.active .editor-actions [aria-label="Run Python File"]


*** Keywords ***
Run Python File
    [Documentation]    Runs the Python file in the active editor with the run button above the editor.
    ...
    ...    The keyword first waits until the Python extension has chosen an interpreter and
    ...    finished discovering the others. Run earlier, the extension reports an invalid
    ...    interpreter and does not run the file.
    Wait For Elements State    ${PYTHON_INTERPRETER}    visible    timeout=60s
    Wait For Elements State    ${PYTHON_DISCOVERY}    detached    timeout=60s
    Click    ${RUN_PYTHON_FILE_BUTTON}
