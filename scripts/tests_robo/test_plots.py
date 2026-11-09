# 점자 plot 과 toy 시뮬레이션 테스트 (상수는 scripts/toys/*.js 에서 읽어 대조)
import re
from pathlib import Path

import pytest
from rich.cells import cell_len

from robo import plots

TOYS = Path(__file__).resolve().parents[1] / "toys"


def test_braille_cell_bits():
    c = plots.Braille(2, 1)                       # 2 cells wide, 4 dot rows -> 4 x 4 dots
    c.set(0, 0)
    assert c.rows()[0][0] == "⠁"
    c.set(1, 3)
    assert c.rows()[0][0] == chr(0x2800 | 0x01 | 0x80)
    c.set(3, 0)
    assert c.rows()[0][1] == chr(0x2800 | 0x08)
    c.set(99, 99)                                  # out of range is ignored
    assert all(cell_len(r) == 2 for r in c.rows())


def test_braille_line_is_connected():
    c = plots.Braille(10, 3)
    c.line(0, 0, 19, 11)
    dots = sum(bin(ord(ch) - 0x2800).count("1") for r in c.rows() for ch in r)
    assert dots >= 20


def test_toy_constants_match_js_source():
    js = (TOYS / "10-control-arm.js").read_text()
    assert f"DT = {plots.PD_DT}" in js and f"T = {plots.PD_T}" in js and f"B = {plots.PD_B}" in js
    assert "kp = 30, kd = 4" in js
    assert f"N = {plots.SL_N}" in js and f"RMAX = {plots.SL_RMAX}" in js and f"YM = {plots.SL_YM}" in js
    k = (TOYS / "20-estimation-mobile-planning.js").read_text()
    m = re.search(r"DT = ([\d.]+), N = (\d+), RATE = \d+, TRUE_SA = ([\d.]+), TRUE_R = ([\d.]+)", k)
    assert (plots.K_DT, plots.K_N, plots.K_SA, plots.K_R) == (float(m[1]), int(m[2]), float(m[3]), float(m[4]))


def test_pd_step_first_step_matches_hand_calc():
    r = plots.pd_step(30, 4)
    v1 = (30 * 1 - 0) * 0.002            # explicit Euler, first step
    assert r["y"][1] == pytest.approx(v1 * 0.002)
    assert len(r["y"]) == 1501


def test_pd_step_regimes():
    default = plots.pd_step(30, 4)
    ringing = plots.pd_step(30, 1)
    stiff_damped = plots.pd_step(30, 12)
    assert default["overshoot"] > 20 and default["settled"] and 0.5 < default["settle_time"] < 2
    assert ringing["overshoot"] > 50 and not ringing["settled"]        # still ringing after 3 s
    assert stiff_damped["overshoot"] == 0 and stiff_damped["settled"]
    never = plots.pd_step(5, 0.0)
    assert not never["settled"] and never["settle_time"] is None


def test_sampling_limit_regimes_and_colors():
    assert plots.sampling_limit(0.6)["regime"] == "ok"
    assert plots.sampling_limit(1.0)["regime"] == "ok" and plots.sampling_limit(1.0)["values"][1] == 0
    assert plots.sampling_limit(1.5)["regime"] == "warn"
    d = plots.sampling_limit(2.4)
    assert d["regime"] == "bad" and d["off"] is not None
    assert len(plots.sampling_limit(0.2)["values"]) == plots.SL_N + 1


def test_kalman_is_deterministic_and_tracks():
    a = plots.kalman_run(0.1, 2.0, seed=3)
    b = plots.kalman_run(0.1, 2.0, seed=3)
    assert a == b and len(a["truth"]) == plots.K_N
    err_est = sum(abs(e - t) for e, t in zip(a["est"][20:], a["truth"][20:]))
    err_raw = sum(abs(z - t) for z, t in zip(a["meas"][20:], a["truth"][20:]))
    assert err_est < err_raw
    trusting = plots.kalman_run(0.1, 0.2, seed=3)["gain"]
    skeptical = plots.kalman_run(0.1, 20.0, seed=3)["gain"]
    assert trusting > skeptical


def test_plot_renders_rectangular_block():
    xs = [i / 10 for i in range(31)]
    lines = plots.render_plot([plots.Series(xs, [x * x for x in xs], "accent")], width=60, height=10,
                              xlim=(0, 3), ylim=(0, 9), xlabel="t", ylabel="y")
    widths = {cell_len(l.plain) for l in lines}
    assert len(widths) == 1 and max(widths) <= 60
    assert any("⠀" <= ch <= "⣿" for l in lines for ch in l.plain)


def test_kalman_survives_singular_covariance():
    for q, r in ((0.0, 0.0), (0.0, 1e-12), (1e-9, 1e-9)):
        d = plots.kalman_run(q, r, seed=1)
        assert all(abs(v) < 1e9 for v in d["est"]) and d["gain"] == d["gain"]


def test_pd_step_extremes_stay_finite():
    for kp, kd in ((1000, 1000), (1000, 0), (0, 0), (0, 1000)):
        r = plots.pd_step(kp, kd)
        assert all(abs(v) < 1e13 for v in r["y"]) and r["overshoot"] == r["overshoot"]
    lines = plots.render_plot([plots.Series([0, 1, 2], [0.0, float("inf"), float("nan")])], 40, 6, (0, 2), (-1, 1))
    assert len(lines) >= 6
