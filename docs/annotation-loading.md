# Configuring annotation loading

Core annotations are always loaded. The CMake pack is disabled by default and
the external pack list is empty. All packs are parsed, never executed.

```text
fleurdelys --enable-cmake-annotations --annotation "packs/first.cmake" --annotation "packs/second.cmake"
```

CLI relative paths are resolved once against the launch directory. Standard IO
is the default transport; existing `--tcp`, `--host`, and `--port` remain available.
Use `python -m fleurdelys` or the installed `fleurdelys` command.

Clients send this exact object as `initializationOptions`, and later as the
`settings` member of `workspace/didChangeConfiguration`:

```json
{"fleurdelys":{"enableCMakeAnnotations":true,"additionalAnnotations":["packs/extra.cmake"]}}
```

`fleurdelys.enableCMakeAnnotations` (**Enable CMake Annotations**) is a boolean.
`fleurdelys.additionalAnnotations` (**Load More Annotations**) is an ordered array
of file path strings. Invalid types warn and fall back to startup defaults.
Each message is a full snapshot: omitted fields restore CLI defaults, explicit
`false` disables CMake and `[]` clears external packs. No disabling CLI flag is
needed because the CLI default is false and clients can explicitly override it.

One configuration snapshot applies to the server. Relative editor paths resolve
against the longest containing workspace folder for each analyzed source, also
in a multi-root workspace. Absolute paths work outside workspace folders;
relative editor paths outside them warn and are skipped. For different settings
per folder, a future extension must run one server per folder. Folder roots are
captured at initialization; restart when the folder list changes.
Paths support spaces, Unicode and Windows drives. There is no globbing, directory
scanning, environment expansion, tilde expansion or VS Code variable substitution.
Normalized paths are deduplicated, keeping their first position. Includes still
resolve relative to their containing file and retain existing variable expansion.

Loading order is core, optional CMake, external packs in order, then consumer.
Later packs replace earlier command overload sets. For example, two declarations
`## function(example FIRST)` and `## function(example SECOND)` in pack A form two
overloads. Pack B's `## function(example THIRD)` replaces both. A consumer's
`## function(example LOCAL)` replaces B's set. Transitive includes belong to their
pack's layer; ordinary consumer includes retain their existing scope behavior.
An implementation without a local annotation gets an inferred signature; one
with a local annotation keeps that signature and supplies its navigation location.
Variables and named symbols keep existing scope/namespace rules, with later
explicit definitions replacing earlier ones.

Configuration changes revalidate open documents. Annotation open/edit/save/close
and watched-file notifications refresh consumers. Open buffers override disk.
Clients should watch external packs and their transitive includes and forward
`workspace/didChangeWatchedFiles` (including creation/deletion); the server handles
this notification but does not dynamically register watchers. Changes outside
these notifications are observed on the next feature analysis. Load warnings use
`window/logMessage` and are deduplicated until a configuration or file event.
Unreadable optional files are skipped; missing bundled files identify an
installation requiring repair. Diagnostics retain their own source URI.

The future VS Code wrapper only needs to contribute the settings, launch a
language client over stdio, forward full snapshots and watched-file events.
See the [language server extension guide](https://code.visualstudio.com/api/language-extensions/language-server-extension-guide).

## Distribution

Wheel resource inclusion remains in `pyproject.toml`. Build a wheel with
`python -m hatchling build -t wheel` and install it in an isolated environment.
Bundled files live under `fleurdelys/annotations/`, resolved relative to the
package, independently of the working directory. Source checkouts fall back to
the repository annotation directory.

The following recipe targets PyInstaller 6.22.3. Install that build tool in the
build environment, then run from the repository root:

```text
python -m PyInstaller --name fleurdelys --onedir --paths src --add-data "annotations/core.cmake:fleurdelys/annotations" --add-data "annotations/cmake.cmake:fleurdelys/annotations" packaging/launcher.py
```

For a single executable replace `--onedir` with `--onefile`. Keep the console
enabled for stdio transport. The launcher uses an absolute package import.
No speculative hidden imports are specified. Additional packs remain external:
`dist/fleurdelys/fleurdelys.exe --enable-cmake-annotations --annotation "C:/my packs/extra.cmake"`.
For one-file output the executable is `dist/fleurdelys.exe`.

This resource layout follows PyInstaller's
[runtime resource documentation](https://pyinstaller.org/en/stable/runtime-information.html)
and [CLI documentation](https://pyinstaller.org/en/stable/usage.html).
Both modes use package-relative `__file__`; one-file extraction paths are valid
only for the running process and must not be persisted as settings.

See [verification results and platform limits](annotation-loading-verification.md)
for the tested wheel and frozen distributions. To repeat the real LSP check,
run `python test/smoke_distribution.py ABSOLUTE_SERVER_COMMAND [ARGS...]`.
