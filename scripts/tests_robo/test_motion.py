# 모션 기반 시설 테스트: ease, 켜짐/꺼짐 규칙, 인트로 프레임, 하루 한 번, 프레임 루프(키 건너뛰기, Ctrl-C 커서 복원), 막대와 별 애니메이션
import io
import re

import pytest
from rich.cells import cell_len

from robo import motion, progress as P, quiz as Q, ui

ANSI = re.compile(r"\x1b\[")
HIDE, SHOW = "\x1b[?25l", "\x1b[?25h"


def term_ui(width=80, lang="en"):
    """색이 켜진 가짜 TTY 콘솔(출력은 StringIO 에 쌓인다)."""
    buf = io.StringIO()
    return ui.make_ui(plain=False, width=width, force_color=True, file=buf, lang=lang, dark=True), buf


class Clock:
    """now() 와 sleep() 이 같은 가짜 시간을 쓴다."""

    def __init__(self):
        self.t, self.sleeps = 0.0, []

    def now(self):
        return self.t

    def sleep(self, dt):
        self.sleeps.append(dt)
        self.t += dt


def test_ease_out_is_monotone_and_bounded():
    xs = [i / 50 for i in range(51)]
    ys = [motion.ease_out(x) for x in xs]
    assert ys[0] == 0 and ys[-1] == 1 and all(a <= b for a, b in zip(ys, ys[1:]))
    assert motion.ease_out(0.5) > 0.5                      # ease-out: fast first, slow last
    assert motion.ease_out(-1) == 0 and motion.ease_out(9) == 1


def test_bar_scale_reaches_one_in_half_a_second():
    assert motion.bar_scale(0) == 0 and motion.bar_scale(0.5) == 1 and motion.bar_scale(3) == 1
    assert 0 < motion.bar_scale(0.1) < motion.bar_scale(0.3) < 1


@pytest.mark.parametrize("case,expect", [("ok", True), ("plain", False), ("no_color", False), ("no_anim", False), ("fast", False), ("not_tty", False)])
def test_anim_enabled_rules(monkeypatch, case, expect):
    for k in ("NO_COLOR", "ROBO_NO_ANIM", "ROBO_FAST"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: case != "not_tty")
    u, _ = term_ui()
    if case == "plain":
        u = ui.make_ui(plain=True, width=80)
    if case == "no_color":
        monkeypatch.setenv("NO_COLOR", "1")
    if case == "no_anim":
        monkeypatch.setenv("ROBO_NO_ANIM", "1")
    if case == "fast":
        monkeypatch.setenv("ROBO_FAST", "1")
    assert motion.anim_enabled(u) is expect


def test_console_that_is_not_a_terminal_never_animates(monkeypatch):
    for k in ("NO_COLOR", "ROBO_NO_ANIM", "ROBO_FAST"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: True)
    u = ui.make_ui(plain=False, width=80, file=io.StringIO())      # StringIO is not a terminal
    assert motion.anim_enabled(u) is False


# ---- intro frames -----------------------------------------------------------------------------
HUD = ui.Text("XP 10   Level 1 Loose Bolt")


def banner_cells(t, width=100):
    u, _ = term_ui(width)
    frame = motion.intro_frame(u, HUD, t)
    return u, frame


def count_blocks(frame):
    return sum(ch in "█▀▄" for ch in frame.plain)


def test_intro_frame_is_deterministic_and_has_constant_height():
    heights = set()
    for t in (0.0, 0.2, 0.6, 1.0, 1.2, 2.0):
        _, a = banner_cells(t)
        _, b = banner_cells(t)
        assert a == b and a.plain == b.plain
        heights.add(a.plain.count("\n"))
    assert len(heights) == 1


def test_intro_sweep_reveals_banner_left_to_right_and_hud_fades_in_last():
    _, f0 = banner_cells(0.0)
    counts = [count_blocks(banner_cells(t)[1]) for t in (0.0, 0.15, 0.3, 0.5, 0.75, 1.2)]
    assert counts[0] == 0 and counts == sorted(counts) and counts[-1] > counts[1] > 0
    mid = banner_cells(0.3)[1].plain.splitlines()
    full = banner_cells(1.2)[1].plain.splitlines()
    # left part already drawn, right part still empty while the sweep is in the middle
    row = next(i for i, l in enumerate(full) if "█" in l or "▀" in l)
    left = mid[row][: len(mid[row]) // 3]
    right = mid[row][len(mid[row]) * 2 // 3 :]
    assert any(c in "█▀▄" for c in left) and not any(c in "█▀▄" for c in right.split("   ")[0])
    assert "XP 10" not in banner_cells(0.5)[1].plain and "XP 10" in banner_cells(1.2)[1].plain
    dim = banner_cells(0.85)[1]
    assert "XP 10" in dim.plain and any("dim" in str(s.style) for s in dim.spans)       # fading in = dim step


def test_intro_final_frame_matches_the_static_banner():
    u, f = banner_cells(motion.INTRO_SECONDS)
    buf = io.StringIO()
    u2 = ui.make_ui(plain=False, width=100, force_color=True, file=buf, dark=True)
    ui.print_banner(u2, tagline=None)
    static_rows = [re.sub(r"\x1b\[[0-9;]*m", "", l).rstrip() for l in buf.getvalue().splitlines() if "█" in l or "▀" in l or "▄" in l]
    shown = [l.rstrip() for l in f.plain.splitlines() if "█" in l or "▀" in l or "▄" in l]
    assert [l[:len(s)] for l, s in zip(shown, static_rows)] == [s for s in static_rows[:len(shown)]]


def test_intro_marker_lives_beside_progress_json_not_in_it(state_home):
    import datetime as dt
    d = dt.date(2026, 11, 9)
    assert motion.intro_due(d)
    motion.mark_intro(d)
    marker = P.progress_path().parent / "last-intro"
    assert marker.read_text().strip() == "2026-11-09" and not P.progress_path().exists()
    assert not motion.intro_due(d) and motion.intro_due(d + dt.timedelta(days=1))
    P.save(P.new_state())
    assert "last-intro" not in P.progress_path().read_text()
    marker.write_text("garbage")
    assert motion.intro_due(d)


# ---- frame loop ----------------------------------------------------------------------------------
def test_run_frames_runs_for_the_duration_at_the_given_fps():
    u, buf = term_ui()
    c = Clock()
    seen = []
    r = motion.run_frames(u, lambda t: (seen.append(t), ui.Text(f"t={t:.2f}"))[1], duration=1.0, fps=10, sleep=c.sleep, now=c.now)
    assert r == "done" and 9 <= len(seen) <= 12 and all(abs(s - 0.1) < 1e-9 for s in c.sleeps)
    assert buf.getvalue().startswith(HIDE) or HIDE in buf.getvalue()
    assert buf.getvalue().rstrip().endswith(SHOW) or SHOW in buf.getvalue()


def test_run_frames_stops_on_a_key_and_shows_the_final_frame():
    u, buf = term_ui()
    c = Clock()
    polls = iter([False, False, True] + [True] * 20)
    r = motion.run_frames(u, lambda t: ui.Text("frame"), duration=5.0, fps=10, sleep=c.sleep, now=c.now, poll=lambda: next(polls),
                          final=lambda: ui.Text("FINAL"))
    assert r == "key" and len(c.sleeps) == 2 and "FINAL" in buf.getvalue()


def test_run_frames_restores_the_cursor_on_keyboard_interrupt():
    u, buf = term_ui()
    c = Clock()
    n = {"i": 0}

    def sleep(dt):
        n["i"] += 1
        if n["i"] == 3:
            raise KeyboardInterrupt
        c.sleep(dt)

    r = motion.run_frames(u, lambda t: ui.Text("x"), duration=None, fps=15, sleep=sleep, now=c.now)
    out = buf.getvalue()
    assert r == "interrupt" and HIDE in out and out.rindex(SHOW) > out.rindex(HIDE)


def test_run_frames_keyboard_interrupt_from_polling_also_restores_cursor():
    u, buf = term_ui()
    c = Clock()

    def poll():
        raise KeyboardInterrupt

    assert motion.run_frames(u, lambda t: ui.Text("x"), duration=2, fps=15, sleep=c.sleep, now=c.now, poll=poll) == "interrupt"
    assert buf.getvalue().rindex(SHOW) > buf.getvalue().rindex(HIDE)


def test_play_intro_does_nothing_when_disabled(monkeypatch):
    for k in ("NO_COLOR", "ROBO_NO_ANIM", "ROBO_FAST"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: False)
    u, buf = term_ui()
    c = Clock()
    assert motion.play_intro(u, HUD, sleep=c.sleep, now=c.now, poll=lambda: False) == "disabled"
    assert buf.getvalue() == "" and c.sleeps == []


def test_play_intro_runs_about_1_2_seconds_and_ends_on_the_final_frame(monkeypatch):
    for k in ("NO_COLOR", "ROBO_NO_ANIM", "ROBO_FAST"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: True)
    u, buf = term_ui(100)
    c = Clock()
    assert motion.play_intro(u, HUD, sleep=c.sleep, now=c.now, poll=lambda: False) == "done"
    assert 1.1 <= c.t <= 1.4 and "XP 10" in re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", buf.getvalue())


def test_play_intro_ctrl_c_is_a_skip_not_an_exit(monkeypatch):
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: True)
    for k in ("NO_COLOR", "ROBO_NO_ANIM", "ROBO_FAST"):
        monkeypatch.delenv(k, raising=False)
    u, buf = term_ui(100)
    c = Clock()
    n = {"i": 0}

    def sleep(dt):
        n["i"] += 1
        if n["i"] == 2:
            raise KeyboardInterrupt
        c.sleep(dt)

    assert motion.play_intro(u, HUD, sleep=sleep, now=c.now, poll=lambda: False) == "interrupt"
    assert "XP 10" in re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", buf.getvalue()) and buf.getvalue().rindex(SHOW) > buf.getvalue().rindex(HIDE)


# ---- bars ---------------------------------------------------------------------------------------------
def bar_line(scale):
    return ui.bar_text(0.8 * scale, 20, plain=False)


def test_animate_fills_bars_from_zero_with_ease_out_then_prints_the_final(monkeypatch):
    for k in ("NO_COLOR", "ROBO_NO_ANIM", "ROBO_FAST"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: True)
    u, buf = term_ui()
    c = Clock()
    fills = []

    def build(scale):
        fills.append(scale)
        return bar_line(scale)

    motion.animate(u, build, sleep=c.sleep, now=c.now)
    assert fills[0] == 0 and fills[-1] == 1 and fills == sorted(fills) and len(fills) >= 8
    assert 0.45 <= c.t <= 0.7
    assert max(fills[1:3]) > 0.15                        # ease-out starts quickly
    assert "▂" not in buf.getvalue()


def test_animate_prints_once_without_sleeping_when_disabled(monkeypatch):
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: False)
    u, buf = term_ui()
    c = Clock()
    motion.animate(u, bar_line, sleep=c.sleep, now=c.now)
    assert c.sleeps == [] and buf.getvalue().count("━") == 16


# ---- stars -----------------------------------------------------------------------------------------------
def card(u, score, total, animate, sleep):
    st = P.new_state()
    Q.results_card(u, score, total, 10 * score, st, "Results", animate=animate, sleep=sleep)


def test_stars_appear_one_by_one_0_2_seconds_apart(monkeypatch):
    for k in ("NO_COLOR", "ROBO_NO_ANIM", "ROBO_FAST"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: True)
    u, buf = term_ui(80)
    sleeps = []
    card(u, 6, 6, True, sleeps.append)
    assert sleeps == [0.2, 0.2, 0.2]
    out = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", buf.getvalue())
    assert "✦ ✦ ✦" in out
    sleeps.clear()
    card(term_ui(80)[0], 4, 6, True, sleeps.append)
    assert sleeps == [0.2, 0.2]


def test_stars_are_static_when_animation_is_off(monkeypatch):
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: False)
    u, buf = term_ui(80)
    sleeps = []
    card(u, 6, 6, True, sleeps.append)
    assert sleeps == [] and "✦ ✦ ✦" in re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", buf.getvalue())


# ---- codex round 4 -----------------------------------------------------------------------------------------
def _anim_env(monkeypatch, tty=True):
    for k in ("NO_COLOR", "ROBO_NO_ANIM", "ROBO_FAST"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: tty)


def test_celebrate_follows_the_shared_animation_policy(monkeypatch):
    _anim_env(monkeypatch)
    u, buf = term_ui()
    sleeps = []
    Q.celebrate(u, sleep=sleeps.append)
    assert len(sleeps) >= 8 and buf.getvalue() != ""                    # animates when allowed
    for k, v in (("ROBO_NO_ANIM", "1"), ("NO_COLOR", "1"), ("ROBO_FAST", "1")):
        _anim_env(monkeypatch)
        monkeypatch.setenv(k, v)
        u, buf = term_ui()
        sleeps.clear()
        Q.celebrate(u, sleep=sleeps.append)
        assert sleeps == [] and buf.getvalue() == "", k
    _anim_env(monkeypatch, tty=False)
    u, buf = term_ui()
    Q.celebrate(u, sleep=sleeps.append)
    assert sleeps == [] and buf.getvalue() == ""
    Q.celebrate(ui.make_ui(plain=True, width=80), sleep=sleeps.append)
    assert sleeps == []


def test_perfect_quiz_and_daily_do_not_animate_with_robo_no_anim(course, state_home, monkeypatch, capsys):
    import io as _io
    from robo import cli
    monkeypatch.setenv("ROBO_ROOT", str(course))
    monkeypatch.setenv("ROBO_NO_ANIM", "1")
    monkeypatch.delenv("ROBO_FAST", raising=False)
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: True)
    called = []
    monkeypatch.setattr(Q.time, "sleep", lambda s: called.append(s))
    monkeypatch.setattr(motion.time, "sleep", lambda s: called.append(s))
    monkeypatch.setattr("sys.stdin", _io.StringIO("1\n1\n1\n1\n1\n1\nn\n"))
    cli.main(["quiz", "00-01", "--plain"])
    assert called == []


def test_resize_during_animation_updates_both_widths(monkeypatch):
    cols = [100]
    monkeypatch.setattr(ui, "term_columns", lambda: cols[0])
    buf = io.StringIO()
    u = ui.make_ui(plain=False, force_color=True, file=buf, dark=True)
    assert (u.width, u.console.width) == (100, 100)
    seen = []
    c = Clock()
    n = {"i": 0}

    def sleep(dt):
        n["i"] += 1
        if n["i"] == 3:
            cols[0] = 70
        if n["i"] == 6:
            cols[0] = 40
        c.sleep(dt)

    motion.run_frames(u, lambda t: (seen.append((u.width, u.console.width, u.read_width)), ui.Text("x"))[1], duration=1.0, fps=10, sleep=sleep, now=c.now)
    widths = [s[0] for s in seen]
    assert widths[0] == 100 and 70 in widths and widths[-1] == 60            # clamped to the 60-column minimum
    assert all(w == cw for w, cw, _ in seen) and all(r == min(w, ui.READ_WIDTH) for w, _, r in seen)
    assert u.below_min is True


def test_explicit_width_is_never_refreshed(monkeypatch):
    monkeypatch.setattr(ui, "term_columns", lambda: 50)
    u = ui.make_ui(plain=False, width=100, force_color=True, file=io.StringIO())
    c = Clock()
    motion.run_frames(u, lambda t: ui.Text("x"), duration=0.3, fps=10, sleep=c.sleep, now=c.now)
    assert (u.width, u.console.width) == (100, 100) and u.below_min is False


def test_scene_rows_follow_the_terminal_width_after_a_resize(monkeypatch):
    from robo import scenes
    _anim_env(monkeypatch)
    cols = [100]
    monkeypatch.setattr(ui, "term_columns", lambda: cols[0])
    u = ui.make_ui(plain=False, force_color=True, file=io.StringIO(), dark=True)
    rows = []
    real = scenes.scene_lines
    monkeypatch.setattr(scenes, "scene_lines", lambda uu, *a: (lambda ls: (rows.append((uu.width, max(ui.cell_len(l.plain) for l in ls))), ls)[1])(real(uu, *a)))
    c = Clock()
    polls = iter([False] * 3 + [True])

    def sleep(dt):
        if len(c.sleeps) == 2:
            cols[0] = 60
        c.sleep(dt)

    scenes.run_scene(u, "lidar", 8, sleep=sleep, now=c.now, poll=lambda: next(polls, True))
    assert rows[0][0] == 100 and rows[-1][0] == 60
    assert all(w_row <= w for w, w_row in rows) and rows[-1][1] <= 60 and rows[0][1] > 60


def test_scene_command_prints_the_60_column_notice_after_a_shrink(course, state_home, monkeypatch, capsys):
    from robo import cli
    monkeypatch.setenv("ROBO_ROOT", str(course))
    monkeypatch.setattr(cli.motion, "anim_enabled", lambda u: True)

    def fake_run(u, name, ph, **k):
        u.below_min = True
        return "interrupt"

    monkeypatch.setattr(cli.scenes, "run_scene", fake_run)
    assert cli.main(["scene", "05"]) == 0
    assert "needs at least 60 columns, output may wrap" in capsys.readouterr().err
