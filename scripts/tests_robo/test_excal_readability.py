# excal.py 가독성 테스트: 폰 폭(350 px)에서 글자 크기, 화살표와 상자·글자의 충돌, 번호 배지, 상자에 붙는 메모, 기존 diagram.py 호환을 잰다
import glob
import runpy
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import excal  # noqa: E402

PHONE = 350       # px: width of a lesson column on a 390 px phone
PAD = 24          # px: padding the Excalidraw exporter adds on each side
MIN_PX = 11       # px: smallest allowed text at phone width
SHAPES = ("rectangle", "ellipse", "diamond")


# ---------- measuring helpers (work on any scene dict) ----------

def _pts(e):
    if e["type"] in ("arrow", "line"):
        return [(e["x"] + px, e["y"] + py) for px, py in e["points"]]
    return [(e["x"], e["y"]), (e["x"] + e["width"], e["y"] + e["height"])]


def scene_width(scene):
    xs = [p[0] for e in scene["elements"] for p in _pts(e)]
    return max(xs) - min(xs) + 2 * PAD


def smallest_text_px(scene):
    """Smallest font size as drawn when the PNG is scaled to PHONE px wide."""
    scale = PHONE / scene_width(scene)
    return min(e["fontSize"] for e in scene["elements"] if e["type"] == "text") * scale


def _role(e):
    return (e.get("customData") or {}).get("role")


def _rect(e, shrink=0.0):
    return (e["x"] + shrink, e["y"] + shrink, e["x"] + e["width"] - shrink, e["y"] + e["height"] - shrink)


def seg_hits_rect(p, q, r):
    """Axis-aligned segment pq against rectangle r = (x0, y0, x1, y1), open interior."""
    x0, y0, x1, y1 = r
    sx0, sx1 = sorted((p[0], q[0]))
    sy0, sy1 = sorted((p[1], q[1]))
    return sx1 > x0 and sx0 < x1 and sy1 > y0 and sy0 < y1 and (sx1 - sx0 > 0 or sy1 - sy0 > 0) and \
        (sx0 < x1 and sx1 > x0 if sx1 > sx0 else x0 < sx0 < x1) and (sy0 < y1 and sy1 > y0 if sy1 > sy0 else y0 < sy0 < y1)


def inside(b, p, margin=0.0):
    """True when p is inside the real outline of box element b, shrunk by margin px."""
    cx, cy, a, c = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2, b["width"] / 2 - margin, b["height"] / 2 - margin
    if a <= 0 or c <= 0:
        return False
    dx, dy = abs(p[0] - cx), abs(p[1] - cy)
    if b["type"] == "rectangle":
        return dx < a and dy < c
    return (dx / a) ** 2 + (dy / c) ** 2 < 1 if b["type"] == "ellipse" else dx / a + dy / c < 1


def boxes(scene):
    return [e for e in scene["elements"] if e["type"] in SHAPES and _role(e) not in ("label_bg", "badge")]


def arrows(scene):
    return [e for e in scene["elements"] if e["type"] == "arrow"]


def free_texts(scene):
    return [e for e in scene["elements"] if e["type"] == "text" and not e.get("containerId") and _role(e) != "badge_text"]


def collisions(scene):
    """Every arrow segment that enters a box interior or a text that is not the arrow's own label."""
    bad = []
    bx = boxes(scene)
    tx = free_texts(scene)
    bgs = [e for e in scene["elements"] if _role(e) == "label_bg"]
    for a in arrows(scene):
        pts = _pts(a)
        for p, q in zip(pts, pts[1:]):
            for b in bx:
                if b["type"] == "rectangle":
                    hit = seg_hits_rect(p, q, _rect(b, 3))
                else:  # ellipse and diamond: walk along the segment and ask the real outline
                    n = max(2, int(abs(q[0] - p[0]) + abs(q[1] - p[1])) // 2)
                    hit = any(inside(b, (p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n), 3) for i in range(n + 1))
                if hit:
                    bad.append(("box", a["id"], b["id"]))
            for t in tx + bgs:
                if (t.get("customData") or {}).get("label_of") == a["id"]:
                    continue
                if seg_hits_rect(p, q, _rect(t, 2)):
                    bad.append(("text", a["id"], t["id"]))
    return bad


def overlap_len(p, q, r, s):
    """Length shared by two collinear axis-aligned segments pq and rs."""
    if p[0] == q[0] == r[0] == s[0]:
        a, b = sorted((p[1], q[1]))
        c, d = sorted((r[1], s[1]))
    elif p[1] == q[1] == r[1] == s[1]:
        a, b = sorted((p[0], q[0]))
        c, d = sorted((r[0], s[0]))
    else:
        return 0
    return max(0, min(b, d) - max(a, c))


def shared_lane_px(scene):
    worst = 0
    ar = arrows(scene)
    for i, a in enumerate(ar):
        pa = _pts(a)
        for b in ar[i + 1:]:
            pb = _pts(b)
            for p, q in zip(pa, pa[1:]):
                for r, s in zip(pb, pb[1:]):
                    worst = max(worst, overlap_len(p, q, r, s))
    return worst


# ---------- running the lessons' own diagram scripts without touching their assets ----------

@pytest.fixture(scope="module")
def corpus():
    """Run every lesson's code/diagram*.py with save() captured, so no asset file is written."""
    out = []
    orig = excal.Diagram.save

    def capture(self, path):
        out.append((str(path), self.scene()))

    excal.Diagram.save = capture
    try:
        for f in sorted(glob.glob(str(ROOT / "phases" / "*" / "*" / "code" / "diagram*.py"))):
            runpy.run_path(f, run_name="__main__")
    finally:
        excal.Diagram.save = orig
    return out


def _chain(n=4, **kw):
    d = excal.Diagram(**kw)
    d.title("Chain")
    ids = [d.box(f"Step {i}\nwords", i, 0, "blue") for i in range(n)]
    for a, b in zip(ids, ids[1:]):
        d.arrow(a, b, label="go")
    return d, ids


# ---------- the bar ----------

def test_corpus_runs_unchanged(corpus):
    assert len(corpus) == 162


def test_text_stays_readable_at_phone_width(corpus):
    small = [(Path(p).name, round(smallest_text_px(s), 1)) for p, s in corpus if smallest_text_px(s) < MIN_PX]
    assert not small, f"{len(small)} of {len(corpus)} diagrams have text under {MIN_PX} px at {PHONE} px wide: {small[:6]}"


def test_no_arrow_crosses_a_box_or_text(corpus):
    bad = {Path(p).name: collisions(s) for p, s in corpus}
    bad = {k: v[:3] for k, v in bad.items() if v}
    assert not bad, f"{len(bad)} diagrams have arrows through boxes or text: {list(bad.items())[:4]}"


def test_different_arrows_do_not_share_a_lane(corpus):
    bad = [(Path(p).name, round(shared_lane_px(s))) for p, s in corpus if shared_lane_px(s) > 8]
    assert not bad, f"arrows run on top of each other in {len(bad)} diagrams: {bad[:6]}"


def test_at_most_three_columns(corpus):
    def columns(scene):
        xs = sorted(round(b["x"] + b["width"] / 2) for b in boxes(scene))
        groups = []
        for x in xs:
            if not groups or x - groups[-1] > 40:
                groups.append(x)
        return len(groups)

    wide = [(Path(p).name, columns(s)) for p, s in corpus if columns(s) > 3]
    assert not wide, f"{len(wide)} diagrams have more than 3 columns: {wide[:6]}"


def test_labels_have_a_background_and_sit_clear(corpus):
    problems = []
    for p, s in corpus:
        els = s["elements"]
        for t in (e for e in els if _role(e) == "label"):
            bg = [e for e in els if _role(e) == "label_bg" and e["customData"]["label_of"] == t["customData"]["label_of"]]
            if not bg:
                problems.append((Path(p).name, "no background"))
                continue
            r = _rect(bg[0])
            for b in boxes(s):
                if seg_hits_rect((r[0], r[1]), (r[2], r[3]), _rect(b, 1)) and (r[2] - r[0]) * (r[3] - r[1]) > 0:
                    if r[0] < b["x"] + b["width"] and r[2] > b["x"] and r[1] < b["y"] + b["height"] and r[3] > b["y"]:
                        problems.append((Path(p).name, "label over a box"))
    assert not problems, problems[:6]


def test_old_style_labels_exist_as_roles(corpus):
    """Every arrow label of the corpus is drawn as a label with a background."""
    n_labels = sum(1 for _, s in corpus for e in s["elements"] if _role(e) == "label")
    assert n_labels >= 60


def test_text_fits_in_its_box(corpus):
    over = []
    for p, s in corpus:
        by_id = {e["id"]: e for e in s["elements"]}
        for t in (e for e in s["elements"] if e["type"] == "text" and e.get("containerId")):
            c = by_id[t["containerId"]]
            if excal.text_width(t["text"], t["fontSize"]) > c["width"] - 8:
                over.append((Path(p).name, t["text"][:20]))
    assert not over, over[:6]


# ---------- new options ----------

def test_numbered_steps_follow_reading_order():
    d, ids = _chain(3, numbered=True)
    s = d.scene()
    badges = [e for e in s["elements"] if _role(e) == "badge_text"]
    assert sorted(e["text"] for e in badges) == ["1", "2", "3"]
    pos = {e["text"]: (e["y"], e["x"]) for e in badges}
    assert pos["1"] < pos["2"] < pos["3"] or pos["1"][0] <= pos["2"][0] <= pos["3"][0]
    assert all(e["fontSize"] * PHONE / scene_width(s) >= MIN_PX for e in badges)


def test_step_numbers_can_be_set_by_hand():
    d = excal.Diagram(numbered=True)
    a = d.box("A", 0, 0, "blue", step=2)
    b = d.box("B", 1, 0, "green", step=1)
    d.arrow(b, a)
    texts = {e["text"] for e in d.scene()["elements"] if _role(e) == "badge_text"}
    assert texts == {"1", "2"}


def test_unnumbered_by_default():
    d, _ = _chain(3)
    assert not [e for e in d.scene()["elements"] if _role(e) == "badge_text"]


def test_note_attached_to_a_box_sits_beside_it():
    d = excal.Diagram()
    a = d.box("Sensor\nvalue", 0, 0, "yellow")
    b = d.box("Filter", 1, 0, "purple")
    d.arrow(a, b)
    d.note("check units first", near=a, side="b")
    s = d.scene()
    note = [e for e in free_texts(s) if e["text"].startswith("check")][0]
    box = [e for e in boxes(s) if e["id"] == a][0] if a in {e["id"] for e in boxes(s)} else boxes(s)[0]
    below = note["y"] >= box["y"] + box["height"]
    assert below and note["y"] - (box["y"] + box["height"]) <= 90
    assert abs((note["x"] + note["width"] / 2) - (box["x"] + box["width"] / 2)) <= box["width"]
    assert not collisions(s)
    assert smallest_text_px(s) >= MIN_PX


def test_feedback_loop_is_orthogonal_and_clear():
    d, ids = _chain(3)
    d.arrow(ids[-1], ids[0], label="measured", dashed=True)
    s = d.scene()
    loop = arrows(s)[-1]
    pts = _pts(loop)
    assert all(abs(p[0] - q[0]) < 0.5 or abs(p[1] - q[1]) < 0.5 for p, q in zip(pts, pts[1:]))
    assert loop.get("roundness") is None
    assert not collisions(s)
    assert shared_lane_px(s) <= 8
    assert smallest_text_px(s) >= MIN_PX


def test_long_chain_wraps_instead_of_running_wide():
    d, _ = _chain(6)
    s = d.scene()
    assert smallest_text_px(s) >= MIN_PX
    assert not collisions(s)


def test_text_width_is_calibrated():
    # Nunito, measured from the font file Excalidraw embeds: 'Hello' advance sum
    assert 2.4 < excal.text_width("Hello", 1) < 2.8


# ---------- arrow ends: touch the outline, centred, symmetric, straight when aligned ----------

def outline_dist(b, p):
    """First-order distance in px from point p to the outline of box element b (rectangle, ellipse or diamond)."""
    x0, y0, x1, y1 = b["x"], b["y"], b["x"] + b["width"], b["y"] + b["height"]
    cx, cy, a, c = (x0 + x1) / 2, (y0 + y1) / 2, b["width"] / 2, b["height"] / 2
    dx, dy = p[0] - cx, p[1] - cy
    if b["type"] == "rectangle":
        ox, oy = max(x0 - p[0], 0, p[0] - x1), max(y0 - p[1], 0, p[1] - y1)
        return (ox * ox + oy * oy) ** 0.5 if ox or oy else min(p[0] - x0, x1 - p[0], p[1] - y0, y1 - p[1])
    if b["type"] == "ellipse":
        f = (dx / a) ** 2 + (dy / c) ** 2
        g = ((2 * dx / a ** 2) ** 2 + (2 * dy / c ** 2) ** 2) ** 0.5 or 1
        return abs(f - 1) / g
    f = abs(dx) / a + abs(dy) / c
    return abs(f - 1) / ((1 / a) ** 2 + (1 / c) ** 2) ** 0.5


def ends(scene):
    """Yield (arrow, which, box, point, side) for both ends of every arrow; side is the box side the arrow uses."""
    by = {e["id"]: e for e in scene["elements"]}
    for a in arrows(scene):
        pts = _pts(a)
        for which, (key, p, q) in (("start", ("startBinding", pts[0], pts[1])), ("end", ("endBinding", pts[-1], pts[-2]))):
            dx, dy = q[0] - p[0], q[1] - p[1]  # direction pointing back along the arrow, i.e. out of the box
            side = ("r" if dx > 0 else "l") if abs(dx) > abs(dy) else ("b" if dy > 0 else "t")
            yield a, which, by[a[key]["elementId"]], p, side


def side_offset(b, p, side):
    return p[0] - (b["x"] + b["width"] / 2) if side in "tb" else p[1] - (b["y"] + b["height"] / 2)


def test_arrow_ends_sit_on_the_outline(corpus):
    far = []
    for path, s in corpus:
        for a, which, b, p, side in ends(s):
            d = outline_dist(b, p)
            if d > 1.0:
                far.append((Path(path).name, a["id"], which, round(d, 1)))
    assert not far, f"{len(far)} arrow ends are more than 1 px off their shape: {far[:5]}"


def test_arrow_ends_leave_and_enter_at_right_angles(corpus):
    bad = []
    for path, s in corpus:
        for a, which, b, p, side in ends(s):
            nx, ny = {"r": (1, 0), "l": (-1, 0), "b": (0, 1), "t": (0, -1)}[side]
            pts = _pts(a)
            q = pts[1] if which == "start" else pts[-2]
            seg = (q[0] - p[0], q[1] - p[1])
            if abs(seg[0] * ny - seg[1] * nx) > 0.5 or inside(b, (p[0] + nx * 6, p[1] + ny * 6)):
                bad.append((Path(path).name, a["id"], which))
    assert not bad, bad[:5]


def test_lone_arrow_on_a_side_is_centred_and_several_are_symmetric(corpus):
    off_centre, uneven = [], []
    for path, s in corpus:
        groups = {}
        for a, which, b, p, side in ends(s):
            groups.setdefault((b["id"], side), []).append((side_offset(b, p, side), b))
        for (bid, side), lst in groups.items():
            offs = sorted(o for o, _ in lst)
            if len(offs) == 1:
                if abs(offs[0]) > 1.0:
                    off_centre.append((Path(path).name, bid, side, round(offs[0], 1)))
                continue
            gaps = [q - p for p, q in zip(offs, offs[1:])]
            if any(abs(o + offs[-1 - i]) > 1.0 for i, o in enumerate(offs)) or max(gaps) - min(gaps) > 1.0 or min(gaps) < 20:
                uneven.append((Path(path).name, bid, side, [round(o) for o in offs]))
    assert not off_centre, f"{len(off_centre)} lone arrows are off centre: {off_centre[:5]}"
    assert not uneven, f"{len(uneven)} sides split their arrows unevenly: {uneven[:5]}"


def test_an_arrow_takes_a_free_side_instead_of_sharing_one():
    d = excal.Diagram()   # a PID loop: the feedback arrow used to share the right side of the error box with the arrow to D
    e, p, i, k = d.box("Error", 1, 0), d.box("P", 0, 1), d.box("I", 1, 1), d.box("D", 2, 1)
    s, j = d.box("Sum", 1, 2), d.box("Joint", 1, 3)
    for t in (p, i, k):
        d.arrow(e, t)
        d.arrow(t, s)
    d.arrow(s, j)
    d.arrow(j, e, label="measured")
    used = [(b["id"], side) for _, _, b, _, side in ends(d.scene())]
    assert len(used) == len(set(used)), "two arrow ends share one box side although a side was free"


def test_aligned_boxes_get_one_straight_arrow_through_both_centres(corpus):
    bad = []
    for path, s in corpus:
        bx = {b["id"]: b for b in boxes(s)}
        ar = arrows(s)
        pairs = {}
        for a in ar:
            pairs.setdefault(frozenset((a["startBinding"]["elementId"], a["endBinding"]["elementId"])), []).append(a)
        for key, lst in pairs.items():
            if len(lst) != 1 or len(key) != 2:
                continue
            a = lst[0]
            A, B = bx[a["startBinding"]["elementId"]], bx[a["endBinding"]["elementId"]]
            ca = (A["x"] + A["width"] / 2, A["y"] + A["height"] / 2)
            cb = (B["x"] + B["width"] / 2, B["y"] + B["height"] / 2)
            level = abs(ca[1] - cb[1]) < 1 and (A["x"] + A["width"] < B["x"] or B["x"] + B["width"] < A["x"])
            plumb = abs(ca[0] - cb[0]) < 1 and (A["y"] + A["height"] < B["y"] or B["y"] + B["height"] < A["y"])
            if not (level or plumb):
                continue
            if any(seg_hits_rect(ca, cb, _rect(o, 1)) for o in bx.values() if o["id"] not in (A["id"], B["id"])):
                continue
            pts = _pts(a)
            if len(pts) != 2 or abs(pts[0][0 if plumb else 1] - ca[0 if plumb else 1]) > 1 or abs(pts[1][0 if plumb else 1] - cb[0 if plumb else 1]) > 1:
                bad.append((Path(path).name, a["id"]))
    assert not bad, f"{len(bad)} aligned pairs are not joined by a straight centred arrow: {bad[:6]}"


def test_label_sits_in_the_middle_of_a_straight_run_of_its_arrow(corpus):
    bad = []
    for path, s in corpus:
        ar = {a["id"]: a for a in arrows(s)}
        for bg in (e for e in s["elements"] if _role(e) == "label_bg"):
            pts = _pts(ar[bg["customData"]["label_of"]])
            c = (bg["x"] + bg["width"] / 2, bg["y"] + bg["height"] / 2)
            if not any(abs(c[0] - (p[0] + q[0]) / 2) < 1.5 and abs(c[1] - (p[1] + q[1]) / 2) < 1.5 for p, q in zip(pts, pts[1:])):
                bad.append((Path(path).name, bg["customData"]["label_of"]))
    assert not bad, f"{len(bad)} labels are not centred on a straight run: {bad[:6]}"


# ---------- animated arrows: dashes flowing along each arrow over the static PNG ----------

import io  # noqa: E402
import math  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402


def fake_png(scene):
    """Stand-in for the rendered PNG: white page, black box outlines and arrows, laid out the way the exporter does (24 px padding)."""
    xs = [p[0] for e in scene["elements"] for p in _pts(e)]
    ys = [p[1] for e in scene["elements"] for p in _pts(e)]
    ox, oy = PAD - min(xs), PAD - min(ys)
    img = Image.new("RGB", (round(max(xs) - min(xs) + 2 * PAD), round(max(ys) - min(ys) + 2 * PAD)), "white")
    d = ImageDraw.Draw(img)
    for e in scene["elements"]:
        if e["type"] in SHAPES and _role(e) is None:
            d.rectangle([e["x"] + ox, e["y"] + oy, e["x"] + e["width"] + ox, e["y"] + e["height"] + oy], outline="black", width=2, fill="#a5d8ff")
    for a in arrows(scene):
        pts = [(x + ox, y + oy) for x, y in _pts(a)]
        if a["strokeStyle"] == "dashed":
            for p, q in zip(pts, pts[1:]):
                n = max(1, int(math.dist(p, q) // 12))
                for i in range(0, n, 2):
                    d.line([(p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n), (p[0] + (q[0] - p[0]) * (i + 1) / n, p[1] + (q[1] - p[1]) * (i + 1) / n)], fill="black", width=2)
        else:
            d.line(pts, fill="black", width=2)
    return img, (ox, oy)


def _row(direction="right", dashed=False, length=300):
    """Two boxes with one long arrow between them, built by hand so the arrow is long enough for the measuring window."""
    dx, dy = {"right": (1, 0), "left": (-1, 0), "down": (0, 1), "up": (0, -1)}[direction]
    x0, y0 = 150 + (length if dx < 0 else 0), 80 + (length if dy < 0 else 0)
    def box(i, x, y):
        return dict(type="rectangle", id=f"b{i}", x=x - 40, y=y - 30, width=80, height=60, strokeColor="#1e1e1e", customData=None)
    arrow = dict(type="arrow", id="a1", x=x0, y=y0, width=abs(dx) * length, height=abs(dy) * length, points=[[0, 0], [dx * length, dy * length]],
                 strokeStyle="dashed" if dashed else "solid", strokeColor="#1e1e1e", startBinding={"elementId": "b0"}, endBinding={"elementId": "b1"})
    return {"elements": [box(0, x0 - dx * 40, y0 - dy * 40), box(1, x0 + dx * (length + 40), y0 + dy * (length + 40)), arrow]}


def _dash_pixels(frame, dashed):
    """Pixels that carry a flowing dash: blue ones on a solid arrow, dark ones on a dashed arrow (its static line is wiped)."""
    px = frame.load()
    return [(x, y) for y in range(frame.height) for x in range(frame.width)
            if (sum(px[x, y]) < 250 if dashed else px[x, y][2] > px[x, y][0] + 60)]


def test_animation_has_a_clean_loop_of_12_to_20_frames():
    s = _row()
    base, _ = fake_png(s)
    frames = excal.animate(s, base)
    assert 12 <= len(frames) <= 20
    buf = io.BytesIO()
    excal.save_webp(frames, buf)
    data = buf.getvalue()
    w = Image.open(io.BytesIO(data))
    assert w.n_frames == len(frames) and w.info["loop"] == 0
    ms = [int.from_bytes(data[i + 20:i + 23], "little") for i in range(len(data) - 23) if data[i:i + 4] == b"ANMF"]   # frame duration field of each ANMF chunk
    assert len(ms) == len(frames) and all(71 <= m <= 100 for m in ms)          # 10 to 14 frames a second


def test_frames_are_the_png_size_and_arrow_free_pixels_never_change():
    s = excal.Diagram()
    a, b, c = s.box("Start", 0, 0, "blue"), s.box("Middle", 1, 0, "yellow"), s.box("End", 2, 0, "green")
    s.arrow(a, b, label="go")
    s.arrow(b, c, dashed=True)
    s.arrow(c, a)
    s.title("T")
    sc = s.scene()
    base, _ = fake_png(sc)
    frames = excal.animate(sc, base)
    ox, oy = excal.png_offset(sc, base)
    zone = Image.new("L", base.size, 0)
    zd = ImageDraw.Draw(zone)
    for a_ in arrows(sc):
        zd.line([(x + ox, y + oy) for x, y in _pts(a_)], fill=255, width=17, joint="curve")
    zone = zone.load()
    bp = base.load()
    for f in frames:
        assert f.size == base.size
        fp = f.load()
        stray = [(x, y) for y in range(f.height) for x in range(f.width) if zone[x, y] == 0 and fp[x, y] != bp[x, y]]
        assert not stray, f"{len(stray)} pixels away from every arrow changed, first {stray[:3]}"


def test_labels_and_arrowheads_stay_unpainted():
    d = excal.Diagram()
    a, b = d.box("A", 0, 0, "blue"), d.box("B", 1, 0, "green")
    d.arrow(a, b, label="a long label here")
    sc = d.scene()
    base, _ = fake_png(sc)
    ox, oy = excal.png_offset(sc, base)
    bg = [e for e in sc["elements"] if _role(e) == "label_bg"][0]
    ar = arrows(sc)[0]
    end = _pts(ar)[-1]
    for f in excal.animate(sc, base):
        crop = (round(bg["x"] + ox), round(bg["y"] + oy), round(bg["x"] + bg["width"] + ox), round(bg["y"] + bg["height"] + oy))
        assert list(f.crop(crop).getdata()) == list(base.crop(crop).getdata())
        head = (round(end[0] + ox - 20), round(end[1] + oy - 12), round(end[0] + ox + 1), round(end[1] + oy + 12))
        assert list(f.crop(head).getdata()) == list(base.crop(head).getdata())


@pytest.mark.parametrize("direction,dashed", [("right", False), ("right", True), ("left", False), ("down", False), ("down", True), ("up", False)])
def test_dashes_advance_along_the_arrow_and_the_loop_closes(direction, dashed):
    s = _row(direction, dashed)
    base, (ox, oy) = fake_png(s)
    frames = excal.animate(s, base)
    ar = arrows(s)[0]
    p, q = _pts(ar)[0], _pts(ar)[-1]
    ux, uy = (q[0] - p[0]), (q[1] - p[1])
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    period = excal.DASH_PERIOD
    lo, hi = 14, 14 + 2 * period                    # a window of exactly two periods, clear of both ends
    phases = []
    for f in frames:
        sx = sy = w = 0.0
        for x, y in _dash_pixels(f, dashed):
            t = (x - ox - p[0]) * ux + (y - oy - p[1]) * uy
            if lo <= t < hi and abs((x - ox - p[0]) * uy - (y - oy - p[1]) * ux) < 8:
                a_ = 2 * math.pi * t / period
                sx += math.sin(a_)
                sy += math.cos(a_)
                w += 1
        assert w > 20, "no dashes found in the window"
        phases.append(math.atan2(sx, sy) / (2 * math.pi) * period)   # where the dashes sit within one period, px
    steps = [((b_ - a_ + period / 2) % period) - period / 2 for a_, b_ in zip(phases, phases[1:] + phases[:1])]   # last to first closes the loop
    assert all(st > 0 for st in steps), f"dashes do not advance toward the arrow head: {steps}"
    assert max(steps) - min(steps) < 1.5, f"uneven step, the seam shows: {steps}"
    assert abs(sum(steps) - period) < 1.5, f"one loop should move one period: {sum(steps)}"


def test_speed_is_about_one_dash_period_a_second():
    s = _row()
    base, _ = fake_png(s)
    frames = excal.animate(s, base)
    cycles_per_second = (1000 / excal.ANIM_MS) / len(frames)
    assert 1.0 <= cycles_per_second <= 1.5


def test_no_arrows_means_no_animation():
    d = excal.Diagram()
    d.box("Only", 0, 0, "blue")
    sc = d.scene()
    base, _ = fake_png(sc)
    assert excal.animate(sc, base) == []
