# robo 테스트 공통 fixture: sys.path, 임시 진행 파일, 작은 가짜 코스
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

REAL_ROOT = SCRIPTS.parent


def _quiz(tag):
    stages = ["pre", "check", "check", "check", "post", "post"]
    return [{"id": i + 1, "stage": s, "question": f"{tag} question {i + 1}?",
             "options": ["right", "wrong one", "wrong two"], "answer": 0,
             "explanation": f"{tag} explanation {i + 1}."} for i, s in enumerate(stages)]


def make_course(root: Path):
    from PIL import Image
    spec = {"00-alpha-tools": ["01-first-steps", "02-second-wind"], "01-beta-gamma": ["01-third-try"]}
    for ph, lessons in spec.items():
        for les in lessons:
            d = root / "phases" / ph / les
            (d / "docs").mkdir(parents=True)
            (d / "assets").mkdir()
            title = les[3:].replace("-", " ").title()
            (d / "docs" / "en.md").write_text(
                f"# {title}\n\n> One line idea of {title}.\n\n**Type:** Build   **Time:** ~15 minutes\n\n"
                "## The Problem\n\nSome `inline` text with **bold**.\n\n"
                "![A red square](../assets/fig.png)\n\n*Caption of the red square.*\n\n"
                "| a | b |\n|---|---|\n| 1 | 2 |\n\n```python\nprint('hi')\n```\n")
            (d / "docs" / "ko.md").write_text(f"# {title} (한글)\n\n> 한 줄 요약입니다.\n\n## 문제\n\n본문 `코드` 입니다.\n")
            (d / "quiz.json").write_text(json.dumps(_quiz("EN")))
            (d / "quiz.ko.json").write_text(json.dumps(_quiz("KO"), ensure_ascii=False))
            (d / "fun.json").write_text(json.dumps({
                "en": {"hook": "Hook text.", "mission": "Do the `thing`."},
                "ko": {"hook": "훅 문장입니다.", "mission": "그것을 하세요."}}, ensure_ascii=False))
            Image.new("RGB", (40, 20), (200, 30, 30)).save(d / "assets" / "fig.png")
    return root


@pytest.fixture
def course(tmp_path):
    return make_course(tmp_path / "course")


@pytest.fixture
def state_home(tmp_path, monkeypatch):
    home = tmp_path / "state"
    monkeypatch.setenv("XDG_STATE_HOME", str(home))
    return home
