# Tasks

Before starting: `fix-electron-first-window` is archived.

## 1. Keywords

- [x] 1.1 Hide the keywords of `HIDDEN_KEYWORDS` in `Electron` by overriding `get_keyword_names`. Add unit tests: the hidden keywords are missing from `Electron` and `VSCode`, every other Browser keyword is there, every hidden name is a method of Browser, and hiding also works with `language=`. Verify that `uv run pytest` passes.
- [x] 1.2 Add `Switch Electron Application`, `Get Electron Application Ids` and `Get Electron Application Catalog`. Rename `browser=` to `application=` and `instance=`, and return the application id and the page details from `New Electron Application` and `Open VS Code`. Update the keyword documentation and the unit tests. Verify that `uv run pytest` passes.
- [x] 1.3 Update the acceptance tests of both packages: teardowns, return values, the tests with a web browser beside an application, `main_process.robot` and `limitations.robot`. Add the tests for several applications and for `Browser` imported beside `Electron`. Verify that all acceptance tests pass with `-p xvfb` and that `analyze code` reports no errors.
- [x] 1.4 Add the storage tests to `context_state.robot`, the endpoint `/slow` to the fixture's web server and the `Cancel Download` test to `dialogs_and_downloads.robot`. Verify that the Electron acceptance tests pass.

## 2. Documentation

- [x] 2.1 Write `Electron`'s own introduction and import documentation with the shared sections and the comparison in `_docs.py`, and update the Libdoc unit tests. Verify that `uv run pytest` passes and that the generated documentation has no unresolved links beyond Browser's and the hidden keywords.
- [x] 2.2 Write `VSCode`'s own introduction and import documentation with the shared sections, and update its Libdoc unit tests. Verify as in 2.1.
- [x] 2.3 Add the comparison to the guide on Browser keywords, update its overview, its table of keywords that fail and the note on `Cancel Download`, and replace the hidden keywords in the getting-started pages. Verify that `npm run build` in `docs/` succeeds and that the internal links resolve.

## 3. Check

- [x] 3.1 Run all acceptance tests of both packages with `-p xvfb`, the VS Code example, `uv run pytest` and `uv run pre-commit run --all-files`.
