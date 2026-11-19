import * as vscode from 'vscode';
import * as path from 'node:path';
import { access } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { LanguageClient, LanguageClientOptions, ServerOptions, InitializeParams } from 'vscode-languageclient/node';

type Session = { client: LanguageClient; disposables: vscode.Disposable[] };
const sessions = new Map<string, Session>();
let queue: Promise<void> = Promise.resolve();
let stopping = false;

function snapshot(folder?: vscode.WorkspaceFolder) {
  const config = vscode.workspace.getConfiguration('fleurdelys', folder?.uri);
  return { fleurdelys: {
    enableCMakeAnnotations: config.get<boolean>('enableCMakeAnnotations', false),
    additionalAnnotations: config.get<string[]>('additionalAnnotations', []),
    expandEnvVariable: config.get<boolean>('expandEnvVariable', false),
  } };
}

function owner(document: vscode.TextDocument): vscode.WorkspaceFolder | undefined {
  return vscode.workspace.getWorkspaceFolder(document.uri);
}

function schedule(action: () => Promise<void>) {
  queue = queue.then(action).catch(error => {
    void vscode.window.showErrorMessage(`Fleurdelys: ${error instanceof Error ? error.message : String(error)}`);
  });
}

async function stopAll() {
  const current = [...sessions.values()];
  sessions.clear();
  await Promise.all(current.map(async session => {
    session.disposables.forEach(item => item.dispose());
    await session.client.dispose();
  }));
}

async function ensureClient(context: vscode.ExtensionContext, document: vscode.TextDocument) {
  if (stopping || document.languageId !== 'cmake' || !['file', 'untitled'].includes(document.uri.scheme)) return;
  const folder = owner(document);
  const key = folder?.uri.toString() ?? 'loose-files';
  if (sessions.has(key)) return;
  const config = vscode.workspace.getConfiguration('fleurdelys', folder?.uri);
  const override = config.get<string>('serverPath', '').trim();
  const command = override ? (path.isAbsolute(override) ? override : folder ? path.resolve(folder.uri.fsPath, override) : override)
    : context.asAbsolutePath(path.join('server', process.platform === 'win32' ? 'fleurdelys.exe' : 'fleurdelys'));
  if (!override) {
    try { await access(command); } catch { throw new Error('Bundled server is missing. Install the VSIX for this platform or set fleurdelys.serverPath.'); }
  }
  const server: ServerOptions = () => new Promise((resolve, reject) => {
    const child = spawn(command, [], { cwd: folder?.uri.fsPath, windowsHide: true, shell: false });
    child.once('error', reject);
    child.once('spawn', () => resolve(child));
  });
  const belongsHere = (doc: vscode.TextDocument) => (owner(doc)?.uri.toString() ?? 'loose-files') === key;
  const fileKey = (value: vscode.Uri) => process.platform === 'win32' ? value.fsPath.toLowerCase() : value.fsPath;
  const dependencyFiles = new Set<string>();
  const syncsHere = (doc: vscode.TextDocument) => belongsHere(doc) || dependencyFiles.has(fileKey(doc.uri));
  const options: LanguageClientOptions = {
    documentSelector: [{ language: 'cmake', scheme: 'file' }, { language: 'cmake', scheme: 'untitled' }],
    workspaceFolder: folder,
    initializationOptions: { ...snapshot(folder), fleurdelysWatchDependencies: true },
    middleware: {
      didOpen: async (doc, next) => { if (syncsHere(doc)) await next(doc); },
      didChange: async (event, next) => { if (syncsHere(event.document)) await next(event); },
      didClose: async (doc, next) => { if (syncsHere(doc)) await next(doc); },
      didSave: async (doc, next) => { if (syncsHere(doc)) await next(doc); },
      provideCompletionItem: (doc, pos, ctx, token, next) => belongsHere(doc) ? next(doc, pos, ctx, token) : null,
      provideHover: (doc, pos, token, next) => belongsHere(doc) ? next(doc, pos, token) : null,
      provideDefinition: (doc, pos, token, next) => belongsHere(doc) ? next(doc, pos, token) : null,
      provideSignatureHelp: (doc, pos, ctx, token, next) => belongsHere(doc) ? next(doc, pos, ctx, token) : null,
    },
  };
  class FolderClient extends LanguageClient {
    protected fillInitializeParams(params: InitializeParams): void {
      super.fillInitializeParams(params);
      params.rootUri = folder?.uri.toString() ?? null;
      params.rootPath = folder?.uri.fsPath ?? null;
      params.workspaceFolders = folder ? [{ uri: folder.uri.toString(), name: folder.name }] : null;
    }
  }
  const client = new FolderClient('fleurdelys', `Fleurdelys (${folder?.name ?? 'loose files'})`, server, options);
  const disposables: vscode.Disposable[] = [];
  const watched = new Set<string>();
  disposables.push(client.onNotification('fleurdelys/watchDependency', (params: { uri: string }) => {
    if (typeof params?.uri !== 'string' || watched.has(params.uri)) return;
    const uri = vscode.Uri.parse(params.uri);
    if (uri.scheme !== 'file') return;
    watched.add(params.uri);
    dependencyFiles.add(fileKey(uri));
    const open = vscode.workspace.textDocuments.find(doc => fileKey(doc.uri) === fileKey(uri));
    if (open && client.isRunning()) {
      void client.sendNotification('textDocument/didOpen', { textDocument: {
        uri: open.uri.toString(), languageId: open.languageId, version: open.version, text: open.getText(),
      } });
    }
    const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(vscode.Uri.file(path.dirname(uri.fsPath)), '*'));
    const forward = (changed: vscode.Uri, type: number) => {
      if (fileKey(changed) === fileKey(uri) && client.isRunning()) {
        void client.sendNotification('workspace/didChangeWatchedFiles', { changes: [{ uri: changed.toString(), type }] });
      }
    };
    disposables.push(watcher, watcher.onDidCreate(uri => forward(uri, 1)), watcher.onDidChange(uri => forward(uri, 2)), watcher.onDidDelete(uri => forward(uri, 3)));
  }));
  sessions.set(key, { client, disposables });
  try { await client.start(); } catch (error) {
    sessions.delete(key);
    disposables.forEach(item => item.dispose());
    await client.dispose();
    throw error;
  }
}

export async function activate(context: vscode.ExtensionContext) {
  stopping = false;
  const startOpenDocuments = async () => {
    for (const doc of vscode.workspace.textDocuments) await ensureClient(context, doc);
  };
  const restart = async () => { await stopAll(); await startOpenDocuments(); };
  context.subscriptions.push(
    vscode.commands.registerCommand('fleurdelys.restartServer', () => { schedule(restart); return queue; }),
    vscode.workspace.onDidOpenTextDocument(doc => schedule(() => ensureClient(context, doc))),
    vscode.workspace.onDidChangeWorkspaceFolders(() => schedule(restart)),
    vscode.workspace.onDidChangeConfiguration(event => {
      if (!event.affectsConfiguration('fleurdelys')) return;
      schedule(async () => {
        if (event.affectsConfiguration('fleurdelys.serverPath')) { await restart(); return; }
        for (const [key, session] of sessions) {
          const folder = vscode.workspace.workspaceFolders?.find(item => item.uri.toString() === key);
          await session.client.sendNotification('workspace/didChangeConfiguration', { settings: snapshot(folder) });
        }
      });
    }),
  );
  await startOpenDocuments();
}

export async function deactivate() {
  stopping = true;
  await queue;
  await stopAll();
}
