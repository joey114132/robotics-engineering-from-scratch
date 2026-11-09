# 화면 기본 요소: 팔레트, 글리프, 한국어 폭 정렬, 막대, 말풍선, Bolt 얼굴, 배너, Console 생성
import colorsys
import os
import shutil
import sys

from rich.cells import cell_len, set_cell_size
from rich.console import Console
from rich.style import Style
from rich.text import Text
from rich.theme import Theme

MIN_WIDTH, READ_WIDTH = 60, 100

# 동아시아 폭이 'N'(중립)인 글리프만 쓴다. 'A'(모호) 글리프는 CJK 터미널에서 2칸으로 그려져 정렬이 깨진다.
GLYPHS = {"done": "✓", "cur": "▸", "todo": "▫", "part": "▪", "star": "✦", "star_off": "✧", "good": "✓", "bad": "✗",
          "bullet": "▪", "arrow": "➜", "up": "▴", "down": "▾", "mouth_up": "◡", "mouth_down": "◠", "eye": "◉", "eye_soft": "◦"}
ASCII_GLYPHS = {"done": "[x]", "cur": "[>]", "todo": "[ ]", "part": "[~]", "star": "*", "star_off": "-", "good": "+", "bad": "x",
                "bullet": "-", "arrow": "->", "up": "^", "down": "v", "mouth_up": "u", "mouth_down": "n", "eye": "o", "eye_soft": "."}


def want_plain(flag, isatty):
    return bool(flag) or not isatty or bool(os.environ.get("NO_COLOR"))


def detect_dark():
    """COLORFGBG 가 'fg;bg' 로 알려 주면 그걸로 배경 밝기를 알아낸다. 모르면 None."""
    v = os.environ.get("COLORFGBG", "")
    try:
        bg = int(v.split(";")[-1])
    except ValueError:
        return None
    return not (bg in (7, 15))


def palette(dark):
    # 어두운 배경은 조금 밝게, 밝은 배경은 조금 어둡게, 모르면 양쪽에서 읽히는 중간 톤
    if dark is True:
        return {"accent": "#5b92f0", "ok": "#3ec27a", "warn": "#f0b240", "bad": "#f06a6a", "teal": "#2fc4ae"}
    if dark is False:
        return {"accent": "#2f6fe4", "ok": "#1a7f45", "warn": "#b87400", "bad": "#c93636", "teal": "#128a78"}
    return {"accent": "#3d7be8", "ok": "#24a35c", "warn": "#d28b0a", "bad": "#dc4d4d", "teal": "#1fa892"}


def hsl_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def phase_color(i, dark=None):
    return hsl_hex((212 + i * 21) % 360, 0.5 if dark is False else 0.55, 0.42 if dark is False else 0.6)


def lerp_rgb(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# ---- 폭을 아는 문자열 도구 -----------------------------------------------------------
def pad(s, width, align="left"):
    gap = width - cell_len(s)
    if gap <= 0:
        return set_cell_size(s, width)
    return s + " " * gap if align == "left" else " " * gap + s if align == "right" else " " * (gap // 2) + s + " " * (gap - gap // 2)


def trunc(s, width):
    if cell_len(s) <= width:
        return s
    return set_cell_size(s, max(0, width - 1)).rstrip() + "…"


def wrap_cells(text, width):
    """공백 기준으로 줄바꿈하되 폭은 cell 로 센다. 한 낱말이 너무 길면 글자 단위로 자른다."""
    lines = []
    for para in str(text).split("\n"):
        cur = ""
        for word in para.split():
            while cell_len(word) > width:
                room = width - (cell_len(cur) + 1 if cur else 0)
                if room < 2:
                    lines.append(cur)
                    cur, room = "", width
                head = set_cell_size(word, room).rstrip()
                head = head or word[0]
                lines.append((cur + " " + head).strip())
                cur, word = "", word[len(head):]
            if not cur:
                cur = word
            elif cell_len(cur) + 1 + cell_len(word) <= width:
                cur += " " + word
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines or [""]


U_pad = pad


def bar_text(frac, width, plain=False, style="accent", empty_style="muted"):
    frac = min(1.0, max(0.0, frac))
    n = round(frac * width)
    if plain:
        return Text("#" * n + "." * (width - n))
    t = Text("━" * n, style=style)                   # 얇은 선 막대: 배경색 블록 없이 한 줄에 한 줄
    t.append("╌" * (width - n), style=empty_style)
    return t


def bubble_lines(text, width, ascii=False, tail=True):
    tl, tr, bl, br, h, v = ("+", "+", "+", "+", "-", "|") if ascii else ("╭", "╮", "╰", "╯", "─", "│")
    inner = max(8, width - 4)
    body = wrap_cells(text, inner)
    lines = [tl + h * (inner + 2) + tr]
    for i, ln in enumerate(body):
        left = ("<" if ascii else "◂") if tail and i == 0 else v
        lines.append(f"{left} {pad(ln, inner)} {v}")
    lines.append(bl + h * (inner + 2) + br)
    return lines


def face_lines(mood="idle", ascii=False):
    g = ASCII_GLYPHS if ascii else GLYPHS
    eyes, mouth = {"idle": (g["eye"], "-" if ascii else "─"), "cheer": ("^", g["mouth_up"]), "oops": (g["eye_soft"], g["mouth_down"])}[mood]
    tl, tr, bl, br, h, v, ant = ("+", "+", "+", "+", "-", "|", "!") if ascii else ("╭", "╮", "╰", "╯", "─", "│", "╷")
    return ["   " + ant + "   ", tl + h * 5 + tr, f"{v} {eyes} {eyes} {v}", f"{v}  {mouth}  {v}", bl + h * 5 + br]


def mini_face(mood="idle", ascii=False):
    """3줄짜리 작은 Bolt. 퀴즈 반응에 쓴다."""
    g = ASCII_GLYPHS if ascii else GLYPHS
    eyes, mouth = {"idle": (g["eye"], "-" if ascii else "─"), "cheer": ("^", g["mouth_up"]), "oops": (g["eye_soft"], g["mouth_down"])}[mood]
    tl, tr, bl, br, h, v = ("+", "+", "+", "+", "-", "|") if ascii else ("╭", "╮", "╰", "╯", "─", "│")
    return [tl + h * 3 + tr, f"{v}{eyes}{mouth}{eyes}{v}", bl + h * 3 + br]


# ---- Console 와 UI ---------------------------------------------------------------------
class RstripOut:
    """plain 출력용 writer: Console 이 칸을 채우려고 붙인 줄 끝 공백을 지운다. sys.stdout 은 쓸 때마다 찾는다(테스트의 capsys 대응)."""

    def __init__(self):
        self._buf = ""

    def write(self, s):
        self._buf += s
        *done, self._buf = self._buf.split("\n")
        if done:
            sys.stdout.write("\n".join(l.rstrip() for l in done) + "\n")
        return len(s)

    def flush(self):
        if self._buf:
            sys.stdout.write(self._buf.rstrip())
            self._buf = ""
        sys.stdout.flush()

    def isatty(self):
        return False


def term_columns():
    return shutil.get_terminal_size((100, 24)).columns


class UI:
    def __init__(self, console, plain, width, lang, dark, fixed=False):
        self.console, self.plain, self.width, self.lang, self.dark = console, plain, width, lang, dark
        self.fixed = fixed                 # --width 처럼 명시한 폭이면 터미널 크기가 바뀌어도 그대로 둔다
        self.below_min = False             # 실행 중 터미널이 최소 폭(60)보다 좁아진 적이 있는가
        self.g = ASCII_GLYPHS if plain else GLYPHS
        self.pal = palette(dark)

    @property
    def read_width(self):
        return min(self.width, READ_WIDTH)

    def t(self, en, ko):
        return ko if self.lang == "ko" else en

    def print(self, *a, **k):
        self.console.print(*a, **k)

    def refresh_width(self):
        """터미널 크기를 다시 읽어 UI.width 와 Console.width 를 함께 맞춘다(명시한 폭은 건드리지 않는다). 최소 폭은 60 이다."""
        if self.fixed:
            return self.width
        cols = term_columns()
        if cols < MIN_WIDTH:
            self.below_min = True
        self.width = self.console.width = max(MIN_WIDTH, cols)
        return self.width

    def para(self, t, indent=2):
        """들여쓰기를 유지한 채 줄바꿈하는 문단 출력. Text 앞의 공백 두 칸 접두는 떼고 Padding 으로 다시 준다."""
        from rich.padding import Padding
        if isinstance(t, Text) and t.plain.startswith("  ") and indent == 2:
            t = t[2:]
        elif isinstance(t, Text) and indent > 2:
            t = Text(t.plain.lstrip(), style=t.style)
        self.console.print(Padding(t, (0, 0, 0, indent)), width=self.read_width)

    def columns(self, rows, indent=2, gap=2, min_last=24):
        """rows: [[(문자열, 스타일), ...]]. 마지막 열만 줄바꿈하고 이어지는 줄은 그 열 위치에 맞춘다. 칸이 모자라면 마지막 열을 아래로 내린다."""
        ncol = len(rows[0])
        widths = [max(cell_len(r[i][0]) for r in rows) + gap for i in range(ncol - 1)]
        room = self.read_width - indent - sum(widths)
        stacked = room < min_last
        for r in rows:
            head = Text(" " * indent)
            for i, (txt, st) in enumerate(r[:-1]):
                head.append(U_pad(txt, widths[i]) if not stacked else txt + ("  " if i < ncol - 2 else ""), style=st)
            last_txt, last_st = r[-1]
            if stacked:
                self.print(head, no_wrap=True, overflow="crop")
                for ln in wrap_cells(last_txt, self.read_width - indent - 4):
                    self.print(Text(" " * (indent + 4) + ln, style=last_st))
                continue
            lines = wrap_cells(last_txt, room)
            for k, ln in enumerate(lines):
                t = head if k == 0 else Text(" " * (indent + sum(widths)))
                t.append(ln, style=last_st)
                self.print(t, no_wrap=True, overflow="crop")

    def rule(self, title=None, width=None):
        w = width or self.read_width
        ch = "-" if self.plain else "─"
        if title:
            head = f"{ch}{ch} {title} "
            self.console.print(Text(head, style="bold") + Text(ch * max(2, w - cell_len(head)), style="muted"), overflow="crop", no_wrap=True)
        else:
            self.console.print(Text(ch * w, style="muted"), overflow="crop", no_wrap=True)


def make_ui(plain=False, width=None, force_color=False, lang="en", file=None, record=False, dark=None):
    dark = detect_dark() if dark is None else dark
    fixed = bool(width)
    width = max(MIN_WIDTH, width or term_columns())
    pal = palette(dark)
    theme = Theme({"accent": pal["accent"], "ok": pal["ok"], "warn": pal["warn"], "bad": pal["bad"], "teal": pal["teal"],
                   "muted": "dim", "key": "bold " + pal["accent"], "title": "bold",
                   **{f"bold {k}": f"bold {pal[k]}" for k in ("accent", "ok", "warn", "bad", "teal")},   # 'bold accent' 같은 합성 이름은 직접 등록해야 먹는다
                   "markdown.h1": "bold", "markdown.h2": "bold " + pal["accent"], "markdown.h3": "bold", "markdown.h4": "italic",
                   "markdown.code": "bold " + pal["accent"], "markdown.block_quote": "dim italic", "markdown.link": "underline " + pal["accent"],
                   "markdown.link_url": "dim", "markdown.item.bullet": pal["accent"], "markdown.item.number": pal["accent"],
                   "markdown.hr": "dim", "markdown.em": "italic", "markdown.strong": "bold"})
    kw = dict(width=width, theme=theme, highlight=False, emoji=False, record=record, file=file, soft_wrap=False)
    if plain:
        if file is None:
            kw["file"] = RstripOut()
        console = Console(force_terminal=False, color_system=None, no_color=True, **kw)
    elif force_color:
        console = Console(force_terminal=True, color_system="truecolor", **kw)
    else:
        console = Console(**kw)
    return UI(console, plain, width, lang, dark, fixed)


# ---- 배너: 반블록 글자 + 가로 그라데이션 (이미지가 아니라 문자) ------------------------------
_FONT = {"R": ["####.", "#...#", "####.", "#.#..", "#..#.", "#...#"],
         "O": [".###.", "#...#", "#...#", "#...#", "#...#", ".###."],
         "B": ["####.", "#...#", "####.", "#...#", "#...#", "####."]}


def banner_rows(word="ROBO"):
    rows = ["", "", ""]
    for ci, ch in enumerate(word):
        glyph = _FONT[ch]
        for r in range(3):
            top, bot = glyph[2 * r], glyph[2 * r + 1]
            rows[r] += "".join({(1, 1): "█", (1, 0): "▀", (0, 1): "▄", (0, 0): " "}[(a == "#", b == "#")] for a, b in zip(top, bot))
            if ci < len(word) - 1:
                rows[r] += " "
    return rows


def banner_lines(u, subtitle=None, tagline=None, sweep=None, side=1.0):
    """배너 줄들. sweep 이 있으면 그 열(왼쪽부터)까지만 그리고 끝에 밝은 머리를 단다(인트로용). side 는 부제의 밝기 0/0.5/1."""
    sub = subtitle or u.t("robotics engineering from scratch", "처음부터 배우는 로봇공학")
    rows = banner_rows()
    c1, c2 = hex_rgb(u.pal["accent"]), hex_rgb(u.pal["teal"])
    w = cell_len(rows[0])
    narrow = u.width < 80                       # 좁으면 부제를 글자 아래로 내린다
    side_txt = ["", sub, tagline or ""] if not narrow else ["", "", ""]
    head_to = (255, 255, 255) if u.dark is not False else (0, 0, 0)
    out = []
    for r, row in enumerate(rows):
        t = Text("  ")
        for i, ch in enumerate(row):
            if ch == " " or (sweep is not None and i > sweep):
                t.append(" ")
                continue
            rgb = lerp_rgb(c1, c2, i / max(1, w - 1))
            if sweep is not None and i > sweep - 3:
                rgb = lerp_rgb(rgb, head_to, 0.45)
            t.append(ch, style=Style(color="#%02x%02x%02x" % rgb))
        if side > 0 and side_txt[r]:
            t.append("   " + side_txt[r], style="dim" if side < 1 else "bold" if r == 1 else "muted")
        out.append(t)
    if narrow:
        for line, style in ((sub, "bold"), (tagline, "muted")):
            if line is None:
                continue
            out.append(Text("  " + line, style=style if side >= 1 else "dim") if side > 0 else Text(" "))
    return out


def print_banner(u, subtitle=None, tagline=None):
    sub = subtitle or u.t("robotics engineering from scratch", "처음부터 배우는 로봇공학")
    if u.plain:
        u.print("ROBO  " + sub)
        if tagline:
            u.print(tagline)
        u.rule()
        return
    u.print()
    for t in banner_lines(u, subtitle, tagline):
        u.print(t)
    u.print()


def bolt_says(u, text, mood="idle", width=None, name="Bolt"):
    """Bolt 얼굴(상자 문자) 옆에 말풍선. 풍선 꼬리가 얼굴 눈높이에 오도록 한 줄 내려 맞춘다."""
    width = width or u.read_width - 4
    face = face_lines(mood, u.plain)
    fw = cell_len(face[0])
    bub = bubble_lines(text, width - fw - 2, ascii=u.plain)
    rows = max(len(face), len(bub) + 1)
    mood_style = {"idle": "accent", "cheer": "ok", "oops": "warn"}[mood]
    out = []
    for i in range(rows):
        f = face[i] if i < len(face) else " " * fw
        b = bub[i - 1] if 0 < i <= len(bub) else ""
        t = Text("  ")
        t.append(f, style=mood_style)
        t.append("  ")
        for ch in b:
            t.append(ch, style=("accent" if ch == "◂" else "muted") if ch in "╭╮╰╯│─◂" else "")
        out.append(t)
    return out
