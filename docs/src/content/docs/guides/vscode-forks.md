---
title: VS Code forks
description: Test extensions in VSCodium and other VS Code forks.
---

Forks of VS Code, such as VSCodium, run with `executable` set to the fork's executable:

```robotframework
Open VS Code    ${EXECDIR}/tests/workspace    executable=/opt/vscodium/codium    extension_development_path=${EXECDIR}
```

- `version` downloads only Microsoft's VS Code builds. For a fork, always give `executable`.
- Extensions in `extensions` are installed with the fork's own command-line script, which the library finds through `applicationName` in the fork's `product.json`. They come from the fork's own extension gallery. VSCodium, for example, uses Open VSX, so extensions that exist only in Microsoft's Marketplace are not available there.
- Locators that a project uses for the workbench may differ between VS Code and a fork, like between VS Code versions.

## Tried so far

- **VSCodium** 1.135 passes the library's own VS Code tests, except that it writes no log files to `user-data/logs`.
- **Cursor** has not been tried yet. It ships as an AppImage, which has to be extracted first. If Cursor's Electron build switches off the Node.js inspector (Electron fuse `EnableNodeCliInspectArguments`), Playwright cannot attach to it.
