# Excalidraw 다이어그램을 코드로 만드는 helper: 상자와 화살표를 기록해 두었다가 save() 때 폰 폭에서 읽히게 배치하고 .excalidraw 로 저장한다
import heapq
import json
import math
import pathlib

from PIL import Image, ImageDraw

COLORS = {  # soft fills, same hues across every lesson
    "blue": "#a5d8ff", "green": "#b2f2bb", "yellow": "#ffec99",
    "red": "#ffc9c9", "purple": "#d0bfff", "gray": "#e9ecef", "white": "#ffffff",
}
INK = "#1e1e1e"
NOTE_INK = "#495057"

# Nunito (Excalidraw font family 6) advance widths per 1000 em for ASCII 32..126, read from the font file the exporter embeds
_ADV = [261, 233, 405, 600, 600, 933, 701, 226, 326, 326, 451, 600, 233, 427, 233, 290, 600, 600, 600, 600, 600, 600, 600, 600,
        600, 600, 233, 233, 600, 600, 600, 447, 947, 733, 679, 675, 747, 586, 551, 729, 764, 262, 331, 634, 548, 858, 741, 771,
        637, 771, 673, 618, 607, 731, 694, 1104, 655, 601, 593, 324, 290, 324, 600, 500, 361, 533, 587, 465, 587, 534, 340, 590,
        572, 237, 241, 508, 301, 861, 572, 560, 587, 587, 365, 483, 358, 565, 518, 844, 530, 517, 466, 361, 270, 361, 600]
FONT = 6
LINE = 1.25          # line height factor used for every text element
F_BOX = 26           # box text size; phone width 350 px gives 26 * 350 / ~700 = 13 px
F_SMALL = 24         # labels, notes, badge digits
F_TITLE = 30
EFF_TARGET = 12.3   # smallest text, in px, wanted when the PNG is shown 350 px wide
CANVAS_MAX = 660     # px of canvas width that keeps F_SMALL >= ~12 px on a 350 px phone
PHONE = 350
PAD_X, PAD_Y = 12, 14
STUB = 24            # straight bit an arrow leaves or enters a box with
BUSY = 240           # extra route cost for ending on a box side another arrow already uses (so each end can sit at the middle)
CLEAR = 8            # router keeps this far from every box
BEND, OVERLAP, CROSS = 45, 400, 70
SHAPE = {"rectangle": (1.0, 1.0, 1.0), "ellipse": (1.1, 0.72, 1.45), "diamond": (1.2, 0.55, 1.9)}  # width budget, text-area ratio, height factor


def text_width(text, size):
    """Width in px of the widest line of text at font size `size`."""
    return max(sum(_ADV[ord(c) - 32] if 32 <= ord(c) < 127 else 600 for c in ln) for ln in text.split("\n")) * size / 1000


def wrap(text, size, max_px):
    """Break at spaces so no line is wider than max_px; the author's own line breaks stay."""
    out = []
    for line in text.split("\n"):
        cur = ""
        for w in line.split(" "):
            t = f"{cur} {w}" if cur else w
            if cur and text_width(t, size) > max_px:
                out.append(cur)
                cur = w
            else:
                cur = t
        out.append(cur)
    return out


def _cluster(vals, tol):
    """Map each value to the dense rank of its cluster (values within tol of each other share a rank)."""
    s = sorted(set(vals))
    rank, r, last = {}, -1, None
    for v in s:
        if last is None or v - last > tol:
            r += 1
        rank[v] = r
        last = v
    return rank


def _hit(p, q, r):
    """Open-interior hit of axis-aligned segment pq with rectangle r = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = r
    ax, bx = sorted((p[0], q[0]))
    ay, by = sorted((p[1], q[1]))
    if ax == bx:
        return x0 < ax < x1 and by > y0 and ay < y1
    return y0 < ay < y1 and bx > x0 and ax < x1


def _rects_hit(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def _inflate(r, d):
    return (r[0] - d, r[1] - d, r[2] + d, r[3] + d)


class Diagram:
    """Collects boxes, arrows and notes; save() lays them out for a phone and writes the .excalidraw file.

    Old calls keep working: box(text, col, row, color), arrow(a, b, label=, dashed=, route=), note(text, x, y), title(text).
    col and row only say which box sits left of or above which; the engine decides the pixels.
    New: Diagram(numbered=True) badges the boxes in reading order, box(step=n) sets a number by hand,
    note(text, near=box_id, side="r") hangs a note on a box.
    """

    def __init__(self, cell=(300, 170), margin=40, numbered=False, columns=3):
        self.cw, self.ch = cell          # kept: old scripts place notes with d.margin / d.cw / d.ch arithmetic
        self.margin = margin
        self.numbered = numbered
        self.columns = columns
        self._nodes, self._edges, self._notes = [], [], []
        self._title = None
        self._n = 0
        self.warnings = []

    # ----- recording -----
    def box(self, text, col=None, row=None, color="blue", w=220, h=88, shape="rectangle", size=20, dx=0, dy=0, step=None):
        if col is None:
            col = (self._nodes[-1]["col"] + 1) if self._nodes else 0
        if row is None:
            row = self._nodes[-1]["row"] if self._nodes else 0
        self._n += 1
        n = dict(id=f"box{self._n}", text=text, col=col, row=row, color=color, shape=shape, w=w, h=h, dx=dx, dy=dy, step=step)
        self._nodes.append(n)
        return n["id"]

    def arrow(self, a, b, label=None, dashed=False, color=INK, route=None, label_dx=0, label_dy=0):
        self._n += 1
        self._edges.append(dict(id=f"arrow{self._n}", a=a, b=b, label=label, dashed=dashed, color=color, route=route))

    def note(self, text, x=None, y=None, size=18, color=NOTE_INK, w=None, near=None, side="r"):
        self._notes.append(dict(text=text, x=x, y=y, near=near, side=side, color=color))

    def title(self, text, size=30):
        self._title = text

    @property
    def boxes(self):
        return {n["id"]: n for n in self._nodes}

    # ----- layout -----
    def _plan(self, mode):
        """Grid positions (cx, cy in cells) of every box for one layout mode, or None if the mode does not apply."""
        ns = self._nodes
        lay = _cluster([n["col"] for n in ns], 0.35)
        lane = _cluster([n["row"] for n in ns], 0.15)
        rows = {r: [n["row"] for n in ns if lane[n["row"]] == r] for r in set(lane.values())}
        rowv = {r: sum(v) / len(v) for r, v in rows.items()}
        r0 = min(rowv.values())
        pos = {}
        if mode == "lr":
            for n in ns:
                pos[n["id"]] = (lay[n["col"]], rowv[lane[n["row"]]] - r0)
        elif mode == "td":
            for n in ns:
                pos[n["id"]] = (rowv[lane[n["row"]]] - r0, lay[n["col"]])
        elif mode == "snake":
            if len(set(lane.values())) != 1 or len(set(lay.values())) != len(ns):
                return None
            L = len(ns)
            c = 2 if L <= 4 else 3
            for n in sorted(ns, key=lambda n: lay[n["col"]]):
                i = lay[n["col"]]
                r, k = divmod(i, c)
                pos[n["id"]] = (k if r % 2 == 0 else c - 1 - k, r)
        return pos

    @staticmethod
    def _axis(items, gap, nominal):
        """items are (id, grid coord, size, grid coord on the other axis). Returns id -> centre in px along this axis:
        boxes that share a column or row keep `gap` between them, otherwise the author's spacing is kept."""
        rank = _cluster([c for _, c, _, _ in items], 0.15)
        groups = {}
        for it in items:
            groups.setdefault(rank[it[1]], []).append(it)
        keys = sorted(groups)
        cval = {k: sum(i[1] for i in groups[k]) / len(groups[k]) for k in keys}
        size = {k: max(i[2] for i in groups[k]) for k in keys}
        y = {}
        for n, k in enumerate(keys):
            lo = size[k] / 2 if n == 0 else y[keys[n - 1]] + (cval[k] - cval[keys[n - 1]]) * nominal
            for j in keys[:n]:
                for a in groups[j]:
                    for b in groups[k]:
                        if abs(a[3] - b[3]) < 0.99:
                            lo = max(lo, y[j] + (a[2] + b[2]) / 2 + gap)
            y[k] = lo
        return {it[0]: y[rank[it[1]]] for it in items}

    @staticmethod
    def _snap(pos):
        """Too many lanes for the column limit: move boxes that sit between two lanes onto a whole column if its cell is free."""
        taken = {(p[0], round(p[1] * 2)) for p in pos.values() if abs(p[0] - round(p[0])) < 1e-6}
        out = {}
        for k, (cx, cy) in sorted(pos.items(), key=lambda kv: kv[1]):
            if abs(cx - round(cx)) > 1e-6:
                for c in sorted({math.floor(cx), math.ceil(cx)}, key=lambda c: abs(c - cx)):
                    if (c, round(cy * 2)) not in taken:
                        taken.add((c, round(cy * 2)))
                        cx = c
                        break
            out[k] = (cx, cy)
        return out

    def _layout(self, mode, budget=CANVAS_MAX):
        pos = self._plan(mode)
        if pos is None:
            return None
        ns, es = self._nodes, self._edges
        if mode == "td" and len(set(_cluster([p[0] for p in pos.values()], 0.2).values())) > self.columns:
            pos = self._snap(pos)
        xs = [p[0] for p in pos.values()]
        span = max(xs) - min(xs)
        cells = math.ceil(span - 1e-6) + 1 if span > 1e-6 else 1
        cols_over = max(0, cells - self.columns)
        # labels decide how much room the gaps between boxes need
        lab = {}
        for e in es:
            if e["label"]:
                lines = wrap(e["label"], F_SMALL, 200)
                lab[e["id"]] = (lines, max(text_width(s, F_SMALL) for s in lines) + 14, len(lines) * F_SMALL * LINE + 8)
        hgap, vgap = (52, 58) if budget > 480 else (40, 48)
        hgap, vgap = hgap + (10 if self.numbered else 0), vgap + (10 if self.numbered else 0)
        for e in es:
            if e["id"] in lab:
                (ax, ay), (bx, by_) = pos[e["a"]], pos[e["b"]]
                if abs(ay - by_) < 0.99 and abs(ax - bx) <= 1.01:
                    hgap = max(hgap, lab[e["id"]][1] + 36)
                if abs(ax - bx) < 0.5 and abs(ay - by_) <= 1.01:
                    vgap = max(vgap, lab[e["id"]][2] + 34)
        # box width from the budget, then text wrapped to it
        wmax = (budget - span * hgap) / (span + 1)
        wmax = max(110, min(wmax, 300))
        lines, wid, hs = {}, {}, {}
        for n in ns:
            kw, k, kh = SHAPE[n["shape"]]
            ln = wrap(n["text"], F_BOX, (wmax * kw - 2 * PAD_X) * k)
            lines[n["id"]] = ln
            wid[n["id"]] = math.ceil(max(110, max(text_width(s, F_BOX) for s in ln) * 1.03 / k + 2 * PAD_X))
            hs[n["id"]] = math.ceil(len(ln) * F_BOX * LINE * kh + 2 * PAD_Y + (6 if self.numbered else 0))
        rects_w = [wid[n["id"]] for n in ns if n["shape"] == "rectangle"]
        wbox = max(rects_w) if rects_w else max(wid.values())
        for n in ns:
            if n["shape"] == "rectangle":
                wid[n["id"]] = wbox
        x0 = 60.0  # room for outer routing lanes
        cxs = self._axis([(n["id"], pos[n["id"]][0], wid[n["id"]], pos[n["id"]][1]) for n in ns], hgap, wbox + hgap)
        cys = self._axis([(n["id"], pos[n["id"]][1], hs[n["id"]], pos[n["id"]][0]) for n in ns], vgap, sorted(hs.values())[len(hs) // 2] + vgap)
        rect = {}
        for n in ns:
            w, h = wid[n["id"]], hs[n["id"]]
            xc, yc = x0 + cxs[n["id"]], 60 + cys[n["id"]]
            rect[n["id"]] = (xc - w / 2, yc - h / 2, xc + w / 2, yc + h / 2)
        order = self._reading_order(pos)
        badges = {}
        if self.numbered:
            for nid, k in order.items():
                r = rect[nid]
                badges[nid] = (r[0], r[1], k)
        obst = {nid: _inflate(r, CLEAR) for nid, r in rect.items()}
        for nid, (bx, by_, _) in badges.items():
            obst["b" + nid] = (bx - 18, by_ - 18, bx + 18, by_ + 18)
        self._rect, self._shape = rect, {n['id']: n['shape'] for n in ns}
        routes = self._route(rect, obst, lab)
        placed = []
        for r in rect.values():
            placed.append(_inflate(r, 3))
        for nid, (bx, by_, _) in badges.items():
            placed.append((bx - 18, by_ - 18, bx + 18, by_ + 18))
        labels, fails = self._place_labels(routes, lab, placed)
        return dict(mode=mode, rect=rect, lines=lines, routes=routes, labels=labels, fails=fails, badges=badges, cols_over=cols_over)

    def _reading_order(self, pos):
        ns = self._nodes
        lay = _cluster([n["col"] for n in ns], 0.35)
        hand = [n for n in ns if n["step"] is not None]
        auto = sorted((n for n in ns if n["step"] is None), key=lambda n: (lay[n["col"]], n["row"]))
        order = {n["id"]: n["step"] for n in hand}
        k = max([n["step"] for n in hand] + [0])
        for n in auto:
            k += 1
            order[n["id"]] = k
        return order

    # ----- orthogonal router -----
    def _route(self, rect, obst, lab):
        xs, ys = set(), set()
        ex, ey = sorted({v for r in rect.values() for v in (r[0], r[2])}), sorted({v for r in rect.values() for v in (r[1], r[3])})
        for a, b in zip(ex, ex[1:]):
            if b - a > 16:
                xs.add((a + b) / 2)
        for a, b in zip(ey, ey[1:]):
            if b - a > 16:
                ys.add((a + b) / 2)
        for r in rect.values():
            xs.add((r[0] + r[2]) / 2)
            ys.add((r[1] + r[3]) / 2)
        lane = max([30] + [min(110, v[1] / 2 + 16) for v in lab.values()])
        for k in (lane, lane + 22):
            xs |= {ex[0] - k, ex[-1] + k}
            ys |= {ey[0] - k, ey[-1] + k}
        stub = {e["id"]: (max(STUB, min(100, math.ceil(max(lab[e["id"]][1] / 2 + 12, lab[e["id"]][2] / 2 + 8)))) if e["id"] in lab else STUB) for e in self._edges}
        clear = {e["id"]: ((max(CLEAR, lab[e["id"]][1] / 2 + 6), max(CLEAR, lab[e["id"]][2] / 2 + 6)) if e["id"] in lab else (CLEAR, CLEAR)) for e in self._edges}
        extras = [v for k, v in obst.items() if k not in rect]
        blockers = [_inflate(r, 3) for r in rect.values()] + extras
        edges = self._edges
        fwd = sorted(edges, key=lambda e: (e["route"] == "below", self._dist(rect, e)))
        # two aligned boxes joined by one arrow get a straight arrow between the middles of facing sides; nobody else may use those sides
        pair_n = {}
        for e in edges:
            k = frozenset((e["a"], e["b"]))
            pair_n[k] = pair_n.get(k, 0) + 1
        straight, reserved = {}, set()
        for e in edges:
            a, b = e["a"], e["b"]
            if a != b and pair_n[frozenset((a, b))] == 1:
                res = self._straight(rect, obst, a, b, {s: self._ep(a, s) for s in "trbl"}, {s: self._ep(b, s) for s in "trbl"})
                if res:
                    straight[e["id"]] = res
                    reserved |= {(a, res[0]), (b, res[1])}
        side_of = {}
        for pass_ in (0, 1):
            ports = self._ports(rect, side_of, lab) if pass_ else {}
            X, Y = set(), set()
            if pass_:
                for e in edges:
                    for k, nid in ((0, e["a"]), (1, e["b"])):
                        s = side_of[e["id"]][k]
                        p, st = self._ep(nid, s, ports[(nid, s)][e["id"]], stub[e["id"]])
                        X |= {p[0], st[0]}
                        Y |= {p[1], st[1]}
            else:
                for e in edges:
                    for nid in (e["a"], e["b"]):
                        for s in "trbl":
                            p, st = self._ep(nid, s, 0, stub[e["id"]])
                            X |= {p[0], st[0]}
                            Y |= {p[1], st[1]}
            X, Y = self._merge(X, xs), self._merge(Y, ys)
            net = _Lattice(X, Y, list(rect.values()), extras)
            done, label_rects, busy = {}, [], set(reserved)   # busy: box sides an arrow already uses; the next arrow prefers a free side
            for e in sorted(fwd, key=lambda e: e["id"] not in straight):
                a, b = e["a"], e["b"]
                if e["id"] in straight:
                    res = straight[e["id"]]
                    net.claim(res[2])
                else:
                    sa = [side_of[e["id"]][0]] if pass_ else [s for s in "trbl" if (a, s) not in reserved]
                    sb = [side_of[e["id"]][1]] if pass_ else [s for s in "trbl" if (b, s) not in reserved]
                    pa = {s: self._ep(a, s, ports[(a, s)][e["id"]] if pass_ else 0, stub[e["id"]]) for s in sa}
                    pb = {s: self._ep(b, s, ports[(b, s)][e["id"]] if pass_ else 0, stub[e["id"]]) for s in sb}
                    pen_a = {s: v + (0 if pass_ or (a, s) not in busy else BUSY) for s, v in self._side_pen(rect[a], rect[b]).items()}
                    pen_b = {s: v + (0 if pass_ or (b, s) not in busy else BUSY) for s, v in self._side_pen(rect[b], rect[a]).items()}
                    res = net.route(pa, pb, pen_a, pen_b, clear[e["id"]])
                if res is None:
                    s1, s2 = ("r", "l") if rect[a][2] <= rect[b][0] else ("b", "t")
                    res = (s1, s2, [self._ep(a, s1)[0], self._ep(b, s2)[0]])
                    self.warnings.append(f"no clear route for {e['id']}")
                done[e["id"]] = res
                busy |= {(a, res[0]), (b, res[1])}
                side_of[e["id"]] = (res[0], res[1])
                if e["id"] in lab:
                    r = self._mid_label(res[2], lab[e["id"]][1], lab[e["id"]][2], blockers + label_rects, [sg for k, v in done.items() if k != e["id"] for sg in zip(v[2], v[2][1:])])
                    if r:
                        label_rects.append(r)
                        net.add_extra(_inflate(r, 4))
            routes = {k: v[2] for k, v in done.items()}
        return routes

    def _ep(self, nid, s, off=0.0, stub=STUB):
        """(point on the outline, stub point STUB px beyond the bounding box) for side s of box nid, `off` px along the side from its middle."""
        r, shape = self._rect[nid], self._shape[nid]
        cx, cy, a, b = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2, (r[2] - r[0]) / 2, (r[3] - r[1]) / 2
        half, across = (b, a) if s in "tb" else (a, b)        # reach to the side, and half the side's length
        reach = half if shape == "rectangle" else (half * math.sqrt(max(0.0, 1 - (off / across) ** 2)) if shape == "ellipse" else half * (1 - abs(off) / across))
        sign = 1 if s in "br" else -1
        if s in "tb":
            return (cx + off, cy + sign * reach), (cx + off, (r[3] + stub) if s == "b" else (r[1] - stub))
        return (cx + sign * reach, cy + off), ((r[2] + stub) if s == "r" else (r[0] - stub), cy + off)

    @staticmethod
    def _straight(rect, obst, a, b, pa, pb):
        """Two boxes that face each other with their middles level: one straight arrow joining the middles of the facing sides."""
        ra, rb = rect[a], rect[b]
        for sa, sb, ok, ax in (("r", "l", ra[2] + 20 <= rb[0], 1), ("l", "r", rb[2] + 20 <= ra[0], 1), ("b", "t", ra[3] + 20 <= rb[1], 0), ("t", "b", rb[3] + 20 <= ra[1], 0)):
            if ok and abs(pa[sa][0][ax] - pb[sb][0][ax]) < 0.5:
                p, q = pa[sa][0], pb[sb][0]
                if not any(_hit(p, q, o) for k, o in obst.items() if k not in (a, b)):
                    return sa, sb, [p, q]
        return None

    @staticmethod
    def _side_pen(ra, rb):
        """Cost of leaving box ra by each side on the way to rb: free toward rb along the longer axis, a little for the other axis, a lot away."""
        dx, dy = (rb[0] + rb[2] - ra[0] - ra[2]) / 2, (rb[1] + rb[3] - ra[1] - ra[3]) / 2
        pen = {}
        for s, (ax, sign) in {"r": (0, 1), "l": (0, -1), "b": (1, 1), "t": (1, -1)}.items():
            d = (dx, dy)[ax] * sign
            pen[s] = 30 if d < 0 else (0 if (abs(dx) >= abs(dy)) == (ax == 0) else 10)
        return pen

    @staticmethod
    def _merge(exact, extra):
        """Lattice lines: every port and stub coordinate exactly as it is, plus the generic lanes that are not within 1.5 px of one."""
        keep = sorted({round(v, 2) for v in exact})
        return sorted(keep + [v for v in sorted(extra) if all(abs(v - k) > 1.5 for k in keep)])

    def _dist(self, rect, e):
        a, b = rect[e["a"]], rect[e["b"]]
        return abs((a[0] + a[2]) / 2 - (b[0] + b[2]) / 2) + abs((a[1] + a[3]) / 2 - (b[1] + b[3]) / 2)

    def _ports(self, rect, side_of, lab):
        """Arrows that share a box side are spread evenly and symmetrically about its middle, ordered by where they head."""
        use = {}
        for e in self._edges:
            for k, nid, other in ((0, e["a"], e["b"]), (1, e["b"], e["a"])):
                use.setdefault((nid, side_of[e["id"]][k]), []).append((e["id"], other))
        spread = {}
        for (nid, s), lst in use.items():
            r = rect[nid]
            ax = 0 if s in "tb" else 1
            c0 = (r[ax] + r[ax + 2]) / 2
            lst.sort(key=lambda t: ((rect[t[1]][ax] + rect[t[1]][ax + 2]) / 2 - c0, t[0]))
            m = len(lst)
            need = max([lab[eid][2 if s in 'lr' else 1] / 2 + 8 for eid, _ in lst if eid in lab] + [34])
            step = min(need, 0.85 * (r[ax + 2] - r[ax]) / m)
            spread[(nid, s)] = {eid: (i - (m - 1) / 2) * step for i, (eid, _) in enumerate(lst)}
        return spread

    # ----- labels -----
    @staticmethod
    def _mid_label(pts, w, h, rects, others):
        """Label rectangle centred on the middle of the longest straight run of the arrow that has room for it, or None."""
        segs = list(zip(pts, pts[1:]))
        for i in sorted(range(len(segs)), key=lambda i: -(abs(segs[i][1][0] - segs[i][0][0]) + abs(segs[i][1][1] - segs[i][0][1]))):
            p, q = segs[i]
            horiz = abs(q[1] - p[1]) < 0.5
            if abs(q[0] - p[0]) + abs(q[1] - p[1]) < (w if horiz else h) + 16:
                continue
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            r = (mx - w / 2, my - h / 2, mx + w / 2, my + h / 2)
            if any(_rects_hit(r, _inflate(o, 2)) for o in rects) or any(_hit(a, b, _inflate(r, 2)) for a, b in others):
                continue
            if any(_hit(a, b, _inflate(r, 1)) for j, (a, b) in enumerate(segs) if j != i):
                continue
            return r
        return None

    def _place_labels(self, routes, lab, placed):
        out, fails = {}, 0
        placed = list(placed)
        segs_all = {k: list(zip(v, v[1:])) for k, v in routes.items()}
        for e in self._edges:
            if e["id"] not in lab:
                continue
            lines, w, h = lab[e["id"]]
            segs = segs_all[e["id"]]
            others = [s for k, v in segs_all.items() if k != e["id"] for s in v]
            mid = self._mid_label(routes[e["id"]], w, h, placed, others)
            if mid:
                placed.append(mid)
                out[e["id"]] = (mid, lines)
                continue
            cands = []
            for i, (p, q) in enumerate(segs):
                L = abs(q[0] - p[0]) + abs(q[1] - p[1])
                horiz = abs(q[1] - p[1]) < 0.5
                for f in (0.5, 0.35, 0.65, 0.25, 0.75):
                    mx, my = p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f
                    along = w if horiz else h
                    if L < along + 18 and f != 0.5:
                        continue
                    if horiz:
                        opts = [(mx - w / 2, my - h / 2, 0), (mx - w / 2, my - h - 6, 3), (mx - w / 2, my + 6, 3)]
                    else:
                        opts = [(mx - w / 2, my - h / 2, 0), (mx + 8, my - h / 2, 3), (mx - w - 8, my - h / 2, 3)]
                    for x, y, pref in opts:
                        fit = 0 if L >= along + 18 else 8
                        cands.append((pref + fit + abs(f - 0.5) * 10 + (0 if i not in (0, len(segs) - 1) else 2) - L / 400, (x, y, x + w, y + h), i))
            cands.sort(key=lambda c: c[0])
            chosen = None
            for _, r, i in cands:
                if any(_rects_hit(r, _inflate(o, 2)) for o in placed):
                    continue
                if any(_hit(p, q, _inflate(r, 2)) for p, q in others):
                    continue
                if any(_hit(p, q, _inflate(r, 1)) for j, (p, q) in enumerate(segs) if j != i):
                    continue
                chosen = r
                break
            if chosen is None:
                fails += 1
                self.warnings.append(f"label '{e["label"]}' has no clear spot")
                chosen = cands[0][1] if cands else (0, 0, w, h)
            placed.append(chosen)
            out[e["id"]] = (chosen, lines)
        return out, fails

    # ----- scoring -----
    @staticmethod
    def _extent(L):
        pts = [p for r in L["routes"].values() for p in r]
        rs = list(L["rect"].values()) + [r for r, _ in L["labels"].values()]
        xs = [r[0] for r in rs] + [r[2] for r in rs] + [p[0] for p in pts]
        ys = [r[1] for r in rs] + [r[3] for r in rs] + [p[1] for p in pts]
        return max(xs) - min(xs) + 48, max(ys) - min(ys) + 48

    @staticmethod
    def _score(L):
        routes = L["routes"]
        segs = {k: list(zip(v, v[1:])) for k, v in routes.items()}
        cross = bends = 0
        length = 0
        keys = list(segs)
        for k, v in segs.items():
            bends += max(0, len(v) - 1)
            length += sum(abs(q[0] - p[0]) + abs(q[1] - p[1]) for p, q in v)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                for p, q in segs[a]:
                    for r, s in segs[b]:
                        if (p[0] == q[0]) != (r[0] == s[0]):
                            v, h = ((p, q), (r, s)) if p[0] == q[0] else ((r, s), (p, q))
                            if min(h[0][0], h[1][0]) < v[0][0] < max(h[0][0], h[1][0]) and min(v[0][1], v[1][1]) < h[0][1] < max(v[0][1], v[1][1]):
                                cross += 1
        w, h = Diagram._extent(L)
        eff = F_SMALL * PHONE / w
        base = {"lr": 0, "snake": 0, "td": 22}[L["mode"]]
        nl = max(len(v) for v in L["lines"].values())
        return (cross * 50 + bends * 4 + length / 80 + L["fails"] * 150 + L["cols_over"] * 400 + max(0, 12.5 - eff) * 120
                + max(0, h * PHONE / w - 380) / 3 + max(0, nl - 3) * 12 + base)

    # ----- output -----
    def _el(self, typ, x, y, w, h, **kw):
        self._eid += 1
        e = dict(type=typ, id=f"e{self._eid}", x=x, y=y, width=w, height=h, angle=0, strokeColor=INK, backgroundColor="transparent",
                 fillStyle="solid", strokeWidth=2, strokeStyle="solid", roughness=1, opacity=100, groupIds=[], frameId=None,
                 roundness=None, seed=1000 + self._eid * 7, version=1, versionNonce=self._eid, isDeleted=False, boundElements=None,
                 updated=1, link=None, locked=False)
        e.update(kw)
        return e

    def _text(self, text, x, y, w, size, container=None, color=INK, align="center", role=None, **extra):
        lines = text.split("\n")
        h = round(len(lines) * size * LINE)
        e = self._el("text", x, y, w, h, text=text, originalText=text, fontSize=size, fontFamily=FONT, textAlign=align,
                     verticalAlign="middle" if container else "top", containerId=container, strokeColor=color, strokeWidth=1,
                     lineHeight=LINE, autoResize=not container, roughness=0)
        if role or extra:
            e["customData"] = dict(extra, **({"role": role} if role else {}))
        return e

    def scene(self):
        if not self._nodes:
            return {"type": "excalidraw", "version": 2, "source": "robotics-engineering-from-scratch", "elements": [],
                    "appState": {"viewBackgroundColor": "#ffffff"}, "files": {}}
        self.warnings = []
        best = None
        for mode in ("lr", "td", "snake"):
            saved = list(self.warnings)
            L = None
            for budget in (CANVAS_MAX, 600, 540, 480, 420):
                self.warnings = list(saved)
                L = self._layout(mode, budget)
                if L is None or F_SMALL * PHONE / self._extent(L)[0] >= EFF_TARGET:
                    break
            if L is None:
                continue
            sc = self._score(L)
            if best is None or sc < best[0]:
                best = (sc, L, list(self.warnings))
            self.warnings = saved
        _, L, self.warnings = best
        self.layout_mode = L["mode"]
        return self._emit(L)

    def _emit(self, L):
        self._eid = 0
        els = []
        rect, routes = L["rect"], L["routes"]
        foot = [n for n in self._notes if n["near"] is None]  # old calls gave x, y: those were always takeaway lines under the picture
        attach = [n for n in self._notes if n["near"] is not None]
        box_el, text_el = {}, {}
        for n in self._nodes:
            r = rect[n["id"]]
            w, h = r[2] - r[0], r[3] - r[1]
            b = self._el(n["shape"], r[0], r[1], w, h, id=n["id"], backgroundColor=COLORS.get(n["color"], n["color"]),
                         roundness={"type": 3} if n["shape"] == "rectangle" else None)
            ln = L["lines"][n["id"]]
            th = round(len(ln) * F_BOX * LINE)
            t = self._text("\n".join(ln), r[0] + PAD_X, r[1] + (h - th) / 2 + (3 if self.numbered else 0), w - 2 * PAD_X, F_BOX, container=n["id"])
            b["boundElements"] = [{"id": t["id"], "type": "text"}]
            box_el[n["id"]] = b
            text_el[n["id"]] = t
        arrow_els = []
        for e in self._edges:
            pts = routes[e["id"]]
            x0, y0 = pts[0]
            rel = [[round(px - x0, 1), round(py - y0, 1)] for px, py in pts]
            ar = self._el("arrow", x0, y0, max(abs(p[0]) for p in rel), max(abs(p[1]) for p in rel), id=e["id"], points=rel,
                          strokeColor=e["color"], strokeStyle="dashed" if e["dashed"] else "solid", roughness=0, roundness=None,
                          startArrowhead=None, endArrowhead="triangle", lastCommittedPoint=None, elbowed=False,
                          startBinding={"elementId": e["a"], "focus": 0, "gap": 1}, endBinding={"elementId": e["b"], "focus": 0, "gap": 1})
            for ref in (box_el[e["a"]], box_el[e["b"]]):
                ref["boundElements"] = (ref["boundElements"] or []) + [{"id": ar["id"], "type": "arrow"}]
            arrow_els.append(ar)
        extra = []
        for eid, (r, lines) in L["labels"].items():
            extra.append(self._el("rectangle", r[0], r[1], r[2] - r[0], r[3] - r[1], backgroundColor="#ffffff", strokeColor="transparent",
                                  strokeWidth=0, roughness=0, customData={"role": "label_bg", "label_of": eid}))
            th = len(lines) * F_SMALL * LINE
            extra.append(self._text("\n".join(lines), r[0] + 7, r[1] + (r[3] - r[1] - th) / 2, r[2] - r[0] - 14, F_SMALL, color=NOTE_INK,
                                    role="label", label_of=eid))
        for nid, (bx, by_, k) in L["badges"].items():
            extra.append(self._el("ellipse", bx - 16, by_ - 16, 32, 32, backgroundColor=INK, strokeWidth=1, roughness=0,
                                  customData={"role": "badge"}))
            extra.append(self._text(str(k), bx - 16, by_ - 16 + (32 - F_SMALL * LINE) / 2, 32, F_SMALL, color="#ffffff", role="badge_text"))
        # title and notes
        allr = list(rect.values()) + [r for r, _ in L["labels"].values()]
        for pts in routes.values():
            allr += [(min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))]
        left = min(r[0] for r in allr)
        right = max(r[2] for r in allr)
        placed = [_inflate(r, 3) for r in rect.values()] + [r for r, _ in L["labels"].values()]
        segs = [s for pts in routes.values() for s in zip(pts, pts[1:])]
        notes = []
        for nt in attach:
            ln = wrap(nt["text"], F_SMALL, 180)
            nw, nh = max(text_width(s, F_SMALL) for s in ln) + 4, len(ln) * F_SMALL * LINE
            r = rect[nt["near"]]
            cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
            opts = {"r": (r[2] + 22, cy - nh / 2), "l": (r[0] - 22 - nw, cy - nh / 2), "b": (cx - nw / 2, r[3] + 16), "t": (cx - nw / 2, r[1] - 16 - nh)}
            order = [nt["side"]] + [s for s in "brlt" if s != nt["side"]]
            free = []
            for s in order:
                x, y = opts[s]
                nr = (x, y, x + nw, y + nh)
                if any(_rects_hit(nr, o) for o in placed) or any(_hit(p, q, _inflate(nr, 3)) for p, q in segs):
                    continue
                free.append((max(right, nr[2]) - min(left, nr[0]) + 48, s, nr))
            roomy = [f for f in free if f[0] <= F_SMALL * PHONE / EFF_TARGET]
            pick = None
            if roomy:
                pick = roomy[0][1:]
            elif free:
                pick = min(free, key=lambda f: f[0])[1:]
            if pick is None:
                s = nt["side"]
                x, y = opts[s]
                pick = (s, (x, y, x + nw, y + nh))
                self.warnings.append(f"note '{nt['text'][:20]}' overlaps something")
            s, nr = pick
            placed.append(_inflate(nr, 2))
            notes.append((nt, ln, nr, s, r))
            left, right = min(left, nr[0]), max(right, nr[2])
        for nt, ln, nr, s, r in notes:
            els_note = self._text("\n".join(ln), nr[0], nr[1], nr[2] - nr[0], F_SMALL, color=NOTE_INK, align="left", role="note")
            cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
            a, b = {"r": ((r[2], cy), (nr[0] - 3, cy)), "l": ((r[0], cy), (nr[2] + 3, cy)),
                    "b": ((cx, r[3]), (cx, nr[1] - 2)), "t": ((cx, r[1]), (cx, nr[3] + 2))}[s]
            if s in "rl":
                b = (b[0], min(max(cy, nr[1] + 4), nr[3] - 4))
                a = (a[0], b[1])
            else:
                b = (min(max(cx, nr[0] + 4), nr[2] - 4), b[1])
                a = (b[0], a[1])
            leader = self._el("line", a[0], a[1], abs(b[0] - a[0]), abs(b[1] - a[1]), points=[[0, 0], [b[0] - a[0], b[1] - a[1]]],
                              strokeColor="#868e96", strokeWidth=1, strokeStyle="dashed", roughness=0, customData={"role": "leader"})
            extra += [leader, els_note]
        bottom = max(r[3] for r in allr + [n[2] for n in notes])
        body_w = max(right - left, 360)
        y = bottom + 34
        for nt in foot:
            ln = wrap(nt["text"], F_SMALL, body_w)
            extra.append(self._text("\n".join(ln), left, y, max(text_width(s, F_SMALL) for s in ln) + 4, F_SMALL, color=NOTE_INK, align="left", role="note"))
            y += len(ln) * F_SMALL * LINE + 10
        if self._title:
            tl = wrap(self._title, F_TITLE, max(body_w, 340))
            tw = max(text_width(s, F_TITLE) for s in tl) + 4
            top = min(r[1] for r in allr + [n[2] for n in notes])
            extra.append(self._text("\n".join(tl), left, top - 22 - len(tl) * F_TITLE * LINE, tw, F_TITLE, align="left", role="title"))
        els = []
        for n in self._nodes:
            els += [box_el[n["id"]], text_el[n["id"]]]
        els += arrow_els + extra
        # shift so the content starts near the origin
        minx = min(e["x"] if e["type"] != "arrow" else min(e["x"] + p[0] for p in e["points"]) for e in els)
        miny = min(e["y"] if e["type"] != "arrow" else min(e["y"] + p[1] for p in e["points"]) for e in els)
        for e in els:
            e["x"] = round(e["x"] - minx + 8, 1)
            e["y"] = round(e["y"] - miny + 8, 1)
            e["width"], e["height"] = round(e["width"], 1), round(e["height"], 1)
        return {"type": "excalidraw", "version": 2, "source": "robotics-engineering-from-scratch", "elements": els,
                "appState": {"viewBackgroundColor": "#ffffff"}, "files": {}}

    def save(self, path):
        scene = self.scene()
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(path).write_text(json.dumps(scene, indent=1))


class _Lattice:
    """Grid of candidate lines; finds the cheapest orthogonal path that keeps clear of boxes and of earlier routes."""

    def __init__(self, X, Y, boxes, extra):
        self.X, self.Y = X, Y
        self.xi = {v: i for i, v in enumerate(X)}
        self.yi = {v: i for i, v in enumerate(Y)}
        self.boxes, self.extra = boxes, list(extra)   # boxes are inflated per route, extra obstacles are used as they are
        self.used = {}
        self.thru_h, self.thru_v = set(), set()
        self._blocked = {}
        self.clear = (CLEAR, CLEAR)

    def _idx(self, p):
        x = min(self.X, key=lambda v: abs(v - p[0]))
        y = min(self.Y, key=lambda v: abs(v - p[1]))
        return self.xi[x], self.yi[y]

    def add_extra(self, rect):
        self.extra.append(rect)
        self._blocked = {}

    def blocked(self, a, b):
        k = (a, b) if a < b else (b, a)
        key = (k, self.clear)
        if key not in self._blocked:
            p, q = (self.X[a[0]], self.Y[a[1]]), (self.X[b[0]], self.Y[b[1]])
            cx, cy = self.clear
            self._blocked[key] = any(_hit(p, q, (r[0] - cx, r[1] - cy, r[2] + cx, r[3] + cy)) for r in self.boxes) or any(_hit(p, q, o) for o in self.extra)
        return self._blocked[key]

    def route(self, pa, pb, penA, penB, clear=(CLEAR, CLEAR)):
        self.clear = clear
        D = ((0, -1), (1, 0), (0, 1), (-1, 0))
        out = {"t": 0, "r": 1, "b": 2, "l": 3}
        sa, sb = {s: v[1] for s, v in pa.items()}, {s: v[1] for s, v in pb.items()}
        tgt = {}
        for s, p in sb.items():
            tgt.setdefault(self._idx(p), []).append(s)
        heap, cnt, best, parent = [], 0, {}, {}
        goal = [self._idx(p) for p in sb.values()]
        h = lambda n: min(abs(self.X[n[0]] - self.X[g[0]]) + abs(self.Y[n[1]] - self.Y[g[1]]) for g in goal)
        for s, p in sa.items():
            n = self._idx(p)
            st = (n[0], n[1], out[s])
            heapq.heappush(heap, (h(n) + penA[s], cnt, float(penA[s]), st, None, s))
            cnt += 1
            best[st] = float(penA[s])
            parent[st] = (None, s)
        while heap:
            f, _, g, st, term, s0 = heapq.heappop(heap)
            if term is not None:
                path = []
                cur = st
                while cur is not None:
                    path.append((self.X[cur[0]], self.Y[cur[1]]))
                    cur = parent[cur][0]
                path.reverse()
                s_start = parent[self._first(parent, st)][1]
                self._mark(path)
                p0 = pa[s_start][0]
                p1 = pb[term][0]
                pts = [p0] + path + [p1]
                return s_start, term, self._simplify(pts)
            if g > best.get(st, 1e18) + 1e-9:
                continue
            n = (st[0], st[1])
            if n in tgt:
                for s in tgt[n]:
                    total = g + penB[s] + (BEND if st[2] != (out[s] + 2) % 4 else 0)
                    heapq.heappush(heap, (total, cnt, total, st, s, None))
                    cnt += 1
            for d, (dx, dy) in enumerate(D):
                m = (n[0] + dx, n[1] + dy)
                if not (0 <= m[0] < len(self.X) and 0 <= m[1] < len(self.Y)) or self.blocked(n, m):
                    continue
                c = g + abs(self.X[m[0]] - self.X[n[0]]) + abs(self.Y[m[1]] - self.Y[n[1]])
                if d != st[2]:
                    if d == (st[2] + 2) % 4:
                        continue
                    c += BEND
                key = (n, m) if n < m else (m, n)
                c += OVERLAP * self.used.get(key, 0)
                if d in (0, 2) and m in self.thru_h or d in (1, 3) and m in self.thru_v:
                    c += CROSS
                ns = (m[0], m[1], d)
                if c < best.get(ns, 1e18) - 1e-9:
                    best[ns] = c
                    parent[ns] = (st, None)
                    heapq.heappush(heap, (c + h(m), cnt, c, ns, None, None))
                    cnt += 1
        return None

    def claim(self, pts):
        """Mark a hand-made path (a straight arrow) as used so later routes keep off it."""
        self._mark(pts)

    @staticmethod
    def _first(parent, st):
        while parent[st][0] is not None:
            st = parent[st][0]
        return st

    def _mark(self, path):
        idx = [self._idx(p) for p in path]
        for a, b in zip(idx, idx[1:]):
            k = (a, b) if a < b else (b, a)
            self.used[k] = self.used.get(k, 0) + 1
        for a, b, c in zip(idx, idx[1:], idx[2:]):
            if a[1] == b[1] == c[1]:
                self.thru_h.add(b)
            elif a[0] == b[0] == c[0]:
                self.thru_v.add(b)

    @staticmethod
    def _simplify(pts):
        out = [pts[0]]
        for p in pts[1:]:
            if p == out[-1]:
                continue
            if len(out) >= 2 and ((out[-2][0] == out[-1][0] == p[0]) or (out[-2][1] == out[-1][1] == p[1])):
                out[-1] = p
            else:
                out.append(p)
        return out


# ----- animated arrows: dashes flow along every arrow of the finished PNG, nothing else moves -----
ANIM_FRAMES, ANIM_MS = 12, 72                 # 13.9 frames a second; one dash period per loop is 1.16 periods a second
DASH_PERIOD, DASH_LEN, DASH_W, DASH_W_THIN = 40, 16, 7, 3.5   # px: spacing and length of a flowing dash, thickness on solid arrows, on dashed arrows
ARROW_HEAD, ARROW_TAIL, ACCENT = 24, 8, (25, 113, 194)   # px kept free at the head and at the box; dash colour on solid arrows
SS = 3                                        # drawing is supersampled this much so dashes are smooth


def _scene_min(scene):
    pts = [(e["x"] + px, e["y"] + py) for e in scene["elements"] for px, py in (e["points"] if e["type"] in ("arrow", "line") else [(0, 0), (e["width"], e["height"])])]
    return min(p[0] for p in pts), min(p[1] for p in pts)


def _arrow_paths(scene):
    return [(a, [(a["x"] + px, a["y"] + py) for px, py in a["points"]]) for a in scene["elements"] if a["type"] == "arrow"]


def _along(pts, step):
    """Points every `step` px along a polyline."""
    out, left = [], 0.0
    for p, q in zip(pts, pts[1:]):
        n = math.dist(p, q)
        t = left
        while t < n:
            out.append((p[0] + (q[0] - p[0]) * t / n, p[1] + (q[1] - p[1]) * t / n))
            t += step
        left = t - n
    return out


def _cut(pts, s0, s1):
    """The part of a polyline between arc lengths s0 and s1."""
    out, at = [], 0.0
    for p, q in zip(pts, pts[1:]):
        n = math.dist(p, q)
        a, b = max(s0, at), min(s1, at + n)
        if b > a:
            f = lambda s: (p[0] + (q[0] - p[0]) * (s - at) / n, p[1] + (q[1] - p[1]) * (s - at) / n)
            out += [f(a), f(b)] if not out else [f(b)]
        at += n
    return out


def png_offset(scene, base):
    """Where scene (0, 0) lands in the exported PNG: the exporter pads the content box by 24 px; checked against the arrows' own pixels."""
    mx, my = _scene_min(scene)
    ox, oy = 24 - mx, 24 - my
    px = base.convert("L").load()
    samples = [pt for _, pts in _arrow_paths(scene) for pt in _along(_cut(pts, 20, 1e9), 4)]
    def dark(dx, dy):
        return sum(255 - px[min(max(round(x + ox + dx), 0), base.width - 1), min(max(round(y + oy + dy), 0), base.height - 1)] for x, y in samples)
    best = max(((dark(dx, dy), -abs(dx) - abs(dy), dx, dy) for dx in range(-3, 4) for dy in range(-3, 4)))
    return ox + best[2], oy + best[3]


def animate(scene, base):
    """Frames (PIL images the size of `base`) with short dashes flowing from the start to the end of every arrow; [] when there are none."""
    paths = _arrow_paths(scene)
    if not paths:
        return []
    ox, oy = png_offset(scene, base)
    xs, ys = [p[0] + ox for _, pts in paths for p in pts], [p[1] + oy for _, pts in paths for p in pts]
    x0, y0 = max(0, int(min(xs)) - 10), max(0, int(min(ys)) - 10)            # only this part of the picture is ever painted
    x1, y1 = min(base.width, int(max(xs)) + 11), min(base.height, int(max(ys)) + 11)
    w, h = x1 - x0, y1 - y0
    big = lambda pts: [((x + ox - x0) * SS, (y + oy - y0) * SS) for x, y in pts]
    inner = [(a, _cut(pts, ARROW_TAIL, math.fsum(math.dist(p, q) for p, q in zip(pts, pts[1:])) - ARROW_HEAD)) for a, pts in paths]
    wipe = Image.new("L", (w * SS, h * SS), 0)   # a dashed arrow's own static dashes are painted out, then redrawn moving
    for a, pts in inner:
        if a["strokeStyle"] == "dashed" and len(pts) > 1:
            ImageDraw.Draw(wipe).line(big(pts), fill=255, width=6 * SS, joint="curve")
    wipe = wipe.reduce(SS)
    region = base.crop((x0, y0, x1, y1))
    labels = [(round(e["x"] + ox - x0) - 1, round(e["y"] + oy - y0) - 1, round(e["x"] + e["width"] + ox - x0) + 1, round(e["y"] + e["height"] + oy - y0) + 1)
              for e in scene["elements"] if (e.get("customData") or {}).get("role") == "label_bg"]   # a label sits on its arrow: keep it readable
    frames = []
    for i in range(ANIM_FRAMES):
        shift = i * DASH_PERIOD / ANIM_FRAMES
        layers = {}
        for a, pts in inner:
            if len(pts) < 2:
                continue
            total = math.fsum(math.dist(p, q) for p, q in zip(pts, pts[1:]))
            color = tuple(int(a["strokeColor"][k:k + 2], 16) for k in (1, 3, 5)) if a["strokeStyle"] == "dashed" else ACCENT
            m = layers.setdefault(color, Image.new("L", (w * SS, h * SS), 0))
            t = shift - DASH_PERIOD
            while t < total:
                seg = _cut(pts, max(t, 0), min(t + DASH_LEN, total))
                if len(seg) > 1:
                    ImageDraw.Draw(m).line(big(seg), fill=255, width=round((DASH_W_THIN if a["strokeStyle"] == "dashed" else DASH_W) * SS), joint="curve")
                t += DASH_PERIOD
        out = region.copy()
        out.paste((255, 255, 255), mask=wipe)
        for color, m in layers.items():
            out.paste(color, mask=m.reduce(SS))
        for box in labels:
            out.paste(region.crop(box), box)
        frame = base.copy()
        frame.paste(out, (x0, y0))
        frames.append(frame)
    return frames


def save_webp(frames, fp):
    frames[0].save(fp, format="WEBP", save_all=True, append_images=frames[1:], duration=ANIM_MS, loop=0, lossless=True, quality=60, method=2)


def write_anim(excalidraw_path, png_path, out_path):
    """Make out_path (animated WebP) from a rendered diagram; returns its size in bytes, 0 if the diagram has no arrows."""
    path = pathlib.Path(out_path)
    frames = animate(json.loads(pathlib.Path(excalidraw_path).read_text()), Image.open(png_path).convert("RGB"))
    if not frames:
        path.unlink(missing_ok=True)
        return 0
    save_webp(frames, path)
    return path.stat().st_size
