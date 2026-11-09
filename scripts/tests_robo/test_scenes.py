# 터미널 scene 테스트: 순수 함수 프레임(시간만으로 결정), 단계 매핑, 각 scene 의 물리/기하, robo scene 명령
import math
import re

import pytest
from rich.cells import cell_len

from robo import scenes, ui

ANSI = re.compile(r"\x1b\[")
NAMES = ["arm", "payload", "pubsub", "lidar", "tree", "swarm"]
CW, CH = 60, 14


def dots(name, t, cw=CW, ch=CH):
    cv = scenes.render_scene(name, t, cw, ch, "b", "d")
    return {(x, y) for y in range(cv.H) for x in range(cv.W) if cv.bits[y // 4][x // 2] & scenes.BITS[(x % 2, y % 4)]}


def test_six_scenes_with_the_documented_phases():
    assert scenes.SCENES == {"02": "arm", "03": "payload", "05": "pubsub", "08": "lidar", "09": "tree", "14": "swarm"}
    assert sorted(scenes.SCENES.values()) == sorted(NAMES)


def test_other_phases_map_to_the_nearest_scene_with_a_note():
    expected = {0: 2, 1: 2, 4: 3, 6: 5, 7: 8, 10: 9, 11: 9, 12: 14, 13: 14, 15: 14, 16: 14}
    for ph in range(17):
        name, note = scenes.scene_for_phase(ph)
        if f"{ph:02d}" in scenes.SCENES:
            assert note is None and name == scenes.SCENES[f"{ph:02d}"]
        else:
            assert name == scenes.SCENES[f"{expected[ph]:02d}"] and note == expected[ph]
    with pytest.raises(ValueError):
        scenes.scene_for_phase(17)


@pytest.mark.parametrize("name", NAMES)
def test_frames_are_deterministic_looping_and_alive(name):
    a, b = dots(name, 2.3), dots(name, 2.3)
    assert a == b and len(a) > 30
    assert dots(name, 1.1) == dots(name, 1.1 + scenes.LOOP) == dots(name, 1.1 + 2 * scenes.LOOP)
    assert dots(name, 0.5) != dots(name, 3.7)
    W, H = CW * 2, CH * 4
    assert all(0 <= x < W and 0 <= y < H for x, y in a)


@pytest.mark.parametrize("name", NAMES)
def test_scene_lines_are_rectangular_and_fit_the_width(name):
    u = ui.make_ui(plain=False, width=60, force_color=True, dark=True)
    lines = scenes.scene_lines(u, name, 2.0, 3)
    widths = {cell_len(l.plain) for l in lines}
    assert len(widths) == 1 and max(widths) <= 60 and len(lines) == scenes.H_CELLS
    assert scenes.scene_cols(u) >= 56 and scenes.scene_cols(ui.make_ui(plain=True, width=200)) <= 72


def test_arm_reaches_the_target_when_reachable_and_stops_at_full_reach_otherwise():
    W, H = 144, 56
    reach = scenes.ARM_L1 * H + scenes.ARM_L2 * H
    hit = 0
    for i in range(80):
        t = i * scenes.LOOP / 80
        base, elbow, tip, target = scenes.arm_pose(t, W, H)
        assert math.dist(base, elbow) == pytest.approx(scenes.ARM_L1 * H) and math.dist(elbow, tip) == pytest.approx(scenes.ARM_L2 * H)
        if math.dist(base, target) < reach - 1:
            assert math.dist(tip, target) < 1e-6
            hit += 1
        else:
            assert math.dist(base, tip) <= reach + 1e-6
    assert hit > 40


def test_payload_swings_and_settles():
    a0 = abs(scenes.payload_angle(0.0))
    assert a0 > 0.5 and abs(scenes.payload_angle(7.9)) < 0.1 * a0
    assert max(abs(scenes.payload_angle(t / 100)) for t in range(0, 150)) > 0.5 * a0
    assert scenes.payload_angle(0.3) == pytest.approx(scenes.payload_angle(0.3 + scenes.LOOP))


def test_pubsub_messages_ride_the_wires_and_loop_exactly():
    W, H = 144, 56
    wires = scenes.pubsub_wires(W, H)
    assert len(wires) >= 4
    for t in (0.0, 1.7, 5.9):
        msgs = scenes.pubsub_messages(t, W, H)
        assert msgs
        for wi, (x, y) in msgs:
            pts = wires[wi]
            d = min(scenes._dist_to_segment((x, y), a, b) for a, b in zip(pts, pts[1:]))
            assert d < 1e-6
    a, b = scenes.pubsub_messages(2.5, W, H), scenes.pubsub_messages(2.5 + scenes.LOOP, W, H)
    assert len(a) == len(b) and all(wa == wb and pa == pytest.approx(pb) for (wa, pa), (wb, pb) in zip(a, b))


def test_lidar_map_grows_and_hits_lie_on_surfaces():
    W, H = 144, 56
    counts = [len(scenes.lidar_hits(t, W, H)) for t in (0.5, 2.0, 5.0, 7.9)]
    assert counts == sorted(counts) and counts[-1] > counts[0] + 100
    segs = scenes.lidar_segments(W, H)
    for hx, hy in scenes.lidar_hits(7.9, W, H)[::7]:
        assert min(scenes._dist_to_segment((hx, hy), a, b) for a, b in segs) < 1e-6
    assert len(scenes.lidar_hits(0.0, W, H)) == 0 and len(scenes.lidar_hits(0.5, W, H)) == len(scenes.lidar_hits(0.5 + scenes.LOOP, W, H))


@pytest.mark.parametrize("size", [(144, 56), (112, 56), (120, 40)])
def test_rrt_is_deterministic_collision_free_and_reaches_the_goal(size):
    W, H = size
    tree = scenes.rrt(W, H)
    assert tree == scenes.rrt(W, H) and tree["goal"] is not None
    nodes = tree["nodes"]
    assert all(p < i for i, (_, _, p) in enumerate(nodes[1:], 1))
    for x, y, _ in nodes:
        assert all(math.hypot(x - cx, y - cy) > r for cx, cy, r in scenes.rrt_obstacles(W, H))
    path = scenes.rrt_path(tree)
    assert path[0] == 0 and path[-1] == tree["goal"]
    assert len(scenes.rrt_shown(tree, 0.2)) < len(scenes.rrt_shown(tree, 3.0)) <= len(nodes)


def test_swarm_converges_and_disperses_periodically():
    W, H = 144, 56
    spread = lambda t: sum(math.dist(p, scenes.swarm_center(W, H)) for p in scenes.swarm_positions(t, W, H)) / scenes.SWARM_N
    assert spread(4.0) < 0.45 * spread(0.0) and spread(2.0) < spread(0.0)
    assert spread(0.0) == pytest.approx(spread(scenes.LOOP)) and len(scenes.swarm_positions(1, W, H)) == scenes.SWARM_N


# ---- robo scene ---------------------------------------------------------------------------------------------
import io

from robo import cli, motion


@pytest.fixture
def env(course, state_home, monkeypatch):
    monkeypatch.setenv("ROBO_ROOT", str(course))
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("ROBO_FAST", "1")

    def run(*argv):
        return cli.main(list(argv))
    return run


def test_scene_plain_prints_one_static_frame_and_a_caption(env, capsys):
    assert env("scene", "02", "--plain") == 0
    out = capsys.readouterr().out
    assert not ANSI.search(out) and out.count("⠀") + sum(ord(c) >= 0x2800 and ord(c) <= 0x28FF for c in out) > 30
    assert "arm" in out.lower() and len(out.splitlines()) <= scenes.H_CELLS + 6


def test_scene_other_phase_prints_the_nearest_note(env, capsys):
    assert env("scene", "06", "--plain") == 0
    out = capsys.readouterr().out
    assert "05" in out and "06" in out and "nearest" in out.lower()
    assert env("scene", "5", "--plain") == 0 and "nearest" not in capsys.readouterr().out.lower()


def test_scene_default_is_the_phase_of_the_next_lesson(env, capsys):
    assert env("scene", "--plain") == 0
    out = capsys.readouterr().out
    assert "Phase 00" in out and "nearest" in out.lower()          # the mini course starts at phase 00 -> nearest scene 02


def test_scene_rejects_bad_phase(env, capsys):
    for bad in ("17", "99", "x", "-1"):
        assert env("scene", bad, "--plain") == 2
        assert "phase" in capsys.readouterr().err.lower()


def test_scene_ko_caption(env, capsys):
    assert env("scene", "09", "--plain", "--lang", "ko") == 0
    out = capsys.readouterr().out
    assert "트리" in out or "RRT" in out


def test_scene_listed_in_help_and_completion(env, capsys):
    env("--help")
    assert "scene" in capsys.readouterr().out
    env("completion", "bash")
    assert "scene" in capsys.readouterr().out


def test_scene_loop_restores_the_cursor_on_ctrl_c(monkeypatch):
    for k in ("NO_COLOR", "ROBO_NO_ANIM", "ROBO_FAST"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(motion, "_stdout_isatty", lambda: True)
    buf = io.StringIO()
    u = ui.make_ui(plain=False, width=80, force_color=True, file=buf, dark=True)
    t = {"v": 0.0, "n": 0}

    def sleep(dt):
        t["n"] += 1
        if t["n"] == 6:
            raise KeyboardInterrupt
        t["v"] += dt

    r = scenes.run_scene(u, "lidar", 8, sleep=sleep, now=lambda: t["v"], poll=lambda: False)
    out = buf.getvalue()
    assert r == "interrupt" and out.rindex("\x1b[?25h") > out.rindex("\x1b[?25l")
    assert abs(t["v"] - 5 / 15) < 0.01                      # 15 fps


def test_nothing_animates_without_a_tty(env, capsys, state_home):
    env()                                                    # home, stdout is not a TTY under pytest
    out = capsys.readouterr().out
    assert not ANSI.search(out) and "\x1b" not in out
    assert not (P_dir(state_home) / "last-intro").exists()


def P_dir(state_home):
    return state_home / "robotics-course"
