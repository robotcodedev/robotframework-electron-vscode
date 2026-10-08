// Example extension whose Robot Framework tests are in tests/.
const vscode = require('vscode');

function activate(context) {
    context.subscriptions.push(
        vscode.commands.registerCommand('robotExample.sayHello', () => {
            vscode.window.showInformationMessage('Hello Robot');
        }),
        vscode.commands.registerCommand('robotExample.pick', async () => {
            const fruit = await vscode.window.showQuickPick(['Apple', 'Banana', 'Cherry'], {
                placeHolder: 'Pick a fruit',
            });
            if (fruit) {
                vscode.window.showInformationMessage(`You picked ${fruit}`);
            }
        }),
        vscode.commands.registerCommand('robotExample.openWebview', () => {
            const panel = vscode.window.createWebviewPanel(
                'robotExample.webview',
                'Robot Example',
                vscode.ViewColumn.One,
                { enableScripts: true },
            );
            panel.webview.html = webviewHtml();
        }),
    );
}

function webviewHtml() {
    return `<!DOCTYPE html>
<html lang="en">
<body>
    <p id="status">Not clicked</p>
    <button id="click-me">Click me</button>
    <script>
        document.getElementById('click-me').addEventListener('click', () => {
            document.getElementById('status').textContent = 'Clicked';
        });
    </script>
</body>
</html>`;
}

function deactivate() {}

module.exports = { activate, deactivate };
