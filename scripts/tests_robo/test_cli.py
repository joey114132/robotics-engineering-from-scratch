# CLI 명령 테스트 (가짜 코스 + 임시 진행 파일, 비 TTY 라서 plain 출력)
import io
import json
import re

import pytest
from rich.cells import cell_len

from robo import cli, progress as P

ANSI = re.compile(r"\x1b\[")


@pytest.fixture
def env(course, state_home, monkeypatch):
    monkeypatch.setenv("ROBO_ROOT", str(course))
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("ROBO_FAST", "1")           # no animation sleeps

    def run(*argv, stdin=""):
        monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
        return cli.main(list(argv))
    return run


def state():
    return P.load(P.progress_path())


def test_home_plain(env, capsys):
    assert env() == 0
    out = capsys.readouterr().out
    assert not ANSI.search(out)
    assert "ROBO" in out.replace(" ", "").upper() and "Alpha Tools" in out and "0/2" in out
    assert "Loose Bolt" in out and "00-01" in out and "robo read" in out


def test_home_ko(env, capsys):
    assert env("--lang", "ko") == 0
    out = capsys.readouterr().out
    assert "헐거운 볼트" in out and "다음" in out


def test_map_lists_every_lesson_with_state(env, capsys):
    s = P.new_state()
    import datetime as dt
    for i in range(6):
        P.answer(s, "00-01-first-steps", i, True, dt.date.today())
    P.mission(s, "00-01-first-steps", dt.date.today())
    P.save(s, P.progress_path())
    assert env("map", "--no-pager") == 0
    out = capsys.readouterr().out
    assert not ANSI.search(out)
    for short in ("00-01", "00-02", "01-01"):
        assert short in out
    line_first = next(l for l in out.splitlines() if "First Steps" in l)
    line_second = next(l for l in out.splitlines() if "Second Wind" in l)
    assert "[x]" in line_first and "[>]" in line_second     # done and current markers in plain mode


def test_read_plain_is_clean(env, capsys):
    assert env("read", "00-01", "--plain", "--no-pager") == 0
    out = capsys.readouterr().out
    assert not ANSI.search(out)
    assert "First Steps" in out and "Hook text." in out
    assert "figure: Caption of the red square" in out
    assert "print('hi')" in out and "`inline`" in out
    assert "|" in out or "+--" in out                       # table survives
    assert all(cell_len(l) <= 100 for l in out.splitlines())


def test_read_ko(env, capsys):
    assert env("read", "second", "--lang", "ko", "--plain", "--no-pager") == 0
    out = capsys.readouterr().out
    assert "(한글)" in out and "훅 문장입니다." in out and "한 줄 요약입니다." in out


def test_read_unknown_lesson(env, capsys):
    assert env("read", "zzz") == 2
    assert "zzz" in capsys.readouterr().err


def test_read_real_lesson_head_is_clean(capsys, monkeypatch, state_home):
    monkeypatch.delenv("ROBO_ROOT", raising=False)
    assert cli.main(["read", "03-02", "--plain", "--no-pager"]) == 0
    out = capsys.readouterr().out
    assert "Gravity Compensation" in out and not ANSI.search(out) and "figure:" in out
    assert max(cell_len(l) for l in out.splitlines()) <= 100


def test_quiz_perfect_awards_60_once_and_replay_awards_nothing(env, capsys):
    assert env("quiz", "00-01", "--plain", stdin="1\n1\n1\n1\n1\n1\ny\n1\n1\n1\n1\n1\n1\nn\n") == 0
    out = capsys.readouterr().out
    assert not ANSI.search(out)
    assert "Warm-up" in out and "Checks" in out and "Boss round" in out
    assert "6/6" in out and "+60" in out and out.count("+0") >= 1
    s = state()
    assert s["xp"] == 60 and len(s["q"]["00-01-first-steps"]) == 6


def test_quiz_wrong_answers_are_kind_and_stars_follow_score(env, capsys):
    assert env("quiz", "00-01", "--plain", stdin="2\n2\n2\n2\n2\n2\nn\n") == 0
    out = capsys.readouterr().out
    assert "0/6" in out and "explanation" in out.lower()
    assert "lives" not in out.lower() and "game over" not in out.lower()
    assert state()["xp"] == 0
    assert out.count("*") >= 1 or "★" in out or "✦" in out


@pytest.mark.parametrize("score,stars", [(6, 3), (5, 2), (4, 2), (3, 1), (0, 1)])
def test_stars_rule(score, stars):
    from robo import quiz
    assert quiz.stars_for(score, 6) == stars


@pytest.mark.parametrize("score,stars", [(5, 3), (4, 2), (3, 1), (2, 1), (0, 1)])
def test_stars_rule_five_questions_matches_the_site(score, stars):
    from robo import quiz
    assert quiz.stars_for(score, 5) == stars       # ceil(2*5/3) = 4 is the two-star threshold, not 3


def test_combo_is_display_only(env, capsys):
    env("quiz", "00-01", "--plain", stdin="1\n1\n2\n1\n1\n1\nn\n")
    out = capsys.readouterr().out
    assert "combo x2" in out.lower() and "combo x3" in out.lower()
    assert state()["xp"] == 50                               # 5 correct x 10, combo adds nothing


def test_quiz_ko_uses_korean_labels(env, capsys):
    env("quiz", "00-01", "--plain", "--lang", "ko", stdin="1\n1\n1\n1\n1\n1\nn\n")
    out = capsys.readouterr().out
    assert "워밍업" in out and "체크" in out and "보스전" in out and "KO question" in out


def test_quiz_input_accepts_letters_and_reprompts_junk(env, capsys):
    env("quiz", "00-01", "--plain", stdin="x\n9\na\n1\n1\n1\n1\n1\nn\n")
    assert state()["xp"] == 60


def test_quiz_eof_stops_without_crash_and_keeps_progress(env, capsys):
    assert env("quiz", "00-01", "--plain", stdin="1\n1\n") == 1
    assert state()["xp"] == 20


def test_mission_card_and_done(env, capsys):
    assert env("mission", "00-01", "--plain") == 0
    out = capsys.readouterr().out
    assert "Do the `thing`." in out or "Do the thing." in out
    assert env("mission", "00-01", "--done", "--plain") == 0
    assert "+20" in capsys.readouterr().out
    assert env("mission", "00-01", "--done", "--plain") == 0
    assert state()["xp"] == 20 and state()["m"] == {"00-01-first-steps": 1}


def test_play_toys(env, capsys):
    assert env("play", "pd-step", "--kp", "30", "--kd", "4", "--plain") == 0
    out = capsys.readouterr().out
    assert "overshoot" in out.lower() and "settle" in out.lower() and not ANSI.search(out)
    assert env("play", "sampling-limit", "--r", "1.5", "--plain") == 0
    assert "chatter" in capsys.readouterr().out
    assert env("play", "kalman", "--q", "0.1", "--r", "2.0", "--plain") == 0
    assert "gain" in capsys.readouterr().out.lower()
    assert env("play", "nope", "--plain") == 2


def test_stats_plain(env, capsys):
    assert env("stats", "--plain") == 0
    out = capsys.readouterr().out
    assert "XP" in out and "streak" in out.lower() and not ANSI.search(out)
    assert len([l for l in out.splitlines() if re.search(r"[.#]{12}", l)]) >= 7   # 7 weekday rows


def test_sync_export_import_roundtrip(env, capsys, tmp_path, monkeypatch):
    s = P.new_state()
    import datetime as dt
    P.answer(s, "00-01-first-steps", 0, True, dt.date.today())
    P.save(s, P.progress_path())
    assert env("sync", "export") == 0
    code = capsys.readouterr().out.strip().splitlines()[-1]
    assert P.import_code(code)["xp"] == 10
    other = tmp_path / "other"
    monkeypatch.setenv("XDG_STATE_HOME", str(other))
    assert state()["xp"] == 0
    assert env("sync", "import", code) == 0
    assert state()["xp"] == 10
    assert env("sync", "import", "###") == 2


def test_daily_uses_answered_lessons_and_caps(env, capsys):
    s = P.new_state()
    import datetime as dt
    P.answer(s, "00-02-second-wind", 0, False, dt.date.today())
    P.save(s, P.progress_path())
    assert env("daily", "--plain", "--seed", "1", stdin="1\n1\n1\n1\n1\n") == 0
    out = capsys.readouterr().out
    assert out.count("second-wind") + out.count("00-02") >= 1 and "01-01" not in out
    s = state()
    assert s["xp"] == 25 and list(s["rv"].values()) == [25]
    assert env("daily", "--plain", "--seed", "2", stdin="1\n1\n1\n1\n1\n") == 0
    out = capsys.readouterr().out
    assert "25/25" in out and state()["xp"] == 25


def test_help_is_pretty_and_lists_commands(env, capsys):
    assert env("--help") == 0
    out = capsys.readouterr().out
    for c in ("read", "quiz", "mission", "play", "stats", "sync", "map", "daily"):
        assert c in out
    assert "--lang" in out and "--plain" in out and "completion" in out.lower()
    assert env("quiz", "--help") == 0
    assert "lesson" in capsys.readouterr().out.lower()


def test_completion_script(env, capsys):
    assert env("completion", "bash") == 0
    assert "complete -F" in capsys.readouterr().out
    assert env("completion", "zsh") == 0
    assert "compdef" in capsys.readouterr().out


def test_ids_lists_short_ids_for_completion(env, capsys):
    assert env("ids") == 0
    assert capsys.readouterr().out.split() == ["00-01", "00-02", "01-01"]


def test_quiz_progress_saved_after_each_answer_and_badge_on_phase_complete(env, capsys):
    for lid in ("00-01", "00-02"):
        env("quiz", lid, "--plain", stdin="1\n1\n1\n1\n1\n1\nn\n")
        env("mission", lid, "--done", "--plain")
    out = capsys.readouterr().out
    assert "Badge earned: phase 00" in out and state()["badges"] == ["phase00"]
    assert state()["xp"] == 2 * (60 + 20)


def test_mission_and_quiz_never_lower_progress(env, capsys):
    env("quiz", "00-01", "--plain", stdin="1\n1\n1\n1\n1\n1\nn\n")
    xp = state()["xp"]
    env("quiz", "00-01", "--plain", stdin="2\n2\n2\n2\n2\n2\nn\n")
    assert state()["xp"] == xp and sum(state()["q"]["00-01-first-steps"].values()) == 6


def test_stdout_is_not_a_tty_so_default_is_plain(env, capsys):
    env("stats")
    assert not ANSI.search(capsys.readouterr().out)


# ---- codex round 3 --------------------------------------------------------------------
@pytest.mark.parametrize("bad", ["A" * 200_001, __import__("base64").urlsafe_b64encode(b"[" * 100_000).decode(),
                                 __import__("base64").urlsafe_b64encode(b"1" * 5000).decode(), "###", "e30"])
def test_sync_import_errors_are_one_friendly_line_exit_2(env, capsys, bad):
    assert env("sync", "import", bad) == 2
    err = capsys.readouterr().err
    assert err.count("\n") == 1 and "Traceback" not in err and "progress code" in err


@pytest.mark.parametrize("argv", [("--kp", "5000"), ("--kp", "-1"), ("--kd", "1001"), ("--kd", "nan"), ("--kp", "inf")])
def test_play_pd_step_rejects_out_of_range(env, capsys, argv):
    assert env("play", "pd-step", *argv) == 2
    err = capsys.readouterr().err
    assert "play" in err and argv[0] in err and "Traceback" not in err


@pytest.mark.parametrize("toy,argv", [("sampling-limit", ("--r", "0.01")), ("sampling-limit", ("--r", "5.5")), ("sampling-limit", ("--r", "nan")),
                                      ("kalman", ("--q", "0")), ("kalman", ("--q", "101")), ("kalman", ("--r", "0.0001")), ("kalman", ("--r", "1000"))])
def test_play_rejects_out_of_range_for_each_toy(env, capsys, toy, argv):
    assert env("play", toy, *argv) == 2
    assert argv[0] in capsys.readouterr().err


def test_play_accepts_the_boundaries(env, capsys):
    for toy, argv in (("pd-step", ("--kp", "1000", "--kd", "1000")), ("pd-step", ("--kp", "0", "--kd", "0")), ("pd-step", ("--kp", "1000", "--kd", "0")),
                      ("sampling-limit", ("--r", "0.05")), ("sampling-limit", ("--r", "5")),
                      ("kalman", ("--q", "0.001", "--r", "0.001")), ("kalman", ("--q", "100", "--r", "100"))):
        assert env("play", toy, "--plain", *argv) == 0, (toy, argv)
        out = capsys.readouterr().out
        assert "inf" not in out.lower().replace("information", "") and "nan" not in out.lower()


def test_zsh_completion_describes_commands_separately(env, capsys):
    assert env("completion", "zsh") == 0
    out = capsys.readouterr().out
    assert "_describe" in out and "compdef _robo robo" in out
    import re
    entries = re.findall(r"^\s+'([a-z]+):(.*)'$", out, re.M)
    assert [e[0] for e in entries] == [c[0] for c in cli.COMMANDS]
    assert all(desc and not re.search(r"(?<!\\):", desc) for _, desc in entries)   # colons in descriptions are escaped


def test_narrow_terminal_prints_notice_on_stderr_only_when_interactive(env, capsys, monkeypatch):
    monkeypatch.setattr(cli, "_stdout_isatty", lambda: True)
    monkeypatch.setattr(cli, "_term_columns", lambda: 50)
    env("stats", "--plain")
    err = capsys.readouterr().err
    assert "needs at least 60 columns, output may wrap" in err
    monkeypatch.setattr(cli, "_term_columns", lambda: 80)
    env("stats", "--plain")
    assert "60 columns" not in capsys.readouterr().err
    monkeypatch.setattr(cli, "_term_columns", lambda: 50)
    monkeypatch.setattr(cli, "_stdout_isatty", lambda: False)
    env("stats", "--plain")
    assert "60 columns" not in capsys.readouterr().err


def test_help_states_the_60_column_minimum(env, capsys):
    env("--help")
    assert "60 columns" in capsys.readouterr().out


def test_today_is_resolved_at_each_award(env, capsys, monkeypatch):
    import datetime as dt
    days = iter([dt.date(2026, 11, 9)] * 3 + [dt.date(2026, 11, 10)] * 3 + [dt.date(2026, 11, 10)] * 20)
    monkeypatch.setattr(cli, "_today", lambda: next(days))
    env("quiz", "00-01", "--plain", stdin="1\n1\n1\n1\n1\n1\nn\n")
    assert {"2026-11-09", "2026-11-10"} <= set(state()["days"])


def test_daily_cap_uses_the_day_of_each_award(env, capsys, monkeypatch):
    import datetime as dt
    s = P.new_state()
    P.answer(s, "00-02-second-wind", 0, False, dt.date(2026, 11, 8))
    P.save(s, P.progress_path())
    seq = [dt.date(2026, 11, 9)] * 4 + [dt.date(2026, 11, 10)] * 40   # call 1 is the command start, then 3 awards before midnight, 2 after
    it = iter(seq)
    monkeypatch.setattr(cli, "_today", lambda: next(it))
    env("daily", "--plain", "--seed", "1", stdin="1\n1\n1\n1\n1\n")
    rv = state()["rv"]
    assert sum(rv.values()) == 25 and len(rv) == 2           # awards straddling midnight land on two different days


def test_quiz_does_not_overwrite_progress_saved_by_another_process(env, capsys, monkeypatch):
    other = P.new_state()
    P.answer(other, "00-02-second-wind", 0, True, cli._today())
    real_save = P.save
    calls = {"n": 0}
    def save_with_interference(s, path=None):
        calls["n"] += 1
        if calls["n"] == 2:                       # another process writes between two of our saves
            real_save(other, path)
        return real_save(s, path)
    monkeypatch.setattr(P, "save", save_with_interference)
    env("quiz", "00-01", "--plain", stdin="1\n1\n1\n1\n1\n1\nn\n")
    s = state()
    assert s["q"]["00-02-second-wind"] == {"0": 1} and len(s["q"]["00-01-first-steps"]) == 6 and s["xp"] == 60   # xp merges by max, never lowers
