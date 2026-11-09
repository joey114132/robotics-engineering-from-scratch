# 코스 로딩과 id 해석 테스트
import pytest

from robo import data
from conftest import REAL_ROOT


def test_loads_phases_and_lessons(course):
    c = data.load_course(course)
    assert [p.no for p in c.phases] == ["00", "01"]
    assert [l.id for l in c.lessons] == ["00-01-first-steps", "00-02-second-wind", "01-01-third-try"]
    assert c.phases[0].title("en") == "Alpha Tools" and c.phases[1].slug == "beta-gamma"
    l = c.lessons[0]
    assert l.short == "00-01" and l.title("en") == "First Steps" and l.title("ko").endswith("(한글)")


def test_phase_ko_titles_for_real_course():
    c = data.load_course(REAL_ROOT)
    assert len(c.lessons) == 67 and len(c.phases) == 17
    assert c.phases[3].title("ko") == "동역학과 제어"
    assert c.phases[3].title("en") == "Dynamics and Control"
    assert c.phases[12].title("en") == "Simulation and Sim-to-Real"


@pytest.mark.parametrize("q", ["00-02", "0-2", "second", "SECOND-wind", "00-02-second-wind"])
def test_resolve(course, q):
    assert data.load_course(course).resolve(q).id == "00-02-second-wind"


def test_resolve_errors(course):
    c = data.load_course(course)
    with pytest.raises(LookupError, match="nothing"):
        c.resolve("nothing-like-this")
    with pytest.raises(LookupError, match="first-steps|second-wind"):
        c.resolve("0")          # '0' alone matches several lessons


def test_resolve_real_course_examples():
    c = data.load_course(REAL_ROOT)
    assert c.resolve("03-02").id == "03-02-gravity-compensation"
    assert c.resolve("gravity-comp").short == "03-02"
    assert c.resolve("3-2").short == "03-02"


def test_lesson_content_by_language(course):
    l = data.load_course(course).lessons[0]
    assert l.quiz("en")[0]["question"].startswith("EN")
    assert l.quiz("ko")[0]["question"].startswith("KO")
    assert l.fun("ko")["hook"] == "훅 문장입니다."
    assert l.doc_path("ko").name == "ko.md" and l.doc_path("en").read_text().startswith("# First Steps")
    assert [p.name for p in l.assets()] == ["fig.png"]


def test_every_real_lesson_has_six_questions_and_fun():
    c = data.load_course(REAL_ROOT)
    for l in c.lessons:
        assert len(l.quiz("en")) == 6 and len(l.quiz("ko")) == 6, l.id
        assert l.fun("en")["hook"] and l.fun("ko")["mission"], l.id


def test_lang_default_from_env(monkeypatch):
    for k in ("LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.delenv(k, raising=False)
    assert data.default_lang() == "en"
    monkeypatch.setenv("LANG", "ko_KR.UTF-8")
    assert data.default_lang() == "ko"
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    assert data.default_lang() == "en"
