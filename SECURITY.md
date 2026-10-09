# Security Policy

> This policy applies to all parts of the **Robot Framework Electron & VS Code** project: the Python packages `robotframework-electron` and `robotframework-vscode`, the documentation site, and the example project.

## Reporting a Vulnerability

**Please do not open public issues for security problems.**

### Preferred Reporting Methods

**Primary:** Use GitHub's **Private Vulnerability Reporting** on this repository:
* Go to the repository's **Security** tab → **Report a vulnerability**
* Creates a private, secure thread with the maintainers
* Automatically tracks communication and resolution

**Alternative:** Email [support@robotcode.io](mailto:support@robotcode.io)
* This address is actively monitored by the maintainers
* PGP encryption available upon request
* If this address is unavailable, contact the maintainer via the email listed in the latest release notes

### Required Information

When reporting, please include:

* **Component**: Affected package and version (`robotframework-electron`, `robotframework-vscode`), the documentation site, or the example project
* **Description**: Clear description of the vulnerability and attack vector
* **Impact**: Potential impact and your severity assessment (CVSS score welcome)
* **Reproduction**: Steps to reproduce, proof of concept, or minimal repro project
* **Environment**: OS, display setup, Python, Robot Framework and Browser library versions, and the Electron application or VS Code version under test
* **Mitigations**: Any known workarounds or temporary fixes

We also accept **supply-chain reports** (malicious dependencies, typosquats, unsafe defaults) affecting the project.

## Our Response Commitments

### Standard Timeline
* **Triage acknowledgement:** within **3 business days**
* **Initial assessment:** within **7 days** we'll confirm scope, assign severity (CVSS score), and provide timeline for resolution
* **Regular updates:** every **14 days** on progress for confirmed vulnerabilities
* **Fix target:** within **90 days** for high/critical issues, next regular release for medium/low severity issues

### Critical Vulnerability Fast-Track
For **critical vulnerabilities** (CVSS 9.0+, active exploitation, or RCE):
* **Acknowledgement:** within **24 hours**
* **Assessment:** within **48 hours**
* **Emergency release:** within **14 days** when feasible

### Coordinated Disclosure
* **Standard disclosure timeline:** 90 days after fix release, or by mutual agreement
* We'll coordinate with you on public disclosure timing
* Please **do not disclose** details publicly until we publish an advisory/release with a fix
* We may request extended timeline for complex fixes requiring upstream coordination

## Severity Classification

We use **CVSS v4.0** (v3.1 also accepted) with the following guidelines:

| Severity | CVSS Score | Examples |
|----------|------------|----------|
| **Critical** | 9.0-10.0 | Remote Code Execution, Privilege Escalation without user interaction |
| **High** | 7.0-8.9 | RCE requiring user interaction, Authentication bypass, Sensitive data exposure |
| **Medium** | 4.0-6.9 | Local privilege escalation, Limited information disclosure, DoS |
| **Low** | 0.1-3.9 | Minor information leakage, UI spoofing |

## Scope

### In Scope ✅
* The `robotframework-electron` and `robotframework-vscode` packages
* How they download VS Code, install extensions, and start Electron applications and VS Code instances
* Documentation site content and example code that could cause vulnerabilities when followed
* Supply chain issues (malicious dependencies, typosquatting)
* Configuration defaults that create security risks

### Out of Scope ❌
* **Browser library**, **Playwright**, **Electron**, **VS Code** and **Robot Framework** themselves (report to the respective project)
* Extensions and Electron applications under test, and extensions installed into the tested VS Code
* Third-party dependencies unless there's a vulnerable usage pattern within this project
* Issues requiring unrealistic attack scenarios (e.g., running arbitrary untrusted Robot tests in production without sandboxing)
* Social engineering attacks against project maintainers
* Physical access scenarios

## Supported Versions

**Project Versions:**
* **Latest release** of both packages receives full security support
* **Older versions** are out of security support while the project is at version 0.x

**Dependencies & Requirements:**
* **Minimum requirements**: Python 3.10+ and the Browser library version declared by the packages
* **Dependency security**: Python, Robot Framework, the Browser library, Playwright, Electron and VS Code have their own security policies and support lifecycles
* **Out of scope**: Security issues in these dependencies should be reported to their respective projects
* **Compatibility**: We may drop support for end-of-life Python, Robot Framework, Electron or VS Code versions without prior notice

## CVE Assignment & Advisories

* We assess severity using **CVSS v4.0** (Base score + Threat/Environmental when applicable)
* **CVEs** will be requested for vulnerabilities with CVSS ≥ 7.0 or significant user impact
* **GitHub Security Advisories** will be published describing impact, affected versions, and remediation
* All advisories include the **CVSS vector** and detailed mitigation steps

## Recognition & Responsible Disclosure

### Credit Policy
Unless you request otherwise, we will:
* Credit reporters by name or handle in security advisories
* Mention contributors in release notes

### Responsible Disclosure Incentives
While we don't offer monetary rewards, we provide:
* Public recognition and attribution
* Direct communication channel with maintainers for future research
* Conference speaking opportunity referrals when appropriate

## Safe Research Guidelines

✅ **Encouraged:**
* Testing in isolated environments
* Responsible proof-of-concept development
* Coordinating with our team before public research

❌ **Prohibited:**
* Data destruction, exfiltration, or privacy violations
* Testing against production systems of other users
* Spam, DoS, or aggressive automated scanning
* Social engineering attempts against maintainers or users

## Security Hardening for Users

### Test Environment
* **Application privileges**: The libraries start Electron applications and VS Code with the privileges of the test run, and the extension under test runs with them too; run tests as a dedicated user, in a container or virtual machine
* **Isolated instances**: VS Code instances get their own user data and extensions directories, so tests do not touch your own VS Code, but they still share your file system and network
* **Extensions**: Install only extensions you trust into the tested VS Code; they come from the Marketplace, or from the gallery of the fork you test
* **Versions**: Pin the VS Code and Electron versions you test against, and update them deliberately

### Test Code
* **Code Review**: Treat Robot Framework test suites as code - review before execution
* **Sandboxing**: Run untrusted tests in containerized or sandboxed environments
* **Access Control**: Limit file system access for automated test execution

### Updates
* Keep Python, Robot Framework, the Browser library and these packages up to date
* Subscribe to GitHub security advisories for notifications
* Monitor release notes for security-related changes

## Legal

This security policy is subject to change. The current version is the one in the repository's default branch.

By participating in our security research program, you agree to:
* Follow responsible disclosure practices
* Comply with applicable laws and regulations
* Respect user privacy and data protection requirements

---

**Thank you for helping keep the project and its users secure!**

*Last updated: 2026-10-10*
*Version: 1.0*
