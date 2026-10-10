# Proposal

## Why

The library documentation of `Electron` and `VSCode` showed a short paragraph of their own and then the Browser library's complete introduction, including Browser's own opening text. The import documentation was Browser's ("Browser library can be taken into use with optional arguments"). Robot Framework 7.5 also added documentation sections in Google style: Libdoc now shows argument, return value and exception documentation along with the arguments, the return type and the exceptions. Our keywords document their arguments that way already, through `*Arguments:*`, but their return values and exceptions only as prose or not at all.

## What Changes

- Each library gets its own introduction with its own sections: starting an application, windows and pages, closing, and recording for `Electron`; opening VS Code, the workbench, closing, recording and the helper library for `VSCode`. The Browser library's sections that Browser keywords link to follow, such as `Browser, Context and Page` and `Assertions`, without Browser's opening text.
- Each library gets its own import documentation: an `__init__` that wraps Browser's with `functools.wraps`, so that Libdoc keeps Browser's arguments, types and defaults, with a docstring of its own followed by Browser's argument descriptions.
- The library's own keywords document their return values in a `*Returns:*` section and their exceptions in a `*Raises:*` section, and every argument is documented.
- The documentation stays in Robot Framework's own format, not Markdown, like the Browser library's.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: the library documentation has its own introduction, import documentation and keyword sections.
- `vscode-launch`: the same for the `VSCode` library.

## Impact

- `packages/electron/src/Electron/__init__.py`, a new `packages/electron/src/Electron/_docs.py`, `packages/electron/src/Electron/Helper.py`, `packages/vscode/src/VSCode/__init__.py` and `packages/vscode/src/VSCode/Helper.py`.
- Libdoc tests in both packages.
- The keyword reference of the documentation site, once it is generated from Libdoc.
