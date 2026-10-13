*** Variables ***
${VSCODE_VERSION}       1.141.0
${VSCODE_EXECUTABLE}    ${NONE}
${VSCODE_CACHE}         ${EXECDIR}/.cache/vscode
${TEST_EXTENSION}       ${EXECDIR}/packages/vscode/atest/fixtures/extension
${TEST_WORKSPACE}       ${EXECDIR}/packages/vscode/atest/fixtures/workspace
# The library's helper extension from the installed package, as its documentation shows. The build packs the .vsix.
${HELPER_EXTENSION}     ${{ pathlib.Path(VSCode.__file__).parent / 'extension' }}
${HELPER_VSIX}          ${{ pathlib.Path(VSCode.__file__).parent / 'extension-host.vsix' }}
