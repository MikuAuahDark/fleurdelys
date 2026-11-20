# Fleurdelys

A lightweight Language Server for CMake, specifically optimized for DSL usage patterns
(e.g. with [Cartethyia](https://github.com/MikuAuahDark/cartethyia)).

## VS Code extension

The [VS Code extension](vscode/README.md) bundles the server, CMake syntax
highlighting and per-folder settings. Build a platform-specific VSIX with
`npm ci` and `npm run package` from `vscode/`; the artifact is written to `dist/`.
The bundler runs on Windows, Linux and macOS and builds for its host architecture.
Release versions are set in `pyproject.toml` as `YYYY.MMDD.P`, where `MMDD` is
`month * 100 + day` and `P` starts at zero each day. Packaging automatically
synchronizes the extension manifest and npm lockfile with that version.

**AI Usage Warning**: This is experimental project made assisted using Google Antigravity and OpenAI Codex. It may contain errors or security vulnerabilities. Use at your own risk!

## Annotation loading

Core annotations are enabled automatically. Use `--enable-cmake-annotations`
and repeatable `--annotation PATH` options for additional packs. See
[configuration, editor integration and standalone builds](docs/annotation-loading.md).
