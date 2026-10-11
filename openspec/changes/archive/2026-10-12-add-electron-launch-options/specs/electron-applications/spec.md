# Spec Delta

## ADDED Requirements

### Requirement: Color scheme
`New Electron Application` SHALL leave the color scheme of the application's pages to the application by default, so that `prefers-color-scheme` reports what the application chose. When `color_scheme` is `light` or `dark`, the pages SHALL report that color scheme instead.

#### Scenario: Application decides the color scheme
- **WHEN** a test starts an application that switches its theme to dark, without `color_scheme`
- **THEN** its page matches `prefers-color-scheme: dark`

#### Scenario: Emulated color scheme
- **WHEN** a test starts the same application with `color_scheme=light`
- **THEN** its page matches `prefers-color-scheme: light`

### Requirement: Locale and time zone
`New Electron Application` SHALL start the application's pages with the given `locale` and `timezone_id`, which apply to the language the pages report and to their number and date formatting. Without them, the pages SHALL follow the system.

#### Scenario: Given locale and time zone
- **WHEN** a test starts an application with `locale=pt-BR` and `timezone_id=Asia/Tokyo`
- **THEN** its page reports the language `pt-BR` and the time zone `Asia/Tokyo`, and formats numbers as in Brazilian Portuguese

### Requirement: Bypass the Content Security Policy
`New Electron Application` SHALL start the application with the Content Security Policy of its pages bypassed, including Trusted Types, when `bypass_csp` is true. By default, the policy SHALL be enforced.

#### Scenario: Script added to a page with a strict policy
- **WHEN** a test starts an application whose page requires Trusted Types for scripts, with `bypass_csp=True`, and adds a script element with inline code through `Evaluate JavaScript`
- **THEN** the script runs

#### Scenario: Policy enforced by default
- **WHEN** the same test starts the application without `bypass_csp`
- **THEN** adding the script fails with an error about Trusted Types
