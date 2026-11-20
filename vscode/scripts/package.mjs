import { cp, mkdir, readFile, readdir, rm, writeFile, access } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { syncVersion } from './version.mjs';

const extensionRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repoRoot = path.resolve(extensionRoot, '..');
const targets = { win32: 'win32', linux: 'linux', darwin: 'darwin' };
if (!targets[process.platform] || !['x64', 'arm64'].includes(process.arch)) {
  throw new Error(`Unsupported build host: ${process.platform}-${process.arch}`);
}
const target = `${targets[process.platform]}-${process.arch}`;
const argIndex = process.argv.indexOf('--target');
if (argIndex !== -1 && process.argv[argIndex + 1] !== target) {
  throw new Error(`Build on the target OS and architecture. This host builds ${target}.`);
}
const version = await syncVersion(repoRoot, extensionRoot);
function run(command, args, cwd = repoRoot) {
  const result = spawnSync(command, args, { cwd, stdio: 'inherit', windowsHide: true, shell: false });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`${command} exited with ${result.status}`);
}
const localTool = path.join(repoRoot, '.venv', process.platform === 'win32' ? 'Scripts/pyinstaller.exe' : 'bin/pyinstaller');
let builder = process.env.FLEURDELYS_PYINSTALLER;
if (!builder) {
  try { await access(localTool); builder = localTool; } catch { builder = 'pyinstaller'; }
}
const output = path.join(repoRoot, 'dist', 'vscode-server', target);
run(builder, ['--noconfirm', '--distpath', output, '--workpath', path.join(repoRoot, 'build', 'vscode', target), 'fleurdelys.spec']);
const serverDir = path.join(extensionRoot, 'server');
// Only replace the extension's generated staging directory.
if (path.dirname(serverDir) !== extensionRoot || path.basename(serverDir) !== 'server') throw new Error('Invalid staging directory');
await rm(serverDir, { recursive: true, force: true });
await cp(path.join(output, 'fleurdelys'), serverDir, { recursive: true, dereference: true });
await mkdir(path.join(extensionRoot, 'syntaxes'), { recursive: true });
await cp(path.join(repoRoot, 'CMake.tmLanguage.json'), path.join(extensionRoot, 'syntaxes', 'CMake.tmLanguage.json'));
const grammarLicense = await readFile(path.join(repoRoot, 'CMake.tmLanguage.LICENSE.txt'), 'utf8');
const notices = [`CMake grammar: microsoft/vscode-cmake-tools\n${grammarLicense}`];
// Preserve license files shipped by the build environment for bundled Python libraries.
const sitePackages = process.platform === 'win32' ? path.join(repoRoot, '.venv', 'Lib', 'site-packages')
  : await (async () => {
    const lib = path.join(repoRoot, '.venv', 'lib');
    try { const entries = await readdir(lib); return path.join(lib, entries.find(name => name.startsWith('python')) ?? 'python3.14', 'site-packages'); }
    catch { return undefined; }
  })();
if (sitePackages) {
  for (const entry of await readdir(sitePackages)) {
    if (!/^(pygls|lsprotocol|attrs|cattrs|typing_extensions)-.*\.dist-info$/i.test(entry)) continue;
    async function collect(directory) {
      for (const item of await readdir(directory, { withFileTypes: true })) {
        const file = path.join(directory, item.name);
        if (item.isDirectory()) await collect(file);
        else if (/^(license|copying|notice)/i.test(item.name)) notices.push(`${entry}/${item.name}\n${await readFile(file, 'utf8')}`);
      }
    }
    await collect(path.join(sitePackages, entry));
  }
}
const pythonCandidates = [process.env.FLEURDELYS_PYTHON_LICENSE];
try {
  const cfg = await readFile(path.join(repoRoot, '.venv', 'pyvenv.cfg'), 'utf8');
  const home = /^home\s*=\s*(.+)$/m.exec(cfg)?.[1].trim();
  if (home) {
    pythonCandidates.push(path.join(home, 'LICENSE.txt'), path.join(home, '..', 'LICENSE.txt'));
    // POSIX Python distributions (including uv-managed Python) keep the
    // runtime license in the standard library, alongside the bin directory.
    const version = /^version_info\s*=\s*(\d+\.\d+)/m.exec(cfg)?.[1];
    if (version) {
      for (const lib of ['lib', 'lib64']) {
        pythonCandidates.push(path.join(home, '..', lib, `python${version}`, 'LICENSE.txt'));
      }
    }
  }
} catch { /* A globally installed builder may supply its own license path. */ }
let pythonLicense;
for (const candidate of pythonCandidates.filter(Boolean)) {
  try { pythonLicense = await readFile(candidate, 'utf8'); break; } catch { /* Try next location. */ }
}
if (!pythonLicense) throw new Error('Set FLEURDELYS_PYTHON_LICENSE to the bundled Python runtime LICENSE file.');
notices.push(`Python runtime\n${pythonLicense}`);
const clientLicense = await readFile(path.join(extensionRoot, 'node_modules', 'vscode-languageclient', 'License.txt'), 'utf8');
notices.push(`vscode-languageclient and Microsoft LSP libraries\n${clientLicense}`);
await writeFile(path.join(extensionRoot, 'THIRD_PARTY_NOTICES.txt'), notices.join('\n\n========================================\n\n'));
run(process.execPath, ['--test', 'test/server.test.mjs'], extensionRoot);
await mkdir(path.join(repoRoot, 'dist'), { recursive: true });
const artifact = path.join(repoRoot, 'dist', `fleurdelys-${version}-${target}.vsix`);
run(process.execPath, [path.join(extensionRoot, 'node_modules', '@vscode', 'vsce', 'vsce'), 'package',
  '--target', target, '--no-dependencies', '--allow-missing-repository', '--skip-license', '--out', artifact], extensionRoot);
console.log(`Packaged ${artifact}`);
