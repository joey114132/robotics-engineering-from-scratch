# 진행 상태: 웹사이트(localStorage 'rfs')와 같은 모양의 JSON, XP 규칙, 연속일, 배지, merge, sync 코드, daily 5
import base64
import contextlib
import datetime as dt
import json
import math
import os
import re
import tempfile
from pathlib import Path

try:
    import fcntl
except ImportError:            # Windows 등: 잠금 없이 동작한다
    fcntl = None

LEVELS = [(0, "Loose Bolt", "헐거운 볼트"), (60, "Servo", "서보"), (180, "Gripper", "그리퍼"),
          (350, "Joint", "관절"), (600, "Arm", "로봇 팔"), (1000, "Rover", "로버"),
          (1600, "Walker", "보행 로봇"), (2500, "Roboticist", "로보티시스트"),
          (4000, "Robot Whisperer", "로봇 조련사")]
XP_PER_ANSWER, XP_PER_MISSION = 10, 20
DAILY_COUNT, DAILY_PER, DAILY_CAP = 5, 5, 25
QUESTIONS_PER_LESSON = 6
# 웹사이트와 공유하는 canonical schema 한도
MAX_CODE_LEN, MAX_XP, MAX_DAYS, MAX_RV = 200_000, 10_000_000, 4000, DAILY_CAP
_DAY = re.compile(r"\d{4}-\d{2}-\d{2}")
_LESSON = re.compile(r"\d\d-[a-z0-9-]{1,80}")
_BADGE = re.compile(r"phase\d\d")
_QIDX = re.compile(r"[0-5]")


def new_state():
    return {"xp": 0, "q": {}, "m": {}, "days": [], "badges": [], "rv": {}}


def _num(v):
    """JSON 숫자만 정수로 읽는다(bool, 문자열, 비정수 실수, inf/nan 은 None). JS 의 Number.isInteger 와 같은 뜻이다."""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and math.isfinite(v) and v.is_integer():
        return int(v)
    return None


def normalize(raw):
    """아무 JSON 이나 받아서 항상 같은 모양의 canonical 상태로 만든다. 잘못된 필드는 버리고 맞는 것은 남긴다."""
    raw = raw if isinstance(raw, dict) else {}
    s = new_state()
    xp = _num(raw.get("xp"))
    s["xp"] = xp if xp is not None and 0 <= xp <= MAX_XP else 0
    q = raw.get("q")
    for lid, answers in (q.items() if isinstance(q, dict) else []):
        if not (isinstance(lid, str) and _LESSON.fullmatch(lid) and isinstance(answers, dict)):
            continue
        rec = {k: v for k, v in answers.items() if isinstance(k, str) and _QIDX.fullmatch(k) and _num(v) in (0, 1)}
        if rec:
            s["q"][lid] = {k: _num(v) for k, v in rec.items()}
    m = raw.get("m")
    s["m"] = {k: 1 for k, v in (m.items() if isinstance(m, dict) else []) if isinstance(k, str) and _LESSON.fullmatch(k) and _num(v) == 1}
    days = raw.get("days")
    ok = sorted({d for d in (days if isinstance(days, list) else []) if isinstance(d, str) and _DAY.fullmatch(d)})
    s["days"] = ok[-MAX_DAYS:]
    badges = raw.get("badges")
    for b in (badges if isinstance(badges, list) else []):
        if isinstance(b, str) and _BADGE.fullmatch(b) and b not in s["badges"]:
            s["badges"].append(b)
    rv = raw.get("rv")
    for d, v in (rv.items() if isinstance(rv, dict) else []):
        n = _num(v)
        if isinstance(d, str) and _DAY.fullmatch(d) and n is not None and 0 <= n <= MAX_RV:
            s["rv"][d] = n
    return s


def progress_path():
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "robotics-course" / "progress.json"


def load(path=None):
    path = Path(path or progress_path())
    try:
        return normalize(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError, OverflowError, RecursionError):
        return new_state()


@contextlib.contextmanager
def _locked(path):
    """같은 폴더의 .lock 파일에 advisory lock 을 건다. 쓸 수 없는 환경이면 조용히 건너뛴다."""
    f = None
    if fcntl is not None:
        try:
            f = open(path.with_name(path.name + ".lock"), "a+")
            fcntl.flock(f, fcntl.LOCK_EX)
        except OSError:
            if f:
                f.close()
            f = None
    try:
        yield
    finally:
        if f:
            try:
                fcntl.flock(f, fcntl.LOCK_UN)
            finally:
                f.close()


def save(state, path=None):
    """잠금 안에서: 디스크의 현재 내용과 합치고(낮추지 않는다) 고유 임시 파일에 써서 fsync 한 뒤 os.replace 한다.
    합친 결과가 메모리 상태에도 반영되므로 다른 프로세스가 저장한 진행을 덮어쓰지 않는다."""
    path = Path(path or progress_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    with _locked(path):
        merged = merge(load(path), state)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(merged, f, ensure_ascii=False, indent=1, sort_keys=True)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(tmp)
            raise
        with contextlib.suppress(OSError):               # 디렉터리 항목도 디스크에 남긴다(지원되는 곳에서만)
            dfd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
    if isinstance(state, dict):
        state.clear()
        state.update(merged)


# ---- levels -----------------------------------------------------------------
def level_index(xp):
    return max(i for i, (t, _, _) in enumerate(LEVELS) if xp >= t)


def level_name(xp, lang="en"):
    return LEVELS[level_index(xp)][2 if lang == "ko" else 1]


def level_progress(xp):
    """(레벨 번호, 이번 레벨에서 얻은 XP, 다음 레벨까지 필요한 XP). 마지막 레벨은 가득 찬 막대."""
    i = level_index(xp)
    if i == len(LEVELS) - 1:
        return i, 1, 1
    return i, xp - LEVELS[i][0], LEVELS[i + 1][0] - LEVELS[i][0]


# ---- XP rules (site: +10 per correct answer once per question, +20 per mission once) ----
def _stamp(s, today):
    d = today.isoformat()
    if d not in s["days"]:
        s["days"] = sorted(s["days"] + [d])


def add_xp(s, n, today):
    if n > 0:
        s["xp"] += n
        _stamp(s, today)
    return n


def answer(s, lesson_id, qi, correct, today):
    rec = s["q"].setdefault(lesson_id, {})
    if str(qi) in rec:
        return 0
    rec[str(qi)] = 1 if correct else 0
    return add_xp(s, XP_PER_ANSWER, today) if correct else 0


def mission(s, lesson_id, today):
    if s["m"].get(lesson_id):
        return 0
    s["m"][lesson_id] = 1
    return add_xp(s, XP_PER_MISSION, today)


def lesson_done(s, lesson_id):
    return len(s["q"].get(lesson_id, {})) >= QUESTIONS_PER_LESSON and bool(s["m"].get(lesson_id))


def lesson_state(s, lesson_id):
    """'done' | 'partial'(뭔가 해 둠) | 'new'"""
    if lesson_done(s, lesson_id):
        return "done"
    return "partial" if s["q"].get(lesson_id) or s["m"].get(lesson_id) else "new"


def award_badges(s, phases):
    """phases: {'03': [lesson ids]}. 새로 얻은 배지 목록을 돌려준다."""
    new = []
    for no, ids in phases.items():
        b = f"phase{no}"
        if b not in s["badges"] and ids and all(lesson_done(s, i) for i in ids):
            s["badges"].append(b)
            new.append(b)
    return new


def streak(s, today):
    days, n, d = set(s["days"]), 0, today
    if d.isoformat() not in days:
        d -= dt.timedelta(days=1)
    while d.isoformat() in days:
        n += 1
        d -= dt.timedelta(days=1)
    return n


# ---- daily 5: 하루 최대 25 XP, 맞힌 문제당 5 XP, 기록은 s["rv"][날짜] = 그날 받은 XP ----
def daily_remaining(s, today):
    return max(0, DAILY_CAP - s["rv"].get(today.isoformat(), 0))


def daily_award(s, correct, today):
    if not correct:
        return 0
    n = min(DAILY_PER, daily_remaining(s, today))
    if n:
        s["rv"][today.isoformat()] = s["rv"].get(today.isoformat(), 0) + n
        add_xp(s, n, today)
    return n


def daily_lessons(s, all_ids):
    seen = [i for i in all_ids if s["q"].get(i)]
    return seen or list(all_ids)


# ---- sync ------------------------------------------------------------------------
def merge(a, b):
    a, b = normalize(a), normalize(b)
    out = new_state()
    out["xp"] = max(a["xp"], b["xp"])
    for lid in sorted(set(a["q"]) | set(b["q"])):
        qa, qb = a["q"].get(lid, {}), b["q"].get(lid, {})
        out["q"][lid] = {k: max(qa.get(k, 0), qb.get(k, 0)) for k in sorted(set(qa) | set(qb), key=lambda x: (len(x), x))}
    out["m"] = {k: 1 for k in sorted(set(a["m"]) | set(b["m"]))}
    out["days"] = sorted(set(a["days"]) | set(b["days"]))
    out["badges"] = sorted(set(a["badges"]) | set(b["badges"]))
    out["rv"] = {d: max(a["rv"].get(d, 0), b["rv"].get(d, 0)) for d in sorted(set(a["rv"]) | set(b["rv"]))}
    return out


def export_code(s):
    raw = json.dumps(normalize(s), separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def import_code(code):
    """base64url -> JSON -> canonical 상태. 어떤 입력이 와도 ValueError 하나로만 실패한다."""
    code = "".join(str(code).split())
    if len(code) > MAX_CODE_LEN:
        raise ValueError("progress code too long")
    code = code.rstrip("=")
    try:
        obj = json.loads(base64.urlsafe_b64decode(code + "=" * (-len(code) % 4)).decode("utf-8"))
        if not isinstance(obj, dict) or not set(obj) & {"xp", "q", "m", "days", "badges", "rv"}:
            raise ValueError("not a progress code")
        return normalize(obj)
    except (ValueError, TypeError, OverflowError, RecursionError) as e:
        raise ValueError("not a progress code") from e
