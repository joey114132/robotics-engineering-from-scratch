# The worked-example clip line is a poster image linked to the video, [![alt](x.jpg)](x.mp4); the checker, the terminal reader and the humanize guard accept that form and only that form.
import io

import pytest
from PIL import Image

import check_lessons as checks
from humanize_guard import cmp_md
from robo import cli, reader

POSTER, VIDEO = "../assets/clip-example.jpg", "../assets/clip-example.mp4"
NEW = f"[![A bench arm turns]({POSTER})]({VIDEO})"
OLD = f"![A bench arm turns]({VIDEO})"
CAPTION = "*The arm turns.*"


@pytest.fixture
def lesson(course):
    d = course / "phases" / "00-alpha-tools" / "01-first-steps"
    Image.new("RGB", (40, 20), (30, 30, 200)).save(d / "assets" / "clip-example.jpg")
    (d / "assets" / "clip-example.mp4").write_bytes(b"x")
    (d / "code").mkdir(exist_ok=True)
    (d / "code" / "clip-example.py").write_text("# clip\n")
    put(d, NEW)
    return d


def put(d, line, lang="en"):
    f = d / "docs" / f"{lang}.md"
    base = f.read_text().split("\n\n[![")[0].split("\n\n![A bench")[0]
    f.write_text(base + f"\n\n{line}\n\n{CAPTION}\n")
    return f


def clip_errors(d, lang="en"):
    return [e for e in checks.check_doc(d, lang) if "clip" in e]


def test_new_form_with_poster_video_and_script_passes(lesson):
    put(lesson, NEW, "ko")
    assert clip_errors(lesson) == [] and clip_errors(lesson, "ko") == []


def test_new_form_needs_its_clip_script(lesson):
    (lesson / "code" / "clip-example.py").unlink()
    assert any("code/clip-example.py" in e for e in clip_errors(lesson))


def test_new_form_needs_the_video_file(lesson):
    (lesson / "assets" / "clip-example.mp4").unlink()
    assert any("clip-example.mp4" in e for e in clip_errors(lesson))


def test_new_form_needs_the_poster_file(lesson):
    (lesson / "assets" / "clip-example.jpg").unlink()
    assert any("image not found" in e for e in checks.check_doc(lesson, "en"))


def test_poster_and_video_share_a_name(lesson):
    put(lesson, f"[![A bench arm turns]({POSTER})](../assets/clip.mp4)")
    assert any("same name" in e for e in clip_errors(lesson))


def test_poster_must_be_a_jpg_because_the_reader_only_shows_jpg(lesson):
    Image.new("RGB", (40, 20)).save(lesson / "assets" / "clip-example.png")
    put(lesson, "[![A bench arm turns](../assets/clip-example.png)](../assets/clip-example.mp4)")
    assert any(".jpg" in e for e in clip_errors(lesson))


def test_old_form_is_rejected(lesson):
    put(lesson, OLD)
    assert any("[![alt](x.jpg)](x.mp4)" in e for e in clip_errors(lesson))


def test_both_languages_link_the_same_clip(lesson):
    put(lesson, f"![A bench arm turns]({POSTER})", "ko")
    assert any("clips differ" in e for e in clip_errors(lesson, "ko"))


def test_reader_parses_the_linked_poster_as_one_figure():
    assert reader.split_blocks(f"a\n\n{NEW}\n\n{CAPTION}\n\nb") == [
        ("md", "a\n"), ("img", "A bench arm turns", POSTER, "The arm turns."), ("md", "\nb")]


def test_reader_does_not_draw_the_old_form():
    assert not [p for p in reader.split_blocks(f"{OLD}\n\n{CAPTION}") if p[0] == "img"]


def test_read_shows_the_poster(lesson, course, state_home, monkeypatch, capsys):
    monkeypatch.setenv("ROBO_ROOT", str(course))
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    assert cli.main(["read", "00-01", "--plain", "--no-pager"]) == 0
    assert "The arm turns. (phases/00-alpha-tools/01-first-steps/assets/clip-example.jpg)" in capsys.readouterr().out


def test_humanize_guard_locks_the_clip_line():
    old = f"# T\n\n{NEW}\n\n{CAPTION}\n"
    errs = []
    cmp_md(old, old.replace("A bench arm turns", "A bench arm swings"), "lesson", errs)
    assert any("image lines changed" in e for e in errs)
