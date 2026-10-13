"""Build hook that packs the helper extension into ``src/VSCode/extension-host.vsix`` with ``@vscode/vsce``."""

import shutil
import subprocess
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

VSIX = Path("src/VSCode/extension-host.vsix")


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        # An editable install loads the helper's folder; only the distributions need the .vsix.
        if version == "editable":
            return
        root = Path(self.root)
        # In the source tree, pack it anew, so that a changed helper or a new version never ships an old .vsix.
        if (root / "package.json").is_file():
            npm = shutil.which("npm")
            if npm is None:
                raise RuntimeError("Packing the helper extension's .vsix needs npm from Node.js 22 or later.")
            # vsce-sign's install script downloads a signing tool that only publishing needs.
            subprocess.run([npm, "ci", "--ignore-scripts"], cwd=root, check=True)
            subprocess.run([npm, "run", "package-helper"], cwd=root, check=True)
        # An unpacked sdist has no npm files, but brings the .vsix along.
        elif not (root / VSIX).is_file():
            raise RuntimeError(f"{VSIX} is missing; build from the source tree, where npm can pack it.")
