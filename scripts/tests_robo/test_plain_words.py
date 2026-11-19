# 쉬운 설명의 구조, 분량, 숫자 근거와 terminal 출력 회귀를 검사한다.
import io

import pytest

import check_lessons as checks
from robo import data, progress, reader, ui


BASE = {
    "en": ["The Problem", "The Concept", "Build It", "Use It", "Ship It", "Exercises"],
    "ko": ["문제", "개념", "만들기", "실제 도구로 보기", "결과물", "연습 문제"],
}
PLAIN = {"en": "In Plain Words", "ko": "쉽게 말하면"}
TERMS = {"en": "## Key Terms\n\n- **Frame**: a set of axes.\n- **Joint**: a hinge.\n- **Link**: a rigid bar.\n\n",
         "ko": "## 핵심 용어\n\n- **Frame**: 축의 묶음입니다.\n- **Joint**: 경첩입니다.\n- **Link**: 단단한 막대입니다.\n\n"}


@pytest.fixture
def lesson(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "assets").mkdir()
    for i in range(3):
        (tmp_path / "assets" / f"fig{i}.png").touch()
    for lang in BASE:
        text = f"# Title\n\n> Idea\n\n**Type:** Build\n\n## {PLAIN[lang]}\n\nA tray tips.\n\n" + TERMS[lang]
        text += "\n\n".join(f"## {heading}\n\nA short paragraph." for heading in BASE[lang])
        text += "\n\n" + "\n".join(f"![Figure](../assets/fig{i}.png)" for i in range(3)) + "\n"
        (tmp_path / "docs" / f"{lang}.md").write_text(text)
    return tmp_path


def edit(lesson, lang, old, new):
    f = lesson / "docs" / f"{lang}.md"
    f.write_text(f.read_text().replace(old, new))


@pytest.mark.parametrize("lang", BASE)
def test_valid_plain_words(lesson, lang):
    assert checks.check_doc(lesson, lang) == []


@pytest.mark.parametrize("lang", BASE)
def test_missing_plain_words_fails_by_default(lesson, lang):
    edit(lesson, lang, f"## {PLAIN[lang]}\n\nA tray tips.\n\n", "")
    assert any("missing" in e and PLAIN[lang] in e for e in checks.check_doc(lesson, lang))


@pytest.mark.parametrize("lang,body", [("en", "word " * 71), ("ko", "설명 " * 91), ("ko", "가" * 601)])
def test_plain_words_over_cap_fails(lesson, lang, body):
    edit(lesson, lang, "A tray tips.", body)
    assert any("plain words" in e and "limit" in e for e in checks.check_doc(lesson, lang))


@pytest.mark.parametrize("lang", BASE)
@pytest.mark.parametrize("claim", ["It moves 17 metres.", "17만큼 움직입니다.", "It uses `17` units."])
def test_unexplained_digit_fails_even_if_repeated_elsewhere(lesson, lang, claim):
    edit(lesson, lang, "A tray tips.", claim)
    with (lesson / "docs" / f"{lang}.md").open("a") as f:
        f.write("\n17 appears elsewhere without evidence.\n")
    assert any("digit" in e for e in checks.check_doc(lesson, lang))


def test_quantity_can_link_directly_to_its_source_or_test(lesson):
    edit(lesson, "en", "A tray tips.", "It moves [17 metres](https://example.org/measurement).")
    assert checks.check_doc(lesson, "en") == []
    tests = lesson / "code" / "tests"
    tests.mkdir(parents=True)
    (tests / "test_distance.py").write_text("# Derived distance checked here.\ndef test_distance():\n    assert 17 == 17\n")
    edit(lesson, "en", "https://example.org/measurement", "../code/tests/test_distance.py")
    assert checks.check_doc(lesson, "en") == []
    edit(lesson, "en", "test_distance.py", "test_missing.py")
    assert any("digit" in e for e in checks.check_doc(lesson, "en"))


@pytest.mark.parametrize("lang", BASE)
def test_sections_must_be_in_order_and_unique(lesson, lang):
    block = f"## {PLAIN[lang]}\n\nA tray tips.\n\n"
    edit(lesson, lang, block, "")
    edit(lesson, lang, f"## {BASE[lang][1]}", block + f"## {BASE[lang][1]}")
    assert any("order" in e for e in checks.check_doc(lesson, lang))
    edit(lesson, lang, block, block + block)
    assert any("duplicate" in e for e in checks.check_doc(lesson, lang))


def test_heading_in_code_is_not_a_section(lesson):
    edit(lesson, "en", "## In Plain Words\n\nA tray tips.", "```text\n## In Plain Words\n```")
    assert any("missing" in e for e in checks.check_doc(lesson, "en"))


def test_english_body_cap_is_380_and_excludes_key_terms_and_math_fold(lesson):
    edit(lesson, "en", "- **Link**: a rigid bar.", "- **Link**: " + "bar " * 24)
    edit(lesson, "en", "## The Concept", "extra " * 320 + "\n\n## The Concept")
    fold = "<details><summary>The math (optional)</summary>\n\n" + "x " * 150 + "\n\n</details>\n\n"
    edit(lesson, "en", "## Build It", fold + "## Build It")
    edit(lesson, "ko", "## 만들기", fold + "## 만들기")
    assert not any("prose words" in e or "fold" in e for e in checks.check_doc(lesson, "en") + checks.check_doc(lesson, "ko"))
    edit(lesson, "en", "## The Concept", "extra " * 60 + "\n\n## The Concept")
    assert any("prose words, limit 380" in e for e in checks.check_doc(lesson, "en"))


def test_math_fold_cap_and_ko_mirror(lesson):
    fold = "<details><summary>The math (optional)</summary>\n\n" + "x " * 170 + "\n\n</details>\n\n"
    edit(lesson, "en", "## Build It", fold + "## Build It")
    assert any("math folds, limit 160" in e for e in checks.check_doc(lesson, "en"))
    assert any("folds differ" in e for e in checks.check_doc(lesson, "ko"))


@pytest.mark.parametrize("lang", BASE)
def test_key_terms_count_is_checked(lesson, lang):
    f = lesson / "docs" / f"{lang}.md"
    t = f.read_text()
    f.write_text("\n".join(l for l in t.splitlines() if "**Link**" not in l and "**Joint**" not in l))
    assert any("key terms 1" in e for e in checks.check_doc(lesson, lang))


def test_key_term_definition_cap_and_ko_term_order(lesson):
    edit(lesson, "en", "a hinge.", "word " * 26)
    assert any("definition 26 words" in e for e in checks.check_doc(lesson, "en"))
    edit(lesson, "ko", "- **Frame**", "- **Frames**")
    assert any("same English terms" in e for e in checks.check_doc(lesson, "ko"))


def test_no_extra_content_between_metadata_and_explainer(lesson):
    edit(lesson, "en", "## In Plain Words", "A stray introduction.\n\n## In Plain Words")
    assert any("directly follow" in e for e in checks.check_doc(lesson, "en"))


def test_checker_cli_is_strict_by_default(lesson, monkeypatch, capsys):
    monkeypatch.setattr(checks, "ROOT", lesson)
    monkeypatch.setattr(checks, "check_lesson", lambda d: ["missing opening"])
    (lesson / "phases" / "00-test" / "01-topic" / "docs").mkdir(parents=True)
    assert checks.main([]) == 1
    assert checks.main(["--strict"]) == 1


@pytest.mark.parametrize("lang", BASE)
def test_terminal_shows_explainer_before_hook_and_problem(course, lang):
    lesson = data.load_course(course).lessons[0]
    f = lesson.doc_path(lang)
    heading = "## The Problem" if lang == "en" else "## 문제"
    f.write_text(f.read_text().replace(heading, f"## {PLAIN[lang]}\n\nA tray tips.\n\n{heading}"))
    buf = io.StringIO()
    u = ui.make_ui(plain=True, width=80, file=buf, lang=lang)
    reader.print_lesson(u, lesson, progress.new_state(), "plain", root=course)
    out = buf.getvalue()
    hook = "Hook text." if lang == "en" else "훅 문장입니다."
    assert out.index(PLAIN[lang]) < out.index("A tray tips.") < out.index(hook) < out.index(heading)
    assert out.count("A tray tips.") == 1


def test_humanizer_guard_keeps_new_heading_and_facts_locked():
    from humanize_guard import cmp_md

    old = "# Title\n\n## In Plain Words\n\nA tray tips.\n\n## The Problem\n\nA wheel turns."
    errs = []
    cmp_md(old, old.replace("A tray tips.", "The tray tips."), "lesson", errs)
    assert not errs
    cmp_md(old, old.replace("## In Plain Words\n", ""), "lesson", errs)
    assert any("headings changed" in e for e in errs)


def test_key_term_name_needs_a_plain_word(lesson):
    edit(lesson, "en", "- **Frame**: a set of axes.", "- **`Tc`**: a set of axes.")
    edit(lesson, "ko", "- **Frame**:", "- **`Tc`**:")
    assert any("plain word" in e for e in checks.check_doc(lesson, "en"))


def test_key_term_definition_has_no_code(lesson):
    edit(lesson, "en", "a set of axes.", "a set from `exp(t)`.")
    assert any("code or math" in e for e in checks.check_doc(lesson, "en"))


def test_key_term_is_defined_before_it_is_used(lesson):
    edit(lesson, "en", "a set of axes.", "axes fixed to a link.")
    assert any("before it is defined" in e for e in checks.check_doc(lesson, "en"))


def test_image_alt_text_does_not_count_toward_the_word_cap(lesson):
    edit(lesson, "en", "![Figure](../assets/fig0.png)", f"![{'alt ' * 400}](../assets/fig0.png)")
    assert not any("prose words" in e for e in checks.check_doc(lesson, "en"))


def test_brackets_without_a_path_are_still_counted_as_prose(lesson):
    with (lesson / "docs" / "en.md").open("a") as f:
        f.write("\n![" + "visible " * 450 + "]\n")   # no (path) after it: ordinary prose
    assert any("prose words" in e for e in checks.check_doc(lesson, "en"))


def test_alt_of_a_linked_clip_poster_is_left_out_of_the_word_cap(lesson):
    edit(lesson, "en", "![Figure](../assets/fig0.png)", f"[![{'alt ' * 400}](../assets/fig0.png)](../assets/fig0.mp4)")
    assert not any("prose words" in e for e in checks.check_doc(lesson, "en"))
