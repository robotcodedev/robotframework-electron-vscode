# Tasks

## 1. Keyword

- [ ] 1.1 Record each instance in `Open VS Code` (browser id → executable and instance directories), and add `Install VS Code Extension    extension    browser=CURRENT` with documentation and an example. Verify with pytest that an unknown browser id fails with a message that names it, and update the boundary test to the three keywords.
- [ ] 1.2 Add a `.vsix` packing helper to `atest/resources/VSCodeFixture.py` and an acceptance test for the scenarios "Extension in a running instance" and "Isolation". Verify that `uv run pytest` and the VSCode acceptance tests pass, and that `uv run robotcode -r . analyze code` reports no errors or warnings.

## 2. Documentation

- [ ] 2.1 Mention `Install VS Code Extension` in the extensions part of `docs/src/content/docs/getting-started/vscode.md`. Verify that `npm run build` in `docs/` succeeds.
