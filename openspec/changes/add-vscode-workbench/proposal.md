# Proposal

## Why

Once VS Code runs, tests still have to drive the workbench. Its DOM is not an API and changes with VS Code releases. Without shared keywords, every extension's test suite carries its own fragile selectors.

## What Changes

- `VSCode` gets workbench keywords for common interactions: running commands, opening files, reading and typing editor text, and handling quick picks and notifications. The scope grows with real tests, starting with what RobotCode's tests need.
- Webviews: Browser keywords can be scoped into an extension's webview, using Browser's `Set Selector Prefix` on the nested webview frames, so no separate webview keywords are needed.
- All workbench selectors live in one place and can be overridden per VS Code version:
  - commands and keybindings are preferred over DOM clicks,
  - ARIA roles and labels are preferred over CSS classes,
  - VS Code's own `test/automation` drivers serve as the reference when VS Code changes.

## Capabilities

### New Capabilities

- `vscode-workbench`: keywords for driving the VS Code workbench, including extension webviews.

### Modified Capabilities

None.

## Impact

- New code in `packages/vscode/`.
- Depends on `add-vscode-launch`.
- Selectors have to follow VS Code releases. Once CI exists, this calls for regular runs against stable, insiders and the oldest supported version.
