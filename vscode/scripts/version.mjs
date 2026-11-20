import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { parse } from 'smol-toml';

// pyproject.toml is the release version source; npm versions are derived metadata.
export async function syncVersion(repoRoot, extensionRoot) {
  const project = parse(await readFile(path.join(repoRoot, 'pyproject.toml'), 'utf8'));
  const version = project.project?.version;
  if (typeof version !== 'string' || !/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(version)) {
    throw new Error('pyproject.toml [project].version must contain three dot-separated integers without leading zeros (YYYY.MMDD.P).');
  }

  const manifestPath = path.join(extensionRoot, 'package.json');
  const lockPath = path.join(extensionRoot, 'package-lock.json');
  const manifestText = await readFile(manifestPath, 'utf8');
  const manifest = JSON.parse(manifestText);
  const lockText = await readFile(lockPath, 'utf8');
  const lock = JSON.parse(lockText);
  if (!lock.packages?.['']) throw new Error('package-lock.json is missing the root package.');

  if (manifest.version !== version) {
    // Preserve the manifest's compact formatting.
    await writeFile(manifestPath, manifestText.replace(/("version"\s*:\s*)"[^"]*"/, (_, prefix) => `${prefix}"${version}"`));
  }
  if (lock.version !== version || lock.packages[''].version !== version) {
    lock.version = version;
    lock.packages[''].version = version;
    const newline = lockText.includes('\r\n') ? '\r\n' : '\n';
    await writeFile(lockPath, (JSON.stringify(lock, null, 2) + '\n').replace(/\n/g, newline));
  }
  return version;
}
