# Annotation loading verification

Verified on Windows 11 x64 with Python 3.14.6, pygls 2.1.1 and PyInstaller
6.22.3 (hooks-contrib 2026.10). Python execution was explicitly authorized for
these checks. Tests needed execution outside the sandbox because temporary
directories created inside it were inaccessible; no test failures were waived.

- `venv/Scripts/python.exe -m unittest discover -s test`: 57 tests passed.
- `git diff --check`: passed.
- `python -m hatchling build -t wheel`: built the wheel, then installed it into
  a separate verification environment with runtime dependencies. Both package
  resources were present under `site-packages/fleurdelys/annotations`.
- Built both PyInstaller formats using the documented resource mappings and
  absolute-import launcher, without extra hidden imports.
- Ran `test/smoke_distribution.py COMMAND [ARGS...]` against the source checkout,
  installed wheel, one-folder executable and one-file executable. Every run
  used an unrelated temporary working directory and an external annotation path
  containing spaces and Unicode.
- Real JSON-RPC checks covered initialization, core/CMake/external completion,
  hover, signature help, definition navigation, invalid-argument diagnostics,
  watched-file refresh, live configuration removal and normal shutdown.
  Frozen and installed-wheel navigation targets were checked against their
  package resource locations.

The frozen launcher accommodates pygls closing stdout on LSP exit: it replaces
both closed stdout references before PyInstaller's final flush. Final frozen
smoke runs completed without stderr output.

Tests also cover ordering, transitive imports/cycles, overload replacement,
local inference/navigation, cursor defaults, unsaved buffers, malformed scopes,
missing/corrupt files, snapshot defaults/type validation, CLI transports,
warning deduplication, close/watcher invalidation and multi-root secondary
analysis. The documented limitations remain: one settings snapshot per server,
folder roots fixed at initialization, and client-managed file watchers. Other
operating systems and Python versions were not exercised.
