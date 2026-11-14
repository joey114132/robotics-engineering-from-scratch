# check_lessons 가 레슨의 클립 스크립트와 두 언어 캡션과 fun.json 을 요구하는지 검사한다 (3D 장면 이름은 웹사이트 저장소가 검사한다)
import json

FUN = {"en": {"hook": "Hook.", "mission": "Do it.", "clip": "A bench arm turns."}, "ko": {"hook": "훅.", "mission": "하세요.", "clip": "팔이 돕니다."},
       "motion": "gone-2d-concept", "three": "gone-3d"}


def lesson_dir(course):
    d = course / "phases" / "00-alpha-tools" / "01-first-steps"
    (d / "code").mkdir(exist_ok=True)
    (d / "code" / "clip.py").write_text("# clip\n")
    (d / "fun.json").write_text(json.dumps(FUN, ensure_ascii=False))
    return d


def test_check_lessons_requires_the_clip_script_the_captions_and_fun_json(course):
    import check_lessons as checks
    d = lesson_dir(course)
    assert [e for e in checks.check_lesson(d) if "clip" in e or "fun.json" in e] == []
    (d / "code" / "clip.py").unlink()
    assert any("code/clip.py" in e for e in checks.check_lesson(d))
    d = lesson_dir(course)
    for lang in ("en", "ko"):
        fun = json.loads((d / "fun.json").read_text())
        fun[lang]["clip"] = "  "
        (d / "fun.json").write_text(json.dumps(fun, ensure_ascii=False))
        assert any(f"fun.json {lang}.clip" in e for e in checks.check_lesson(d))
        d = lesson_dir(course)
    (d / "fun.json").unlink()
    assert any("fun.json" in e for e in checks.check_lesson(d))


def test_check_lessons_ignores_leftover_motion_and_three_keys(course):
    import check_lessons as checks
    d = lesson_dir(course)
    assert "motion" in json.loads((d / "fun.json").read_text())
    assert not any("motion" in e or "three" in e for e in checks.check_lesson(d))
    fun = json.loads((d / "fun.json").read_text())
    del fun["three"]
    (d / "fun.json").write_text(json.dumps(fun, ensure_ascii=False))
    assert not any("three" in e or "3D" in e for e in checks.check_lesson(d))   # the scene name is the website's concern
