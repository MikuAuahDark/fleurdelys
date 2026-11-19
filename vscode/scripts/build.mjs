import { build } from 'esbuild';
await build({ entryPoints: ['src/extension.ts'], outfile: 'out/extension.js', bundle: true,
  platform: 'node', format: 'cjs', target: 'node18', external: ['vscode'], sourcemap: true,
  legalComments: 'external' });
