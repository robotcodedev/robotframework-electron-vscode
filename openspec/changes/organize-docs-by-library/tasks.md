# Tasks

## 1. Sections and sidebar

- [ ] 1.1 Move the pages with `git mv` into `electron/`, `vscode/` and `running/`, still whole, as design.md lays out:
  - the getting-started pages to `electron/getting-started.md` and `vscode/getting-started.md`, both with `sidebar.label: Getting started` and `sidebar.order: 1`;
  - `vscode-versions.mdx` to `vscode/versions.mdx` and `vscode-forks.md` to `vscode/forks.md`;
  - each mixed guide to the section of its general part.

  Replace the sidebar in `docs/astro.config.mjs` with the groups `Electron`, `VS Code` and `Running tests`, each `autogenerate` for its folder, without the reference group. Verify that `npm run build` in `docs/` succeeds, and that the built sidebar lists the three groups, with each library's group starting with "Getting started".
- [ ] 1.2 Change every relative link between the pages and the cards of `index.mdx` to the new paths. Change the absolute links in `packages/vscode/README.md` and `examples/vscode-extension/README.md` to the new URLs. Verify that:
  - a script finds no broken internal link or anchor in `docs/dist` after the build;
  - `grep` finds the old paths `guides/` and `getting-started/` nowhere in `docs/src`, the READMEs and `examples/`.
- [ ] 1.3 Describe the sections in the documentation part of `CONTRIBUTING.md`: which section a new page belongs to, and that a page's path is its URL, for example `vscode/extensions.mdx` at `/vscode/extensions/`. Verify that the described paths exist in the built site.

## 2. VS Code parts of the general pages

- [ ] 2.1 Move the section "In VS Code" of `electron/browser-keywords.md` into the new page `vscode/browser-keywords.md`, "Browser keywords in VS Code". The page starts by linking to the Electron page. Verify that:
  - the build and the link check pass;
  - the VS Code page names `explorer.confirmDragAndDrop`, and for `Save Page As PDF` it leads to the Electron page;
  - the Electron page has no section about VS Code.
- [ ] 2.2 Create `vscode/videos-and-traces.mdx`, "Videos and traces of VS Code", from:
  - "A full frame of VS Code" of `electron/videos.mdx`, with `video.robot`;
  - "The example" of `electron/traces.mdx`, with `tracing.robot`;
  - the paragraph on how VS Code fills the screen from `running/ci-and-display.mdx`, which links to the new page instead.

  Verify that the build shows both example files on the VS Code page and neither on the Electron pages, and that the link check passes.
- [ ] 2.3 Create `vscode/instances.md`, "Instances, logs and troubleshooting", from the section on the VS Code instance directories and the troubleshooting item on the command palette in `running/logs.md`. Link to it from the VS Code getting-started page. Verify that the build and the link check pass, and that `running/logs.md` has no section about VS Code.
- [ ] 2.4 Make the VS Code getting-started page say that the Electron section applies to VS Code as well, with links to the Electron pages. Change the `description` in the frontmatter of every page whose content changed in this group. Verify that the build and the link check pass, and that no page of the Electron section has a heading about VS Code.

## 3. Integration of the structure

- [ ] 3.1 Verify the new structure as a whole:
  - `npm ci` and `npm run build` in `docs/`, and the link check over `docs/dist`;
  - `uv run pre-commit run --all-files`;
  - `grep` finds no old page path in the repository outside `openspec/changes/archive/` and `CHANGELOG.md`;
  - the scenarios of the delta specs hold in the built site.

## 4. Keyword reference (after RobotCode 2.8.0 is released)

- [ ] 4.1 Upgrade RobotCode with `uv lock --upgrade-package robotcode && uv sync`. Verify that `uv run robotcode -r . doc keywords VSCode` works, and that `uv run pre-commit run --all-files` passes with the new version.
- [ ] 4.2 Write `docs/scripts/generate_reference.py` as design.md describes. Generate `electron/reference.md` and `vscode/reference.md`, with the sidebar label "Keyword reference" and the last place in their section. Add the regeneration step to `AGENTS.md`. Verify that:
  - the build shows the reference as the last page of each library's section;
  - after a changed docstring, regenerating changes the reference page; then revert the docstring.

## Workflow follow-up

- Archive the change after the tasks of the keyword reference. The archive syncs the deltas of `documentation-site` and `vscode-examples`.
