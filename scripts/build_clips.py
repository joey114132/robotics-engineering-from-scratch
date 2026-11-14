#!/usr/bin/env python3
# 레슨 클립 렌더러: code/clip.py 를 Blender 로 하나씩 돌려 assets/clip.mp4 와 clip.jpg 를 만든다
"""Render lesson clips with Blender, one at a time.

    python3 scripts/build_clips.py 03-04            # lessons whose path contains the fragment
    python3 scripts/build_clips.py --missing        # only clip scripts (code/clip*.py) whose .mp4 is not there yet
    python3 scripts/build_clips.py 03-04 --still 60 # one frame, for a quick look (prints the PNG path)

Needs `blender` (5.x) and `ffmpeg` on PATH. Renders are serialised with a lock file, so several shells can queue.
"""
import argparse
import fcntl
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK = pathlib.Path(tempfile.gettempdir()) / "robotics-blender.lock"


def lessons(fragment: str, missing: bool) -> list[pathlib.Path]:
    out = []
    for clip in sorted(ROOT.glob("phases/*/*/code/clip*.py")):
        les = clip.parents[1]
        key = f"{les.parent.name[:2]}-{les.name[:2]}"
        if fragment and fragment not in str(les) and fragment != key:
            continue
        if missing and (les / "assets" / f"{clip.stem}.mp4").exists():
            continue
        out.append(clip)
    return out


def render(clip: pathlib.Path, still: int | None, tmp: str) -> bool:
    env = {**os.environ, "CLIP_TMP": tmp}
    if still is not None:
        env["CLIP_STILL"] = str(still)
    with open(LOCK, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        t = time.time()
        p = subprocess.run(["blender", "-b", "--python-exit-code", "1", "-P", str(clip)], env=env, capture_output=True, text=True)
    tail = [line for line in p.stdout.splitlines() if line.startswith(("CLIP", "STILL"))]
    ok = p.returncode == 0 and bool(tail)
    print(f"{'ok  ' if ok else 'FAIL'} {clip.relative_to(ROOT)}  {time.time() - t:.0f}s  {tail[-1] if tail else ''}")
    if not ok:
        print((p.stdout + p.stderr)[-1500:])
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fragment", nargs="?", default="")
    ap.add_argument("--missing", action="store_true")
    ap.add_argument("--still", type=int)
    ap.add_argument("--tmp", default=tempfile.gettempdir())
    a = ap.parse_args()
    for tool in ("blender", "ffmpeg"):
        if not shutil.which(tool):
            print(f"{tool} is not on PATH")
            return 1
    todo = lessons(a.fragment, a.missing)
    if not todo:
        print("no clip.py matches")
        return 1
    return 0 if all([render(c, a.still, a.tmp) for c in todo]) else 1


if __name__ == "__main__":
    sys.exit(main())
