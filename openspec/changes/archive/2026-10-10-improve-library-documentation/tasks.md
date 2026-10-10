# Tasks

## 1. Introduction and import documentation

- [x] 1.1 Add `Electron/_docs.py`, which cuts the Browser sections and the import argument descriptions out of Browser's documentation.
- [x] 1.2 Write the `Electron` library's own introduction and import documentation, with an `__init__` that wraps Browser's. Do the same for `VSCode`, whose `__init__` wraps Electron's.
- [x] 1.3 Add libdoc tests for both libraries: the introduction starts with the library's own text, contains `Assertions` and not Browser's opening text, and the import documentation starts with the library's own text and has Browser's arguments with their descriptions. Verify that `uv run pytest` passes.

## 2. Keyword documentation

- [x] 2.1 Document return values in a `*Returns:*` section and exceptions in a `*Raises:*` section in the keywords of `Electron`, `Electron.Helper`, `VSCode` and `VSCode.Helper`, and document the argument `browser` of `Close VS Code`.
- [x] 2.2 Add a libdoc test for each package: every argument of the own keywords has a description, keywords with a return value document it, and keywords that raise for invalid input document it. Verify that `uv run pytest` passes and that `uv run robotcode -r . analyze code` reports no errors or warnings.
