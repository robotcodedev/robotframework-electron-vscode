# Spec Delta

## MODIFIED Requirements

### Requirement: Library documentation
The library documentation SHALL start with an introduction of the `Electron` library's own, followed by the Browser library's sections that Browser keywords link to, without Browser's opening text. The import documentation SHALL be the library's own and SHALL show Browser's import arguments with their types, defaults and descriptions. The documentation SHALL report the version of the `Electron` library, not that of Browser.

#### Scenario: Generated documentation
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** it reports the version of `robotframework-electron`, and links in the Browser keyword documentation, such as those to `Assertions`, resolve to sections of the same document

#### Scenario: Own introduction
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** the introduction starts with the `Electron` library's own text and sections, contains the Browser library's section `Assertions`, and does not contain Browser's opening text

#### Scenario: Own import documentation
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** the import documentation starts with the `Electron` library's own text, and the import arguments are Browser's, with Browser's description of each argument

## ADDED Requirements

### Requirement: Keyword documentation
The library's own keywords SHALL document every argument, their return value and the exceptions they raise for invalid input, so that Libdoc shows them with the arguments, the return type and the exceptions.

#### Scenario: Keyword documentation
- **WHEN** libdoc generates the documentation of `Electron` or `Electron.Helper`
- **THEN** every argument of their own keywords has a description, keywords that return a value document it, and keywords that raise an exception for invalid input document it
