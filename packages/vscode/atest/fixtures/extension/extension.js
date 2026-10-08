// Fixture extension for the acceptance tests of the VSCode library.
const vscode = require('vscode');

function activate(context) {
    context.subscriptions.push(
        vscode.commands.registerCommand('robotTest.sayHello', () => {
            vscode.window.showInformationMessage('Hello Robot');
        }),
    );
}

function deactivate() {}

module.exports = { activate, deactivate };
