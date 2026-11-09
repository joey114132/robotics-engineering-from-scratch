# Excalidraw 다이어그램을 코드로 만드는 작은 helper: 상자, 화살표, 메모를 격자 위에 놓고 .excalidraw 로 저장한다
import json
import pathlib

COLORS = {  # soft fills, same hues across every lesson
    "blue": "#a5d8ff", "green": "#b2f2bb", "yellow": "#ffec99",
    "red": "#ffc9c9", "purple": "#d0bfff", "gray": "#e9ecef", "white": "#ffffff",
}
INK = "#1e1e1e"


class Diagram:
    def __init__(self, cell=(300, 170), margin=40):
        self.cw, self.ch = cell
        self.margin = margin
        self.els: list[dict] = []
        self.boxes: dict[str, dict] = {}
        self._n = 0

    def _base(self, typ, x, y, w, h, **kw):
        self._n += 1
        e = dict(type=typ, id=f"e{self._n}", x=x, y=y, width=w, height=h, angle=0, strokeColor=INK,
                 backgroundColor="transparent", fillStyle="solid", strokeWidth=2, strokeStyle="solid",
                 roughness=1, opacity=100, groupIds=[], frameId=None, roundness=None, seed=1000 + self._n * 7,
                 version=1, versionNonce=self._n, isDeleted=False, boundElements=None, updated=1, link=None, locked=False)
        e.update(kw)
        return e

    def _text(self, text, x, y, w, size, container=None, color=INK, align="center"):
        lines = text.split("\n")
        h = round(len(lines) * size * 1.25)
        return self._base("text", x, y, w, h, text=text, originalText=text, fontSize=size, fontFamily=1,
                          textAlign=align, verticalAlign="middle" if container else "top", containerId=container,
                          strokeColor=color, strokeWidth=1, lineHeight=1.25, autoResize=not container)

    def box(self, text, col, row, color="blue", w=220, h=88, shape="rectangle", size=20, dx=0, dy=0):
        x, y = self.margin + col * self.cw + dx, self.margin + 60 + row * self.ch + dy
        r = self._base(shape, x, y, w, h, backgroundColor=COLORS.get(color, color), roundness={"type": 3} if shape == "rectangle" else None)
        n = len(text.split("\n"))
        th = round(n * size * 1.25)
        t = self._text(text, x + 10, y + (h - th) / 2, w - 20, size, container=r["id"])
        r["boundElements"] = [{"id": t["id"], "type": "text"}]
        self.els += [r, t]
        self.boxes[r["id"]] = r
        return r["id"]

    def note(self, text, x, y, size=18, color="#495057", w=None):
        w = w or round(max(len(s) for s in text.split("\n")) * size * 0.55)
        self.els.append(self._text(text, x, y, w, size, color=color, align="left"))

    def title(self, text, size=30):
        w = round(len(text) * size * 0.55)
        self.els.append(self._text(text, self.margin, self.margin - 10, w, size, align="left"))

    def _side(self, b, side, gap=6):
        x, y, w, h = b["x"], b["y"], b["width"], b["height"]
        return {"r": (x + w + gap, y + h / 2), "l": (x - gap, y + h / 2), "b": (x + w / 2, y + h + gap), "t": (x + w / 2, y - gap)}[side]

    def arrow(self, a, b, label=None, dashed=False, color=INK, route=None, label_dx=0, label_dy=0):
        A, B = self.boxes[a], self.boxes[b]
        dx = (B["x"] + B["width"] / 2) - (A["x"] + A["width"] / 2)
        dy = (B["y"] + B["height"] / 2) - (A["y"] + A["height"] / 2)
        if route == "below":
            p0, p3 = self._side(A, "b"), self._side(B, "b")
            drop = max(A["y"], B["y"]) + A["height"] + 70
            pts = [p0, (p0[0], drop), (p3[0], drop), p3]
        else:
            sa, sb = ("r", "l") if abs(dx) >= abs(dy) and dx > 0 else ("l", "r") if abs(dx) >= abs(dy) else ("b", "t") if dy > 0 else ("t", "b")
            pts = [self._side(A, sa), self._side(B, sb)]
        x0, y0 = pts[0]
        rel = [[round(px - x0), round(py - y0)] for px, py in pts]
        ar = self._base("arrow", x0, y0, max(abs(p[0]) for p in rel), max(abs(p[1]) for p in rel), points=rel, strokeColor=color,
                        strokeStyle="dashed" if dashed else "solid", roundness={"type": 2}, startArrowhead=None, endArrowhead="arrow",
                        startBinding={"elementId": a, "focus": 0, "gap": 6}, endBinding={"elementId": b, "focus": 0, "gap": 6},
                        lastCommittedPoint=None, elbowed=False)
        for ref in (A, B):
            ref["boundElements"] = (ref["boundElements"] or []) + [{"id": ar["id"], "type": "arrow"}]
        self.els.append(ar)
        if label:
            mx = (pts[0][0] + pts[-1][0]) / 2 + label_dx
            my = (pts[0][1] + pts[-1][1]) / 2 + label_dy
            if route == "below":
                my = pts[1][1] + 6 + label_dy
            else:
                my -= 30 if abs(dx) >= abs(dy) else 0
                mx += 0 if abs(dx) >= abs(dy) else 10
            w = round(max(len(s) for s in label.split("\n")) * 16 * 0.55)
            self.els.append(self._text(label, mx - w / 2, my, w, 16, color="#495057"))

    def save(self, path):
        scene = {"type": "excalidraw", "version": 2, "source": "robotics-engineering-from-scratch", "elements": self.els,
                 "appState": {"viewBackgroundColor": "#ffffff"}, "files": {}}
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(path).write_text(json.dumps(scene, indent=1))
