*** Settings ***
Documentation       The Browser library's import arguments that are about browsers have no effect on applications.
Library             Electron    external_browser_executable=${{ {"chromium": "/does/not/exist"} }}
Library             resources/ElectronFixture.py


*** Test Cases ***
Browser Executable Has No Effect On Applications
    ${app} =    Get Fixture App
    ${user_data} =    New User Data Dir    ${OUTPUT_DIR}
    Start Electron Application    ${ELECTRON_EXECUTABLE}    args=${{ [$app, "--user-data-dir=" + $user_data] }}
    Get Title    ==    Electron Fixture
    [Teardown]    Close Electron Application    ALL
