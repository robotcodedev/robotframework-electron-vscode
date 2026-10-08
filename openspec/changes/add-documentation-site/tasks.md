# Tasks

## 1. Site skeleton

- [ ] 1.1 Create `docs/` with Astro and Starlight: `package.json` with a lockfile, `astro.config.mjs` with `site` and `base` as marked placeholder constants, a sidebar with getting started, guides and reference (each `autogenerate`), and an `index.mdx`. Add `docs/node_modules` and `docs/dist` to `.gitignore`. Verify that `npm ci && npm run build` in `docs/` succeeds and that the sidebar shows the three groups.
- [ ] 1.2 Check including a file from outside `docs/` with `?raw` and `<Code lang="robotframework">` (for example `packages/vscode/atest/helper.robot`), in both `npm run build` and `npm run dev`, and set `vite.server.fs.allow` if needed. Verify that the code is shown highlighted, then remove the trial page.

## 2. Content

- [ ] 2.1 Write `getting-started/electron.md` and `getting-started/vscode.md` from the package READMEs, keeping their verified quick-start code. Verify that the build succeeds and that the quick-start code still runs as written.
- [ ] 2.2 Write the guides on CI and the Linux display (Xvfb, Wayland), VS Code forks, downloads and cache, and logs and troubleshooting, from the package READMEs. Verify that every command and snippet in them runs as written.
- [ ] 2.3 Write the root `README.md` (overview of both libraries, pilot status, Browser hook, link to the site, short development section) and shorten both package READMEs to description, installation, a minimal example and a link to the site. Verify that the minimal examples run and that all links resolve.

## 3. Deployment

- [ ] 3.1 Add `.github/workflows/docs.yml` (`withastro/action` with `path: docs`, then `actions/deploy-pages`; triggers: pushes to the default branch that change `docs/**` or `examples/**`, and manual dispatch). Verify that the YAML parses and that its build steps (`npm ci`, `npm run build`) succeed locally. Check the deployment itself once the repository has a remote.
- [ ] 3.2 Add the docs commands (`npm ci`, `npm run dev`, `npm run build` in `docs/`) to `AGENTS.md`. Verify that they run as written.

## 4. Keyword reference (after RobotCode 2.8.0 is released)

- [ ] 4.1 Upgrade RobotCode with `uv lock --upgrade-package robotcode && uv sync`. Verify that `uv run robotcode -r . doc keywords VSCode` works.
- [ ] 4.2 Write `docs/scripts/generate_reference.py`. It generates the pages for `Electron`, `Electron.Helper`, `VSCode` and `VSCode.Helper` into `src/content/docs/reference/` with Starlight frontmatter. Generate and commit the pages, and add the regeneration step to `AGENTS.md`. Verify that the build shows the four reference pages, and that changing a keyword's docstring and regenerating changes its page.
