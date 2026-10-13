# Spec Delta

## MODIFIED Requirements

### Requirement: Library documentation
The library documentation SHALL be the `VSCode` library's own: an introduction about opening VS Code, its instances, the workbench, extensions, the extension host, closing, recording and the helper library, and import documentation with a link to the Browser library's import arguments. The sections that Browser keywords link to SHALL exist with short texts that point to the Browser library's documentation, as in `Electron`.

#### Scenario: Own introduction
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the introduction consists of the `VSCode` library's own text, its section `Assertions` links to the Browser library's documentation, and its section `Browser, Context and Page` compares the library with the Browser library

#### Scenario: The extension host
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the introduction has a section `The extension host`, which names the helper extension's folder and `.vsix` in the package and how a test loads each

#### Scenario: Own import documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the import documentation is the `VSCode` library's own text with a link to the Browser library's import arguments, and the import arguments are Browser's, with their types and defaults
