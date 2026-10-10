# Design

## Context

See proposal.md for motivation and the spec deltas for the requirements. Findings from 2026-10-10, with Robot Framework 7.5 and Browser 20.6:
- **Introduction:** Libdoc takes it from the class docstring. The libraries set it to their own paragraph followed by the complete `Browser.__doc__`.
- **Import documentation:** robotlibcore builds it from `self.__init__`, which both libraries inherited from Browser.
- **Links:** Browser keywords link to the sections `Browser, Context and Page` (13 times), `Assertions` (10), `Finding elements` (8) and `Implicit waiting` (1), and Browser's types link to others such as `Automatic page and context closing`. Without these sections, the links break, and the operator table of `Assertions` is needed anyway.
- **Robot Framework 7.5:** Libdoc parses `Args:` (also `Arguments:`, `Parameters:`), `Returns:` and `Raises:` sections in Google style, also with bold formatting such as `*Arguments:*`, and items like ``- ``name``: text``. It moves them out of the text and shows them with the arguments, the return type and the exceptions. Browser's import documentation therefore shows only its first sentence as text, and the descriptions with the arguments.

## Goals / Non-Goals

**Goals:**
- Documentation that reads as the library's own, from the first line on.
- Browser's argument descriptions and the sections its keywords link to, kept up to date with Browser.
- The Robot Framework 7.5 sections for the library's own keywords.

**Non-Goals:**
- Markdown as documentation format. The libraries stay with Robot Framework's own format, like Browser.
- Changing Browser's keyword documentation.

## Decisions

- **Browser's parts are cut from Browser's own documentation at runtime.** `Electron/_docs.py` returns `Browser.__doc__` from the section `Browser, Context and Page` on and the import documentation from `*Arguments:*` on. Both libraries use it, so a new Browser release brings its current text. If a marker disappears, the import fails, and the libdoc tests catch it.
- **The import documentation through a wrapped `__init__`.** `__init__` wraps Browser's with `functools.wraps` and gets its own docstring. `inspect.signature` and `typing.get_type_hints` follow `__wrapped__`, so Libdoc shows Browser's arguments with their types and defaults, and new Browser arguments appear without a change here. `VSCode.__init__` wraps `Electron.__init__`. Overriding `get_keyword_documentation` was the alternative; the docstring also shows in Python's `help()` and in editors.
- **All import arguments of Browser.** A library that contains every Browser keyword is configured like Browser. Some arguments matter less for applications, such as `external_browser_executable`, but none is removed.
- **Bold section headers like Browser's.** The keywords use `*Returns:*` and `*Raises:*` next to their existing `*Arguments:*`, which Robot Framework 7.5 parses and older versions show as ordinary text.

## Risks / Trade-offs

- [`functools.wraps` copies Browser's `__qualname__` and `__module__` to the wrapper] → Only introspection that reads these names sees Browser's; Libdoc and robotlibcore do not.
- [Older Robot Framework versions show the sections as text] → They still read correctly, as Browser's `*Arguments:*` does.
