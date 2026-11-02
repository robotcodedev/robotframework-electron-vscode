## MODIFIED Requirements

### Requirement: Failed start
If the application cannot be started, opens no window within the time allowed, or cannot be taken over by the Browser library, `Start Electron Application` SHALL fail with an error that names the cause. It SHALL leave no application process running and SHALL add nothing to Browser's state. Applications and browsers that are already open SHALL keep working, and the next start SHALL work.

#### Scenario: Wrong executable path
- **WHEN** the executable path does not exist
- **THEN** the keyword fails with an error that names the path

#### Scenario: No window
- **WHEN** the application opens no window within the time allowed
- **THEN** the keyword fails, and afterwards no process of the application is running

#### Scenario: Browser cannot take the application over
- **WHEN** the Browser library cannot take over the started application
- **THEN** the keyword fails with an error that names the cause, and afterwards no process of the application is running

#### Scenario: Application ends during the start
- **WHEN** the executable ends before the application has answered, for example because a system library is missing
- **THEN** the keyword fails with an error that shows the output and the exit code of the executable, an application that was already open keeps working, and the next start works

#### Scenario: Application does not answer in time
- **WHEN** the time allowed runs out before the application has answered, for example because it was built with the Electron fuse `EnableNodeCliInspectArguments` switched off
- **THEN** the keyword fails with a timeout error, afterwards no process of the application is running, an application that was already open keeps working, and the next start works
