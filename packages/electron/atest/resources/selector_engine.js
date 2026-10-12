// A custom selector engine for the acceptance tests: `tag=h1` finds elements by tag name.
// It is registered through a JavaScript extension, as a project would do it.

async function fixtureRegisterTagEngine(playwright) {
    try {
        await playwright.selectors.register('tag', () => ({
            query: (root, selector) => root.querySelector(selector),
            queryAll: (root, selector) => Array.from(root.querySelectorAll(selector)),
        }));
    } catch (error) {
        // Browser's Node process lives for the whole run, and an engine can be registered only once.
        if (!String(error.message).includes('already registered')) throw error;
    }
}

exports.__esModule = true;
exports.fixtureRegisterTagEngine = fixtureRegisterTagEngine;
