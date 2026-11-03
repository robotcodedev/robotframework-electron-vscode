# documentation-site Specification

## Purpose

The published documentation of `robotframework-electron` and `robotframework-vscode`. It has getting-started pages, guides, generated keyword references and code taken from the runnable examples, and it is built with Astro and Starlight and deployed to GitHub Pages.

## Requirements

### Requirement: Site builds from the repository
The documentation site SHALL be an Astro and Starlight project in `docs/` that builds into a static site with one command.

#### Scenario: Build
- **WHEN** `npm run build` runs in `docs/` after `npm ci`
- **THEN** the build succeeds and writes a static site to `docs/dist/`

### Requirement: Structure of the site
The site SHALL have a section for Electron, a section for VS Code and a section for running tests, each a group in the sidebar. The Electron section SHALL describe what both libraries can do. The VS Code section SHALL describe only what is specific to VS Code and link to the Electron section for the rest. The test environment, such as the display and the logs of a run, SHALL be in the section for running tests. Each library's section SHALL start with its getting-started page.

#### Scenario: Sidebar
- **WHEN** the built site is opened
- **THEN** the sidebar lists the sections Electron, VS Code and Running tests, each library's section starts with its getting-started page, and every page can be reached from it

#### Scenario: A page of the Electron section
- **WHEN** someone reads a page of the Electron section, for example the one on videos
- **THEN** it has no section about VS Code, and a page of the VS Code section covers what is specific to VS Code on that topic

### Requirement: Code from the examples
Code that a guide shows from the example project SHALL be included from the files in `examples/`, not copied into the page.

#### Scenario: Changed example file
- **WHEN** a file of the example project changes
- **THEN** the next build of the site shows the changed file in every guide that includes it

### Requirement: READMEs point to the site
The repository root SHALL have a README with an overview of both libraries, the project's status and a link to the site. Each package README SHALL be a short page with installation and a minimal example that links to the site.

#### Scenario: Package README
- **WHEN** someone reads the README of `robotframework-vscode`
- **THEN** it shows what the library does, how to install it and a minimal example, and it links to the site for everything else

### Requirement: Deployment to GitHub Pages
A GitHub Actions workflow SHALL build the site and deploy it to GitHub Pages on changes to the default branch. The site's `site` and `base` settings SHALL be a single, marked place in the configuration until the repository's location is decided.

#### Scenario: Deployment
- **WHEN** a commit that changes `docs/` or `examples/` reaches the default branch
- **THEN** the workflow builds the site and publishes it to GitHub Pages

### Requirement: Keyword reference
Each library's section SHALL have a reference page with the keyword documentation of its library, `Electron` or `VSCode`, generated as Markdown with `robotcode doc`. A script SHALL regenerate both pages, and the generated pages SHALL be committed.

#### Scenario: Reference in its section
- **WHEN** the built site is opened
- **THEN** the Electron section has the reference of `Electron`, and the VS Code section the reference of `VSCode`, each with every keyword of its library, including those that come from the Browser library

#### Scenario: Regenerate the reference
- **WHEN** the reference script runs after a keyword's documentation has changed
- **THEN** the corresponding reference page shows the new documentation
