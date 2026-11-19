const vscode = require('vscode');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');

async function eventually(action, description) {
  const deadline = Date.now() + 25000;
  let last;
  while (Date.now() < deadline) {
    try { return await action(); } catch (error) { last = error; }
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  throw new Error(`${description}: ${last?.stack}`);
}
exports.run = async () => {
  const root = process.env.FLEURDELYS_EDITOR_TEST_ROOT;
  async function open(folder, filename, text) {
    const uri = vscode.Uri.file(path.join(root, folder, filename));
    await fs.writeFile(uri.fsPath, text);
    const doc = await vscode.workspace.openTextDocument(uri);
    await vscode.window.showTextDocument(doc);
    assert.equal(doc.languageId, 'cmake');
    return doc;
  }
  const one = await open('one', 'CMakeLists.txt', 'message(${PROJECT_');
  const extension = vscode.extensions.getExtension('MikuAuahDark.fleurdelys');
  assert.ok(extension);
  await extension.activate();
  const labels = async doc => {
    const pos = doc.lineAt(doc.lineCount - 1).range.end;
    const list = await vscode.commands.executeCommand('vscode.executeCompletionItemProvider', doc.uri, pos);
    return list?.items.map(item => typeof item.label === 'string' ? item.label : item.label.label) ?? [];
  };
  await eventually(async () => assert.ok((await labels(one)).includes('PROJECT_NAME')), 'CMake annotations enabled');
  const two = await open('two', 'test.cmake', 'message(${PROJECT_');
  await eventually(async () => assert.ok((await labels(two)).includes('CMAKE_CURRENT_LIST_DIR')), 'second folder server ready');
  assert.ok(!(await labels(two)).includes('PROJECT_NAME'), 'folder settings must remain isolated');
  const external = await open('one', 'external.cmake', 'external_probe(');
  await eventually(async () => assert.ok((await labels(external)).includes('FIRST')), 'external annotation loaded');
  await fs.writeFile(path.join(root, 'external', 'nested.cmake'), '## function(external_probe SECOND)\n');
  await eventually(async () => {
    const items = await labels(external);
    assert.ok(items.includes('SECOND'));
    assert.ok(!items.includes('FIRST'));
  }, 'external transitive include watcher');
  const packDoc = await vscode.workspace.openTextDocument(vscode.Uri.file(path.join(root, 'external', 'nested.cmake')));
  const edit = new vscode.WorkspaceEdit();
  edit.replace(packDoc.uri, new vscode.Range(packDoc.positionAt(0), packDoc.positionAt(packDoc.getText().length)), '## function(external_probe UNSAVED)\n');
  await vscode.workspace.applyEdit(edit);
  await eventually(async () => assert.ok((await labels(external)).includes('UNSAVED')), 'unsaved annotation buffer');
  const navigation = await open('one', 'navigate.cmake', 'message(${PROJECT_NAME})\n');
  await eventually(async () => {
    const hover = await vscode.commands.executeCommand('vscode.executeHoverProvider', navigation.uri, new vscode.Position(0, 15));
    assert.ok(hover.length);
    const definitions = await vscode.commands.executeCommand('vscode.executeDefinitionProvider', navigation.uri, new vscode.Position(0, 15));
    assert.ok(definitions.length);
  }, 'hover and definition');
  const config = vscode.workspace.getConfiguration('fleurdelys', one.uri);
  await config.update('enableCMakeAnnotations', false, vscode.ConfigurationTarget.WorkspaceFolder);
  await eventually(async () => assert.ok(vscode.languages.getDiagnostics(navigation.uri).some(item => item.message.includes('PROJECT_NAME'))), 'settings revalidate diagnostics');
  await vscode.commands.executeCommand('fleurdelys.restartServer');
  await eventually(async () => assert.ok((await labels(external)).includes('UNSAVED')), 'restart');
  await packDoc.save();
  await vscode.commands.executeCommand('workbench.action.closeAllEditors');
  console.log('Fleurdelys editor integration passed: multi-root settings, completion, external watcher, hover, definition, diagnostics and restart.');
};
