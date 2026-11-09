import * as vscode from 'vscode';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

let mcpClient: Client | undefined;

export async function activate(context: vscode.ExtensionContext) {
    console.log('Windows MCP Extension is now active!');

    const getWorkspaceRoot = (): string | undefined => {
        return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    };

    const resolveServerCommand = (): { command: string; args: string[] } => {
        const workspaceRoot = getWorkspaceRoot();
        const repoRoot = workspaceRoot && path.basename(workspaceRoot) === 'vscode-extension'
            ? path.dirname(workspaceRoot)
            : workspaceRoot;

        if (repoRoot) {
            const bundledExe = path.join(repoRoot, 'venv', 'Scripts', 'windows-server-mcp.exe');
            if (fs.existsSync(bundledExe)) {
                return { command: bundledExe, args: [] };
            }

            const bundledPython = path.join(repoRoot, 'venv', 'Scripts', 'python.exe');
            if (fs.existsSync(bundledPython)) {
                return {
                    command: bundledPython,
                    args: ['-m', 'windows_server_mcp.server']
                };
            }
        }

        return { command: 'windows-server-mcp', args: [] };
    };

    const startServer = async () => {
        try {
            const { command, args } = resolveServerCommand();
            const transport = new StdioClientTransport({
                command,
                args
            });

            mcpClient = new Client(
                {
                    name: 'vscode-windows-server-mcp-client',
                    version: '1.0.0'
                },
                {
                    capabilities: {}
                }
            );

            await mcpClient.connect(transport);
            vscode.window.showInformationMessage(`Windows MCP Server connected successfully via ${command}.`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start Windows MCP Server: ${error}`);
        }
    };

    const restartCommand = vscode.commands.registerCommand('windows-server-mcp.restartServer', async () => {
        if (mcpClient) {
            await mcpClient.close();
        }
        await startServer();
    });

    context.subscriptions.push(restartCommand);

    // Start server on activation
    await startServer();
}

export async function deactivate() {
    if (mcpClient) {
        await mcpClient.close();
    }
}
