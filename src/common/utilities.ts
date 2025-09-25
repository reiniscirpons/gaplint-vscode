// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import * as fs from 'fs-extra';
import * as path from 'path';
import { ConfigurationScope, LogLevel, Uri, WorkspaceFolder } from 'vscode';
import { Trace } from 'vscode-jsonrpc/node';
import { getConfiguration, getWorkspaceFolders, isVirtualWorkspace } from './vscodeapi';
import { DocumentSelector } from 'vscode-languageclient';

function logLevelToTrace(logLevel: LogLevel): Trace {
    switch (logLevel) {
        case LogLevel.Error:
        case LogLevel.Warning:
        case LogLevel.Info:
            return Trace.Messages;

        case LogLevel.Debug:
        case LogLevel.Trace:
            return Trace.Verbose;

        case LogLevel.Off:
        default:
            return Trace.Off;
    }
}

export function getLSClientTraceLevel(channelLogLevel: LogLevel, globalLogLevel: LogLevel): Trace {
    if (channelLogLevel === LogLevel.Off) {
        return logLevelToTrace(globalLogLevel);
    }
    if (globalLogLevel === LogLevel.Off) {
        return logLevelToTrace(channelLogLevel);
    }
    const level = logLevelToTrace(channelLogLevel <= globalLogLevel ? channelLogLevel : globalLogLevel);
    return level;
}

export async function getProjectRoot(): Promise<WorkspaceFolder> {
    const workspaces: readonly WorkspaceFolder[] = getWorkspaceFolders();
    if (workspaces.length === 0) {
        return {
            uri: Uri.file(process.cwd()),
            name: path.basename(process.cwd()),
            index: 0,
        };
    } else if (workspaces.length === 1) {
        return workspaces[0];
    } else {
        let rootWorkspace = workspaces[0];
        let root = undefined;
        for (const w of workspaces) {
            if (await fs.pathExists(w.uri.fsPath)) {
                root = w.uri.fsPath;
                rootWorkspace = w;
                break;
            }
        }

        for (const w of workspaces) {
            if (root && root.length > w.uri.fsPath.length && (await fs.pathExists(w.uri.fsPath))) {
                root = w.uri.fsPath;
                rootWorkspace = w;
            }
        }
        return rootWorkspace;
    }
}

export function getDocumentSelector(): DocumentSelector {
    // virtual workspaces are not supported yet
    // TODO(reiniscirpons): check if we need to change this to gap
    return isVirtualWorkspace()
        ? [{ language: 'gap' }, { language: 'gaptst' }, { pattern: '*.{g,gi,gd,tst}' }]
        : [
            { scheme: 'file', language: 'gap' },
            { scheme: 'untitled', language: 'gap' },
            { scheme: 'vscode-notebook', language: 'gap' },
            { scheme: 'vscode-notebook-cell', language: 'gap' },
            { scheme: 'file', language: 'gaptst' },
            { scheme: 'untitled', language: 'gaptst' },
            { scheme: 'vscode-notebook', language: 'gaptst' },
            { scheme: 'vscode-notebook-cell', language: 'gaptst' },
            { scheme: 'file', pattern: '*.{g,gi,gd,tst}' },
            { scheme: 'untitled', pattern: '*.{g,gi,gd,tst}' },
            { scheme: 'vscode-notebook', pattern: '*.{g,gi,gd,tst}' },
            { scheme: 'vscode-notebook-cell', pattern: '*.{g,gi,gd,tst}' },
        ];
}

export function getInterpreterFromSetting(namespace: string, scope?: ConfigurationScope) {
    const config = getConfiguration(namespace, scope);
    return config.get<string[]>('interpreter');
}
