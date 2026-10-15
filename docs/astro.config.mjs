// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
// Robot Framework grammar copied from RobotCode (syntaxes/robotframework.tmLanguage.json);
// Shiki has none. Copy it again when RobotCode's grammar changes.
import robotframework from './grammars/robotframework.tmLanguage.json' with { type: 'json' };

// The site is published on GitHub Pages of robotcodedev/robotframework-electron-vscode.
// The READMEs link to the same URL.
const SITE = 'https://robotcodedev.github.io';
const BASE = '/robotframework-electron-vscode/';

export default defineConfig({
	site: SITE,
	base: BASE,
	trailingSlash: 'always',
	integrations: [
		starlight({
			title: 'Robot Framework Electron & VS Code',
			routeMiddleware: './src/routeData.ts',
			expressiveCode: {
				shiki: { langs: [{ ...robotframework, name: 'robotframework', aliases: ['robot'] }] },
			},
			// A section per library and one for the test environment. The Electron section covers what both
			// libraries share; the VS Code section adds what is specific to VS Code.
			sidebar: [
				{ label: 'Electron', items: [{ autogenerate: { directory: 'electron' } }] },
				{ label: 'VS Code', items: [{ autogenerate: { directory: 'vscode' } }] },
				{ label: 'Running tests', items: [{ autogenerate: { directory: 'running' } }] },
			],
		}),
	],
});
