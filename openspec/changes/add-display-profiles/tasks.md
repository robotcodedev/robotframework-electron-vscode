# Tasks

## 1. Profiles

- [ ] 1.1 Add `scripts/xephyr-run` and the profiles `xvfb`, `xephyr` and `local` to the root `robot.toml`. Verify that `uv run robotcode -r . profiles list` shows them, that `uv run robotcode -r . -p xvfb robot` passes from the Wayland desktop without opening windows, and that a `-p xephyr` run (nested in an Xvfb) passes and leaves no Xephyr process.
- [ ] 1.2 Add the same profiles and a copy of the script to `examples/vscode-extension`. Verify the scenarios "Hidden run from a Wayland desktop" and "Visible run in a separate window" with the example, and check "Other platforms" by evaluating the `enabled.if` expressions for `Windows` and `Darwin`.

## 2. Documentation

- [ ] 2.1 Replace the display prefixes in `AGENTS.md`, the root README and the example's README with the profiles. Rewrite the display part of `ci-and-display.md` (profiles, plain `xvfb-run` with screen size, the 640×480 default, the viewport note). Verify that every command runs as written and that `npm run build` in `docs/` succeeds.
