# Proposal

## Why

The documentation site mixes both libraries:
- One getting-started folder and one guides folder hold everything. Some guides are about Electron applications, some about VS Code, and some about both, with sections on VS Code inside general pages.
- A reader of one library has to pick their way through pages and sections about the other.
- The sidebar shows a reference group that is empty.

## What Changes

- **A section per library and one for the test environment,** each a folder and a group in the sidebar:
  - **Electron** (`electron/`): getting started, Browser keywords in applications, traces and HAR files, videos and slow motion. These pages describe what both libraries can do, because `VSCode` contains every keyword of `Electron`.
  - **VS Code** (`vscode/`): getting started, extensions, the extension host, workbench keywords, Browser keywords in VS Code, videos and traces of VS Code, instances and logs, versions and profiles, forks. These pages link to the Electron section and add only what is specific to VS Code.
  - **Running tests** (`running/`): CI and the Linux display, logs and troubleshooting.
- **The VS Code parts of general pages move to VS Code pages:**
  - the section "In VS Code" of the guide on Browser keywords;
  - "A full frame of VS Code" from the video guide, and the example from the trace guide;
  - the VS Code instance directories from the guide on logs.
- **Keyword reference:** the empty reference group goes away. The reference moved here from the archived `add-documentation-site`. It gets one page per library, generated with `robotcode doc` from RobotCode 2.8.0, in that library's section.
- **URLs:** the URLs of the published site change; for example, `guides/extensions/` becomes `vscode/extensions/`. The links in the READMEs, the example's README and the pages follow. There are no redirects: the libraries are in a pilot phase and not yet on PyPI.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `documentation-site`:
  - "Structure of the site" gets a section per library and one for running tests;
  - the keyword reference becomes a page in each library's section.
- `vscode-examples`: the guides on the Browser features, the videos and the traces of the example become pages of the VS Code section.

## Impact

- **Pages:**
  - the pages in `docs/src/content/docs/` move into `electron/`, `vscode/` and `running/`;
  - three pages are split;
  - `index.mdx` links to the new pages.
- **Configuration:** the sidebar in `docs/astro.config.mjs`.
- **Links:** `packages/vscode/README.md` and `examples/vscode-extension/README.md` link to pages of the site; the other READMEs link to its start page only.
- **Keyword reference:**
  - after RobotCode 2.8.0, the new script `docs/scripts/generate_reference.py`, a RobotCode upgrade in `uv.lock`, and the regeneration step in `AGENTS.md`;
  - RobotCode 2.8.0 is not released yet; on 2026-10-13, PyPI has 2.7.0. The tasks of the reference wait for it, and the change stays open until then. The new structure does not wait.
