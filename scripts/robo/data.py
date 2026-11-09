# 코스 데이터: phases/*/* 폴더 읽기, 레슨 id 해석, 언어별 문서·퀴즈·fun.json
import json
import os
import re
from functools import cached_property
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
PHASE_KO = {"setup-and-tooling": "설치와 도구", "math-foundations": "수학 기초", "manipulator-kinematics": "매니퓰레이터 기구학",
            "dynamics-and-control": "동역학과 제어", "actuators-and-sensors": "액추에이터와 센서", "robot-software": "로봇 소프트웨어",
            "perception-and-calibration": "인식과 캘리브레이션", "state-estimation": "상태 추정", "mobile-robots": "이동로봇",
            "motion-planning": "모션 플래닝", "legged-and-aerial": "다리와 비행", "contact-and-manipulation": "접촉과 조작",
            "simulation-and-sim-to-real": "시뮬레이션과 sim-to-real", "learning-for-robots": "로봇 학습",
            "multi-robot-and-swarms": "다중 로봇과 swarm", "safety-and-deployment": "안전과 배포", "capstones": "캡스톤"}
ACRONYMS = {"se3": "SE(3)", "pid": "PID", "ik": "IK", "fk": "FK", "slam": "SLAM", "urdf": "URDF", "ros2": "ROS 2", "rrt": "RRT",
            "imu": "IMU", "zmp": "ZMP", "mujoco": "MuJoCo", "numpy": "NumPy", "dh": "DH", "vs": "vs", "ros": "ROS", "pd": "PD"}
SMALL = {"and", "of", "to", "in", "for", "vs", "with", "the", "a"}


def nice(slug):
    slug = slug.replace("sim-to-real", "simtoreal")
    out = []
    for i, w in enumerate(slug.split("-")):
        if w == "simtoreal":
            out.append("Sim-to-Real")
        elif w in ACRONYMS:
            out.append(ACRONYMS[w])
        elif i and w in SMALL:
            out.append(w)
        else:
            out.append(w.capitalize())
    return " ".join(out)


def default_lang():
    for k in ("LC_ALL", "LC_MESSAGES", "LANG"):
        v = os.environ.get(k)
        if v:
            return "ko" if v.lower().startswith("ko") else "en"
    return "en"


def _heading(path):
    try:
        m = re.search(r"^# (.+)$", path.read_text(encoding="utf-8"), re.M)
    except OSError:
        return None
    return m.group(1).strip() if m else None


class Phase:
    def __init__(self, path):
        self.path, self.no, self.slug = path, path.name[:2], path.name[3:]
        self.lessons = []

    def title(self, lang="en"):
        return PHASE_KO.get(self.slug, nice(self.slug)) if lang == "ko" else nice(self.slug)


class Lesson:
    def __init__(self, path, phase):
        self.path, self.phase = path, phase
        self.num, self.slug = path.name[:2], path.name[3:]
        self.id = f"{phase.no}-{path.name}"          # 웹사이트와 같은 id: 03-02-gravity-compensation
        self.short = f"{phase.no}-{self.num}"

    def title(self, lang="en"):
        return (_heading(self.doc_path(lang)) if lang == "ko" else None) or _heading(self.path / "docs" / "en.md") or nice(self.slug)

    def doc_path(self, lang="en"):
        p = self.path / "docs" / f"{lang}.md"
        return p if p.exists() else self.path / "docs" / "en.md"

    def _json(self, name):
        try:
            return json.loads((self.path / name).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def quiz(self, lang="en"):
        return (self._json("quiz.ko.json") if lang == "ko" else None) or self._json("quiz.json") or []

    def fun(self, lang="en"):
        f = self._json("fun.json") or {}
        out = dict(f.get(lang) or f.get("en") or {})
        out["toy"] = f.get("toy")
        return out

    def assets(self):
        return sorted((self.path / "assets").glob("*.png"))


class Course:
    def __init__(self, root):
        self.root = Path(root)
        self.phases = []
        for pd in sorted((self.root / "phases").glob("[0-9][0-9]-*")):
            ph = Phase(pd)
            ph.lessons = [Lesson(ld, ph) for ld in sorted(pd.glob("[0-9][0-9]-*")) if ld.is_dir()]
            if ph.lessons:
                self.phases.append(ph)
        self.lessons = [l for p in self.phases for l in p.lessons]

    @cached_property
    def phase_ids(self):
        return {p.no: [l.id for l in p.lessons] for p in self.phases}

    def by_id(self, lesson_id):
        return next((l for l in self.lessons if l.id == lesson_id), None)

    def resolve(self, query):
        q = query.strip().lower()
        m = re.fullmatch(r"(\d{1,2})-(\d{1,2})", q)
        if m:
            short = f"{int(m[1]):02d}-{int(m[2]):02d}"
            hit = [l for l in self.lessons if l.short == short]
        else:
            hit = [l for l in self.lessons if l.id == q] or [l for l in self.lessons if q in l.id]
        if len(hit) == 1:
            return hit[0]
        if not hit:
            raise LookupError(f"nothing matches '{query}'")
        names = ", ".join(l.id for l in hit[:5]) + (" ..." if len(hit) > 5 else "")
        raise LookupError(f"'{query}' matches {len(hit)} lessons: {names}")

    def next_lesson(self, state, done_fn):
        return next((l for l in self.lessons if not done_fn(state, l.id)), None)


def load_course(root=None):
    return Course(root or os.environ.get("ROBO_ROOT") or DEFAULT_ROOT)
