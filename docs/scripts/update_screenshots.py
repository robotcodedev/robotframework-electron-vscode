"""Regenerate the documentation's screenshots from the example project.

Runs the tests of examples/vscode-extension with its `xvfb` profile, hidden on a Full HD screen
with a window manager, and copies the screenshots that the tests take to
docs/src/assets/screenshots/. Run it from the repository root:

    uv run python docs/scripts/update_screenshots.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "vscode-extension"
TARGET = ROOT / "docs" / "src" / "assets" / "screenshots"
SCREENSHOTS = ["notification", "quick-pick", "webview", "editor", "terminal", "python-run"]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="screenshots-") as output:
        command = ["robotcode", "-r", str(EXAMPLE), "-p", "xvfb", "robot", "--outputdir", output]
        if subprocess.run(command, cwd=ROOT, check=False).returncode != 0:
            print("The example's tests failed; the screenshots were not updated.", file=sys.stderr)
            return 1
        TARGET.mkdir(parents=True, exist_ok=True)
        for name in SCREENSHOTS:
            shutil.copyfile(Path(output, "browser", "screenshot", f"{name}.png"), TARGET / f"{name}.png")
            print(f"Updated {(TARGET / name).relative_to(ROOT)}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
