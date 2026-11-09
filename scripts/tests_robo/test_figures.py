# 그림을 half-block 터미널 이미지로 바꾸는 코드 테스트
from PIL import Image
from rich.cells import cell_len
from rich.text import Text

from robo import figures


def test_halfblock_dimensions_and_colors():
    img = Image.new("RGB", (4, 4))
    for x in range(4):
        img.putpixel((x, 0), (255, 0, 0))     # top row red
        img.putpixel((x, 1), (0, 0, 255))     # second row blue
        img.putpixel((x, 2), (0, 255, 0))
        img.putpixel((x, 3), (0, 255, 0))
    rows = figures.halfblock_rows(img, cols=4)
    assert len(rows) == 2 and all(len(r) == 4 for r in rows)
    top, bottom = rows[0][0]
    assert top == (255, 0, 0) and bottom == (0, 0, 255)
    assert rows[1][0] == ((0, 255, 0), (0, 255, 0))


def test_downscale_to_cols_and_even_pixel_rows():
    img = Image.new("RGB", (200, 91), (10, 20, 30))
    rows = figures.halfblock_rows(img, cols=50)
    assert all(len(r) == 50 for r in rows)
    assert 10 <= len(rows) <= 14


def test_rgba_composited_on_white():
    img = Image.new("RGBA", (2, 2), (0, 0, 0, 0))
    rows = figures.halfblock_rows(img, cols=2)
    assert rows[0][0] == ((255, 255, 255), (255, 255, 255))


def test_text_lines_use_upper_half_block_with_fg_bg():
    img = Image.new("RGB", (2, 2), (9, 9, 9))
    lines = figures.image_text(img, cols=2)
    assert all(isinstance(l, Text) and l.plain == "▀▀" and cell_len(l.plain) == 2 for l in lines)
    st = lines[0].spans[0].style
    assert st.color.triplet == (9, 9, 9) and st.bgcolor.triplet == (9, 9, 9)


def test_figure_lines_modes(course):
    png = next((course / "phases/00-alpha-tools/01-first-steps/assets").glob("*.png"))
    img = figures.render_figure(png, "Caption here", cols=30, mode="blocks")
    assert len(img) >= 3 and "Caption here" in img[-1].plain
    plain = figures.render_figure(png, "Caption here", cols=30, mode="plain")
    assert len(plain) == 1 and plain[0].plain.startswith("figure: Caption here (") and str(png) in plain[0].plain
    missing = figures.render_figure(png.with_name("nope.png"), "X", cols=30, mode="blocks")
    assert missing[0].plain.startswith("figure: X (")


def test_choose_mode():
    assert figures.choose_mode(plain=True, color_system="truecolor") == "plain"
    assert figures.choose_mode(plain=False, color_system=None) == "plain"
    assert figures.choose_mode(plain=False, color_system="standard") == "plain"
    assert figures.choose_mode(plain=False, color_system="256") == "quad"
    assert figures.choose_mode(plain=False, color_system="truecolor") == "quad"
    assert figures.choose_mode(plain=False, color_system="truecolor", pref="half") == "blocks"
    assert figures.choose_mode(plain=False, color_system="truecolor", pref="full") == "full"
    assert figures.choose_mode(plain=False, color_system="truecolor", pref="off") == "plain"


def test_quadrant_cells_pick_the_matching_glyph():
    img = Image.new("RGB", (2, 2), (255, 255, 255))
    img.putpixel((0, 0), (0, 0, 0))                    # only top-left is dark
    (ch, fg, bg), = figures.quad_cells(img, cols=1)[0]
    assert ch == "▘" and fg == (0, 0, 0) and bg == (255, 255, 255)
    img2 = Image.new("RGB", (2, 2), (9, 9, 9))
    (ch, fg, bg), = figures.quad_cells(img2, cols=1)[0]
    assert ch == " " and bg == (9, 9, 9)


def test_quad_text_width_and_caption(course):
    png = next((course / "phases/00-alpha-tools/01-first-steps/assets").glob("*.png"))
    lines = figures.render_figure(png, "Cap", cols=10, mode="quad")
    assert all(cell_len(l.plain) == 10 for l in lines[:-1]) and lines[-1].plain == "Cap"


def _fig(tmp_path, w, h):
    p = tmp_path / f"f{w}x{h}.png"
    Image.new("RGB", (w, h), (120, 140, 200)).save(p)
    return p


def test_compact_figures_are_capped_at_16_rows_and_70_cols(tmp_path):
    for w, h in ((1600, 800), (1000, 1000), (400, 1600), (3000, 600)):
        for mode in ("quad", "blocks"):
            lines = figures.render_figure(_fig(tmp_path, w, h), "cap", cols=70, mode=mode, max_rows=figures.MAX_ROWS)
            body = lines[:-1]
            assert len(body) <= figures.MAX_ROWS, (w, h, mode, len(body))
            assert max(cell_len(l.plain) for l in body) <= figures.MAX_COLS
            assert lines[-1].plain == "cap"                      # caption stays under the picture


def test_wide_figure_uses_the_full_70_cols_and_full_mode_is_larger(tmp_path):
    p = _fig(tmp_path, 1600, 300)
    compact = figures.render_figure(p, "c", cols=70, mode="quad", max_rows=16)
    assert cell_len(compact[0].plain) == 70
    big = figures.render_figure(p, "c", cols=96, mode="full")
    assert cell_len(big[0].plain) == 96 and len(big) > len(compact)


def test_cli_read_default_figure_is_compact(course, state_home, monkeypatch):
    import io
    from robo import cli, ui
    from rich.cells import cell_len as cl
    monkeypatch.setenv("ROBO_ROOT", str(course))
    from PIL import Image
    noise = Image.frombytes("RGB", (1600, 1000), bytes((i * 37 + i // 7) % 256 for i in range(1600 * 1000 * 3)))
    noise.save(course / "phases/00-alpha-tools/01-first-steps/assets/fig.png")
    buf = io.StringIO()
    u = ui.make_ui(plain=False, width=120, force_color=True, file=buf, lang="en")
    top, _ = cli.build_parser()
    cli.dispatch(top.parse_args(["read", "00-01"]), u)
    rows = [l for l in __import__("re").sub(r"\x1b\[[0-9;]*m", "", buf.getvalue()).splitlines() if l.strip() and set(l.strip()) <= set(" ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█")]
    assert 3 <= len(rows) <= 16 and max(cl(l.strip("\n")) for l in rows) <= 72
