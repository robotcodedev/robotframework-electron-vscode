# Spec Delta

## MODIFIED Requirements

### Requirement: Structure of the site
The site SHALL have a section for Electron, a section for VS Code and a section for running tests, each a group in the sidebar. The Electron section SHALL describe what both libraries can do. The VS Code section SHALL describe only what is specific to VS Code and link to the Electron section for the rest. The test environment, such as the display and the logs of a run, SHALL be in the section for running tests. Each library's section SHALL start with its getting-started page.

#### Scenario: Sidebar
- **WHEN** the built site is opened
- **THEN** the sidebar lists the sections Electron, VS Code and Running tests, each library's section starts with its getting-started page, and every page can be reached from it

#### Scenario: A page of the Electron section
- **WHEN** someone reads a page of the Electron section, for example the one on videos
- **THEN** it has no section about VS Code, and a page of the VS Code section covers what is specific to VS Code on that topic

## ADDED Requirements

### Requirement: Keyword reference
Each library's section SHALL have a reference page with the keyword documentation of its library, `Electron` or `VSCode`, generated as Markdown with `robotcode doc`. A script SHALL regenerate both pages, and the generated pages SHALL be committed.

#### Scenario: Reference in its section
- **WHEN** the built site is opened
- **THEN** the Electron section has the reference of `Electron`, and the VS Code section the reference of `VSCode`

#### Scenario: Regenerate the reference
- **WHEN** the reference script runs after a keyword's documentation has changed
- **THEN** the corresponding reference page shows the new documentation
