#!/usr/bin/env python3
# 레슨 클립 실사화: Blender 클립의 움직임은 그대로 두고 겉모습만 실제 촬영처럼 바꾼다 (Higgsfield CLI 필요, 크레딧 사용)
"""Restyle rendered lesson clips as live-action footage, keeping every position and the timing.

    python3 scripts/restyle_clips.py 03-04 11-04         # lessons by NN-LL key or path fragment
    python3 scripts/restyle_clips.py --list keys.txt     # one key per line

For each clip (assets/clip.mp4, or clip-example.mp4 with --example) this
  1. takes one frame and asks an image model for a photograph with the same layout (the look reference),
  2. asks a video model to restyle the clip so it looks like that photograph, with the clip as the motion reference,
  3. checks that the moving things are where they were (motion centroid per frame against the original),
  4. writes assets/<name>.real.mp4 and .real.jpg. The website shows the .real file when it exists.

It spends credits on the account the `higgsfield` CLI is logged into (about 4.5 per clip in November 2026) and is
never run by the tests or by CI. The Blender render stays the source of truth: delete the .real files to go back.

The motion check only compares where things move. It does not notice an object the model invented and left standing
still (in the first batch of ten, one restyle added arrows on the floor and three were rejected for motion), so look
at every result before keeping it. The course's own real look is `CLIP_LOOK=real` in scripts/blender/kit.py, which
costs nothing; this script is an optional extra.
"""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOOK = ("Photorealistic live-action footage filmed with a cinema camera in soft daylight: every object is a real physical thing with real "
        "materials (brushed aluminium and black anodised robot parts, painted die-cast toy cars with rubber tyres, real plastic, wood, steel, "
        "rubber and glass), standing in a real workshop or lab or on a real floor, with realistic reflections, soft shadows and a slight depth "
        "of field. Blue things stay blue, green stay green, amber stay amber, red stay red. Flat arrows and flat markers stay flat graphic "
        "arrows and markers. No text, no letters, no numbers, no logos anywhere.")
KEEP = ("Keep every object's position, size, pose, motion, speed and timing and the camera framing exactly as in the reference video. "
        "Do not add or remove any object.")


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    urls = [line for line in p.stdout.splitlines() if line.startswith("https")]
    if not urls:
        raise RuntimeError((p.stdout + p.stderr)[-400:])
    return urls[-1]


def frames(video: pathlib.Path, n: int = 24, size=(160, 90)) -> np.ndarray:
    """n grey frames spread over the clip, as floats."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(video), "-vf", f"fps={n / dur:.4f},scale={size[0]}:{size[1]},format=gray", "-frames:v", str(n),
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, size[1], size[0]).astype(float)


def motion_track(video: pathlib.Path) -> np.ndarray:
    """(x, y) of the centre of what moved between consecutive sampled frames, in 0..1; nan where nothing moved."""
    f = frames(video)
    out = []
    for a, b in zip(f[:-1], f[1:]):
        d = np.abs(b - a)
        d[d < 12] = 0
        if d.sum() < 2000:
            out.append((np.nan, np.nan))
            continue
        ys, xs = np.mgrid[0:d.shape[0], 0:d.shape[1]]
        out.append(((xs * d).sum() / d.sum() / d.shape[1], (ys * d).sum() / d.sum() / d.shape[0]))
    return np.array(out)


def motion_error(original: pathlib.Path, restyled: pathlib.Path) -> float:
    """Mean distance between the two motion tracks, as a fraction of the frame; 1.0 when they cannot be compared."""
    a, b = motion_track(original), motion_track(restyled)
    n = min(len(a), len(b))
    ok = ~np.isnan(a[:n, 0]) & ~np.isnan(b[:n, 0])
    if ok.sum() < 4:
        return 1.0
    return float(np.hypot(*(a[:n][ok] - b[:n][ok]).T).mean())


def restyle(les: pathlib.Path, name: str, tmp: pathlib.Path, limit: float) -> bool:
    src = les / "assets" / f"{name}.mp4"
    fun = json.loads((les / "fun.json").read_text(encoding="utf-8"))
    scene = fun["en"].get("clip", "") if name == "clip" else ""
    still_in, still, out = tmp / "frame.png", tmp / "still.png", tmp / "out.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2.2", "-i", str(src), "-frames:v", "1", "-vf", "scale=1280:720:flags=lanczos", str(still_in)], check=True)
    url = run(["higgsfield", "generate", "create", "nano_banana_2", "--image", str(still_in), "--aspect_ratio", "16:9", "--resolution", "1k", "--wait", "--prompt",
               "Turn this 3D render into a photorealistic photograph without changing the layout: same camera angle, same positions, sizes and poses "
               f"of every object. {LOOK} What the scene shows: {scene}"])
    subprocess.run(["curl", "-sL", "-o", str(still), url], check=True)
    url = run(["higgsfield", "generate", "create", "seedance_2_0_mini", "--video", str(src), "--image", str(still), "--duration", "5", "--resolution", "480p",
               "--aspect_ratio", "16:9", "--wait", "--wait-timeout", "30m", "--prompt",
               f"Restyle the reference video so it looks like the reference photograph. {LOOK} {KEEP}"])
    subprocess.run(["curl", "-sL", "-o", str(out), url], check=True)
    err = motion_error(src, out)
    if err > limit:
        print(f"REJECT {les.relative_to(ROOT)} {name}: motion differs by {err:.3f} of the frame (limit {limit}); nothing written")
        return False
    real = les / "assets" / f"{name}.real.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-an", "-vf", "scale=640:360:force_original_aspect_ratio=increase,crop=640:360,fps=24",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(real)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "3.3", "-i", str(real), "-frames:v", "1", "-q:v", "4", str(real.with_suffix(".jpg"))], check=True)
    print(f"ok     {les.relative_to(ROOT)} {name}: motion error {err:.3f}, {real.stat().st_size} bytes")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--list")
    ap.add_argument("--example", action="store_true", help="restyle clip-example.mp4 instead of clip.mp4")
    ap.add_argument("--redo", action="store_true", help="restyle even when the .real file is newer than the clip")
    ap.add_argument("--limit", type=float, default=0.06, help="largest mean motion difference accepted, as a fraction of the frame")
    a = ap.parse_args()
    keys = a.keys + ([k.strip() for k in pathlib.Path(a.list).read_text().split() if k.strip()] if a.list else [])
    name, good = ("clip-example" if a.example else "clip"), True
    for les in sorted(p.parent for p in ROOT.glob("phases/*/*/fun.json")):
        key = f"{les.parent.name[:2]}-{les.name[:2]}"
        if not any(k == key or k in str(les) for k in keys):
            continue
        src, real = les / "assets" / f"{name}.mp4", les / "assets" / f"{name}.real.mp4"
        if not src.exists() or (real.exists() and real.stat().st_mtime >= src.stat().st_mtime and not a.redo):
            continue
        with tempfile.TemporaryDirectory() as tmp:
            try:
                good &= restyle(les, name, pathlib.Path(tmp), a.limit)
            except (RuntimeError, subprocess.CalledProcessError) as e:
                print(f"FAIL   {les.relative_to(ROOT)} {name}: {str(e)[-300:]}")
                good = False
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
