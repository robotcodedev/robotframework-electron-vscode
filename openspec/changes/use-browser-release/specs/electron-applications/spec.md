## ADDED Requirements

### Requirement: Supported versions
`robotframework-electron` SHALL run on Browser library 21.0.0, Python 3.11 and Robot Framework 7.1.1 as its lowest versions. Its package metadata SHALL require the Browser and Python versions, so that installing it brings a suitable Browser library and, with that, Robot Framework. `robotframework-vscode` SHALL get the same lowest versions by requiring the `robotframework-electron` of its own version.

#### Scenario: Older Browser library in the environment
- **WHEN** `robotframework-electron` is installed into an environment with a Browser library older than 21.0.0
- **THEN** the installer upgrades the Browser library to 21.0.0 or later

#### Scenario: Python that is too old
- **WHEN** `robotframework-electron` or `robotframework-vscode` is installed on Python 3.10
- **THEN** the installer refuses

#### Scenario: VS Code library
- **WHEN** `robotframework-vscode` is installed
- **THEN** the installer also installs `robotframework-electron` of the same version, and with it Browser library 21.0.0 or later

#### Scenario: Lowest versions
- **WHEN** the unit and acceptance tests run with Python 3.11, Browser library 21.0.0 and Robot Framework 7.1.1
- **THEN** they pass

### Requirement: Guide on installation
The getting-started pages of `robotframework-electron` and `robotframework-vscode` SHALL name the lowest versions of the Browser library, Python and Robot Framework, SHALL show the installation with Node.js and without it, neither of which downloads a web browser, and SHALL name the commands for what needs more: recording videos and a visible web browser beside an application.

#### Scenario: Checking an existing project
- **WHEN** someone with an existing Browser project looks up on a getting-started page whether their versions fit
- **THEN** the page names Browser library 21.0.0, Python 3.11 and Robot Framework 7.1.1 as the lowest versions

#### Scenario: Installation without Node.js
- **WHEN** someone without Node.js follows the page
- **THEN** the page shows the installation with BrowserBatteries, and the application's tests run without `rfbrowser init`

#### Scenario: Recording videos after the installation
- **WHEN** someone who followed the page wants to record videos
- **THEN** the page names the command for this, with Node.js and without it, and after that command a video is recorded

#### Scenario: Web browser beside an application
- **WHEN** someone wants a visible web browser beside an application
- **THEN** the page names the command for this, with Node.js and without it

### Requirement: Guide on ffmpeg
The guide on videos SHALL say that recording needs Playwright's own ffmpeg, that it comes with any browser that Browser installs but not with `--skip-browsers`, and which error `Start Electron Application` fails with when ffmpeg is missing.

#### Scenario: Start fails without ffmpeg
- **WHEN** someone gets the error `Video recording has not been started` from `Start Electron Application` and looks it up in the guide
- **THEN** the guide explains that ffmpeg is missing and points to the command that brings it

### Requirement: Guide on CI runners
The guide on running tests on CI SHALL name the command that also installs the system packages which Electron needs, and the setting that the Chromium sandbox of Electron and VS Code needs on Ubuntu.

#### Scenario: Setting up a CI job
- **WHEN** someone sets up a CI job on an Ubuntu runner with the guide
- **THEN** the guide names the installation with system packages and the `sysctl` setting for the sandbox

## MODIFIED Requirements

### Requirement: Failed start
If the application cannot be started, opens no window within the time allowed, or cannot be taken over by the Browser library, `Start Electron Application` SHALL fail with an error that names the cause. It SHALL leave no application process running and SHALL add nothing to Browser's state.

#### Scenario: Wrong executable path
- **WHEN** the executable path does not exist
- **THEN** the keyword fails with an error that names the path

#### Scenario: No window
- **WHEN** the application opens no window within the time allowed
- **THEN** the keyword fails, and afterwards no process of the application is running

#### Scenario: Browser cannot take the application over
- **WHEN** the Browser library cannot take over the started application
- **THEN** the keyword fails with an error that names the cause, and afterwards no process of the application is running
