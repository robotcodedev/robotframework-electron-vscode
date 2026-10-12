*** Settings ***
Documentation       The Browser library's import arguments that are about browsers have no effect on applications.
Library             Electron    external_browser_executable=${{ {"chromium": "/does/not/exist"} }}
Library             Electron.Helper
Library             resources/ElectronFixture.py
Resource            resources/variables.resource


*** Test Cases ***
Browser Executable Has No Effect On Applications
    ${electron} =    Get Electron Executable    ${ELECTRON_VERSION}    ${ELECTRON_EXECUTABLE}    ${ELECTRON_CACHE}
    ${app} =    Get Fixture App
    ${user_data} =    New User Data Dir    ${OUTPUT_DIR}
    New Electron Application    ${electron}    args=${{ [$app, "--user-data-dir=" + $user_data] }}
    Get Title    ==    Electron Fixture
    [Teardown]    Close Electron Application    ALL
