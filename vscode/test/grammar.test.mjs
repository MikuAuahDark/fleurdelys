import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import textmate from 'vscode-textmate';
import oniguruma from 'vscode-oniguruma';
const { Registry, parseRawGrammar, INITIAL } = textmate;
const { loadWASM, OnigScanner, OnigString } = oniguruma;
const require = createRequire(import.meta.url);

test('upstream grammar tokenizes CMake variables, custom commands and bracket comments', async () => {
  const wasm = await readFile(require.resolve('vscode-oniguruma/release/onig.wasm'));
  await loadWASM(wasm.buffer.slice(wasm.byteOffset, wasm.byteOffset + wasm.byteLength));
  const registry = new Registry({
    onigLib: Promise.resolve({ createOnigScanner: patterns => new OnigScanner(patterns), createOnigString: value => new OnigString(value) }),
    loadGrammar: async () => parseRawGrammar(await readFile('../CMake.tmLanguage.json', 'utf8'), 'CMake.tmLanguage.json'),
  });
  const grammar = await registry.loadGrammar('source.cmake');
  const variable = grammar.tokenizeLine('message("${FOO}")', INITIAL);
  assert.ok(variable.tokens.some(token => token.scopes.includes('variable.other.cmake')));
  const custom = grammar.tokenizeLine('my_custom_command(value)', INITIAL);
  assert.ok(custom.tokens.some(token => token.scopes.some(scope => scope.startsWith('entity.name.function') || scope.startsWith('support.function'))));
  const comment = grammar.tokenizeLine('#[=[ block', INITIAL);
  const next = grammar.tokenizeLine('${literal} ]=]', comment.ruleStack);
  assert.ok(next.tokens.some(token => token.scopes.includes('comment.block.bracket.cmake')));
  assert.ok(!next.tokens.some(token => token.scopes.includes('variable.other.cmake')));
  registry.dispose();
});

test('language configuration has valid JavaScript patterns', async () => {
  const config = JSON.parse(await readFile('language-configuration.json', 'utf8'));
  assert.ok(new RegExp(config.indentationRules.increaseIndentPattern).test('IF(ENABLED)'));
  assert.ok(new RegExp(config.indentationRules.decreaseIndentPattern).test('endif()'));
  assert.deepEqual(config.comments.blockComment, ['#[[', ']]']);
});
