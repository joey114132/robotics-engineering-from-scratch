# robo scene: 단계별 손으로 만든 점자 애니메이션 6개. 모든 프레임은 시간 t 만의 순수 함수라서 같은 t 면 같은 그림이다.
import math
import random
import time
from functools import lru_cache

from rich.text import Text

from . import motion
from . import ui as U
from .plots import _BITS as BITS, Braille

LOOP = 8.0                 # 한 바퀴 길이(초)
FPS = 15
H_CELLS = 14               # 그림 높이(칸): 56 dots
SCENES = {"02": "arm", "03": "payload", "05": "pubsub", "08": "lidar", "09": "tree", "14": "swarm"}
STATIC_T = {"arm": 2.0, "payload": 2.4, "pubsub": 1.3, "lidar": 5.5, "tree": 6.5, "swarm": 4.0}
INFO = {
    "arm": ("Arm reaching", "팔이 목표로 뻗습니다", "Two-link inverse kinematics: the arm follows a moving target and stops at full reach.",
            "2링크 역기구학: 팔이 움직이는 목표를 따라가다 끝까지 뻗으면 멈춥니다."),
    "payload": ("Swinging payload settling", "흔들리는 짐이 가라앉습니다", "A damped swing: the angle trace on the right shrinks until it sits inside the settle band.",
                "감쇠 진동: 오른쪽 각도 곡선이 줄어들어 정착 띠 안으로 들어옵니다."),
    "pubsub": ("Pub/sub messages on wires", "선을 따라 흐르는 pub/sub 메시지", "Publishers send on a topic, subscribers receive; a node lights up when a message arrives.",
               "publisher 가 topic 으로 보내면 subscriber 가 받습니다. 메시지가 도착하면 노드가 켜집니다."),
    "lidar": ("Lidar sweep building a map", "라이다가 지도를 만듭니다", "Each beam that hits a surface leaves a dot; the dots add up to a map of the room.",
              "표면에 닿은 빔마다 점이 남고, 점이 쌓여 방의 지도가 됩니다."),
    "tree": ("Tree growing to a goal", "트리가 목표까지 자랍니다 (RRT)", "RRT: random samples pull the tree outward around obstacles until it reaches the goal.",
             "RRT: 무작위 샘플이 트리를 장애물 사이로 뻗게 하고, 목표에 닿으면 경로가 켜집니다."),
    "swarm": ("Swarm converging", "무리가 모입니다", "Each agent only moves toward its own slot, yet the swarm forms a ring and spreads out again.",
              "각 개체는 자기 자리만 향해 움직이는데도 무리가 고리를 이루었다가 다시 흩어집니다."),
}


def _wrap(t):
    """t 를 한 바퀴 안으로 접는다. 부동소수 오차로 t 와 t+LOOP 의 프레임이 달라지지 않게 반올림한다."""
    return round(t % LOOP, 9) % LOOP


def scene_for_phase(ph):
    """단계 번호(0-16) -> (scene 이름, 대신 보여 주는 단계 번호나 None). 가장 가까운 scene 을 고르고 동률이면 낮은 번호."""
    if not 0 <= ph <= 16:
        raise ValueError("phase must be 0-16")
    if f"{ph:02d}" in SCENES:
        return SCENES[f"{ph:02d}"], None
    near = min(sorted(int(k) for k in SCENES), key=lambda k: abs(k - ph))
    return SCENES[f"{near:02d}"], near


def scene_cols(u):
    return max(20, min(u.read_width - 4, 72))


# ---- 그리기 도구 ---------------------------------------------------------------------------------------
class Pen:
    def __init__(self, cv, bright, dim):
        self.cv, self.bright, self.dim, self.W, self.H = cv, bright, dim, cv.W, cv.H

    def dot(self, x, y, dim=False):
        self.cv.set(round(x), round(y), self.dim if dim else self.bright)

    def line(self, a, b, dim=False, thick=False):
        st = self.dim if dim else self.bright
        self.cv.line(round(a[0]), round(a[1]), round(b[0]), round(b[1]), st)
        if thick:
            self.cv.line(round(a[0]) + 1, round(a[1]), round(b[0]) + 1, round(b[1]), st)

    def poly(self, pts, dim=False):
        for a, b in zip(pts, pts[1:]):
            self.line(a, b, dim)

    def circle(self, c, r, dim=False):
        n = max(10, int(r * 5))
        for i in range(n):
            a = 2 * math.pi * i / n
            self.dot(c[0] + r * math.cos(a), c[1] + r * math.sin(a), dim)

    def rect(self, x0, y0, x1, y1, dim=False, fill=False):
        for y in (range(round(y0), round(y1) + 1) if fill else (y0, y1)):
            self.line((x0, y), (x1, y), dim)
        if not fill:
            self.line((x0, y0), (x0, y1), dim)
            self.line((x1, y0), (x1, y1), dim)

    def blob(self, c, dim=False, size=2):
        for dx in range(size):
            for dy in range(size):
                self.dot(c[0] + dx, c[1] + dy, dim)


def _dist_to_segment(p, a, b):
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    u = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L))
    return math.hypot(p[0] - (ax + u * dx), p[1] - (ay + u * dy))


# ---- 1. arm (02) ------------------------------------------------------------------------------------------
ARM_L1, ARM_L2 = 0.40, 0.34          # 링크 길이(높이 H 에 대한 비율)


def arm_pose(t, W, H):
    L1, L2 = ARM_L1 * H, ARM_L2 * H
    reach = L1 + L2
    base = (W / 2, H - 4.0)
    ph = 2 * math.pi * _wrap(t) / LOOP
    target = (base[0] + 0.78 * reach * math.cos(ph), base[1] - reach * (0.5 + 0.25 * math.sin(2 * ph)))
    dx, dy = target[0] - base[0], base[1] - target[1]           # y 가 위로 가는 좌표
    d = min(max(math.hypot(dx, dy), abs(L1 - L2) + 0.5), reach - 1e-9)
    c2 = max(-1.0, min(1.0, (d * d - L1 * L1 - L2 * L2) / (2 * L1 * L2)))
    best = None
    for q2 in (-math.acos(c2), math.acos(c2)):                    # 팔꿈치가 위로 가는 해를 고른다
        q1 = math.atan2(dy, dx) - math.atan2(L2 * math.sin(q2), L1 + L2 * math.cos(q2))
        elbow = (base[0] + L1 * math.cos(q1), base[1] - L1 * math.sin(q1))
        if best is None or elbow[1] < best[0][1]:
            best = (elbow, q1, q2)
    elbow, q1, q2 = best
    tip = (elbow[0] + L2 * math.cos(q1 + q2), elbow[1] - L2 * math.sin(q1 + q2))
    return base, elbow, tip, target


def draw_arm(pen, t):
    W, H = pen.W, pen.H
    for k in range(26, 0, -1):                                   # 끝점이 지나온 자리
        _, _, tip, _ = arm_pose(t - k * 0.07, W, H)
        pen.dot(*tip, dim=True)
    base, elbow, tip, target = arm_pose(t, W, H)
    pen.line((4, H - 2), (W - 5, H - 2), dim=True)
    pen.rect(base[0] - 6, H - 5, base[0] + 6, H - 3, fill=True)
    pen.line(base, elbow, thick=True)
    pen.line(elbow, tip, thick=True)
    pen.circle(elbow, 2.2), pen.circle(base, 2.2), pen.blob((tip[0] - .5, tip[1] - .5))
    for d in (-3, -2, 2, 3):                                     # 목표 십자
        pen.dot(target[0] + d, target[1], dim=True), pen.dot(target[0], target[1] + d, dim=True)


# ---- 2. payload (03) --------------------------------------------------------------------------------------
PAYLOAD_W, PAYLOAD_Z, PAYLOAD_A = 2 * math.pi / 1.5, 0.22, 0.9


def payload_angle(t):
    t = _wrap(t)
    return PAYLOAD_A * math.exp(-PAYLOAD_Z * PAYLOAD_W * t) * math.cos(PAYLOAD_W * math.sqrt(1 - PAYLOAD_Z ** 2) * t)


def draw_payload(pen, t):
    W, H = pen.W, pen.H
    px, py, cable = 0.27 * W, 5.0, 0.62 * H
    pen.line((0.08 * W, 3), (0.46 * W, 3), dim=True)
    for k in range(-8, 9):                                       # 흔들림 폭의 희미한 호
        a = PAYLOAD_A * k / 8
        pen.dot(px + cable * math.sin(a), py + cable * math.cos(a), dim=True)
    th = payload_angle(t)
    bob = (px + cable * math.sin(th), py + cable * math.cos(th))
    pen.line((px, py), bob)
    pen.circle((px, py), 1.8)
    pen.rect(bob[0] - 3, bob[1] - 3, bob[0] + 3, bob[1] + 3, fill=True)
    x0, x1, mid, amp = 0.56 * W, W - 4.0, H / 2, 0.4 * H
    pen.line((x0, mid), (x1, mid), dim=True)
    for x in range(round(x0), round(x1), 3):                     # 정착 띠 ±10%
        pen.dot(x, mid - 0.1 * amp, dim=True), pen.dot(x, mid + 0.1 * amp, dim=True)
    tt = _wrap(t)
    n = max(2, int(tt / LOOP * (x1 - x0)))
    pts = [(x0 + (x1 - x0) * (tt * i / n) / LOOP, mid - payload_angle(tt * i / n) / PAYLOAD_A * amp) for i in range(n + 1)]
    pen.poly(pts)
    pen.blob((pts[-1][0] - .5, pts[-1][1] - .5))


# ---- 3. pubsub (05) ---------------------------------------------------------------------------------------
PUBSUB_LAPS = (2, 3, 2, 3)
PUBSUB_PER_WIRE = 3


def pubsub_nodes(W, H):
    return {"p1": (0.10 * W, 0.25 * H), "p2": (0.10 * W, 0.75 * H), "hub": (0.50 * W, 0.50 * H), "s1": (0.90 * W, 0.25 * H), "s2": (0.90 * W, 0.75 * H)}


def pubsub_wires(W, H):
    n, bw = pubsub_nodes(W, H), 8.0
    hub_r = 7.0
    return [
        [(n["p1"][0] + bw, n["p1"][1]), (0.32 * W, n["p1"][1]), (0.32 * W, n["hub"][1]), (n["hub"][0] - hub_r, n["hub"][1])],
        [(n["p2"][0] + bw, n["p2"][1]), (0.38 * W, n["p2"][1]), (0.38 * W, n["hub"][1]), (n["hub"][0] - hub_r, n["hub"][1])],
        [(n["hub"][0] + hub_r, n["hub"][1]), (0.68 * W, n["hub"][1]), (0.68 * W, n["s1"][1]), (n["s1"][0] - bw, n["s1"][1])],
        [(n["hub"][0] + hub_r, n["hub"][1]), (0.74 * W, n["hub"][1]), (0.74 * W, n["s2"][1]), (n["s2"][0] - bw, n["s2"][1])],
    ]


def _along(pts, s):
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    d = s * sum(segs)
    for (a, b), L in zip(zip(pts, pts[1:]), segs):
        if d <= L or (a, b) == (pts[-2], pts[-1]):
            f = 0 if L == 0 else min(1.0, d / L)
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        d -= L


def pubsub_messages(t, W, H):
    out = []
    for wi, pts in enumerate(pubsub_wires(W, H)):
        for j in range(PUBSUB_PER_WIRE):
            s = (PUBSUB_LAPS[wi] * _wrap(t) / LOOP + j / PUBSUB_PER_WIRE) % 1.0
            out.append((wi, _along(pts, s), s))
    return [(wi, p) for wi, p, _ in out]


def draw_pubsub(pen, t):
    W, H = pen.W, pen.H
    nodes, wires = pubsub_nodes(W, H), pubsub_wires(W, H)
    for pts in wires:
        pen.poly(pts, dim=True)
    arrived = set()
    for wi in range(4):
        for j in range(PUBSUB_PER_WIRE):
            s = (PUBSUB_LAPS[wi] * _wrap(t) / LOOP + j / PUBSUB_PER_WIRE) % 1.0
            if s > 0.9:
                arrived.add(("hub", "hub", "s1", "s2")[wi])
    for name, (x, y) in nodes.items():
        grow = 1 if name in arrived else 0
        if name == "hub":
            pen.circle((x, y), 7 + grow)
            pen.circle((x, y), 3, dim=True)
        else:
            pen.rect(x - 8 - grow, y - 5 - grow, x + 8 + grow, y + 5 + grow)
            pen.line((x - 4, y), (x + 4, y), dim=True)
    for wi, (x, y) in pubsub_messages(t, W, H):
        pen.blob((x - 1, y - 1), size=3)


# ---- 4. lidar (08) --------------------------------------------------------------------------------------
LIDAR_RATE, LIDAR_REVS = 90, 1.5


def lidar_segments(W, H):
    segs = []
    for x0, y0, x1, y1 in ((4, 4, W - 5, H - 5), (0.25 * W, 0.30 * H, 0.34 * W, 0.55 * H), (0.55 * W, 0.45 * H, 0.66 * W, 0.80 * H), (0.78 * W, 0.25 * H, 0.86 * W, 0.45 * H)):
        c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        segs += [(c[i], c[(i + 1) % 4]) for i in range(4)]
    return segs


def lidar_pose(k, W, H):
    tau = k / LIDAR_RATE
    return (0.1 * W + 0.8 * W * tau / LOOP, 0.15 * H), 2 * math.pi * LIDAR_REVS * tau


@lru_cache(maxsize=8192)
def _lidar_hit(k, W, H):
    (ox, oy), ang = lidar_pose(k, W, H)
    dx, dy = math.cos(ang), math.sin(ang)
    best = 0.55 * W                                              # 라이다 최대 거리
    hit = None
    for (ax, ay), (bx, by) in lidar_segments(W, H):
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        s = ((ax - ox) * ey - (ay - oy) * ex) / den
        v = ((ax - ox) * dy - (ay - oy) * dx) / den
        if 1e-9 < s < best and 0 <= v <= 1:
            best, hit = s, (ax + ex * v, ay + ey * v)
    return hit


def lidar_hits(t, W, H):
    return [h for k in range(int(_wrap(t) * LIDAR_RATE)) if (h := _lidar_hit(k, W, H)) is not None]


def draw_lidar(pen, t):
    W, H = pen.W, pen.H
    tt = _wrap(t)
    kmax = int(tt * LIDAR_RATE)
    hits = [(k, _lidar_hit(k, W, H)) for k in range(kmax)]
    for k, h in hits:
        if h is not None:
            pen.dot(*h, dim=k < kmax - 70)
    (ox, oy), ang = lidar_pose(tt * LIDAR_RATE, W, H)
    cur = _lidar_hit(int(tt * LIDAR_RATE), W, H)
    end = cur or (ox + 0.55 * W * math.cos(ang), oy + 0.55 * W * math.sin(ang))
    pen.line((ox, oy), end, dim=True)
    pen.circle((ox, oy), 2.5), pen.blob((ox - .5, oy - .5))


# ---- 5. tree (09) ------------------------------------------------------------------------------------------
def rrt_obstacles(W, H):
    return [(0.36 * W, 0.55 * H, 0.17 * H), (0.62 * W, 0.34 * H, 0.16 * H), (0.58 * W, 0.80 * H, 0.12 * H)]


def _free(p, obs, W, H, pad=0.0):
    return 2 <= p[0] <= W - 3 and 2 <= p[1] <= H - 3 and all(math.hypot(p[0] - cx, p[1] - cy) > r + pad for cx, cy, r in obs)


@lru_cache(maxsize=16)
def rrt(W, H):
    obs, rng, step = rrt_obstacles(W, H), random.Random(9), 5.0
    start, goal = (0.07 * W, 0.88 * H), (0.93 * W, 0.14 * H)
    nodes = [(start[0], start[1], -1)]
    for _ in range(6000):
        sample = goal if rng.random() < 0.08 else (rng.uniform(2, W - 3), rng.uniform(2, H - 3))
        i = min(range(len(nodes)), key=lambda j: (nodes[j][0] - sample[0]) ** 2 + (nodes[j][1] - sample[1]) ** 2)
        nx, ny, _ = nodes[i]
        d = math.hypot(sample[0] - nx, sample[1] - ny)
        if d < 1e-9:
            continue
        new = (nx + (sample[0] - nx) * min(1.0, step / d), ny + (sample[1] - ny) * min(1.0, step / d))
        if not all(_free((nx + (new[0] - nx) * f / 4, ny + (new[1] - ny) * f / 4), obs, W, H, 0.5) for f in range(1, 5)):
            continue
        nodes.append((new[0], new[1], i))
        if math.hypot(new[0] - goal[0], new[1] - goal[1]) < step:
            nodes.append((goal[0], goal[1], len(nodes) - 1))
            return {"nodes": nodes, "goal": len(nodes) - 1}
    return {"nodes": nodes, "goal": None}


def rrt_path(tree):
    path, i = [], tree["goal"]
    while i is not None and i >= 0:
        path.append(i)
        i = tree["nodes"][i][2]
    return path[::-1]


GROW = 5.5


def rrt_shown(tree, t):
    n = len(tree["nodes"])
    return list(range(max(1, int(n * motion.ease_out(_wrap(t) / GROW)))))


def draw_tree(pen, t):
    W, H = pen.W, pen.H
    tree = rrt(W, H)
    nodes = tree["nodes"]
    for cx, cy, r in rrt_obstacles(W, H):
        pen.circle((cx, cy), r, dim=True)
    shown = rrt_shown(tree, t)
    for i in shown[1:]:
        x, y, p = nodes[i]
        pen.line((nodes[p][0], nodes[p][1]), (x, y), dim=i < len(shown) - 12)
    s, g = nodes[0], (0.93 * W, 0.14 * H)
    pen.circle(s[:2], 2.5), pen.circle(g, 2.5)
    if tree["goal"] is not None and _wrap(t) >= GROW:
        blink = int(_wrap(t) * 4) % 2 == 0 or _wrap(t) > GROW + 1.2
        if blink:
            path = rrt_path(tree)
            for a, b in zip(path, path[1:]):
                pen.line(nodes[a][:2], nodes[b][:2], thick=True)


# ---- 6. swarm (14) --------------------------------------------------------------------------------------------
SWARM_N = 28


def swarm_center(W, H):
    return (W / 2, H / 2)


def swarm_positions(t, W, H):
    rng = random.Random(14)
    cx, cy = swarm_center(W, H)
    out = []
    s = motion.smoothstep(0.5 - 0.5 * math.cos(2 * math.pi * _wrap(t) / LOOP))
    for i in range(SWARM_N):
        start = (rng.uniform(0.08, 0.92) * W, rng.uniform(0.1, 0.9) * H)
        a = 2 * math.pi * i / SWARM_N
        slot = (cx + 0.2 * H * math.cos(a), cy + 0.2 * H * math.sin(a))
        wob = 3.0 * (1 - s) * math.sin(2 * math.pi * _wrap(t) / LOOP * 3 + i)
        out.append((start[0] + (slot[0] - start[0]) * s + wob, start[1] + (slot[1] - start[1]) * s + wob * 0.6))
    return out


def draw_swarm(pen, t):
    W, H = pen.W, pen.H
    for k in range(6, 0, -1):
        for p in swarm_positions(t - k * 0.09, W, H):
            pen.dot(*p, dim=True)
    for p in swarm_positions(t, W, H):
        pen.blob((p[0] - .5, p[1] - .5))


DRAW = {"arm": draw_arm, "payload": draw_payload, "pubsub": draw_pubsub, "lidar": draw_lidar, "tree": draw_tree, "swarm": draw_swarm}


def render_scene(name, t, cw, ch, bright, dim):
    cv = Braille(cw, ch)
    DRAW[name](Pen(cv, bright, dim), t)
    return cv


def scene_lines(u, name, t, phase_idx):
    col = U.phase_color(phase_idx, u.dark)
    cv = render_scene(name, t, scene_cols(u), H_CELLS, f"bold {col}", f"dim {col}")
    return [Text("  ") + row for row in cv.text_rows()]


def caption_text(u, name, phase_idx, hint=True):
    title, title_ko, cap, cap_ko = INFO[name]
    t = Text("  ")
    t.append(u.t(title, title_ko), style="bold")
    t.append("   " + u.t(cap, cap_ko), style="muted")
    if hint:
        t.append("   " + u.t("Ctrl-C to quit", "Ctrl-C 로 종료"), style="muted")
    return t


def run_scene(u, name, phase_idx, sleep=time.sleep, now=time.monotonic, poll=None):
    """8초 장면을 15 fps 로 무한 반복한다. Ctrl-C 나 q 로 끝나며 커서는 Live 가 되돌린다."""
    def frame(t):
        return Text("\n").join(scene_lines(u, name, t, phase_idx) + [caption_text(u, name, phase_idx)])
    if poll is not None:
        return motion.run_frames(u, frame, duration=None, fps=FPS, sleep=sleep, now=now, poll=poll)
    with motion.keys() as p:
        return motion.run_frames(u, frame, duration=None, fps=FPS, sleep=sleep, now=now, poll=p)
