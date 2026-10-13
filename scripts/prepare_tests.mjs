// Prepares the VS Code and Electron builds that the acceptance tests run against, in the repository's .cache/,
// and prints their executables. `npm run prepare-tests -- insiders` also prepares the newest VS Code Insiders.
// robot.toml and its profiles point to these executables; keep the versions here and there the same.
import fs from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

import { downloadAndUnzipVSCode } from '@vscode/test-electron';

const root = path.resolve(import.meta.dirname, '..');
const require = createRequire(import.meta.url);

// @vscode/test-electron creates only the last folder of its cache path.
const vscodeCache = path.join(root, '.cache', 'vscode');
fs.mkdirSync(vscodeCache, { recursive: true });
for (const version of ['1.141.0', ...process.argv.slice(2)]) {
    const executable = await downloadAndUnzipVSCode({ version, cachePath: vscodeCache });
    console.log(`VS Code ${version}: ${executable}`);
}

// The Electron packages download their binary on the first require, into this folder instead of the user's cache.
process.env.electron_config_cache = path.join(root, '.cache', 'electron');
fs.mkdirSync(process.env.electron_config_cache, { recursive: true });
for (const name of ['electron', 'electron-previous']) {
    console.log(`${name}: ${require(name)}`);
}
