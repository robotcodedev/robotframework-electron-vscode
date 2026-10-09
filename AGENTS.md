# Repository Guidelines

Short orientation for automated contributors.

## What This Is

Two Robot Framework libraries built on top of the [Browser library](https://github.com/MarketSquare/robotframework-browser):

- `packages/electron/` — `robotframework-electron`, import name `Electron`: start Electron applications and hand their windows to the Browser library.
- `packages/vscode/` — `robotframework-vscode`, import name `VSCode`: end-to-end testing of VS Code extensions (download and isolated launch of VS Code, workbench keywords). Not specific to any one extension; RobotCode is the first consumer.

Background, research and the initial design ideas are in [dev-docs/background.md](dev-docs/background.md).

## Layout

- `packages/*/src/<Module>/` — library sources (uv workspace members, `uv_build` backend with `module-name`).
- `openspec/` — planned and archived changes (OpenSpec, `/opsx:*` commands).
- `dev-docs/` — planning and design notes, not user-facing.

## Browser Library Dependency

Until our hook is merged and released upstream, `robotframework-browser` comes from a local clone at `../robotframework-browser` (editable path source in the root `pyproject.toml`).

- The hook is developed in the clone on the branch `adopt-context-hook`.
- The clone's `origin` is the fork `d-biehl/robotframework-browser`, and `upstream` is `MarketSquare/robotframework-browser`. The hook is proposed upstream in MarketSquare/robotframework-browser#5318. Push to the fork over SSH (`git@github.com:d-biehl/robotframework-browser.git`); the HTTPS `origin` has no credentials.

The clone needs its generated gRPC stubs and the built Node wrapper, which are not in git:

```sh
cd ../robotframework-browser
uv venv .venv && uv pip install pip          # invoke tasks call pip; without it they hit the system Python
source .venv/bin/activate
uv pip install -r Browser/dev-requirements.txt
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 inv build # runs deps, protobuf, node-build
```

The browser download is skipped there, but some acceptance tests need Chromium and the video tests need Playwright's ffmpeg: run `PLAYWRIGHT_BROWSERS_PATH=0 npx playwright install chromium` in the clone once, which installs both.

After switching branches in the clone or changing its TypeScript or proto files, run `inv node-build` there again; it regenerates the gRPC code too. Do not install `robotframework-browser-batteries`: it brings its own gRPC server and would bypass the patched Node code of the clone.

## Common Commands

- `uv sync` — install the workspace into `.venv`, including the dev tools (pytest, RobotCode).
- Always start RobotCode from the repository root with `-r .`. Each workspace package has its own `pyproject.toml`; without `-r`, RobotCode searches the project root upward from the given paths, stops at a package's `pyproject.toml` and ignores `robot.toml`.
- `uv run robotcode -r . robot` — run the Robot Framework acceptance tests. Paths, output directory and profiles come from `robot.toml`; select a profile with `-p <name>` before the subcommand, and one test or suite with `-bl "<longname>"`. The display profiles choose where the windows open: `-p xvfb` hidden on a Full HD Xvfb screen, also on a Wayland desktop and without any desktop; `-p xephyr` in a separate Xephyr window; `-p local` or no display profile on the normal desktop. Combine them with other profiles, for example `-p xvfb -p vscode-insiders`. Agents use `-p xvfb`. The profiles need Xvfb, and Xephyr for `xephyr`; both start Openbox, if it is installed, so that windows can be maximised.
- `uv run robotcode -r . discover tests`, `uv run robotcode -r . results summary`, `uv run robotcode -r . analyze code` — list tests, inspect the last run, analyse statically.
- `uv run pytest` — Python unit tests of all packages.
- `uv run robotcode -r examples/vscode-extension robot` — run the VS Code example project. It has its own `robot.toml` with the same display profiles and is not part of the root `robot.toml` paths. Its guides in `docs/` include its files, so check them when you change the example.
- `uv run python docs/scripts/update_screenshots.py` — run the example with `-p xvfb` and copy its screenshots to `docs/src/assets/screenshots/`. Run it after changing the example or its VS Code version, and commit the images. It needs Xvfb, Openbox and network access for the Python tests.
- Personal settings, such as a local `ELECTRON_EXECUTABLE`, go into `.robot.toml`, which is gitignored.
- `npm ci`, then `npm run dev` or `npm run build` in `docs/` — install the documentation site's dependencies, serve it locally with live reload, or build it into `docs/dist/`. Only Node.js is needed, no Python. Started by an agent, `npm run dev` runs in the background; stop it with `npx astro dev stop` in `docs/`.

## Agent Notes

- Never open issues, pull requests or comments in other repositories (including the Browser library) unless explicitly asked.
- Make small, focused changes; plan larger work as an OpenSpec change first.
- Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [AI_POLICY.md](AI_POLICY.md): issues and pull requests end with an "AI / tooling disclosure", and commits must be cryptographically signed.
- Write commit messages as [Conventional Commits](https://www.conventionalcommits.org/): `<type>(<optional scope>): <description>`, for example `feat(electron): add New Electron Application` or `docs(openspec): plan vscode workbench keywords change`. Use the package (`electron`, `vscode`) or `openspec` as scope where it fits.
