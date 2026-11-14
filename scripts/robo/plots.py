# 순수 파이썬 점자 plot 과 toy 시뮬레이션 (상수는 웹사이트 저장소의 scripts/toys/*.js 와 같아야 하며 그 저장소의 테스트가 대조한다)
import math
import random
from dataclasses import dataclass, field

from rich.cells import cell_len
from rich.text import Text

# 웹 toy 10-control-arm.js: pd-step 은 단위 관성 J=1, 마찰 B, dt 0.002 s, 3 s
PD_DT, PD_T, PD_B = 0.002, 3, 0.2
# sampling-limit: 40 스텝, r 슬라이더 최대 2.5, y 축 ±1.5
SL_N, SL_RMAX, SL_YM = 40, 2.5, 1.5
# 웹 toy 20-estimation-mobile-planning.js: kalman (레슨 07/02 와 같은 숫자)
K_DT, K_N, K_SA, K_R = 1.0, 60, 0.1, 2.0


BIG = 1e12            # 불안정한 설정에서도 inf/nan 이 그림으로 새지 않게 값을 이 크기로 자른다


def pd_step(kp, kd):
    n = round(PD_T / PD_DT)
    y, q, v, peak, last = [0.0] * (n + 1), 0.0, 0.0, 0.0, -1
    for i in range(1, n + 1):
        v += (kp * (1 - q) - (kd + PD_B) * v) * PD_DT
        q += v * PD_DT
        v, q = max(-BIG, min(BIG, v)), max(-BIG, min(BIG, q))
        y[i] = q
        peak = max(peak, q)
        if abs(q - 1) > 0.02:
            last = i
    settled = last < n
    return {"y": y, "peak": peak, "overshoot": max(0.0, peak - 1) * 100, "settled": settled,
            "settle_time": (last + 1) * PD_DT if settled else None}


def sampling_limit(r):
    f, v, vals, off = 1 - r, 1.0, [], None
    for k in range(SL_N + 1):
        if abs(v) > SL_YM:
            off = k
            break
        vals.append(v)
        v *= f
    regime = "ok" if r <= 1 + 1e-9 else "warn" if r < 2 - 1e-9 else "bad"
    return {"r": r, "f": f, "values": vals, "off": off, "regime": regime, "magnitude": abs(f) ** SL_N}


def kalman_run(qs, rs, seed=1):
    """x=[pos, vel], F=[[1,dt],[0,1]], G=[dt²/2, dt], Q=sa²·GGᵀ, H=[1 0]. 실제 잡음은 K_SA, K_R 고정, 필터는 qs, rs 를 믿는다."""
    rng = random.Random(seed)
    dt = K_DT
    truth, vel = 0.0, 1.0
    x, v, P = truth + 2 * rng.gauss(0, 1), 1.0, [4.0, 0.0, 0.0, 1.0]
    T, Z, X, S, gain = [truth], [truth], [x], [2.0], 0.5
    g0, g1, q = dt * dt / 2, dt, qs * qs
    for _ in range(K_N - 1):
        a = K_SA * rng.gauss(0, 1)
        truth += vel * dt + 0.5 * a * dt * dt
        vel += a * dt
        z = truth + K_R * rng.gauss(0, 1)
        x += v * dt
        p00 = P[0] + dt * (P[1] + P[2]) + dt * dt * P[3] + q * g0 * g0
        p01 = P[1] + dt * P[3] + q * g0 * g1
        p11 = P[3] + q * g1 * g1
        s = p00 + rs * rs
        if s > 1e-12:
            k0, k1 = p00 / s, p01 / s
        else:                                  # 공분산이 특이하면 이번 보정은 건너뛴다(0 으로 나누지 않는다)
            k0 = k1 = 0.0
        y = z - x
        x += k0 * y
        v += k1 * y
        gain = k0
        P = [(1 - k0) * p00, (1 - k0) * p01, (1 - k0) * p01, p11 - k1 * p01]
        T.append(truth), Z.append(z), X.append(x), S.append(P[0] ** 0.5)
    return {"truth": T, "meas": Z, "est": X, "sigma": S, "gain": gain}


# ---- 점자 canvas ------------------------------------------------------------------------
_BITS = {(0, 0): 0x01, (0, 1): 0x02, (0, 2): 0x04, (1, 0): 0x08, (1, 1): 0x10, (1, 2): 0x20, (0, 3): 0x40, (1, 3): 0x80}


class Braille:
    """cw x ch 칸 = (2cw x 4ch) 점. 칸마다 색 하나(나중에 찍은 점의 색)."""

    def __init__(self, cw, ch):
        self.cw, self.ch, self.W, self.H = cw, ch, cw * 2, ch * 4
        self.bits = [[0] * cw for _ in range(ch)]
        self.color = [[None] * cw for _ in range(ch)]

    def set(self, x, y, color=None):
        if 0 <= x < self.W and 0 <= y < self.H:
            cx, cy = x // 2, y // 4
            self.bits[cy][cx] |= _BITS[(x % 2, y % 4)]
            if color:
                self.color[cy][cx] = color

    def line(self, x0, y0, x1, y1, color=None):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy, err = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1), dx + dy
        for _ in range(4 * (self.W + self.H)):          # 화면 밖으로 멀리 나가는 선분 방어
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err, x0 = err + dy, x0 + sx
            if e2 <= dx:
                err, y0 = err + dx, y0 + sy

    def rows(self):
        return ["".join(chr(0x2800 | b) for b in row) for row in self.bits]

    def text_rows(self):
        out = []
        for r in range(self.ch):
            t = Text(no_wrap=True, overflow="crop")
            for c in range(self.cw):
                b = self.bits[r][c]
                t.append(chr(0x2800 | b) if b else " ", style=self.color[r][c] or "")
            out.append(t)
        return out


@dataclass
class Series:
    xs: list
    ys: list
    style: str = "accent"
    kind: str = "line"            # line | dots | stem
    base: float = 0.0             # stem 이 시작하는 y
    extra: dict = field(default_factory=dict)


def _num(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".") if abs(v) < 100 else f"{v:.0f}"
    return "0" if s in ("-0", "") else s


def render_plot(series, width, height, xlim, ylim, xlabel="", ylabel="", hlines=(), bands=()):
    """series 를 점자로 그리고 왼쪽 y 눈금, 아래 x 눈금을 붙인 Text 줄 목록을 돌려준다(모든 줄 같은 폭)."""
    gut = max(cell_len(_num(v)) for v in (ylim[0], ylim[1], (ylim[0] + ylim[1]) / 2)) + 1
    cw = max(10, width - gut - 1)
    cv = Braille(cw, height)
    x0, x1 = xlim
    y0, y1 = ylim
    X = lambda x: round((x - x0) / (x1 - x0) * (cv.W - 1)) if math.isfinite(x) else None
    Y = lambda y: round((y1 - y) / (y1 - y0) * (cv.H - 1)) if math.isfinite(y) else None
    for y, style in list(hlines) + [(b, s) for lo, hi, s in bands for b in (lo, hi)]:
        for px in range(0, cv.W, 3):
            cv.set(px, Y(y), style)
    for s in series:
        pts = [(X(x), Y(y)) for x, y in zip(s.xs, s.ys)]
        pts = [p for p in pts if p[0] is not None and p[1] is not None]      # 유한하지 않은 점은 그리지 않는다
        if s.kind == "line":
            for a, b in zip(pts, pts[1:]):
                cv.line(*a, *b, s.style)
        elif s.kind == "stem":
            for px, py in pts:
                cv.line(px, Y(s.base), px, py, s.style)
                for dx in (0, 1):
                    for dy in (0, 1):
                        cv.set(px + dx - 0, py + dy - 1, s.style)
        else:
            for px, py in pts:
                cv.set(px, py, s.style)
                cv.set(px + 1, py, s.style)
    total = gut + 1 + cw
    out = []
    labels = {0: _num(y1), height - 1: _num(y0), height // 2: _num((y0 + y1) / 2)}
    for r, row in enumerate(cv.text_rows()):
        line = Text(no_wrap=True, overflow="crop")
        line.append(labels.get(r, "").rjust(gut - 1) + " ", style="dim")
        line.append("┤" if r in labels else "│", style="dim")
        line.append_text(row)
        out.append(line)
    axis = Text(" " * gut, no_wrap=True) + Text("└" + "─" * (cw - 1) + "▸", style="dim")
    out.append(axis)
    lo, mid, hi = _num(x0), _num((x0 + x1) / 2), _num(x1)
    xl = [" "] * total
    for txt, pos in ((lo, gut + 1), (mid, gut + 1 + cw // 2 - cell_len(mid) // 2), (hi, total - cell_len(hi))):
        xl[pos:pos + len(txt)] = list(txt)
    ticks = "".join(xl)[:total]
    out.append(Text(ticks, style="dim", no_wrap=True))
    if ylabel:
        out.insert(0, Text(" " * (gut + 1) + ylabel, style="dim", no_wrap=True))
    if xlabel:
        out.append(Text(xlabel.rjust(total), style="dim", no_wrap=True))
    for t in out:
        gap = total - t.cell_len
        if gap > 0:
            t.append(" " * gap)
    return out
