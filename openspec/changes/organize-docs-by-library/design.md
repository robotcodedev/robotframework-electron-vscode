# Design

## Context

See proposal.md for the motivation and the specs for the requirements. Today `docs/src/content/docs/` has `getting-started/` with one page per library, `guides/` with ten pages, and a sidebar of three `autogenerate` groups: getting started, guides, and reference, whose folder does not exist. Five guides mix both libraries:
- `browser-keywords.md` ends with a section "In VS Code";
- `videos.mdx` has "A full frame of VS Code" with the example's `video.robot`;
- `traces.mdx` shows the example's `tracing.robot`;
- `logs.md` has a section on the VS Code instance directories, and a troubleshooting item on VS Code's command palette;
- `ci-and-display.mdx` explains in its section on the screen size how VS Code fills the screen.

Pages include files from `examples/` with `?raw` imports and screenshots from `src/assets/`, both by relative paths. RobotCode 2.8.0, which brings `robotcode doc`, is not released yet.

## Goals / Non-Goals

**Goals:**
- A reader of one library finds every page about it in one sidebar group.
- Each topic is written once: shared behaviour in the Electron section, VS Code specifics in the VS Code section.

**Non-Goals:**
- Rewriting the content beyond what the split needs.
- Redirects from the old URLs.
- Keyword documentation in the guides; the reference pages hold it.

## Decisions

### Layout

```
docs/src/content/docs/
  index.mdx
  electron/
    getting-started.md      ← getting-started/electron.md
    browser-keywords.md     ← guides/browser-keywords.md without "In VS Code"
    traces.mdx              ← guides/traces.mdx without "The example"
    videos.mdx              ← guides/videos.mdx without "A full frame of VS Code"
    reference.md            generated
  vscode/
    getting-started.md      ← getting-started/vscode.md
    extensions.mdx          ← guides/extensions.mdx
    extension-host.md       ← guides/extension-host.md
    workbench-keywords.mdx  ← guides/workbench-keywords.mdx
    browser-keywords.md     ← "In VS Code" from guides/browser-keywords.md
    videos-and-traces.mdx   ← "A full frame of VS Code", "The example" of the trace guide,
                              and VS Code's window size from guides/ci-and-display.mdx
    instances.md            ← "VS Code instance directories" and the command palette item from guides/logs.md
    versions.mdx            ← guides/vscode-versions.mdx
    forks.md                ← guides/vscode-forks.md
    reference.md            generated
  running/
    ci-and-display.mdx      ← guides/ci-and-display.mdx
    logs.md                 ← guides/logs.md without the parts on VS Code
```

- **Folders are the sections.** They give the URLs, for example `vscode/extensions/`. Inside `vscode/`, the prefix `vscode-` of the old file names goes away.
- **History:** files move with `git mv`, so that their history stays.
- **Same depth:** every page stays one folder below `src/content/docs/`, as today, so the relative paths of the `?raw` imports and of the screenshots do not change.

### Sidebar

- **Groups:** `Electron`, `VS Code` and `Running tests`, each with `autogenerate` for its folder. A new page then needs no change of the configuration, as today.
- **Order and labels:** set in the frontmatter, with `sidebar.order` and `sidebar.label`. The getting-started page comes first with the label "Getting started", and the reference page last with the label "Keyword reference". The other pages keep their titles.
- **Reference group:** the empty group goes away. Until the reference exists, the sections simply have no reference page.

### Splitting the mixed pages

- **The VS Code page links back:** each VS Code page that comes out of a general page starts by linking to the Electron page of its topic. For example, Browser keywords in VS Code begins: VS Code is an Electron application, so everything on Browser keywords in applications applies; in addition: …
- **Mentions stay:** a general page may still name VS Code in passing, for example that its results come from Electron and VS Code. Only sections about VS Code move.
- **Instances, logs and troubleshooting:** the VS Code getting-started page keeps its short description of the instance directories and links to the new page `instances.md` for the details: the logs, the cleanup of earlier runs, parallel runs, and the troubleshooting item on the command palette.
- **Screen size:** the section on the screen size in `running/ci-and-display.mdx` keeps the screen of the display profiles and links to the VS Code page for how VS Code fills it.

### Links

- **Relative links between pages** change to the new paths. The build does not check links, so a script checks every internal link and anchor in `docs/dist` after the build, as during the last review.
- **Absolute links** in `packages/vscode/README.md` and `examples/vscode-extension/README.md` change to the new URLs.
- **`index.mdx`** links to both getting-started pages and to the running-tests section.

**Alternative:** Astro's `redirects` from every old URL. They are left out because the site is new and the libraries are in a pilot phase; they can be added later without changing the pages.

### Keyword reference

This decision moved here from `add-documentation-site`, with the reference pages now in the library sections:
- **Script:** `docs/scripts/generate_reference.py` runs `uv run robotcode -r . doc …` once for each library. It writes the Markdown with Starlight frontmatter (title, description, `sidebar.order` and `sidebar.label`) to `electron/reference.md` and `vscode/reference.md`.
- **Options:** the exact `robotcode doc` options are fixed once RobotCode 2.8.0 is released.
- **Committed pages:** the pages are committed, because the build has no Python and no Browser clone. AGENTS.md says when to regenerate them: after a keyword or its documentation changes. Once Browser comes from PyPI, the script can move into the workflow.

## Risks / Trade-offs

- **[Old URLs break for links outside the repository]** → The site is young and the libraries are not on PyPI yet. Redirects can follow if needed.
- **[VS Code readers miss shared content that now lives in the Electron section]** → The VS Code getting-started page says that the Electron section applies to VS Code as well, and each VS Code page links to the Electron page of its topic.
- **[The change stays open until RobotCode 2.8.0]** → The tasks of the structure do not depend on the reference. The structure can be published at once, and the change is archived after the reference tasks.
- **[`robotcode doc` output needs adjusting for Starlight, for example its headings or links]** → The script owns the post-processing. The output is checked in the first build after 2.8.0.

## Migration Plan

1. Move and split the pages, change the sidebar and the links, build and check the links.
2. After RobotCode 2.8.0: generate the reference pages, then archive the change.
