# 레슨 구조 검사: 필수 파일, en/ko 구조 일치, 이미지 3장 이상, quiz 6문항, 테스트 5개 이상, 분량 상한
import argparse
import json
import re
import sys
from pathlib import Path

from lesson_sections import PLAIN_HEADINGS, SECTIONS, headings, split_plain_words

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["docs/en.md", "docs/ko.md", "code/main.py", "quiz.json", "quiz.ko.json"]
EN_SECTIONS = SECTIONS["en"]
KO_SECTIONS = SECTIONS["ko"]
MAX_WORDS = 540
PLAIN_WORDS = 90
PLAIN_KO_CHARS = 600
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


def check_plain_words(d: Path, lang: str, block: str) -> list[str]:
    body = block.partition("\n")[2].strip()
    errs = []
    # Count visible link labels, not the URL or evidence filename.
    visible = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    w = prose_words(visible)
    if not visible:
        errs.append(f"{lang}: plain words block is empty")
    if w > PLAIN_WORDS:
        errs.append(f"{lang}: plain words {w} words, limit {PLAIN_WORDS}")
    if lang == "ko" and len(visible) > PLAIN_KO_CHARS:
        errs.append(f"ko: plain words {len(visible)} characters, limit {PLAIN_KO_CHARS}")

    def evidence(m):
        label, target = m.groups()
        if re.match(r"https?://[^\s/]+/", target):
            return ""  # A reviewer still verifies that the source supports the quantity.
        test = (d / "docs" / target).resolve()
        tests = (d / "code" / "tests").resolve()
        if test.is_relative_to(tests) and test.is_file() and test.name.startswith("test_") and test.suffix == ".py":
            return ""  # The linked test must derive/check the quantity; existence is the mechanical gate.
        return label

    unsupported = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", evidence, body)
    if re.search(r"\d", unsupported):
        errs.append(f"{lang}: plain words unexplained digit; link the quantity to its source or lesson test")
    if fences(body) or re.search(r"^\s*(?:```|~~~|#|>|!\[|\||- |\d+\. )", body, re.M):
        errs.append(f"{lang}: plain words must contain only prose paragraphs")
    if "—" in body or "–" in body:
        errs.append(f"{lang}: plain words must not join clauses with dashes")
    if lang == "ko":
        if "·" in body or re.search(r"(?:고|며|지만|면서),", body):
            errs.append("ko: plain words readability: noun chains or connective comma")
        if any(len(line) > 160 for line in body.splitlines()):
            errs.append("ko: plain words line exceeds 160 characters")
    return errs


def check_doc(d: Path, lang: str, *, allow_missing_plain_words=False) -> list[str]:
    f = d / "docs" / f"{lang}.md"
    if not f.exists():
        return []
    t = f.read_text()
    errs = []
    hs = [h[0].strip() for h in headings(t, 2)]
    if lang in SECTIONS:
        required = SECTIONS[lang]
        if allow_missing_plain_words and PLAIN_HEADINGS[lang] not in hs:
            required = required[1:]
        errs += [f"{lang}: missing '{s}'" for s in required if s not in hs]
        errs += [f"{lang}: duplicate '{s}'" for s in required if hs.count(s) > 1]
        if all(s in hs for s in required) and hs != required:
            errs.append(f"{lang}: required sections out of order or unexpected section")
        prelude, plain, _ = split_plain_words(t)
        if plain:
            lines = [line for line in prelude.splitlines() if line.strip()]
            if (len(lines) != 3 or not lines[0].startswith("# ") or not lines[1].startswith("> ")
                    or not re.match(r"^\*\*(?:Type|유형):\*\*", lines[2])):
                errs.append(f"{lang}: plain words must directly follow title, idea and Type metadata")
            errs += check_plain_words(d, lang, plain)
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
        w = prose_words(t)
        if w > MAX_WORDS:
            errs.append(f"en: {w} prose words, limit {MAX_WORDS}")
    else:
        en = (d / "docs" / "en.md").read_text() if (d / "docs" / "en.md").exists() else ""
        if len(headings(t, 2)) != len(headings(en, 2)):
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


def check_lesson(d: Path, *, allow_missing_plain_words=False) -> list[str]:
    errs = [f"missing {f}" for f in REQUIRED if not (d / f).exists()]
    if not list((d / "outputs").glob("skill-*.md")):
        errs.append("missing outputs/skill-*.md")
    tests = list((d / "code" / "tests").glob("test_*.py"))
    if not tests:
        errs.append("missing code/tests/test_*.py")
    elif sum(len(re.findall(r"^def test_", t.read_text(), re.M)) for t in tests) < 5:
        errs.append("fewer than 5 tests")
    for lang in sorted(p.stem for p in (d / "docs").glob("*.md")):
        errs += check_doc(d, lang, allow_missing_plain_words=allow_missing_plain_words)
    qe, qk = check_quiz(d, "quiz.json"), check_quiz(d, "quiz.ko.json")
    errs += qe + qk
    if not qe and not qk and (d / "quiz.json").exists() and (d / "quiz.ko.json").exists():
        a = [x["answer"] for x in json.loads((d / "quiz.json").read_text())]
        b = [x["answer"] for x in json.loads((d / "quiz.ko.json").read_text())]
        if a != b:
            errs.append("quiz answers differ between en and ko")
    return errs


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check bilingual lesson structure (strict by default).")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--allow-missing-plain-words", action="store_true", help="rollout only: permit absent opening blocks; validate every block that exists")
    mode.add_argument("--strict", action="store_true", help="require opening blocks in every lesson (the default)")
    args = parser.parse_args(argv)
    lessons = sorted(p.parent for p in (ROOT / "phases").glob("*/*/docs"))
    failed = 0
    for d in lessons:
        errs = check_lesson(d, allow_missing_plain_words=args.allow_missing_plain_words)
        print(("FAIL " if errs else "ok   ") + str(d.relative_to(ROOT)))
        for e in errs:
            print("     -", e)
        failed += bool(errs)
    print(f"{len(lessons)} lessons, {failed} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
