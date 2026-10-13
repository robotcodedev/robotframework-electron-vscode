// Helper extension of the robotframework-vscode library. `Open VS Code` loads it as a development
// extension, and `Evaluate In Extension Host` runs functions in this window's extension host through it.
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const http = require('http');
const path = require('path');
const vscode = require('vscode');

let server;
let endpointFile;

// The path of the workspace, for the keyword's `workspace` argument: the workspace file of a
// multi-root workspace or the single folder. Empty windows and untitled workspaces have none.
function workspacePath() {
    const file = vscode.workspace.workspaceFile;
    if (file) {
        return file.scheme === 'file' ? file.fsPath : null;
    }
    const folders = vscode.workspace.workspaceFolders;
    return folders && folders.length === 1 ? folders[0].uri.fsPath : null;
}

// VS Code's id of the workspace, which the page of the window knows as well: the folder above the
// extension's workspace storage, `workspaceStorage/<workspace id>/<extension id>`. Empty windows have none.
function workspaceId(context) {
    return context.storageUri ? path.basename(path.dirname(context.storageUri.fsPath)) : null;
}

function describe(error) {
    return error instanceof Error ? { message: error.message, stack: error.stack } : { message: String(error) };
}

async function evaluate(body) {
    let result;
    try {
        const { script, arg } = JSON.parse(body);
        result = await new Function(`return (${script})`)()(vscode, arg);
    } catch (error) {
        return JSON.stringify({ error: describe(error) });
    }
    try {
        // undefined, functions and symbols have no JSON, as in JSON.stringify's arrays.
        const json = JSON.stringify(result);
        return `{"result":${json === undefined ? 'null' : json}}`;
    } catch (error) {
        const message = `The function's result cannot be serialised as JSON: ${error.message}`;
        return JSON.stringify({ error: { message } });
    }
}

function answer(response, status, text) {
    response.writeHead(status, { 'Content-Type': 'application/json' });
    response.end(text);
}

function handle(token, request, response) {
    if (request.headers.authorization !== `Bearer ${token}`) {
        request.resume();
        answer(response, 403, JSON.stringify({ error: { message: 'The request has no valid token.' } }));
    } else if (request.method === 'GET') {
        answer(response, 200, JSON.stringify({ pid: process.pid }));
    } else if (request.method === 'POST') {
        const chunks = [];
        request.on('data', (chunk) => chunks.push(chunk));
        request.on('end', () => {
            evaluate(Buffer.concat(chunks).toString('utf8')).then((text) => answer(response, 200, text));
        });
    } else {
        request.resume();
        answer(response, 405, JSON.stringify({ error: { message: `Method ${request.method} is not allowed.` } }));
    }
}

async function activate(context) {
    const token = crypto.randomBytes(32).toString('hex');
    server = http.createServer((request, response) => handle(token, request, response));
    await new Promise((resolve, reject) => {
        server.once('error', reject);
        server.listen(0, '127.0.0.1', resolve);
    });
    const directory = path.join(context.globalStorageUri.fsPath, 'hosts');
    fs.mkdirSync(directory, { recursive: true });
    endpointFile = path.join(directory, `${process.pid}.json`);
    const endpoint = {
        port: server.address().port,
        token,
        pid: process.pid,
        workspace: workspacePath(),
        workspaceId: workspaceId(context),
    };
    // Written under another name first, so that the library never reads a half-written file.
    fs.writeFileSync(`${endpointFile}.tmp`, JSON.stringify(endpoint), { mode: 0o600 });
    fs.renameSync(`${endpointFile}.tmp`, endpointFile);
}

function deactivate() {
    if (endpointFile) {
        fs.rmSync(endpointFile, { force: true });
        endpointFile = undefined;
    }
    if (server) {
        server.close();
        server = undefined;
    }
}

module.exports = { activate, deactivate };
