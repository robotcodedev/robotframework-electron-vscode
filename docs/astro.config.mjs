// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
// Robot Framework grammar copied from RobotCode (syntaxes/robotframework.tmLanguage.json);
// Shiki has none. Copy it again when RobotCode's grammar changes.
import robotframework from './grammars/robotframework.tmLanguage.json' with { type: 'json' };

// Placeholders until the repository's location is decided. On GitHub Pages,
// SITE becomes https://<owner>.github.io and BASE becomes /<repository>/.
// The READMEs link to the site with the same placeholder URL.
const SITE = 'https://example.github.io';
const BASE = '/';

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
