# 화면 요소 테스트: 글리프 폭, 한국어 정렬, plain 에 ANSI 없음
import re
import unicodedata

from rich.cells import cell_len

from robo import ui

ANSI = re.compile(r"\x1b\[")


def test_glyphs_have_width_one_and_are_not_east_asian_ambiguous():
    for name, ch in ui.GLYPHS.items():
        assert cell_len(ch) == 1, name
        assert unicodedata.east_asian_width(ch) in ("N", "Na"), (name, ch)   # CJK terminals draw 'A' as 2 cells
    assert not any(ord(c) > 0x1F000 for c in "".join(ui.GLYPHS.values()))     # no emoji


def test_block_and_box_characters_are_single_width():
    for ch in "─│╭╮╰╯├└┬█▀▄░⠿⣿":
        assert cell_len(ch) == 1


def test_pad_and_trunc_use_cell_widths():
    assert cell_len(ui.pad("한글", 10)) == 10
    assert cell_len(ui.pad("abc", 10)) == 10
    t = ui.trunc("가나다라마바사", 8)
    assert cell_len(t) <= 8 and t.endswith("…")
    assert ui.trunc("short", 8) == "short"


def test_bar_has_exact_width_and_proportion():
    for frac in (0, 0.25, 0.5, 1):
        b = ui.bar_text(frac, 20, plain=True)
        assert cell_len(b.plain) == 20
    assert ui.bar_text(0.5, 20, plain=True).plain.count("#") == 10
    assert cell_len(ui.bar_text(0.37, 17).plain) == 17


def test_bubble_is_rectangular_with_korean():
    for text in ("short", "한국어 문장이 길어지면 줄이 바뀌어야 합니다. 그리고 영어 mixed 도 섞입니다.", ""):
        lines = ui.bubble_lines(text, 40)
        assert len({cell_len(l) for l in lines}) == 1
        assert cell_len(lines[0]) <= 40


def test_faces_are_aligned_and_distinct():
    shapes = {}
    for mood in ("idle", "cheer", "oops"):
        f = ui.face_lines(mood)
        assert len({cell_len(l) for l in f}) == 1
        shapes[mood] = f
    assert shapes["idle"] != shapes["cheer"] != shapes["oops"]


def test_plain_console_has_no_ansi_and_no_color():
    u = ui.make_ui(plain=True, width=80)
    with u.console.capture() as cap:
        u.console.print("[bold red]hello[/] 한글")
        u.rule("Title")
    out = cap.get()
    assert "hello 한글" in out and not ANSI.search(out)
    assert u.plain


def test_banner_plain_and_color():
    u = ui.make_ui(plain=True, width=80)
    with u.console.capture() as cap:
        ui.print_banner(u)
    txt = cap.get()
    assert not ANSI.search(txt) and "ROBO" in txt.upper().replace(" ", "")
    c = ui.make_ui(plain=False, width=80, force_color=True)
    with c.console.capture() as cap:
        ui.print_banner(c)
    assert "38;2;" in cap.get()          # truecolor gradient


def test_width_is_clamped_to_minimum_60(monkeypatch):
    assert ui.make_ui(plain=True, width=20).width == 60
    assert ui.make_ui(plain=True, width=140).width == 140


def test_plain_decision(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert ui.want_plain(flag=True, isatty=True)
    assert ui.want_plain(flag=False, isatty=False)
    assert not ui.want_plain(flag=False, isatty=True)
    monkeypatch.setenv("NO_COLOR", "1")
    assert ui.want_plain(flag=False, isatty=True)


def test_dark_detection_from_colorfgbg(monkeypatch):
    monkeypatch.setenv("COLORFGBG", "15;0")
    assert ui.detect_dark() is True
    monkeypatch.setenv("COLORFGBG", "0;15")
    assert ui.detect_dark() is False
    monkeypatch.delenv("COLORFGBG")
    assert ui.detect_dark() is None


def test_phase_colors_distinct_hex():
    cols = [ui.phase_color(i) for i in range(17)]
    assert len(set(cols)) == 17 and all(re.fullmatch(r"#[0-9a-f]{6}", c) for c in cols)


def test_columns_align_with_korean_and_wrap_last_column():
    import io
    buf = io.StringIO()
    u = ui.make_ui(plain=True, width=60, file=buf)
    u.columns([[("a", ""), ("한글 인자", ""), ("짧은 설명", "")],
               [("longer", ""), ("x", ""), ("이것은 아주 긴 설명이라서 한 줄에 다 들어가지 않고 다음 줄로 넘어가야 합니다 " * 2, "")]])
    lines = buf.getvalue().splitlines()
    first, second = lines[0], lines[1]
    assert cell_len(first[: first.index("짧은")]) == cell_len(second[: second.index("이것은")])
    assert len(lines) >= 3 and all(cell_len(l) <= 60 for l in lines)
    cont = lines[2]
    assert cell_len(cont) - cell_len(cont.lstrip()) == cell_len(second[: second.index("이것은")])


def test_narrow_banner_puts_subtitle_below():
    import io
    buf = io.StringIO()
    u = ui.make_ui(plain=False, width=60, force_color=True, file=buf)
    ui.print_banner(u, subtitle="sub title")
    plain = [l for l in __import__("re").sub(r"\x1b\[[0-9;]*m", "", buf.getvalue()).splitlines()]
    assert not any("sub title" in l and "█" in l for l in plain) and any("sub title" in l for l in plain)
