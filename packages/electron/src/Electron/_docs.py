"""Parts of the Browser library's documentation that the libraries built on it reuse."""

from inspect import cleandoc, getdoc

from Browser import Browser

_FIRST_BROWSER_SECTION = "= Browser, Context and Page ="
_BROWSER_ARGUMENTS = "*Arguments:*"


def browser_sections() -> str:
    """Return the Browser library's introduction from its first section on, without its opening text.

    Browser keywords link to these sections, for example to `Assertions`.
    """
    doc = cleandoc(Browser.__doc__ or "")
    return doc[doc.index(_FIRST_BROWSER_SECTION) :]


def browser_import_arguments() -> str:
    """Return the description of the Browser library's import arguments."""
    doc = getdoc(Browser.__init__) or ""
    return doc[doc.index(_BROWSER_ARGUMENTS) :]
