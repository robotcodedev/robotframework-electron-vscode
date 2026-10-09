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
			expressiveCode: {
				shiki: { langs: [{ ...robotframework, name: 'robotframework', aliases: ['robot'] }] },
			},
			sidebar: [
				{ label: 'Getting Started', items: [{ autogenerate: { directory: 'getting-started' } }] },
				{ label: 'Guides', items: [{ autogenerate: { directory: 'guides' } }] },
				{ label: 'Reference', items: [{ autogenerate: { directory: 'reference' } }] },
			],
		}),
	],
});
