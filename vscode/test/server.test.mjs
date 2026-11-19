import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdtemp, writeFile, rm, realpath } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

test('bundled server: stdio, settings, environment and external dependencies', { timeout: 30000 }, async t => {
  const root = await realpath(await mkdtemp(path.join(os.tmpdir(), 'fleurdelys-vsix-')));
  const pack = path.join(root, 'external pack ü.cmake');
  await writeFile(pack, '## Probe documentation.\n## function(pack_probe EXTERNAL)\n');
  const child = spawn(path.resolve('server', process.platform === 'win32' ? 'fleurdelys.exe' : 'fleurdelys'), [],
    { cwd: root, windowsHide: true, env: { ...process.env, FLEURDELYS_TEST_PACK: pack } });
  let stderr = '';
  child.stderr.on('data', data => { stderr += data; });
  t.after(async () => { child.kill(); await rm(root, { recursive: true, force: true }); });
  const pending = new Map();
  const notifications = [];
  let buffer = Buffer.alloc(0), sequence = 0;
  child.stdout.on('data', data => {
    buffer = Buffer.concat([buffer, data]);
    for (;;) {
      const separator = buffer.indexOf('\r\n\r\n');
      if (separator < 0) return;
      const length = Number(/Content-Length:\s*(\d+)/i.exec(buffer.subarray(0, separator).toString())?.[1]);
      if (buffer.length < separator + 4 + length) return;
      const message = JSON.parse(buffer.subarray(separator + 4, separator + 4 + length).toString());
      buffer = buffer.subarray(separator + 4 + length);
      if (message.id !== undefined) {
        const waiter = pending.get(message.id);
        if (waiter) { pending.delete(message.id); message.error ? waiter.reject(new Error(JSON.stringify(message.error))) : waiter.resolve(message.result); }
      } else notifications.push(message);
    }
  });
  function send(message) {
    const body = Buffer.from(JSON.stringify({ jsonrpc: '2.0', ...message }));
    child.stdin.write(`Content-Length: ${body.length}\r\n\r\n`);
    child.stdin.write(body);
  }
  function request(method, params) {
    const id = ++sequence;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { pending.delete(id); reject(new Error(`Timed out: ${method}\n${stderr}`)); }, 10000);
      pending.set(id, { resolve: value => { clearTimeout(timer); resolve(value); }, reject: error => { clearTimeout(timer); reject(error); } });
      send({ id, method, params });
    });
  }
  const editorUri = file => pathToFileURL(file).href.replace(/\/([a-z]):\//i, '/$1%3A/');
  await request('initialize', { processId: process.pid, rootUri: editorUri(root),
    capabilities: {}, initializationOptions: { fleurdelys: { expandEnvVariable: true,
      additionalAnnotations: [path.basename(pack)] }, fleurdelysWatchDependencies: true } });
  send({ method: 'initialized', params: {} });
  const uri = editorUri(path.join(root, 'main.cmake'));
  const source = 'include("$ENV{FLEURDELYS_TEST_PACK}")\npack_probe(';
  send({ method: 'textDocument/didOpen', params: { textDocument: { uri, languageId: 'cmake', version: 1, text: source } } });
  const position = { line: 1, character: 11 };
  const result = await request('textDocument/completion', { textDocument: { uri }, position });
  assert.ok(result.items.some(item => item.label === 'EXTERNAL'));
  assert.ok(notifications.some(message => message.method === 'fleurdelys/watchDependency' &&
    decodeURIComponent(message.params.uri).toLowerCase() === decodeURIComponent(pathToFileURL(pack).href).toLowerCase()), JSON.stringify(notifications));
  send({ method: 'workspace/didChangeConfiguration', params: { settings: { fleurdelys: { expandEnvVariable: false } } } });
  const disabled = await request('textDocument/completion', { textDocument: { uri }, position });
  assert.ok(!disabled.items.some(item => item.label === 'EXTERNAL'));
  await request('shutdown', null);
  const exited = new Promise(resolve => child.once('exit', code => resolve(code)));
  send({ method: 'exit' });
  assert.equal(await exited, 0, stderr);
});
