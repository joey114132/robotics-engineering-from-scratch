# 모든 레슨의 code/diagram*.py 와 code/figure*.py 를 실행하고 .excalidraw 를 SVG·PNG 로 렌더한 뒤 도해마다 화살표가 흐르는 .anim.webp 도 만든다
import fcntl
import os
import pathlib
import subprocess
import sys

import excal

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main(only: str | None = None) -> int:
    lessons = sorted(p for p in (ROOT / "phases").glob("*/*") if p.is_dir() and (only is None or only in str(p)))
    for d in lessons:
        for script in sorted((d / "code").glob("diagram*.py")) + sorted((d / "code").glob("figure*.py")):
            r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=ROOT / "scripts", env={**os.environ, "MATPLOTLIBRC": str(ROOT / "scripts")})
            if r.returncode:
                print(f"FAIL {script.relative_to(ROOT)}\n{r.stderr[-600:]}")
                return 1
    sources = [str(p) for d in lessons for p in sorted((d / "assets").glob("*.excalidraw"))]
    if sources:
        with open("/tmp/robotics-render.lock", "w") as lock:  # one headless browser at a time across all agents
            fcntl.flock(lock, fcntl.LOCK_EX)
            r = subprocess.run(["node", str(ROOT / "scripts" / "render_excalidraw.cjs"), *sources], capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip()[-800:])
        if r.returncode == 0:
            for src in sources:   # next to every diagram-<name>.png: diagram-<name>.anim.webp with dashes flowing along the arrows
                stem = src[:-len(".excalidraw")]
                excal.write_anim(src, stem + ".png", stem + ".anim.webp")
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
