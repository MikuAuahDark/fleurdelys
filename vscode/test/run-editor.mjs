import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { downloadAndUnzipVSCode } from '@vscode/test-electron';
const extensionRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
await mkdir(path.join(extensionRoot, '.vscode-test'), { recursive: true });
const root = await mkdtemp(path.join(extensionRoot, '.vscode-test', 'integration-'));
for (const name of ['one', 'two', 'external']) await mkdir(path.join(root, name));
await writeFile(path.join(root, 'external', 'pack.cmake'), '## include(nested.cmake)\n');
await writeFile(path.join(root, 'external', 'nested.cmake'), '## function(external_probe FIRST)\n');
await writeFile(path.join(root, 'test.code-workspace'), JSON.stringify({
  folders: [{ path: 'one' }, { path: 'two' }], settings: { 'security.workspace.trust.enabled': false, 'update.mode': 'none' },
}));
for (const name of ['one', 'two']) {
  await mkdir(path.join(root, name, '.vscode'));
  await writeFile(path.join(root, name, '.vscode', 'settings.json'), JSON.stringify({
    'fleurdelys.enableCMakeAnnotations': name === 'one',
    'fleurdelys.additionalAnnotations': ['../external/pack.cmake'],
  }));
}
const executable = process.env.VSCODE_EXECUTABLE_PATH ?? await downloadAndUnzipVSCode();
const env = { ...process.env, FLEURDELYS_EDITOR_TEST_ROOT: root };
delete env.ELECTRON_RUN_AS_NODE;
const child = spawn(executable, [path.join(root, 'test.code-workspace'), '--new-window', '--disable-extensions',
  '--skip-welcome', '--skip-release-notes', '--disable-workspace-trust', '--no-sandbox',
  '--user-data-dir', path.join(root, 'user-data'), '--extensions-dir', path.join(root, 'extensions'),
  `--extensionDevelopmentPath=${extensionRoot}`, `--extensionTestsPath=${path.join(extensionRoot, 'test', 'editor.cjs')}`],
{ cwd: extensionRoot, env, windowsHide: true, stdio: 'inherit' });
const timer = setTimeout(() => { console.error('VS Code integration test timed out.'); child.kill(); process.exitCode = 1; }, 120000);
child.once('error', error => { clearTimeout(timer); console.error(error); process.exitCode = 1; });
child.once('exit', code => { clearTimeout(timer); console.log(`VS Code test process exited with ${code}.`); process.exitCode = code ?? 1; });
