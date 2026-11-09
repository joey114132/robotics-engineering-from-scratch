# 그림(PNG)을 터미널 이미지로: PIL 로 줄이고 ▀ 한 칸에 위/아래 픽셀 두 개(전경색/배경색)를 담는다
from pathlib import Path

from rich.color import Color
from rich.style import Style
from rich.text import Text

try:
    from PIL import Image
except ImportError:           # 선택 의존성: 없으면 캡션 줄로 대체
    Image = None


MAX_ROWS, MAX_COLS = 16, 70          # 기본(compact) 그림의 상한


def choose_mode(plain, color_system, pref="quad"):
    """pref: quad(2x2 사분블록, 기본, 작게) | half(▀ 반블록, 작게) | full(quad, 터미널 폭 가득) | off. 색이 없거나 PIL 이 없으면 캡션 줄."""
    if plain or pref == "off" or color_system not in ("truecolor", "256") or Image is None:
        return "plain"
    return {"half": "blocks", "full": "full"}.get(pref, "quad")


def fit_cols(img_w, img_h, cols, max_rows, mode):
    """줄 수가 max_rows 를 넘지 않도록 열 수를 줄인다. quad 는 한 칸이 2x2 픽셀, 반블록은 1x2 픽셀이다."""
    per_col = img_h / img_w * (1 if mode != "blocks" else 0.5)      # 열 하나당 늘어나는 줄 수
    return max(2, min(cols, int(max_rows / per_col))) if max_rows else cols


def _to_rgb(img):
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img)
    return img.convert("RGB")


def halfblock_rows(img, cols):
    img = _to_rgb(img)
    cols = max(1, min(cols, img.width))
    h = round(img.height * cols / img.width)
    h += h % 2                                   # 픽셀 행은 짝수여야 두 개씩 묶인다
    img = img.resize((cols, max(2, h)), Image.Resampling.LANCZOS)
    px = img.load()
    return [[(px[x, y], px[x, y + 1]) for x in range(cols)] for y in range(0, img.height, 2)]


def image_text(img, cols):
    lines = []
    for row in halfblock_rows(img, cols):
        t, run, prev = Text(no_wrap=True, overflow="crop"), 0, None
        for cell in row + [None]:
            if cell == prev and cell is not None:
                run += 1
                continue
            if prev is not None:
                t.append("▀" * run, Style(color=Color.from_rgb(*prev[0]), bgcolor=Color.from_rgb(*prev[1])))
            prev, run = cell, 1
        lines.append(t)
    return lines


# 사분블록: 한 칸에 2x2 픽셀. 비트 tl=1 tr=2 bl=4 br=8 이 켜진 쪽이 전경색
QUAD = " ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█"


def quad_cells(img, cols):
    img = _to_rgb(img)
    cols = max(1, min(cols, img.width // 2 or 1))
    w = cols * 2
    h = round(img.height * w / img.width)
    h += h % 2
    img = img.resize((w, max(2, h)), Image.Resampling.LANCZOS)
    px = img.load()
    rows = []
    for y in range(0, img.height, 2):
        row = []
        for x in range(0, w, 2):
            p = [px[x, y], px[x + 1, y], px[x, y + 1], px[x + 1, y + 1]]
            best = None
            for mask in range(8):               # 0 은 단색, 1..7 은 두 덩어리로 가르는 모든 경우(보색 대칭)
                fg = [p[i] for i in range(4) if mask >> i & 1]
                bg = [p[i] for i in range(4) if not mask >> i & 1]
                mean = lambda g: tuple(sum(c[k] for c in g) / len(g) for k in range(3)) if g else (0, 0, 0)
                mf, mb = mean(fg), mean(bg)
                err = sum(sum((c[k] - m[k]) ** 2 for k in range(3)) for g, m in ((fg, mf), (bg, mb)) for c in g)
                if best is None or err < best[0] - 1e-9:
                    best = (err, mask, mf, mb)
            _, mask, mf, mb = best
            row.append((QUAD[mask], tuple(round(c) for c in mf), tuple(round(c) for c in mb)))
        rows.append(row)
    return rows


def quad_text(img, cols):
    lines = []
    for row in quad_cells(img, cols):
        t = Text(no_wrap=True, overflow="crop")
        for ch, fg, bg in row:
            t.append(ch, Style(color=Color.from_rgb(*fg), bgcolor=Color.from_rgb(*bg)))
        lines.append(t)
    return lines


def render_figure(path, caption, cols, mode="blocks", rel_to=None, max_rows=None):
    shown = path
    if rel_to is not None:
        try:
            shown = Path(path).relative_to(rel_to)
        except ValueError:
            pass
    fallback = [Text(f"figure: {caption} ({shown})")]
    if mode not in ("blocks", "quad", "full") or Image is None:
        return fallback
    try:
        with Image.open(path) as img:
            img.load()
            cols = fit_cols(img.width, img.height, cols, max_rows, mode)
            lines = image_text(img, cols) if mode == "blocks" else quad_text(img, cols)
    except (OSError, ValueError):
        return fallback
    lines.append(Text(caption, style="italic dim"))
    return lines
