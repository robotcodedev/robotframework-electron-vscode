# Spec Delta

## ADDED Requirements

### Requirement: Launch options
`Open VS Code` SHALL accept `color_scheme`, `locale`, `timezone_id` and `bypass_csp` and start VS Code with them as `New Electron Application` does.

#### Scenario: Options reach the workbench
- **WHEN** a test opens VS Code with `color_scheme=dark`, `locale=pt-BR` and `timezone_id=Asia/Tokyo`
- **THEN** the workbench page matches `prefers-color-scheme: dark` and reports the language `pt-BR` and the time zone `Asia/Tokyo`

#### Scenario: Script added to the workbench
- **WHEN** a test opens VS Code with `bypass_csp=True` and adds a script element with inline code to the workbench through `Evaluate JavaScript`
- **THEN** the script runs, although the workbench requires Trusted Types for scripts
