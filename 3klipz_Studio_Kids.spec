# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['comfy_companion.py'],
    pathex=[],
    binaries=[],
    # v9.8: app_icon.ico/.png and LOCAL_SETUP_GUIDE.md were missing here,
    # which caused two silent shipped-build failures: the watermark helper
    # (comfy_companion.py, "Stamp the brand kit ... else the app logo")
    # could never find app_icon.png in a frozen build, and Help > Local
    # Setup Guide always returned "Setup guide not found." The .ico is
    # also what root.iconbitmap() loads at startup.
    # v9.11: piper.exe + its native DLLs (espeak-ng.dll, onnxruntime.dll,
    # onnxruntime_providers_shared.dll, piper_phonemize.dll,
    # libtashkeel_model.ort) bundle the Piper TTS narration feature -
    # these are standalone native binaries, not the Python `onnxruntime`
    # pip package (still correctly excluded below), so no conflict with
    # that exclude entry.
    datas=[('personas.json', '.'), ('style_presets.json', '.'), ('wildcards.json', '.'), ('lora_registry.json', '.'), ('model_registry.json', '.'), ('animegan_bridge.py', '.'), ('app_icon.ico', '.'), ('app_icon.png', '.'), ('LOCAL_SETUP_GUIDE.md', '.'), ('piper.exe', '.'), ('espeak-ng.dll', '.'), ('onnxruntime.dll', '.'), ('onnxruntime_providers_shared.dll', '.'), ('piper_phonemize.dll', '.'), ('libtashkeel_model.ort', '.')],
    # v7.1: kept identical to 3klipz_Studio_Pro_v2.spec except name=
    # below - Kids mode activates purely from the output filename
    # (IS_KIDS_MODE = "Kids" in sys.executable, comfy_companion.py
    # near the top of the file), so the two specs must not diverge in
    # content. This file was found missing from disk entirely partway
    # through this session (an external process appears to periodically
    # touch this project's files outside this session) and was
    # recreated here.
    hiddenimports=['requests', 'matplotlib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # v8.2: torch/opencv/ultralytics etc. were pulled into this build
    # (887MB bloat, up from ~78MB) after installing Impact-Pack's own
    # dependencies into this same Python environment - comfy_companion.py
    # itself has no reachable import of any of these (grep-confirmed),
    # they're PyInstaller's own hook auto-discovery reacting to their
    # mere presence in site-packages. None of them belong in this app -
    # ComfyUI (a separate process) is what actually uses them.
    # v8.3: scipy (scikit-image transitive dep, 85 bundled files) and a
    # cluster of unrelated packages (pandas, chardet, lxml, sqlalchemy,
    # aiohttp, psycopg_binary, zstandard, imageio_ffmpeg) were also being
    # swept in by the same hook-auto-discovery mechanism as v8.2 - none
    # of these are imported anywhere in comfy_companion.py (grep-confirmed).
    # numpy/matplotlib/PIL/win32/pywin32_system32/charset_normalizer/
    # markupsafe are genuinely used and must NOT be added here.
    excludes=['torch', 'torchvision', 'torchaudio', 'cv2', 'opencv-python',
              'opencv-python-headless', 'ultralytics', 'ultralytics-thop',
              'segment_anything', 'sam_2', 'onnxruntime', 'timm',
              'groundingdino', 'hydra', 'omegaconf', 'polars',
              'nvidia_ml_py', 'scipy', 'pandas', 'chardet', 'lxml',
              'sqlalchemy', 'aiohttp', 'psycopg_binary', 'psycopg2',
              'zstandard', 'imageio_ffmpeg', 'skimage', 'scikit-image'],
    noarchive=False,
)
pyz = PYZ(a.pure)

# v9.5: bundles the AnimeGAN photo-to-anime feature's code as plain
# DATA (never imported by comfy_companion.py itself, so it adds zero
# import-graph risk to the excludes list above) - it's invoked as a
# subprocess using ComfyUI Desktop's OWN Python venv (which already has
# torch), not this app's interpreter. Weights auto-download to a .cache
# folder on first use - excluded here since it doesn't exist at build
# time and shouldn't be bundled anyway (a few MB, fetched once).
animegan_tree = Tree('pytorch-animeGAN', prefix='pytorch-animeGAN',
                     excludes=['.git', '.cache', '__pycache__', '*.pyc'])

# v9.11: espeak-ng-data (phoneme/lexicon data Piper's espeak-ng.dll
# needs at runtime) and piper_voices (the .onnx voice model +
# .onnx.json config _synthesize_narration loads via
# app_dir()/"piper_voices") - same Tree-as-plain-data pattern as
# animegan_tree above, since neither is ever imported by
# comfy_companion.py itself.
espeak_data_tree = Tree('espeak-ng-data', prefix='espeak-ng-data')
piper_voices_tree = Tree('piper_voices', prefix='piper_voices')

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas + animegan_tree + espeak_data_tree + piper_voices_tree,
    [],
    name='3klipz_Studio_Kids',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)
