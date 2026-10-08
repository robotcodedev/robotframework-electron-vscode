# Spec Delta

## Purpose

The published documentation of `robotframework-electron` and `robotframework-vscode`. It has getting-started pages, guides, generated keyword references and code taken from the runnable examples, and it is built with Astro and Starlight and deployed to GitHub Pages.

## ADDED Requirements

### Requirement: Site builds from the repository
The documentation site SHALL be an Astro and Starlight project in `docs/` that builds into a static site with one command.

#### Scenario: Build
- **WHEN** `npm run build` runs in `docs/` after `npm ci`
- **THEN** the build succeeds and writes a static site to `docs/dist/`

### Requirement: Structure of the site
The site SHALL have a getting-started section for Electron apps and for VS Code extensions, a guides section and a reference section, all reachable from the sidebar.

#### Scenario: Sidebar
- **WHEN** the built site is opened
- **THEN** the sidebar lists getting started, guides and reference, and every page in them can be reached from it

### Requirement: Keyword reference
The reference section SHALL have one page for each of `Electron`, `Electron.Helper`, `VSCode` and `VSCode.Helper`, generated as Markdown with `robotcode doc`. A script SHALL regenerate them, and the generated pages SHALL be committed until the Browser hook is released upstream.

#### Scenario: Regenerate the reference
- **WHEN** the reference script runs after a keyword's documentation has changed
- **THEN** the corresponding reference page shows the new documentation

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
