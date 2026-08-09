"""v9.5: standalone bridge script for the AnimeGAN photo-to-anime feature.

Deliberately NOT imported by comfy_companion.py - it's invoked as a
subprocess using ComfyUI's OWN Python venv (which already has torch +
opencv installed for running SDXL), not this app's own interpreter.
This keeps torch entirely out of the PyInstaller build (a documented
constraint elsewhere in this codebase: any reachable `import torch`
balloons the exe from ~80MB to ~2.9GB).

Usage: <comfyui_venv_python> animegan_bridge.py <style> <in_path> <out_path>
style is one of: hayao, shinkai, arcane (matches pytorch-animeGAN's
RELEASED_WEIGHTS keys, using the v2 generator variants).
Prints exactly one line on success: "OK <out_path>"
Prints "ERROR <message>" on failure (still exit code 0 - caller checks
the printed prefix, not the exit code, so a partial torch/cuda warning
on stderr never gets mistaken for total failure).
"""
import sys
import os
import shutil
import tempfile

# v9.5.6: when this script is invoked via PyInstaller's own onefile
# extraction (resource_path() resolves it inside _MEIPASS when no
# external copy sits next to the exe), CPython sets sys.path[0] to this
# script's own directory - which is _MEIPASS itself. PyInstaller dumps
# ALL of the frozen app's bundled native extension modules (compiled
# for ITS OWN cp311 interpreter) flatly into that same _MEIPASS root,
# including its own _ctypes.pyd. Since this script is executed by
# ComfyUI's separate cp313 venv interpreter (not this app's own), that
# stray cp311 _ctypes.pyd shadows the venv's correct cp313 one the
# moment `import ctypes` (pulled in transitively by `import torch`)
# resolves _ctypes via sys.path - triggering CPython's own multi-init
# ABI guard ("Module use of python311.dll conflicts with this version
# of Python"). We insert our own repo_dir explicitly below, so the
# auto-added script-directory entry is never needed - drop it before
# any heavier import happens.
_self_dir = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [p for p in sys.path if os.path.abspath(p) != _self_dir]

STYLE_WEIGHTS = {
    "hayao": "hayao:v2",
    "shinkai": "shinkai:v2",
    "arcane": "arcane:v2",
}


def main():
    if len(sys.argv) != 4:
        print("ERROR usage: animegan_bridge.py <style> <in_path> <out_path>")
        return
    style = sys.argv[1]
    in_path = os.path.abspath(sys.argv[2])
    out_path = os.path.abspath(sys.argv[3])
    weight = STYLE_WEIGHTS.get(style.lower())
    if weight is None:
        print(f"ERROR unknown style '{style}' - expected one of "
              f"{list(STYLE_WEIGHTS)}")
        return
    if not os.path.isfile(in_path):
        print(f"ERROR input file not found: {in_path}")
        return

    repo_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "pytorch-animeGAN")
    if repo_dir not in sys.path:
        sys.path.insert(0, repo_dir)
    os.chdir(repo_dir)

    # v10.4: pytorch-animeGAN's Predictor.transform_file uses OpenCV
    # internally (cv2.imread/cv2.imwrite), which silently returns None
    # for any path containing non-ASCII characters on Windows (a known,
    # long-standing OpenCV limitation - it does not raise, it just fails
    # to read/write, surfacing later as a confusing "'NoneType' object
    # has no attribute 'shape'"). Confirmed live: a source photo path
    # with an accented character reproduced this exactly. Since real
    # user photos (and this app's own persona-name-derived output
    # filenames) very often contain non-ASCII characters, route both
    # ends through ASCII-safe temp files - Python's own file I/O
    # (shutil.copy2) handles Unicode paths correctly, so only the cv2
    # calls ever see a guaranteed-ASCII path.
    with tempfile.TemporaryDirectory(prefix="animegan_") as tmpdir:
        safe_in = os.path.join(tmpdir, "in" + os.path.splitext(in_path)[1])
        safe_out = os.path.join(tmpdir, "out" + os.path.splitext(out_path)[1])
        shutil.copy2(in_path, safe_in)
        try:
            from inference import Predictor
            # retain_color=True fixes the model's known greenish-tint
            # artifact (documented in the repo's own README) by
            # transferring the original photo's color statistics onto
            # the stylized output - confirmed live this made a real
            # visible difference.
            predictor = Predictor(weight=weight, device="cuda",
                                  retain_color=True)
            predictor.transform_file(safe_in, safe_out)
        except Exception as e:
            print(f"ERROR {e}")
            return
        if not os.path.isfile(safe_out):
            print(f"ERROR conversion produced no output file")
            return
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        shutil.copy2(safe_out, out_path)
    print(f"OK {out_path}")


if __name__ == "__main__":
    main()
