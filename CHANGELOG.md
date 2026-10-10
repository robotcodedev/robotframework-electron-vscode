# Changelog

All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.

## [Unreleased]

### Bug Fixes

- **electron:** Resolve paths against the test run, clean up failed starts and harden downloads ([3affc44](https://github.com/robotcodedev/robotframework-electron-vscode/commit/3affc44e1eab7359111f1a1b4a5a4edee33a1a76))

  Relative executable paths and working directories are relative to the test run's working directory, which is also the default working directory. electron.js checks for the adoptContext hook before the launch and closes the application when anything after the launch fails. A missing pageId no longer fails the keyword. Downloads time out after 60 seconds without data, archives with entries or links outside the target folder are rejected, and unsupported processor architectures are reported.

- **vscode:** Resolve the executable, limit installs and reject closed instances ([831fa92](https://github.com/robotcodedev/robotframework-electron-vscode/commit/831fa92a3cf6f2bb266be6e7d1b0ee2c7e060018))

  Open VS Code follows PATH and symbolic links for a given executable and installs all extensions with one call that times out after 10 minutes. When the workbench does not become ready, the original error is kept even if closing fails. Install VS Code Extension rejects closed instances. stable and insiders are looked up once per process and fall back to the newest cached build when the update service cannot be reached. The downloads use the shared helpers of Electron.Helper.

- **vscode:** Retry the palette after Install VS Code Extension ([6269792](https://github.com/robotcodedev/robotframework-electron-vscode/commit/6269792c2756bc3aca2c14c4719177c35ec1ae3e))

  VS Code registers an extension installed into a running instance shortly after the install, and an open command palette does not refresh, so the acceptance test opened the palette too early now and then. The test now retries with a fresh palette, and the keyword's documentation says so.

### Documentation

- Describe the checks and the pre-commit hooks ([089a7c3](https://github.com/robotcodedev/robotframework-electron-vscode/commit/089a7c3e9d163cdbd70981d956e8ffd224585d27))
- Give the libraries their own introduction, import and keyword documentation ([6bc7b2c](https://github.com/robotcodedev/robotframework-electron-vscode/commit/6bc7b2ca4782926ff0770bd1d9d09f9674189615))

  Electron and VSCode start their documentation with their own introduction, followed by the Browser sections that Browser keywords link to, and document their import with an __init__ that wraps Browser's. Their keywords document return values and exceptions in the sections that Robot Framework 7.5 shows with the arguments.

- Add a guide on traces and HAR files ([40a68b5](https://github.com/robotcodedev/robotframework-electron-vscode/commit/40a68b58e13f3b638347b26d0877ce6690276527))

  The example's tracing.robot traces two tests and records the network traffic of a webview. The Browser features guide lists tracing, HAR recording and Download.

- Drop the link to the missing favicon ([c6b3763](https://github.com/robotcodedev/robotframework-electron-vscode/commit/c6b3763d6cf13e01bcff67a0e8bb3af343e82749))

  Starlight always links /favicon.svg, which the site does not have. A route middleware removes the link.

- Add contribution guide, AI policy, code of conduct and security policy ([958d525](https://github.com/robotcodedev/robotframework-electron-vscode/commit/958d525ade2ddcf0a6147bd2ab551d4b09240a07))

  They follow RobotCode's. AGENTS.md points agents to them and describes the Browser fork.

- Remove the upstream adoptContext draft ([5c255e7](https://github.com/robotcodedev/robotframework-electron-vscode/commit/5c255e7f92b04ecf09f070ec72f727c7999cd6d5))

  It is posted as MarketSquare/robotframework-browser#5317 and #5318.

- Add documentation site with Astro and Starlight ([dccfd37](https://github.com/robotcodedev/robotframework-electron-vscode/commit/dccfd37f77ec2cc6736f428a67979fd0bc59ce7e))

  Getting started pages, guides, a GitHub Pages workflow and a Robot Framework grammar copied from RobotCode. The package READMEs become short pages that link to the site; the site URL is a placeholder until the repository's location is decided. The keyword reference waits for robotcode doc in RobotCode 2.8.0.

- Draft upstream proposal for the adoptContext hook ([9e81af6](https://github.com/robotcodedev/robotframework-electron-vscode/commit/9e81af65797ece6207428abfe45ca17e0b0e1425))
- Require conventional commits in agent guidelines ([67fc910](https://github.com/robotcodedev/robotframework-electron-vscode/commit/67fc91061af1e7363061aac786a1a6779af1c94c))
- Add contributor guidelines and background notes ([e097857](https://github.com/robotcodedev/robotframework-electron-vscode/commit/e0978577b16cecb1c27fef7b498b632d5a66963f))

### Features

- **electron:** Record traces and HAR files and accept downloads ([3249d1d](https://github.com/robotcodedev/robotframework-electron-vscode/commit/3249d1d3552dc6ff11b8084396324a052fb51182))

  New Electron Application takes tracing, as New Context does, including ROBOT_FRAMEWORK_BROWSER_TRACING, and record_har, which goes to Playwright's Electron launch. The application's context options go to Browser with adoptContext, so that Download works.

- **electron:** Name the application electron in the browser catalog ([02298d6](https://github.com/robotcodedev/robotframework-electron-vscode/commit/02298d699c8c31f779cca67f512b465f6d6b0a4d))

  electron.js passes { name: 'electron' } to adoptContext, which now takes its options as one object.

- **electron:** Record videos of applications ([8bec0e3](https://github.com/robotcodedev/robotframework-electron-vscode/commit/8bec0e31a577d1dcbebd043d18510b5f811f2478))

  New Electron Application gets record_video with Browser's recordVideo keys and Playwright's showActions overlay. Folder, default size and the video in the log come from Browser's own helpers, and the page details carry the video's path. Open VS Code passes record_video on. A guide covers recording, ffmpeg, a full frame with Set Viewport Size, and presenter mode as slow motion.

- **electron:** Add Electron library with New and Close Electron Application ([0c79af4](https://github.com/robotcodedev/robotframework-electron-vscode/commit/0c79af4df4368b575869c788901a943d4cc8d8da))

  Electron(Browser) starts Electron apps through Playwright and hands their context to Browser via the adoptContext hook. Electron.Helper downloads and caches Electron releases. Includes a fixture app and acceptance tests.

- **examples:** Stabilise the video tests and add one without presenter mode ([74a8dba](https://github.com/robotcodedev/robotframework-electron-vscode/commit/74a8dba4f3b8bca31bb818c32d1e5df0c89ea91d))

  Run Python File waits until VS Code has stopped redrawing the run button, because presenter mode fails on a redrawn element. The Python video test creates greeting.py through the Save As dialog again (New File, Save File With Dialog), and a third video test records without presenter mode and creates the file in the explorer. Each video test sets presenter mode itself. editor.robot gets a test for Create File In Explorer.

- **examples:** Run Python files with the run button and create files in the explorer ([d22dba9](https://github.com/robotcodedev/robotframework-electron-vscode/commit/d22dba9148ccd86054215fc33ec1522494d8cfa5))

  Run Python File in the new python.resource clicks the run button above the editor once the Python extension has chosen an interpreter and finished discovering. The video suite switches presenter mode on for the whole suite and lets Browser close VS Code, and its Python test creates greeting.py in the explorer. add-video-example records the redrawn run button under presenter mode as an open task.

- **examples:** Record a video in the VS Code example ([0e75639](https://github.com/robotcodedev/robotframework-electron-vscode/commit/0e756394c2bf19fa052330247dcc78a939a3139f))

  video.robot demonstrates the example extension while it records a video in the size of the screen, with the action overlay and presenter mode. Open Example VS Code returns the ids and page details, and the video guide includes the suite instead of its own snippet. Planned and implemented as the change add-video-example.

- **examples:** Extend the VS Code example with workspace, editor, terminal and extensions ([2278513](https://github.com/robotcodedev/robotframework-electron-vscode/commit/2278513866e768642e37fb160ec27f6d48252168))

  The example gets a workspace copy per instance, resources for the editor, VS Code's own file dialog and the terminal, suites for these, a second window and the Python extension, and screenshots at its important steps. Run Command opens a fresh palette until late commands appear and matches rows by their exact label. A script regenerates the documentation's screenshots, and new guides cover dependency extensions and the Browser features that work in VS Code.

- **vscode:** Pass tracing and record_har on to the application ([3c91141](https://github.com/robotcodedev/robotframework-electron-vscode/commit/3c91141040cea3fc8461773f74d95512d150a6c9))
- **vscode:** Add Install VS Code Extension ([46147a6](https://github.com/robotcodedev/robotframework-electron-vscode/commit/46147a69474b9d3f8539b8af4484b17c85e9e76a))

  Installs a Marketplace extension or a .vsix file into a running instance that Open VS Code started, through the instance's command-line script and directories. Open VS Code records each instance for this. The acceptance tests pack the test extension into a .vsix at run time.

- **vscode:** Add VS Code extension example and workbench guides ([2edafa1](https://github.com/robotcodedev/robotframework-electron-vscode/commit/2edafa10510d49920f25a26335a9afc782ad29cd))

  The example project drives the command palette, quick picks, notifications and a webview with its own keywords and locators, one resource per workbench part. Two guides include its files. VSCode drops its unused instance registry, and a test pins that it adds only Open VS Code and Close VS Code to Electron.

- **vscode:** Add VSCode.Helper, clean up old instances and support forks ([c85962f](https://github.com/robotcodedev/robotframework-electron-vscode/commit/c85962fbdf95268400efdef653b2e329626b170f))

  - VSCode.Helper provides Get VS Code Executable, shaped like Get Electron Executable; a given executable is returned unchanged. It replaces Download VS Code in the VSCode library.
  - The first suite start of a run removes the vscode folder that earlier runs left in the output directory.
  - The command-line script for installing extensions is found through applicationName in product.json, so forks such as VSCodium work. The acceptance tests no longer assume the product name; the logs test is tagged vscode-only.

- **vscode:** Add Download VS Code, Open VS Code and Close VS Code ([8375ced](https://github.com/robotcodedev/robotframework-electron-vscode/commit/8375cedfc8bf27ed89e00cec339aefd806f15c0d))

  VSCode(Electron) downloads and caches verified VS Code builds and starts isolated instances with their own user-data and extensions directories, the extension under test, dependency extensions and preset settings. Includes a test extension, acceptance tests and unit tests. robot.toml runs both packages' acceptance tests, named Electron and VSCode, with the profile vscode-insiders; pytest covers both packages.

- Start Openbox in the display profiles and maximise the example's VS Code ([88195da](https://github.com/robotcodedev/robotframework-electron-vscode/commit/88195da3c2771808521f44b5c294c76ca152f58b))

  The xvfb and xephyr wrappers start the window manager Openbox on their display, if it is installed, because only a window manager can maximise windows on Xvfb and Xephyr. The example opens VS Code maximised, so it fills the screen, and screenshots and videos get the screen's size. The guides and READMEs name Xvfb, Xephyr and Openbox as prerequisites.

- Add display profiles for Xvfb, Xephyr and the desktop ([bfc78ec](https://github.com/robotcodedev/robotframework-electron-vscode/commit/bfc78ecc97d31fd3994fbf294a2dabfdca00f4d6))

  The repository's and the example's robot.toml get the profiles xvfb (hidden, Full HD), xephyr (separate window) and local, with xvfb and xephyr only on Linux. Both wrappers are short shell scripts in robot.toml, so they work from any folder, remove WAYLAND_DISPLAY and read SCREEN_SIZE. The example's small-screen profile shows how to change the size with extend-env. AGENTS.md, the READMEs and the CI guide use the profiles instead of display prefixes.

### Refactor

- **electron:** Share zip extraction and the user cache directory from Electron.Helper ([9512eb0](https://github.com/robotcodedev/robotframework-electron-vscode/commit/9512eb0817d39af8cfefe9311f48042452404b2f))

  extract_zip and user_cache_dir are now public so that the VSCode library reuses them. The keyword example builds the app path from ${EXECDIR}.

<!-- generated by git-cliff -->
