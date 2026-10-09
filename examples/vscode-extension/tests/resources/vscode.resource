*** Settings ***
Documentation       Opens VS Code with the extension of this folder.

Library             VSCode


*** Variables ***
# The VS Code version that the tests run against: a fixed version, `stable` or `insiders`.
${VSCODE_VERSION}       1.141.0
# An installed VS Code to use instead of a download, for example /usr/share/code/code.
${VSCODE_EXECUTABLE}    ${NONE}
# Where downloaded VS Code builds are cached; ${NONE} is the user's cache directory.
${VSCODE_CACHE}         ${NONE}


*** Keywords ***
Open Example VS Code
    [Documentation]    Opens an isolated VS Code with the extension of this folder loaded from source.
    ...
    ...    VS Code opens maximised, so that it fills the screen. On Xvfb and Xephyr this
    ...    needs a window manager, which the display profiles start.
    Open VS Code
    ...    version=${VSCODE_VERSION}
    ...    executable=${VSCODE_EXECUTABLE}
    ...    cache_dir=${VSCODE_CACHE}
    ...    extension_development_path=${EXECDIR}
    ...    settings=${{ {"window.newWindowDimensions": "maximized"} }}
