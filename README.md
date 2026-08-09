# 3klipz Studio

A local, ComfyUI-driven creative production suite — anime/illustration image
generation, video (AnimateDiff + native Wan 2.1 text-to-video), channel/content
pipelines, character design tooling, and a large set of post-processing and
distribution features, all built around a single Python/Tkinter application
that talks to a locally-running ComfyUI server over HTTP.

Ships as two editions built from the same source: **Pro** (full feature set)
and **Kids** (a content-restricted build with a hard safety floor and a
reduced tool surface).

## Requirements

- Windows 10/11
- A running local [ComfyUI](https://github.com/comfyanonymous/ComfyUI) server
  (default checkpoints/, loras/, controlnet/, etc. as usual)
- Optional: [Ollama](https://ollama.com) for local LLM-assisted features
  (character invention, prompt enhancement, quote generation) — the app
  degrades gracefully without it

Neither ComfyUI, model weights, nor Ollama models are part of this
repository. See `SETUP_OTHER_MACHINE.md` (generated alongside a build) for
the exact custom node packs and model files this app's optional features
expect.

## Running from source

```bash
pip install requests pillow numpy matplotlib
python comfy_companion.py
```

## Building a standalone exe

```bash
pip install pyinstaller
pyinstaller 3klipz_Studio_Pro_v2.spec
pyinstaller 3klipz_Studio_Kids.spec
```

Output lands in `dist/`.

## Structure

This is a single-file application (`comfy_companion.py`) by design — no
build step, no package layout, easy to read top-to-bottom. The two `.spec`
files are PyInstaller build configs; they're identical except for the
output name, since the app detects Kids vs. Pro from its own executable
filename at runtime.
