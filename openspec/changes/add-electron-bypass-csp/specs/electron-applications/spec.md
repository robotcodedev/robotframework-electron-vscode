# Spec Delta

## ADDED Requirements

### Requirement: Bypass the Content Security Policy
`New Electron Application` SHALL start the application with the Content Security Policy of its pages bypassed, including Trusted Types, when `bypass_csp` is true. By default, the policy SHALL be enforced.

#### Scenario: Script added to a page with a strict policy
- **WHEN** a test starts an application whose page requires Trusted Types for scripts, with `bypass_csp=True`, and adds a script element with inline code through `Evaluate JavaScript`
- **THEN** the script runs

#### Scenario: Policy enforced by default
- **WHEN** the same test starts the application without `bypass_csp`
- **THEN** adding the script fails with an error about Trusted Types
