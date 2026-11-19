# CMake syntax highlighting

`CMake.tmLanguage.json` is vendored without modifications from Microsoft's
[vscode-cmake-tools](https://github.com/microsoft/vscode-cmake-tools) repository.

- Revision: `c757bfc851ca01d18601b64178ea40190e72d5d1`
- Source: https://github.com/microsoft/vscode-cmake-tools/blob/c757bfc851ca01d18601b64178ea40190e72d5d1/syntaxes/CMake.tmLanguage.json
- License: MIT; the upstream copyright and permission notice are preserved in
  `CMake.tmLanguage.LICENSE.txt` at the repository root.

When updating the grammar, fetch both the grammar and upstream `LICENSE.txt`
from the same revision and update the revision and source link above. Include
the license file when distributing the grammar, including in a future VSIX.

The grammar uses scope `source.cmake`. The VS Code extension in `vscode/`
registers language ID `cmake`, associates `.cmake` files and `CMakeLists.txt`,
and stages this grammar during packaging. Comments, bracket pairs and
indentation are supplied separately by `vscode/language-configuration.json`.
