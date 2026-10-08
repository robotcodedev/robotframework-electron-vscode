# Proposal

## Why

The documentation of the two libraries is spread out. There are two long package READMEs and keyword docs that exist only inside the code, and there is no README at the repository root. The planned examples (`add-vscode-examples`) need a place where guides explain them and show their files. A documentation site fixes that before the examples are written, so that the examples can be cut to fit the guides.

## What Changes

- A documentation site built with Astro and Starlight in `docs/`, published on GitHub Pages:
  - **Getting started:** testing an Electron app, and testing a VS Code extension.
  - **Guides:** CI and the Linux display (Xvfb, Wayland), VS Code forks, downloads and cache, logs and troubleshooting. The guides on writing your own workbench keywords and locators and on profiles per VS Code version come with `add-vscode-examples`, because they show its files.
  - **Reference:** one Markdown page per library (`Electron`, `Electron.Helper`, `VSCode`, `VSCode.Helper`), generated with `robotcode doc`. Until the Browser hook is released upstream, a script generates the pages locally and they are committed.
- Code shown in guides comes from the files in `examples/`, so that what the docs show is what the example tests run.
- A README at the repository root gives an overview and the project's status, and links to the site. The package READMEs become short PyPI pages that link to the site.
- A GitHub Actions workflow builds the site and deploys it to GitHub Pages. The repository location, and with it the site's `site`/`base` URL, is not decided yet and stays a marked placeholder until it is.

## Capabilities

### New Capabilities

- `documentation-site`: the published documentation of the libraries — its structure, its reference pages, its code taken from the examples, and how it is built and deployed.

### Modified Capabilities

None.

## Impact

- New folder `docs/` with its own `package.json`. Node.js and npm are needed only to build the docs, not to use the libraries.
- New workflow under `.github/workflows/`.
- The reference pages depend on `robotcode doc`, which ships with RobotCode 2.8.0. Generating them waits for that release.
- `README.md` at the root, shorter package READMEs, and `AGENTS.md` for the docs commands.
- `add-vscode-examples` is adjusted afterwards so that its files can be shown in the guides.
