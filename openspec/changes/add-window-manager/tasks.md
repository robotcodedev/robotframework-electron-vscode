# Tasks

## 1. Window manager and example

- [ ] 1.1 Start Openbox in the `xvfb` and `xephyr` wrappers of the root `robot.toml` and the example's `robot.toml`, only if it is installed. Verify that all acceptance tests pass with `-p xvfb`, that a `-p xephyr` run (nested in an Xvfb) leaves neither Xephyr nor Openbox running, and the scenario "Without a window manager" with `openbox` hidden from the `PATH`.
- [ ] 1.2 Open VS Code maximised in `Open Example VS Code`. Verify the scenario "VS Code fills the screen" with a probe under `-p xvfb`, `-p xephyr` and `-p xvfb -p small-screen`, and that the example passes.

## 2. Documentation

- [ ] 2.1 Update `ci-and-display.mdx` (Openbox, maximised VS Code) and the full-frame recipe in `videos.md`, and add the Linux prerequisites (Xvfb, Openbox, Xephyr) to the example's README, the root README and AGENTS.md. Verify the recipe's snippet, and that `npm run build` in `docs/` succeeds.
