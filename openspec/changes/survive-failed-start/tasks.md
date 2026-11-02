# Tasks

## 1. Handler around the launch

- [ ] 1.1 In the harness of `packages/electron/tests/test_electron_js.py`, add a scenario `launch-leaves-rejection`, whose fake `launch` leaves a rejected promise behind, waits one `setImmediate` and then rejects, and report `process.listenerCount('unhandledRejection')` in the harness's output. Add a test that expects the error of the launch, the calls `["launch"]` and no listener, and check for no listener after a successful launch too; verify that `uv run pytest packages/electron/tests/test_electron_js.py` fails the new test, because the harness's Node process ends.
- [ ] 1.2 In `packages/electron/src/Electron/electron.js`, add a function around `playwright._electron.launch` with the listener from design.md, whose comment says what it prevents and that it goes away when Playwright is fixed, and call it from `robotframeworkElectronLaunch`; verify that `uv run pytest packages/electron/tests/test_electron_js.py` passes.

## 2. Acceptance tests

- [ ] 2.1 In `packages/electron/atest/failed_start.robot`, add the tests `Application Ends During The Start`, with `${{ sys.executable }}` and the expected error `*Process failed to launch*usage:*`, and `Application Does Not Answer In Time`, with the fixture application, a marker argument, `timeout=50ms` and the expected error `*Timeout 50ms exceeded*`. Each starts the fixture application first, and after the failed start checks its title, that `Get Electron Application Ids` lists one application, and that another start works; the second test also waits for `Fixture App Has Exited` with its marker. Verify that `uv run robotcode -r . -p xvfb robot -bl "Electron & VSCode.Electron.Failed Start"` passes, and that both tests fail without the listener of 1.2.
- [ ] 2.2 In `packages/vscode/atest/start_vs_code.robot`, add the test `VS Code Does Not Start`: `Start Test VS Code`, a failed `Start VS Code` with `${{ sys.executable }}`, the first instance still answers, and another `Start Test VS Code` works; verify that `uv run robotcode -r . -p xvfb robot -bl "Electron & VSCode.VSCode.Start VS Code"` passes, and that the test fails without the listener of 1.2.

## 3. The guide

- [ ] 3.1 Add the texts in design.md to the section "Troubleshooting" of `docs/src/content/docs/running/logs.md`; verify with `npm run build` in `docs/`, and that the link to the section on CI resolves.

## 4. Integration

- [ ] 4.1 Repeat in the scratchpad, with the implemented `electron.js`, the cases of the table in design.md that the tests do not cover: a real Electron that lacks a system library, one with the fuse `EnableNodeCliInspectArguments` off, and `/bin/false` with BrowserBatteries; verify that each fails with the error in the table, that the application that was open before keeps working, and that the next start works.
- [ ] 4.2 Run `uv run pre-commit run --all-files`, `uv run pytest`, `uv run robotcode -r . -p xvfb robot` and `openspec validate survive-failed-start --strict`; verify that all pass.

## Workflow follow-up

- Archive `use-browser-release` first, after its CI run is green, because both changes modify "Failed start" and the delta here builds on its text.
- Archive this change after its CI run is green.
- Whether to report the cause to Playwright, and whether to ask for a handler in Browser's Node process, is decided separately.
- When Browser ships a Playwright with the cause fixed, remove the listener and its unit test.
