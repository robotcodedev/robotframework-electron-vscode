# Spec Delta

## ADDED Requirements

### Requirement: Bypass the Content Security Policy
`Open VS Code` SHALL accept `bypass_csp` and start VS Code with the policy of its pages bypassed as `New Electron Application` does.

#### Scenario: Script added to the workbench
- **WHEN** a test opens VS Code with `bypass_csp=True` and adds a script element with inline code to the workbench through `Evaluate JavaScript`
- **THEN** the script runs, although the workbench requires Trusted Types for scripts
