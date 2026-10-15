---
title: VS Code forks
description: Test extensions in VSCodium and other VS Code forks.
sidebar:
  order: 9
---

Forks of VS Code, such as VSCodium, start like VS Code, from the fork's executable:

```robotframework
Start VS Code    /opt/vscodium/codium    ${EXECDIR}/tests/workspace    extension_development_path=${EXECDIR}
```

- `@vscode/test-electron` downloads only Microsoft's VS Code builds. Install or unpack a fork yourself, and point a variable such as `VSCODE_EXECUTABLE` to it.
- `Execute VS Code CLI Command` on an instance of the fork, or with the fork's `executable`, runs the fork's own command-line script, which the library finds through `applicationName` in the fork's `product.json`. Extensions it installs come from the fork's own extension gallery. VSCodium, for example, uses Open VSX, so extensions that exist only in Microsoft's Marketplace are not available there.
- Locators that a project uses for the workbench may differ between VS Code and a fork, like between VS Code versions.

## Tried so far

- **VSCodium** 1.135 passes the library's own VS Code tests, except that it writes no log files to `user-data/logs`.
- **Cursor** has not been tried yet. It ships as an AppImage, which has to be extracted first. If Cursor's Electron build switches off the Node.js inspector (Electron fuse `EnableNodeCliInspectArguments`), Playwright cannot attach to it.
