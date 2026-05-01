# Tauri Wrapper Notes

Use the same web app as the desktop surface.

This directory is documentation and example config only. It is not an active desktop runtime root yet.

## Why Tauri

- keeps one frontend codebase
- lighter than maintaining a second desktop UI
- works well with a local FastAPI gateway

## Suggested integration

### Development
Run the local gateway using `docs/dev.md` first.

Then point Tauri dev to:

```text
http://127.0.0.1:8765/app/
```

### Packaging strategy

For a later production step, choose one of:

1. embed the static frontend and run a local Rust/Python sidecar
2. bundle the FastAPI gateway as a local sidecar process
3. keep desktop mode as a local wrapper around the same dev server during internal use

The simplest path is:
- stabilize the web app first
- only then wrap with Tauri

## Contract

- Keep wrapper notes under `docs/desktop/tauri/` until desktop packaging becomes active runtime code.
- Do not create a top-level `desktop/` directory just for notes or examples.
- `web/app/` remains the single frontend implementation for both web and future desktop use.
