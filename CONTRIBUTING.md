<!-- omit in toc -->
# Contributing to Robot Framework Electron & VS Code

First off, thanks for taking the time to contribute!

All types of contributions are encouraged and valued. See the [Table of Contents](#table-of-contents) for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution. It will make it a lot easier for us maintainers and smooth out the experience for all involved. The community looks forward to your contributions.

**New here? Find your path:**

- Have a question → [I Have a Question](#i-have-a-question)
- Found a bug → [Reporting Bugs](#reporting-bugs)
- Have an idea → [Suggesting Enhancements](#suggesting-enhancements)
- Want to change code or docs → [Your First Code Contribution](#your-first-code-contribution)

Whatever you bring, two short ground rules apply to everything — please skim the [AI and Automated Contribution Policy](AI_POLICY.md) and our note on [payment and bounty requests](#payment-bounty-and-monetization-requests). Everything after that is about *how* to contribute.

And if you like the project, but just don't have time to contribute, that's fine. There are other easy ways to support the project and show your appreciation, which we would also be very happy about:
- Star the project
- Refer this project in your project's readme
- Mention the project at local meetups and tell your friends/colleagues

<!-- omit in toc -->
## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [I Have a Question](#i-have-a-question)
- [Project-Wide Rules](#project-wide-rules)
  - [AI and Automated Contributions](#ai-and-automated-contributions)
  - [Payment, Bounty, and Monetization Requests](#payment-bounty-and-monetization-requests)
- [I Want To Contribute](#i-want-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
    - [Development Environment Setup](#development-environment-setup)
    - [IDE Configuration](#ide-configuration)
    - [Development Workflow](#development-workflow)
    - [Pull Request Guidelines](#pull-request-guidelines)
    - [Running Tests](#running-tests)
    - [Additional Development Commands](#additional-development-commands)
    - [Troubleshooting Development Setup](#troubleshooting-development-setup)
  - [Improving The Documentation](#improving-the-documentation)
- [Styleguides](#styleguides)
  - [Commit Messages](#commit-messages)
  - [Robot Framework Code](#robot-framework-code)
- [Join The Project Team](#join-the-project-team)


## Code of Conduct

This project and everyone participating in it is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report unacceptable behavior
to <support@robotcode.io>.


## I Have a Question

If you want to ask a question, we assume that you have read the available documentation, which is linked from the [README](README.md).

Before you ask a question, it is best to search for existing issues in this repository that might help you. In case you have found a suitable issue and still need clarification, you can write your question in this issue. It is also advisable to search the internet for answers first.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an issue in this repository.
- Provide as much context as you can about what you're running into.
- Provide project and platform versions (Python, Robot Framework, Browser library, Electron or VS Code, operating system, display), depending on what seems relevant.

We will then take care of the issue as soon as possible.

You can also ask questions in the [Robot Framework Slack](https://robotframework.slack.com) or in the [Robot Framework Forum](https://forum.robotframework.org).

## Project-Wide Rules

Just two ground rules, and they apply to every interaction with the project — pull requests, issues, discussions, comments, code review replies, and anything else. They're short; please read them before opening a contribution of any kind.

### AI and Automated Contributions

AI-assisted or automated contributions, including agent-generated ones, must follow our [AI and Automated Contribution Policy](AI_POLICY.md). In short: the human submitter must understand, review, test, and maintain the contribution, and must disclose AI or tool assistance in the pull request, issue, or comment.

### Payment, Bounty, and Monetization Requests

This is an open-source project, not a lead-generation or micro-bounty platform.

Do not include payment links, invoices, donation requests, wallet addresses, "paid fix" notes, bounty claims, sponsorship requests, or similar monetization requests in pull requests, issues, discussions, comments, or any other project interaction unless paid work or a bounty process was explicitly agreed with the maintainers before the work started.

Unsolicited monetization requests attached to contributions are not accepted. Pull requests containing such requests may be closed without review, and issues or discussions containing such requests may be declined or closed.

If a contribution is part of an agreed paid engagement, sponsored work, or bounty process, disclose that context clearly and follow the agreed process. Do not add ad-hoc payment requests to the contribution body.

Contributions are reviewed on their technical merit, usefulness to the project's users, and compliance with the project's contribution standards — not on payment requests attached to them.

## I Want To Contribute

> [!IMPORTANT]
> **Legal Notice**
>
> The project is licensed under the [Mozilla Public License 2.0](LICENSE). When contributing to this project, you must agree that you have the right to submit the contribution under the project license.
>
> This means that the contribution was created in whole or in part by you, is based on previous work that you are allowed to submit under a compatible license, or was otherwise lawfully provided to you for contribution.
>
> This corresponds to the spirit of the [Developer Certificate of Origin](https://developercertificate.org/). You are encouraged to add a DCO sign-off to your commits with `git commit -s` — this only adds a `Signed-off-by` trailer and is separate from the cryptographic commit signature (`-S`, GPG/SSH) required by [Signed Commits Required](#signed-commits-required) below.
>
> If AI tools or automated agents were used, you remain the human submitter responsible for the contribution and must follow the AI and Automated Contribution Policy.

### Reporting Bugs

<!-- omit in toc -->
#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Therefore, we ask you to investigate carefully, collect information and describe the issue in detail in your report. Please complete the following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug of this project and not an error on your side or in another component:
  - Keywords and locators for the VS Code workbench belong to your tests. When VS Code changes its DOM and a locator stops matching, update the locator in your project; see the guide *Writing your own workbench keywords* in the documentation.
  - Problems of Browser keywords themselves belong to the [Browser library](https://github.com/MarketSquare/robotframework-browser), and problems of the application under test to that application.
- To see if other users have experienced (and potentially already solved) the same issue you are having, check if there is not already a bug report existing for your bug or error in the issues of this repository.
- Also make sure to search the internet (including Stack Overflow) to see if users outside of the GitHub community have discussed the issue.
- Collect information about the bug:
  - Stack trace (Traceback) and the Robot Framework log, ideally with `output.xml`
  - `playwright-log.txt` from the output directory
  - OS, Platform and Version (Windows, Linux, macOS, x86, ARM), and on Linux the display: X11, Wayland, or one of the display profiles `xvfb` or `xephyr`
  - Versions of Python, Robot Framework, the Browser library, and the Electron application or VS Code (or fork) under test
  - Possibly your input and the output
  - Can you reliably reproduce the issue? And can you also reproduce it with older versions?

<!-- omit in toc -->
#### How Do I Submit a Good Bug Report?

> [!WARNING]
> Never report security related issues, vulnerabilities or bugs including sensitive information to the issue tracker, or elsewhere in public. Follow the [Security Policy](SECURITY.md) instead.

We use GitHub issues to track bugs and errors. If you run into an issue with the project:

- Open an issue in this repository. (Since we can't be sure at this point whether it is a bug or not, we ask you not to talk about a bug yet and not to label the issue.)
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the *reproduction steps* that someone else can follow to recreate the issue on their own. This usually includes your code. For good bug reports you should isolate the problem and create a reduced test case.
- Provide the information you collected in the previous section.

Once it's filed:

- The project team will label the issue accordingly.
- A team member will try to reproduce the issue with your provided steps. If there are no reproduction steps or no obvious way to reproduce the issue, the team will ask you for those steps and mark the issue as `needs-repro`. Bugs with the `needs-repro` tag will not be addressed until they are reproduced.
- If the team is able to reproduce the issue, it will be marked `needs-fix`, as well as possibly other tags (such as `critical`), and the issue will be left to be [implemented by someone](#your-first-code-contribution).

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion, **including completely new features and minor improvements to existing functionality**. Following these guidelines will help maintainers and the community to understand your suggestion and find related suggestions.

<!-- omit in toc -->
#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the documentation carefully and find out if the functionality is already covered, maybe by an individual configuration.
- Perform a search in the issues of this repository to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. The libraries provide the technique: starting Electron applications and VS Code and handing their windows to the Browser library. Keywords for the VS Code workbench, such as the command palette or the explorer, belong to your test project, because they depend on the VS Code version and on the extension under test; the example project shows how to write them. Features that every Browser user would need belong to the Browser library. It's up to you to make a strong case to convince the project's developers of the merits of this feature. Keep in mind that we want features that will be useful to the majority of our users and not just a small subset.

<!-- omit in toc -->
#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as GitHub issues in this repository.

- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why. At this point you can also tell which alternatives do not work for you.
- You may want to **include screenshots and animated GIFs** which help you demonstrate the steps or point out the part which the suggestion is related to.
- **Explain why this enhancement would be useful** to most users. You may also want to point out the other projects that solved it better and which could serve as inspiration.

### Your First Code Contribution

Welcome to your first code contribution! Here's how to set up your development environment and get started.

#### Development Environment Setup

1. **Prerequisites** (see each project's site for install instructions):
   - [Python](https://www.python.org/) 3.10 or newer
   - [uv](https://docs.astral.sh/uv/)
   - [Node.js](https://nodejs.org/), for the Browser library and the documentation site
   - [Git](https://git-scm.com/)
   - On Linux, for the display profiles: Xvfb (`xvfb` on Debian and Ubuntu, `xorg-server-xvfb` on Arch Linux), Xephyr (`xserver-xephyr` or `xorg-server-xephyr`) and the window manager Openbox (`openbox`)

2. **Browser library:** the libraries need the `adoptContext` hook of the Browser library, which is not in a Browser release yet. Until it is, the workspace takes `robotframework-browser` from a clone next to this repository, `../robotframework-browser`, on the branch `adopt-context-hook`. The clone needs its generated gRPC code and the built Node wrapper:

   ```bash
   git clone --branch adopt-context-hook https://github.com/d-biehl/robotframework-browser.git
   cd robotframework-browser
   uv venv .venv && uv pip install pip      # the invoke tasks call pip
   source .venv/bin/activate
   uv pip install -r Browser/dev-requirements.txt
   PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 inv build
   PLAYWRIGHT_BROWSERS_PATH=0 npx playwright install chromium   # Chromium and ffmpeg for some tests
   ```

   Do not install `robotframework-browser-batteries`: it brings its own Node process and would bypass the clone.

3. **This repository:** clone it next to the Browser clone and install the workspace with the development tools:

   ```bash
   git clone git@github.com:robotcodedev/robotframework-electron-vscode.git
   cd robotframework-electron-vscode
   uv sync
   ```

#### IDE Configuration

We recommend VS Code with the [RobotCode](https://robotcode.io) extension, which runs and debugs the acceptance tests and analyses Robot Framework files.

> [!IMPORTANT]
> After `uv sync`, select the interpreter of the workspace, `.venv` in the repository root, in VS Code:
>
> 1. Open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P` or `F1`).
> 2. Type "Python: Select Interpreter".
> 3. Choose the interpreter in `.venv`.

Open the repository root as the workspace folder, so that RobotCode reads the root `robot.toml`. Personal settings belong into gitignored files: test variables such as a local `ELECTRON_EXECUTABLE` or `VSCODE_EXECUTABLE` into `.robot.toml`, editor settings into `.vscode/` or a `*.code-workspace` file.

#### Development Workflow

1. **Discuss larger changes first** in an issue. Larger work is planned as an [OpenSpec](https://github.com/Fission-AI/OpenSpec) change in `openspec/changes/` — proposal, specs, design and tasks — before it is implemented; the main specs in `openspec/specs/` describe the current behavior.
2. **Create a branch:** `git checkout -b feature/your-feature-name`
3. **Make your changes** following the project's [styleguides](#styleguides)
4. **Run tests:** `uv run pytest` and `uv run robotcode -r . -p xvfb robot` (see [Running Tests](#running-tests)) — run all tests before committing or pushing, not only the tests you added or changed
5. **Run the static analysis:** `uv run robotcode -r . analyze code`
6. **Commit your changes** with a descriptive, [signed](#signed-commits-required) commit message
7. **Push and create a pull request**

#### Pull Request Guidelines

<!-- omit in toc -->
##### PR Checklist

Before submitting your pull request, make sure that:

- [ ] The change is **focused** on a single concern (no unrelated refactors or formatting noise).
- [ ] **Tests** for the change have been added or updated, and `uv run pytest` and `uv run robotcode -r . -p xvfb robot` pass locally — *not required for documentation-only or other non-code changes; note that in the PR*.
- [ ] The **example project** still passes, `uv run robotcode -r examples/vscode-extension -p xvfb robot`, if you changed a library or the example.
- [ ] The **static analysis** reports no errors or warnings: `uv run robotcode -r . analyze code`.
- [ ] **Documentation** has been updated where relevant (user docs, docstrings, README).
- [ ] **Generated files** (if any) were regenerated with the documented script, not edited by hand.
- [ ] **Commits** follow [Conventional Commits](#commit-messages) and are [cryptographically signed](#signed-commits-required) (`git commit -S`, GPG/SSH).
- [ ] **AI / tooling disclosure** is included if AI tools or automated agents were used for a substantial part of the change (see [AI_POLICY.md](AI_POLICY.md)).
- [ ] No payment, bounty, or monetization requests are attached (see [Payment, Bounty, and Monetization Requests](#payment-bounty-and-monetization-requests)).

<!-- omit in toc -->
##### PR Description

A good PR description:
- Explains **what** changed and **why**.
- References any related issues (e.g. `Fixes #123`).
- Includes screenshots for visible changes, for example in the documentation site.
- Lists any breaking changes explicitly.

<!-- omit in toc -->
##### PR Review Process

- Automated checks must pass (tests, static analysis, etc.).
- At least one maintainer review is required.
- Address feedback promptly.
- Keep your PR up to date with the main branch.

#### Running Tests

**Unit tests** of both packages:

```bash
uv run pytest
```

**Acceptance tests** of both packages, written in Robot Framework. Paths, output directory and profiles come from `robot.toml`:

```bash
uv run robotcode -r . -p xvfb robot                          # hidden on a Full HD Xvfb screen (Linux)
uv run robotcode -r . -p xephyr robot                        # in a separate Xephyr window (Linux)
uv run robotcode -r . robot                                  # on the normal desktop
uv run robotcode -r . -p xvfb robot -bl "<longname>"         # a single suite or test
```

> [!NOTE]
> Always start RobotCode from the repository root with `-r .`. Each package has its own `pyproject.toml`; without `-r`, RobotCode stops its search for the project root at a package's `pyproject.toml` and ignores `robot.toml`.

- The display profile `xvfb` also works on a Wayland desktop and without any desktop; `xephyr` opens a separate window on your desktop. Both start Openbox if it is installed, so that windows can be maximised. Prefer `-p xvfb`: the tests do not open windows on your desktop and do not depend on its size.
- The tests download Electron and VS Code into the repository's `.cache/`. To use local executables instead, set `ELECTRON_EXECUTABLE` or `VSCODE_EXECUTABLE` in `.robot.toml`.
- Other versions: `-p electron-previous` runs the Electron tests against an older Electron major, and `-p vscode-insiders` the VS Code tests against the newest VS Code Insiders build. Combine them with a display profile, for example `-p xvfb -p vscode-insiders`.
- For individual tests, the Test Explorer of VS Code with RobotCode is the most convenient way to run and debug a single test.

**Example project** in `examples/vscode-extension`, which has its own `robot.toml` with the same display profiles. Its Python tests need network access and are tagged `network`:

```bash
uv run robotcode -r examples/vscode-extension -p xvfb robot
uv run robotcode -r examples/vscode-extension -p xvfb robot -e network   # without network access
```

#### Additional Development Commands

- `uv run robotcode -r . discover tests` — List the acceptance tests.
- `uv run robotcode -r . results summary` — Summarise the last run.
- `uv run robotcode -r . analyze code` — Analyse the Robot Framework files statically.
- `uv run robotcode -r . repl` — Run keywords one by one against a running application, for example to find locators.
- `uv run python docs/scripts/update_screenshots.py` — Run the example project with `-p xvfb` and copy its screenshots into the documentation site. Run it after changing the example or its VS Code version, and commit the images. It needs Xvfb, Openbox and network access.

#### Troubleshooting Development Setup

**Common Issues:**

1. **`inv build` in the Browser clone fails with `externally-managed-environment`:**
   The clone's virtual environment has no pip, so the invoke tasks reach the system Python. This happens, for example, after `uv sync` in the clone, which removes pip:
   ```bash
   uv pip install --python .venv/bin/python pip
   ```

2. **Browser keywords fail after switching branches in the Browser clone:**
   Rebuild the Node wrapper and the generated gRPC code with `inv node-build` in the clone, also after changing its TypeScript or proto files.

3. **Video or Chromium tests fail:**
   Install Chromium and Playwright's ffmpeg in the clone: `PLAYWRIGHT_BROWSERS_PATH=0 npx playwright install chromium`.

4. **Windows open on the desktop, or tests behave differently on Wayland:**
   Use the display profile `-p xvfb`.

5. **VS Code does not fill the screen in screenshots and videos:**
   Install Openbox; without a window manager, VS Code cannot be maximised.

### Improving The Documentation

Documentation is crucial for helping users understand and use the libraries effectively. Here are ways you can help improve it:

#### Types of Documentation Contributions

1. **User Documentation** (`docs/` folder)
   - Getting started guides
   - Guides for tasks, such as CI, VS Code versions or videos
   - The example project in `examples/vscode-extension`, which the guides show

2. **Keyword Documentation**
   - Docstrings of the keywords, which are the reference documentation

3. **README Updates**
   - Installation instructions
   - Quick start examples

#### Documentation Setup

The documentation site is built with [Astro](https://astro.build/) and [Starlight](https://starlight.astro.build/) from the `docs/` folder and needs only Node.js, no Python:

```bash
cd docs
npm ci
npm run dev       # Start the development server with live reload
npm run build     # Build the site into docs/dist
```

#### Writing Documentation Pages

The pages live in `docs/src/content/docs/`, and a page's path is its URL: `guides/videos.mdx` is published at `/guides/videos/`.

- **Where a page belongs:** setting up a library goes to `getting-started/`, doing a task to `guides/`.
- **Frontmatter:** every page declares a `title` and a one-sentence `description`.
- **Example code:** guides include the files of the example project with `?raw` imports and the `<Code>` component instead of copying them, so the code on the site is the code that runs. Change the example, not a copy, and check the guides that include a file you changed.
- **Screenshots:** the screenshots in `docs/src/assets/screenshots/` are generated by `docs/scripts/update_screenshots.py` from the example's tests. Do not edit or replace them by hand.
- **Components:** a page with components is an `.mdx` file; use `.mdx` only where you need components and plain `.md` everywhere else.

#### Documentation Standards

- **Clear and concise:** Write for users of all skill levels
- **Examples:** Include practical code examples, preferably from the example project
- **Links:** Reference related concepts and external resources
- **Testing:** Verify that code examples actually work

## Styleguides
### Commit Messages

Good commit messages help maintain a clean project history and make it easier to understand changes. Please follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

#### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- **feat:** A new feature
- **fix:** A bug fix
- **docs:** Documentation only changes
- **style:** Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **refactor:** A code change that neither fixes a bug nor adds a feature
- **perf:** A code change that improves performance
- **test:** Adding missing tests or correcting existing tests
- **chore:** Changes to the build process or auxiliary tools and libraries

#### Scope

The scope should indicate the package or area affected:
- **electron:** The `robotframework-electron` package
- **vscode:** The `robotframework-vscode` package
- **examples:** The example project
- **docs:** The documentation site
- **openspec:** Planned and archived OpenSpec changes

#### Examples

```
feat(electron): add New Electron Application
```

```
feat(examples): run Python files with the run button and create files in the explorer
```

```
docs(openspec): plan vscode workbench keywords change
```

#### Guidelines

- **Subject line:** short, imperative mood ("add" not "added")
- **Body:** explain what and why (not how)
- **Footer:** Reference issues and breaking changes
- **Breaking changes:** Start footer with "BREAKING CHANGE:" followed by description

#### Signed Commits Required

**All commits and pull requests must be signed** to be accepted into the project. This helps ensure the authenticity and integrity of the codebase.

This refers to the **cryptographic commit signature** (`git commit -S`, GPG/SSH/X.509) — not to be confused with the DCO `Signed-off-by` trailer (`git commit -s`) mentioned in the [Legal Notice](#i-want-to-contribute).

**Setting up commit signing:**

The simplest setup is SSH signing — reuse the SSH key you already use for GitHub (or create one), no GPG toolchain needed:

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub   # your public key
git config --global commit.gpgsign true
```

Then add that key on GitHub once more as a **Signing Key** under *Settings → SSH and GPG keys*. Every commit is now signed automatically — verify with `git log --show-signature`.

Prefer GPG (or already have a GPG key)? Follow GitHub's [Managing commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification) guide, then set `commit.gpgsign true` the same way.

**For pull requests:**
- All commits in the PR must be signed
- You can sign previous commits using: `git rebase --exec 'git commit --amend --no-edit -S' -i HEAD~<number-of-commits>`

### Robot Framework Code

Write test and resource files whose variables RobotCode can resolve statically; see [Why is my variable not found?](https://robotcode.io/04_tip_and_tricks/02_why_variable_not_found).

- Do not use `Set Test Variable`, `Set Suite Variable` or `Set Global Variable` to pass data around. Let keywords `RETURN` their values, or let them fetch what they need themselves.
- Declare configuration in `*** Variables ***`, a resource file or a variable file. Locators go into the `*** Variables ***` section of the resource that uses them, so that a profile or the command line can override them.
- Where a variable really must be created dynamically, use the `VAR` statement, with `scope=` if needed.
- Build paths from `${EXECDIR}`, the project root, not from `${CURDIR}`: moving a file breaks `${CURDIR}/../..` chains.
- Keep the static analysis free of errors and warnings: `uv run robotcode -r . analyze code`.

## Join The Project Team

We're always looking for dedicated contributors! If you've been actively contributing and are interested in taking on more responsibility, here's how you can get involved:

- **Build a track record** of meaningful contributions over time
- **Engage with the community** by helping other users and contributors
- **Reach out** to the maintainers via email at <support@robotcode.io>
- **Express your interest** in specific areas where you'd like to contribute more

We value diversity and welcome contributors from all backgrounds.
