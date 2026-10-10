# Spec Delta

## ADDED Requirements

### Requirement: Library documentation
The library documentation SHALL start with an introduction of the `VSCode` library's own, which describes opening VS Code, the workbench, closing it, recording it and the helper library, followed by the Browser library's sections that Browser keywords link to, without Browser's opening text. The import documentation SHALL be the library's own and SHALL show Browser's import arguments with their types, defaults and descriptions.

#### Scenario: Own introduction
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the introduction starts with the `VSCode` library's own text and sections, contains the Browser library's section `Assertions`, and does not contain Browser's opening text

#### Scenario: Own import documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the import documentation starts with the `VSCode` library's own text, and the import arguments are Browser's, with Browser's description of each argument

### Requirement: Keyword documentation
The library's own keywords SHALL document every argument, their return value and the exceptions they raise for invalid input, so that Libdoc shows them with the arguments, the return type and the exceptions.

#### Scenario: Keyword documentation
- **WHEN** libdoc generates the documentation of `VSCode` or `VSCode.Helper`
- **THEN** every argument of their own keywords has a description, keywords that return a value document it, and keywords that raise an exception for invalid input document it
