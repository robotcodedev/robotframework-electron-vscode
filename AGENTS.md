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
- The clone's `origin` is `MarketSquare/robotframework-browser`; there is no GitHub fork yet.

The clone needs its generated gRPC stubs and the built Node wrapper, which are not in git:

```sh
cd ../robotframework-browser
uv venv .venv && uv pip install pip          # invoke tasks call pip; without it they hit the system Python
source .venv/bin/activate
uv pip install -r Browser/dev-requirements.txt
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 inv build # runs deps, protobuf, node-build
```

After switching branches in the clone or changing its TypeScript or proto files, run `inv node-build` there again; it regenerates the gRPC code too. Do not install `robotframework-browser-batteries`: it brings its own gRPC server and would bypass the patched Node code of the clone.

## Common Commands

- `uv sync` — install the workspace into `.venv`.
- `uv run robot ...` — run Robot Framework tests.

## Agent Notes

- Never open issues, pull requests or comments in other repositories (including the Browser library) unless explicitly asked.
- Make small, focused changes; plan larger work as an OpenSpec change first.
