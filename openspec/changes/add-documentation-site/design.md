# Design

## Context

See proposal.md for motivation and specs/documentation-site/spec.md for the requirements. Today the user documentation lives in `packages/electron/README.md` and `packages/vscode/README.md`. Their quick-start examples were verified by running them. Keyword documentation exists only in the docstrings. The repository has no git remote yet, and RobotCode 2.8.0 with `robotcode doc` is due within days.

Starlight facts, checked with Context7 on 2026-10-08:
- `<Code>` from `@astrojs/starlight/components` renders a string, and a Vite `?raw` import turns any file into such a string.
- Starlight prefixes the links it generates itself with Astro's `base`.

## Goals / Non-Goals

**Goals:**
- One documentation site for both libraries, with the structure from the spec.
- Code from the example project is included, never copied.
- Building and deploying needs no Python and no Browser clone.

**Non-Goals:**
- The guides on writing your own workbench keywords and on profiles per VS Code version. They show the example project, so `add-vscode-examples` writes them.
- Translations, versioned docs, or a custom theme. Starlight's defaults are used.
- Contributor documentation. AGENTS.md and dev-docs stay as they are, and the root README gets a short development section.

## Decisions

### Layout of `docs/`

```
docs/
  package.json, package-lock.json, astro.config.mjs
  scripts/generate_reference.py
  src/content/docs/
    index.mdx                       what the libraries are, status, where to start
    getting-started/electron.md     test an Electron app
    getting-started/vscode.md       test a VS Code extension
    guides/                         ci-and-display.md, vscode-forks.md, downloads-and-cache.md, logs.md, …
    reference/                      electron.md, electron-helper.md, vscode.md, vscode-helper.md (generated)
```

- The sidebar has three groups, each with Starlight's `autogenerate` for its folder, so a new page needs no configuration change.
- The project uses npm, which is the plainest choice for a docs-only Node project.

### `site` and `base` in one marked place

`astro.config.mjs` defines `site` and `base` as two constants at the top, under a comment that marks them as placeholders until the repository's location is decided. The placeholder values build a site that works at the root (`base: '/'`). The READMEs link to the site with the same placeholder URL, so once the location is known, a search for it finds every place to change.

### Content from the existing READMEs

- The getting-started pages and the guides take over the details from the package READMEs: the quick starts, `ELECTRON_RUN_AS_NODE`, the Linux display and Wayland, forks, downloads and cache, the cleanup of instance directories, and the logs.
- The quick-start code stays the code that was verified by running it.
- Afterwards each package README keeps a short description, installation, one minimal example and a link to the site.

### Code from `examples/`

- A guide imports the example file with `?raw` and shows it with `<Code lang="robotframework" title="…">`. Pages that include code are therefore `.mdx`.
- The import works from outside `docs/` in the build and in the dev server without further configuration, because MDX pages are rendered on the server.
- Shiki, which Starlight's code renderer Expressive Code uses, has no Robot Framework grammar. `docs/grammars/` holds a copy of RobotCode's TextMate grammar (`syntaxes/robotframework.tmLanguage.json`), registered as `robotframework` with the alias `robot`. It is copied again by hand when RobotCode's grammar changes, so the build needs no network.

### Reference pages

- `docs/scripts/generate_reference.py` runs `uv run robotcode -r . doc …` once for each library. It writes the Markdown to `src/content/docs/reference/` with Starlight frontmatter (`title`, `description`) in front of it.
- The exact `robotcode doc` options are fixed once RobotCode 2.8.0 is released.
- The pages are committed. AGENTS.md says when to regenerate them: after a keyword or its documentation changes. Once the Browser hook is released upstream and Browser comes from PyPI, the script can move into the workflow.

### Deployment

`.github/workflows/docs.yml` runs on pushes to the default branch that change `docs/**` or `examples/**`, and on manual dispatch:
- `withastro/action` builds the site from `docs/` (with `path: docs`).
- `actions/deploy-pages` publishes it.

Since the reference pages are committed and the examples are plain files, the workflow needs only Node.js.

## Risks / Trade-offs

- [The committed reference pages fall behind the code] → AGENTS.md names the regeneration step. The script makes it one command, and keyword changes go through OpenSpec changes whose tasks can include it.
- [`robotcode doc` output needs adjusting for Starlight, for example its headings or links] → The script owns the post-processing. The output is checked in the first build after 2.8.0.
- [Without a remote, the workflow cannot be tried] → The local build runs the same `npm ci` and `npm run build`. The workflow is checked once the repository exists.
- [Moving details out of the package READMEs loses their verified examples] → The quick-start code is taken over unchanged, and the minimal README example is run again.
