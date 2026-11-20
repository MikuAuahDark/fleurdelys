# Fleurdelys for VS Code

CMake language support optimized for scripting and DSLs. Includes syntax
highlighting, completion, hover, signature help, definitions and diagnostics.
The platform-specific VSIX bundles the server; Python is not required to use it.

Install the VSIX using **Extensions: Install from VSIX...**, then open a
`CMakeLists.txt` or `.cmake` file. The language mode is **CMake**.

Automatic suggestions are enabled in strings for CMake because the grammar
classifies unfinished command names (such as `me`) as unquoted strings.
An explicit `editor.quickSuggestions` setting can override this default.

Settings:

- `fleurdelys.enableCMakeAnnotations`: enable project/build-system annotations (default false).
- `fleurdelys.additionalAnnotations`: ordered annotation file paths, relative to each workspace folder or absolute.
- `fleurdelys.expandEnvVariable`: expand `$ENV{NAME}` on the server host (default false).
- `fleurdelys.serverPath`: optional alternative server executable; empty uses the bundled server.
- `fleurdelys.trace.server`: protocol tracing in the output channel.

Each workspace folder uses its own server and settings. Files outside workspace
folders share a separate server. **Fleurdelys: Restart Language Server** restarts
all instances. The extension watches imported files, including external
annotation packs and transitive includes. Workspace folder changes restart the
servers. Use a trusted, local-filesystem workspace; browser-only VS Code is not
supported. Remote installations need a server build for the remote host.

If CMake Tools also provides language services, disable its
`cmake.enableLanguageServices` setting to avoid duplicate suggestions/diagnostics.
Another installed CMake grammar may affect highlighting.

The CMake grammar is from Microsoft's vscode-cmake-tools; its MIT notice and
bundled runtime notices are in `THIRD_PARTY_NOTICES.txt`.

## Build

Install Node.js 22 or newer, and the Python project with its development
dependencies (Python 3.14 and PyInstaller). From this directory:

```text
npm ci
npm run package
npm test
```

The portable Node bundler rebuilds the server using the repository's PyInstaller
spec, stages the runtime and grammar, compiles TypeScript and creates a VSIX in
`../dist`. Build on each target OS/architecture: Windows, Linux or macOS, x64 or
arm64. PyInstaller does not cross-compile. Linux builds must use a sufficiently
old compatible glibc baseline; Alpine/musl is not a supported target here.
Only Windows x64 has been verified in this repository so far.

The bundler prefers `.venv`'s PyInstaller. Set `FLEURDELYS_PYINSTALLER` to override
the executable. It collects runtime notices from `.venv`; use that environment
for release builds. If the Python license cannot be found through
`.venv/pyvenv.cfg`, set `FLEURDELYS_PYTHON_LICENSE` to its license file.
The packaging workflows use the same commands and locked dependencies.

`npm run test:editor` launches an isolated VS Code extension host for integration
tests. Set `VSCODE_EXECUTABLE_PATH` to use an installed VS Code executable;
otherwise the test runner downloads VS Code. On Linux this needs a display
(for example `xvfb-run`).
