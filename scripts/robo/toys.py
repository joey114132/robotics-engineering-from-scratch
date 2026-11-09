# robo play: pd-step, sampling-limit, kalman 을 점자 plot 으로 (수식은 plots.py, 웹 toy 와 같은 상수)
from rich.cells import cell_len
from rich.text import Text

from . import plots as PL
from . import ui as U


def _print_plot(u, lines):
    for ln in lines:
        u.print(Text("  ") + ln, no_wrap=True, overflow="crop")


def _title(u, en, ko, sub):
    u.print()
    t = Text("  ")
    t.append(u.t(en, ko), style="bold accent"), t.append("   " + sub, style="muted")
    u.para(t)
    u.print()


def pd_step(u, kp, kd):
    r = PL.pd_step(kp, kd)
    _title(u, "PD step response", "PD 계단 응답", f"kp {kp:g}   kd {kd:g}   " + u.t("unit inertia, friction 0.2, dt 0.002 s, 3 s", "단위 관성, 마찰 0.2, dt 0.002 s, 3 s"))
    ts = [i * PL.PD_DT for i in range(len(r["y"]))]
    lo, hi = min(0, min(r["y"]) - 0.05), max(1.5, r["peak"] * 1.08)
    lines = PL.render_plot([PL.Series(ts, r["y"], "bold accent")], u.read_width - 4, 14, (0, PL.PD_T), (lo, hi),
                           xlabel=u.t("time (s)", "시간 (s)"), ylabel=u.t("position", "위치"),
                           hlines=[(1.0, "muted")], bands=[(0.98, 1.02, "ok")])
    _print_plot(u, lines)
    u.print()
    over = r["overshoot"]
    t = Text("  ")
    t.append(u.t("overshoot ", "오버슈트 "), style="muted"), t.append(f"{over:.1f}%", style="bold warn" if over > 10 else "bold ok")
    t.append(u.t("     settle time ", "     정착 시간 "), style="muted")
    t.append(f"{r['settle_time']:.2f} s" if r["settled"] else u.t("not within 3 s", "3 s 안에 못 들어옴"), style="bold ok" if r["settled"] else "bold bad")
    t.append(u.t("  (2% band, green dots)", "  (2% 띠, 초록 점선)"), style="muted")
    u.para(t)
    msg = (u.t("rings: too little damping, raise kd", "떨립니다: 감쇠가 부족하니 kd 를 올리세요") if over > 10
           else u.t("clean: little overshoot and it settles", "깔끔합니다: 오버슈트가 적고 금방 정착합니다") if r["settled"]
           else u.t("slow: raise kp to settle within 3 s", "느립니다: kp 를 올려야 3 s 안에 정착합니다"))
    u.print(Text("  " + msg, style="muted"))


def sampling_limit(u, r):
    d = PL.sampling_limit(r)
    _title(u, "The sampling limit: r = dt·kd/J", "샘플링 한계: r = dt·kd/J", f"r {r:g}   1-r {1 - r:+.2f}")
    style = {"ok": "ok", "warn": "warn", "bad": "bad"}[d["regime"]]
    ks = list(range(len(d["values"])))
    lines = PL.render_plot([PL.Series(ks, d["values"], style, kind="stem")], u.read_width - 4, 12, (0, PL.SL_N), (-PL.SL_YM, PL.SL_YM),
                           xlabel=u.t("step", "스텝"), ylabel="v", hlines=[(0.0, "muted")])
    _print_plot(u, lines)
    u.print()
    # r 막대: 초록 [0,1], 주황 [1,2], 빨강 [2,2.5] 와 현재 r 위치
    wbar = min(60, u.read_width - 10)
    cell = lambda x: min(wbar - 1, round(x / PL.SL_RMAX * (wbar - 1)))
    ptr = [" "] * wbar
    ptr[cell(r)] = "▾" if not u.plain else "v"
    u.print(Text("  " + "".join(ptr), style="bold"), no_wrap=True)
    zone = Text("  ")
    for i in range(wbar):
        x = i / (wbar - 1) * PL.SL_RMAX
        zone.append("━" if not u.plain else "=", style="ok" if x <= 1 else "warn" if x < 2 else "bad")
    u.print(zone, no_wrap=True)
    ticks = [" "] * wbar
    for v in (0, 1, 2):
        ticks[cell(v)] = str(v)
    u.print(Text("  " + "".join(ticks), style="muted"), no_wrap=True)
    u.print()
    eq = abs(r - 1) < 1e-9
    mag = d["magnitude"]
    if d["regime"] == "ok":
        msg = u.t("smooth: deadbeat, velocity hits 0 in one step", "부드러움: 한 스텝 만에 속도 0 (deadbeat)") if eq else u.t("smooth: velocity shrinks every step", "부드러움: 속도가 매 스텝 줄어듦")
    elif d["regime"] == "warn":
        msg = u.t("chatter: sign flips every step but it still shrinks", "떨림(chatter): 매 스텝 부호가 뒤집히지만 줄어들긴 함")
    else:
        m = f"{mag:.1e}" if mag > 1e3 else f"{mag:.2f}"
        msg = u.t(f"diverges: never decays (|v| after {PL.SL_N} steps = {m})", f"발산: 줄지 않음 ({PL.SL_N} 스텝 뒤 |v| = {m})")
    t = Text("  ")
    t.append(f"r = {r:.2f}, 1-r = {1 - r:+.2f}   ", style="muted"), t.append(msg, style=f"bold {style}")
    u.para(t)
    if d["off"] is not None:
        u.print(Text("  " + u.t(f"off scale from step {d['off']}", f"{d['off']} 스텝부터 범위 밖"), style="muted"))


def kalman(u, q, r, seed):
    d = PL.kalman_run(q, r, seed)
    _title(u, "Kalman filter: trust the sensor?", "칼만 필터: 센서를 믿을까?",
           u.t(f"believes {q:g} / {r:g}   truth {PL.K_SA:g} / {PL.K_R:g}", f"믿는 값 {q:g} / {r:g}   실제 {PL.K_SA:g} / {PL.K_R:g}"))
    n = len(d["truth"])
    ks = list(range(n))
    # 위치 자체는 추세(1 m/s)에 눌려 잡음이 안 보이므로 실제 위치와의 차이로 그린다: 0 이 정답이고 점이 흩어진 만큼이 오차
    err = lambda xs: [x - t for x, t in zip(xs, d["truth"])]
    meas, est = err(d["meas"]), err(d["est"])
    up = [e + 2 * s for e, s in zip(est, d["sigma"])]
    dn = [e - 2 * s for e, s in zip(est, d["sigma"])]
    allv = meas + up + dn
    lim = max(2.0, max(abs(v) for v in allv)) * 1.05
    series = [PL.Series(ks, up, "teal", kind="dots"), PL.Series(ks, dn, "teal", kind="dots"), PL.Series(ks, meas, "", kind="dots"),
              PL.Series(ks, est, "bold accent", kind="line")]
    lines = PL.render_plot(series, u.read_width - 4, 15, (0, n - 1), (-lim, lim), xlabel=u.t("time (s)", "시간 (s)"),
                           ylabel=u.t("error vs truth (m), 0 = exact", "실제와의 차이 (m), 0 이 정답"), hlines=[(0.0, "muted")])
    _print_plot(u, lines)
    leg = Text("  ")
    for label, st in ((u.t("sensor", "센서"), ""), (u.t("estimate", "추정값"), "bold accent"), (u.t("±2σ band", "±2σ 띠"), "teal")):
        leg.append("⠶ " if not u.plain else "- ", style=st), leg.append(label + "   ", style="muted")
    u.print(leg)
    u.print()
    k = d["gain"]
    msg = (u.t("it mostly trusts the sensor: the estimate chases the dots.", "센서를 주로 믿는 상태라 추정값이 점을 따라갑니다.") if k >= 0.6
           else u.t("it mostly trusts its own model: smooth but slow to react.", "자기 모델을 주로 믿는 상태라 추정값이 부드럽지만 반응이 느립니다.") if k <= 0.25
           else u.t("it blends the model and the sensor.", "모델과 센서를 섞어 쓰는 상태입니다."))
    t = Text("  ")
    t.append(u.t("Kalman gain K = ", "칼만 이득 K = "), style="muted"), t.append(f"{k:.2f}", style="bold"), t.append("  " + msg)
    u.para(t)
    u.print(Text("  " + u.t("try --r 0.2 (trust the sensor) or --r 20 (trust the model)", "--r 0.2 (센서를 믿음) 나 --r 20 (모델을 믿음)을 넣어 보세요"), style="muted"))


TOYS = {"pd-step": ("kp", "kd"), "sampling-limit": ("r",), "kalman": ("q", "r")}


def play(u, name, kp=None, kd=None, r=None, q=None, seed=1):
    if name == "pd-step":
        pd_step(u, 30.0 if kp is None else kp, 4.0 if kd is None else kd)
    elif name == "sampling-limit":
        sampling_limit(u, 0.6 if r is None else r)
    else:
        kalman(u, PL.K_SA if q is None else q, PL.K_R if r is None else r, seed)
