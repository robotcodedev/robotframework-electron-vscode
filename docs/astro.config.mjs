// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
// Robot Framework grammars copied from RobotCode (syntaxes/); Shiki has none. Copy them again when RobotCode's
// grammars change. Examples with sections use `robotframework`, examples that are only steps `robotframework-repl`.
import robotframework from './grammars/robotframework.tmLanguage.json' with { type: 'json' };
import robotframeworkRepl from './grammars/robotframework-repl.tmLanguage.json' with { type: 'json' };

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
			customCss: ['./src/styles/custom.css'],
			expressiveCode: {
				shiki: {
					// TypeScript's type of the JSON grammars does not fit Shiki's type, but Shiki reads them.
					langs: /** @type {any[]} */ ([
						{ ...robotframework, name: 'robotframework', aliases: ['robot'] },
						{ ...robotframeworkRepl, name: 'robotframework-repl', aliases: ['robot-repl'] },
					]),
				},
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
