# 진행 로직 테스트: XP 규칙, 레벨, 연속일, 배지, merge, sync 코드, daily 상한
import datetime as dt
from pathlib import Path

import pytest

from robo import progress as P

L1, L2, L3 = "00-01-first-steps", "00-02-second-wind", "01-01-third-try"
PHASES = {"00": [L1, L2], "01": [L3]}
D = dt.date(2026, 11, 9)


def test_levels_match_site():
    assert [t for t, _, _ in P.LEVELS] == [0, 60, 180, 350, 600, 1000, 1600, 2500, 4000]
    assert [n for _, n, _ in P.LEVELS][:3] == ["Loose Bolt", "Servo", "Gripper"]
    assert P.LEVELS[-1][2] == "로봇 조련사"
    assert P.level_index(0) == 0 and P.level_index(59) == 0 and P.level_index(60) == 1
    assert P.level_index(3999) == 7 and P.level_index(99999) == 8


def test_level_progress_to_next():
    assert P.level_progress(90) == (1, 30, 120)      # Servo, 30 of the 120 to Gripper
    assert P.level_progress(5000) == (8, 1, 1)           # top level: full bar


def test_answer_awards_10_once_per_question():
    s = P.new_state()
    assert P.answer(s, L1, 0, True, D) == 10
    assert P.answer(s, L1, 0, True, D) == 0        # same question again
    assert s["xp"] == 10 and s["q"][L1] == {"0": 1}


def test_wrong_answer_records_but_gives_nothing_and_cannot_be_retried_for_xp():
    s = P.new_state()
    assert P.answer(s, L1, 1, False, D) == 0
    assert s["q"][L1]["1"] == 0
    assert P.answer(s, L1, 1, True, D) == 0        # first answer counts, like the site
    assert s["xp"] == 0 and s["q"][L1]["1"] == 0


def test_mission_awards_20_once_and_untick_never_lowers():
    s = P.new_state()
    assert P.mission(s, L1, D) == 20
    assert P.mission(s, L1, D) == 0
    assert s["xp"] == 20 and s["m"][L1] == 1


def test_lesson_done_needs_six_answers_and_mission():
    s = P.new_state()
    for i in range(6):
        P.answer(s, L1, i, i % 2 == 0, D)
    assert not P.lesson_done(s, L1)
    P.mission(s, L1, D)
    assert P.lesson_done(s, L1)
    assert not P.lesson_done(s, L2)


def test_phase_badge_when_all_lessons_done():
    s = P.new_state()
    for lid in (L1, L2):
        for i in range(6):
            P.answer(s, lid, i, True, D)
        P.mission(s, lid, D)
        if lid == L1:
            assert P.award_badges(s, PHASES) == []
    assert P.award_badges(s, PHASES) == ["phase00"]
    assert P.award_badges(s, PHASES) == []
    assert s["badges"] == ["phase00"]


def test_streak_counts_local_days_ending_today_or_yesterday():
    s = P.new_state()
    s["days"] = ["2026-11-06", "2026-11-07", "2026-11-08", "2026-11-09"]
    assert P.streak(s, D) == 4
    assert P.streak(s, D + dt.timedelta(days=1)) == 4   # yesterday still counts
    assert P.streak(s, D + dt.timedelta(days=2)) == 0
    s["days"] = ["2026-11-06", "2026-11-08", "2026-11-09"]
    assert P.streak(s, D) == 2


def test_xp_award_stamps_today_but_wrong_answer_does_not():
    s = P.new_state()
    P.answer(s, L1, 0, False, D)
    assert s["days"] == []
    P.answer(s, L1, 1, True, D)
    assert s["days"] == ["2026-11-09"]


def test_normalize_tolerates_junk():
    s = P.normalize({"xp": "x", "q": [], "days": None, "rv": {"2026-11-09": "7", "bad": 1}})
    assert s == P.new_state()                      # strings are not numbers in the canonical schema


def test_merge_never_lowers_and_unions():
    a = {"xp": 100, "q": {L1: {"0": 1, "1": 0}}, "m": {L1: 1}, "days": ["2026-11-01"], "badges": ["phase00"], "rv": {"2026-11-08": 10}}
    b = {"xp": 140, "q": {L1: {"1": 1, "2": 1}, L2: {"0": 1}}, "m": {L2: 1}, "days": ["2026-11-02", "2026-11-01"], "badges": ["phase01"], "rv": {"2026-11-08": 25, "2026-11-09": 5}}
    m = P.merge(a, b)
    assert m["xp"] == 140
    assert m["q"][L1] == {"0": 1, "1": 1, "2": 1}      # answered questions kept, a correct record wins
    assert m["q"][L2] == {"0": 1}
    assert m["m"] == {L1: 1, L2: 1}
    assert m["days"] == ["2026-11-01", "2026-11-02"]
    assert m["badges"] == ["phase00", "phase01"]
    assert m["rv"] == {"2026-11-08": 25, "2026-11-09": 5}   # max per day
    assert P.merge(b, a) == m                                # commutative
    assert P.merge(m, m) == m                                # idempotent


def test_merge_xp_is_at_least_both_sides_even_with_rv():
    assert P.merge({"xp": 5, "rv": {"2026-11-09": 25}}, {"xp": 3})["xp"] == 5


def test_export_import_roundtrip_is_base64url_without_padding():
    s = P.new_state()
    P.answer(s, L1, 0, True, D)
    P.mission(s, L1, D)
    code = P.export_code(s)
    assert "=" not in code and "+" not in code and "/" not in code and code.isascii()
    assert P.import_code(code) == s
    assert P.import_code(code + "==") == s           # padding tolerated
    assert P.import_code("  " + code + "\n") == s


def test_import_rejects_garbage():
    for bad in ("", "###", "bm90IGpzb24", "W10"):
        with pytest.raises(ValueError):
            P.import_code(bad)


def test_save_load_roundtrip_and_path(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "x"))
    assert P.progress_path() == tmp_path / "x" / "robotics-course" / "progress.json"
    monkeypatch.delenv("XDG_STATE_HOME")
    assert P.progress_path().as_posix().endswith(".local/state/robotics-course/progress.json")
    path = tmp_path / "p" / "progress.json"
    assert P.load(path) == P.new_state()
    s = P.new_state()
    P.answer(s, L1, 0, True, D)
    P.save(s, path)
    assert P.load(path) == s
    path.write_text("{not json")
    assert P.load(path) == P.new_state()            # corrupt file does not crash


# ---- daily 5 ----------------------------------------------------------------
def test_daily_awards_5_each_and_caps_at_25_per_day():
    s = P.new_state()
    assert P.daily_remaining(s, D) == 25
    got = [P.daily_award(s, True, D) for _ in range(7)]
    assert got == [5, 5, 5, 5, 5, 0, 0]
    assert s["rv"] == {"2026-11-09": 25} and s["xp"] == 25
    assert P.daily_remaining(s, D) == 0
    assert P.daily_remaining(s, D + dt.timedelta(days=1)) == 25   # new local day, new budget


def test_daily_partial_cap_and_wrong_answers():
    s = P.new_state()
    s["rv"] = {"2026-11-09": 22}
    assert P.daily_award(s, False, D) == 0
    assert P.daily_award(s, True, D) == 3            # only 3 XP left of the cap
    assert s["rv"]["2026-11-09"] == 25 and s["xp"] == 3


def test_daily_does_not_touch_question_record_and_stamps_day():
    s = P.new_state()
    P.daily_award(s, True, D)
    assert s["q"] == {} and s["days"] == ["2026-11-09"]


def test_daily_pool_uses_answered_lessons_else_any():
    s = P.new_state()
    all_ids = [L1, L2, L3]
    assert P.daily_lessons(s, all_ids) == all_ids
    P.answer(s, L2, 0, False, D)
    assert P.daily_lessons(s, all_ids) == [L2]


# ---- canonical schema shared with the website -------------------------------------------
import base64
import json


def _code(obj):
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip("=")


def test_xp_is_a_finite_int_in_range():
    n = lambda v: P.normalize({"xp": v})["xp"]
    assert n(0) == 0 and n(10_000_000) == 10_000_000 and n(120) == 120
    assert n(10_000_001) == 0 and n(-5) == 0 and n(True) == 0 and n("9") == 0 and n(1.5) == 0
    assert n(float("inf")) == 0 and n(float("nan")) == 0 and n([1]) == 0 and n(10 ** 400) == 0


def test_q_schema_ids_indexes_and_values():
    good = "03-02-gravity-compensation"
    s = P.normalize({"q": {good: {"0": 1, "5": 0, "6": 1, "05": 1, "-1": 1, "x": 1, "1": True, "2": "1", "3": 1.5, "4": [1]},
                           "3-02-bad": {"0": 1}, "03-02-UPPER": {"0": 1}, "03-" + "a" * 81: {"0": 1},
                           "__proto__": {"0": 1}, "constructor": {"0": 1}, "03-02-x\n": {"0": 1}}})
    assert s["q"] == {good: {"0": 1, "5": 0}}


def test_m_value_must_be_exactly_one():
    s = P.normalize({"m": {"03-02-a": 1, "03-03-b": 0, "03-04-c": True, "03-05-d": "1", "03-06-e": 2, "bad": 1}})
    assert s["m"] == {"03-02-a": 1}


def test_days_format_and_limit():
    days = ["2026-11-09", "2026-11-09\n", "26-11-09", "2026-1-9", "x", 5, None]
    assert P.normalize({"days": days})["days"] == ["2026-11-09"]
    many = [(dt.date(2000, 1, 1) + dt.timedelta(days=i)).isoformat() for i in range(4100)]
    out = P.normalize({"days": many})["days"]
    assert len(out) == 4000 and out[-1] == many[-1] and out[0] == many[100] and out == sorted(out)   # newest 4000 kept, oldest 100 dropped


def test_badges_format():
    assert P.normalize({"badges": ["phase03", "phase3", "phase031", "Phase03", "phase03\n", 3, "phase03", "phase16"]})["badges"] == ["phase03", "phase16"]


def test_rv_range_and_types():
    rv = {"2026-11-09": 25, "2026-11-08": 0, "2026-11-07": 26, "2026-11-06": -1, "2026-11-05": True, "2026-11-04": "5", "2026-11-03": 2.5, "bad": 3}
    assert P.normalize({"rv": rv})["rv"] == {"2026-11-09": 25, "2026-11-08": 0}


def test_unknown_and_dangerous_keys_ignored_valid_kept():
    s = P.normalize({"xp": 50, "__proto__": {"xp": 9}, "constructor": 1, "prototype": 2, "extra": [1], "q": {"__proto__": {"0": 1}}, "badges": ["phase00"]})
    assert s == P.new_state() | {"xp": 50, "badges": ["phase00"]}
    assert "__proto__" not in json.dumps(s)


def test_import_code_length_limit_and_hostile_inputs():
    with pytest.raises(ValueError):
        P.import_code("A" * 200_001)
    deep = base64.urlsafe_b64encode(b"[" * 100_000).decode()
    for bad in (deep, _code({"xp": 1})[:-3] + "!!", base64.urlsafe_b64encode(b"\xff\xfe").decode(),
                base64.urlsafe_b64encode(b"1" * 5000).decode()):
        with pytest.raises(ValueError):
            P.import_code(bad)
    ok = P.import_code(_code({"xp": 1e999, "q": {"03-02-a": {"0": 1}}, "rv": {"2026-11-09": 99}}))
    assert ok["xp"] == 0 and ok["q"] == {"03-02-a": {"0": 1}} and ok["rv"] == {}


def test_load_applies_schema_and_survives_hostile_file(tmp_path):
    path = tmp_path / "p.json"
    path.write_text(json.dumps({"xp": 99999999, "q": {"03-02-a": {"0": 1, "9": 1}}, "m": {"03-02-a": 3}}))
    assert P.load(path) == P.new_state() | {"q": {"03-02-a": {"0": 1}}}
    path.write_text("[" * 100_000)
    assert P.load(path) == P.new_state()
    path.write_bytes(b"\xff\xfe\x00")
    assert P.load(path) == P.new_state()


def test_merge_with_canonical_schema_never_lowers():
    a = {"xp": 10, "q": {"03-02-a": {"0": 1}}, "days": ["2026-11-01"]}
    b = {"xp": 5, "q": {"03-02-a": {"0": 0, "1": 1}}, "rv": {"2026-11-09": 25}}
    m = P.merge(a, b)
    assert m["xp"] == 10 and m["q"]["03-02-a"] == {"0": 1, "1": 1} and m["rv"] == {"2026-11-09": 25}


# ---- persistence: unique temp file, fsync, reload-merge-save under a lock -----------------
def test_save_merges_with_what_another_process_wrote(tmp_path):
    path = tmp_path / "progress.json"
    mine = P.load(path)                              # this process read an empty file at start
    other = P.new_state()
    P.answer(other, L1, 0, True, D)
    P.save(other, path)                              # another process saves meanwhile
    P.answer(mine, L1, 1, True, D)
    P.mission(mine, L2, D)
    P.save(mine, path)                               # must not erase the other process's answer
    on_disk = P.load(path)
    assert on_disk["q"][L1] == {"0": 1, "1": 1} and on_disk["m"] == {L2: 1} and on_disk["xp"] == 30   # xp merges by max, as on the website
    assert mine == on_disk                           # in-memory state adopts the merged result


def test_save_never_lowers_xp_or_answers(tmp_path):
    path = tmp_path / "progress.json"
    big = P.new_state()
    big["xp"] = 500
    big["q"] = {L1: {"0": 1}}
    P.save(big, path)
    P.save(P.new_state(), path)
    assert P.load(path)["xp"] == 500 and P.load(path)["q"] == {L1: {"0": 1}}


def test_save_uses_mkstemp_in_same_dir_fsync_and_replace(tmp_path, monkeypatch):
    path = tmp_path / "sub" / "progress.json"
    seen = {"dir": None, "fsync": 0, "replace": None}
    real_mkstemp, real_fsync, real_replace = P.tempfile.mkstemp, P.os.fsync, P.os.replace
    monkeypatch.setattr(P.tempfile, "mkstemp", lambda **k: (seen.__setitem__("dir", k.get("dir")), real_mkstemp(**k))[1])
    monkeypatch.setattr(P.os, "fsync", lambda fd: (seen.__setitem__("fsync", seen["fsync"] + 1), real_fsync(fd))[1])
    monkeypatch.setattr(P.os, "replace", lambda a, b: (seen.__setitem__("replace", (a, b)), real_replace(a, b))[1])
    P.save(P.new_state(), path)
    assert Path(seen["dir"]) == path.parent and seen["fsync"] >= 1
    assert Path(seen["replace"][0]).parent == path.parent and Path(seen["replace"][1]) == path
    assert sorted(p.name for p in path.parent.iterdir() if p.suffix == ".tmp") == []


def test_save_cleans_temp_file_when_write_fails(tmp_path, monkeypatch):
    path = tmp_path / "progress.json"
    monkeypatch.setattr(P.os, "replace", lambda a, b: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(OSError):
        P.save(P.new_state(), path)
    assert [p for p in tmp_path.iterdir() if p.suffix == ".tmp"] == []


def test_save_works_without_fcntl(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "fcntl", None)
    P.save(P.new_state(), tmp_path / "progress.json")
    assert (tmp_path / "progress.json").exists()


def test_concurrent_saves_from_threads_lose_nothing(tmp_path):
    import threading
    path = tmp_path / "progress.json"
    def work(i):
        s = P.new_state()
        P.answer(s, f"0{i}-x", 0, True, D)
        P.save(s, path)
    ts = [threading.Thread(target=work, args=(i,)) for i in range(8)]
    [t.start() for t in ts]; [t.join() for t in ts]
    assert sorted(P.load(path)["q"]) == [f"0{i}-x" for i in range(8)]
