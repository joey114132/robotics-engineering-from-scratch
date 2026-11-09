# 레슨 구조 검사: 필수 파일, en/ko 구조 일치, 이미지 3장 이상, quiz 6문항, 테스트 5개 이상, 분량 상한
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["docs/en.md", "docs/ko.md", "code/main.py", "quiz.json", "quiz.ko.json"]
EN_SECTIONS = ["## The Problem", "## The Concept", "## Build It", "## Use It", "## Ship It", "## Exercises"]
MAX_WORDS = 450
MIN_IMAGES = 3
IMG = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def fences(text: str):
    """Yield (lang, body) of fenced blocks; report untagged ones through the lang value ''."""
    out, cur, lang = [], None, None
    for line in text.splitlines():
        if line.startswith("```"):
            if cur is None:
                lang, cur = line[3:].strip(), []
            else:
                out.append((lang, "\n".join(cur)))
                cur = None
        elif cur is not None:
            cur.append(line)
    return out


def prose_words(text: str) -> int:
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    return len(re.findall(r"\S+", body))


def check_doc(d: Path, lang: str) -> list[str]:
    f = d / "docs" / f"{lang}.md"
    if not f.exists():
        return []
    t = f.read_text()
    errs = []
    blocks = fences(t)
    errs += [f"{lang}: fenced block without language tag" for g, _ in blocks if not g]
    errs += [f"{lang}: mermaid is not allowed, use an Excalidraw diagram" for g, _ in blocks if g == "mermaid"]
    imgs = IMG.findall(t)
    if len(imgs) < MIN_IMAGES:
        errs.append(f"{lang}: {len(imgs)} images, need {MIN_IMAGES}+")
    for p in imgs:
        if not (f.parent / p).resolve().exists():
            errs.append(f"{lang}: image not found: {p}")
    if lang == "en":
        errs += [f"en: missing '{s}'" for s in EN_SECTIONS if s not in t]
        w = prose_words(t)
        if w > MAX_WORDS:
            errs.append(f"en: {w} prose words, limit {MAX_WORDS}")
    else:
        en = (d / "docs" / "en.md").read_text() if (d / "docs" / "en.md").exists() else ""
        if t.count("\n## ") != en.count("\n## "):
            errs.append(f"{lang}: heading count differs from en")
        if IMG.findall(en) != imgs:
            errs.append(f"{lang}: images differ from en")
        if [g for g, _ in fences(en)] != [g for g, _ in blocks]:
            errs.append(f"{lang}: code block sequence differs from en")
    return errs


def check_quiz(d: Path, name: str) -> list[str]:
    q = d / name
    if not q.exists():
        return []
    try:
        data = json.loads(q.read_text())
    except json.JSONDecodeError as e:
        return [f"{name} invalid: {e}"]
    errs, stages = [], [x.get("stage") for x in data]
    if len(data) != 6 or [stages.count(s) for s in ("pre", "check", "post")] != [1, 3, 2]:
        errs.append(f"{name}: need 1 pre, 3 check, 2 post; got {stages}")
    errs += [f"{name} id {x.get('id')}: answer index out of range" for x in data if not 0 <= x.get("answer", -1) < len(x.get("options", []))]
    return errs


def check_lesson(d: Path) -> list[str]:
    errs = [f"missing {f}" for f in REQUIRED if not (d / f).exists()]
    if not list((d / "outputs").glob("skill-*.md")):
        errs.append("missing outputs/skill-*.md")
    tests = list((d / "code" / "tests").glob("test_*.py"))
    if not tests:
        errs.append("missing code/tests/test_*.py")
    elif sum(len(re.findall(r"^def test_", t.read_text(), re.M)) for t in tests) < 5:
        errs.append("fewer than 5 tests")
    for lang in sorted(p.stem for p in (d / "docs").glob("*.md")):
        errs += check_doc(d, lang)
    qe, qk = check_quiz(d, "quiz.json"), check_quiz(d, "quiz.ko.json")
    errs += qe + qk
    if not qe and not qk and (d / "quiz.json").exists() and (d / "quiz.ko.json").exists():
        a = [x["answer"] for x in json.loads((d / "quiz.json").read_text())]
        b = [x["answer"] for x in json.loads((d / "quiz.ko.json").read_text())]
        if a != b:
            errs.append("quiz answers differ between en and ko")
    return errs


def main() -> int:
    lessons = sorted(p.parent for p in (ROOT / "phases").glob("*/*/docs"))
    failed = 0
    for d in lessons:
        errs = check_lesson(d)
        print(("FAIL " if errs else "ok   ") + str(d.relative_to(ROOT)))
        for e in errs:
            print("     -", e)
        failed += bool(errs)
    print(f"{len(lessons)} lessons, {failed} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
