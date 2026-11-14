# 레슨 클립: clip.py 가 있으면 캡션이 두 언어로 있고, 렌더된 mp4 와 jpg 가 있는지 검사한다
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
CLIPS = sorted(ROOT.glob("phases/*/*/code/clip*.py"))   # clip.py is the lead clip; clip-<name>.py is linked from the lesson text


@pytest.mark.parametrize("clip", CLIPS, ids=lambda p: f"{p.parents[2].name[:2]}-{p.parents[1].name[:2]}-{p.stem}")
def test_clip_script_and_captions(clip):
    src = clip.read_text(encoding="utf-8")
    assert src.startswith("# "), "one-line header comment"
    assert "kit.lesson_main(__file__)" in src, "the motion must come from the lesson's own code/main.py"
    assert src.rstrip().endswith("kit.render(__file__)")
    if clip.stem != "clip":   # a clip in the text: both docs link it, the caption is the italic line under the link
        for lang in ("en", "ko"):
            assert f"](../assets/{clip.stem}.mp4)" in (clip.parents[1] / "docs" / f"{lang}.md").read_text(encoding="utf-8")
        return
    fun = json.loads((clip.parents[1] / "fun.json").read_text(encoding="utf-8"))
    for lang in ("en", "ko"):
        cap = fun[lang].get("clip", "")
        assert 40 <= len(cap) <= 620, f"{lang} caption length {len(cap)}"   # two to four sentences, with the scale or speed when it was changed
    assert re.search("[가-힣]", fun["ko"]["clip"]) and not re.search("[가-힣]", fun["en"]["clip"])
    assert "수업" not in fun["ko"]["clip"] and "—" not in fun["ko"]["clip"] and "·" not in fun["ko"]["clip"]


@pytest.mark.parametrize("clip", CLIPS, ids=lambda p: f"{p.parents[2].name[:2]}-{p.parents[1].name[:2]}-{p.stem}")
def test_clip_is_rendered(clip):
    for ext in ("mp4", "jpg"):
        out = clip.parents[1] / "assets" / f"{clip.stem}.{ext}"
        assert out.exists() and out.stat().st_size > 2000, f"run: python3 scripts/build_clips.py {clip.parents[1].name}"
