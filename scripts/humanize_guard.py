# 윤문 보호 검사: .board/humanize-backup 의 원본과 현재 파일을 비교해 문체 밖의 것이 바뀌었는지 잡는다
"""Usage: python3 scripts/humanize_guard.py [--phase NN ...] [--lang en|ko]
Checks, per lesson and language, that humanizing changed style only:
docs/<lang>.md  headings, fenced code, inline code, image lines, table row counts, URLs and every digit sequence are identical.
fun.json        inline code and digits identical, hook <= 150 chars, mission <= 220 chars, toy/motion keys untouched.
quiz*.json      same questions and options count, same answer index, digits and inline code identical.
Exit 1 when anything differs."""
import json, re, sys
from collections import Counter
from pathlib import Path

from lesson_sections import headings

ROOT = Path(__file__).resolve().parents[1]
BK = ROOT / ".board" / "humanize-backup"
DIGITS = re.compile(r"\d+(?:\.\d+)?")
CODE = re.compile(r"`[^`\n]+`")
URL = re.compile(r"https?://[^\s)>\]]+")


def split_md(t):
    fences, prose, inside, cur = [], [], False, []
    for ln in t.splitlines():
        if ln.startswith("```"):
            if inside:
                cur.append(ln); fences.append("\n".join(cur)); cur = []
            else:
                cur = [ln]
            inside = not inside
        elif inside:
            cur.append(ln)
        else:
            prose.append(ln)
    return fences, prose


def facts(prose):
    body = "\n".join(l for l in prose if not l.startswith("!["))
    return Counter(DIGITS.findall(body)), Counter(CODE.findall(body)), Counter(URL.findall(body))


def cmp_md(old, new, tag, errs):
    fo, po = split_md(old); fn, pn = split_md(new)
    if fo != fn: errs.append(f"{tag}: fenced code changed")
    # Shared parser includes In Plain Words / 쉽게 말하면 and ignores headings in code.
    # A structural rollout must refresh only that lesson's baseline before humanizing.
    ho = [h[0] for h in headings(old)]; hn = [h[0] for h in headings(new)]
    if ho != hn: errs.append(f"{tag}: headings changed")
    io = [l for l in po if l.startswith("![")]; inn = [l for l in pn if l.startswith("![")]
    if io != inn: errs.append(f"{tag}: image lines changed")
    to = sum(1 for l in po if l.startswith("|")); tn = sum(1 for l in pn if l.startswith("|"))
    if to != tn: errs.append(f"{tag}: table rows {to} -> {tn}")
    for name, a, b in zip(("digits", "inline code", "urls"), facts(po), facts(pn)):
        if a != b:
            lost, gained = a - b, b - a
            errs.append(f"{tag}: {name} differ: lost {dict(lost)} gained {dict(gained)}")


def cmp_json(old, new, tag, errs, kind):
    o, n = json.loads(old), json.loads(new)
    if kind == "fun":
        for k in ("toy", "motion"):
            if o.get(k) != n.get(k): errs.append(f"{tag}: key {k} changed")
        for lg in ("en", "ko"):
            if lg not in o: continue
            for k, lim in (("hook", 150), ("mission", 220)):
                a, b = o[lg][k], n[lg][k]
                if len(b) > lim: errs.append(f"{tag}: {lg}.{k} {len(b)} > {lim}")
                if Counter(DIGITS.findall(a)) != Counter(DIGITS.findall(b)): errs.append(f"{tag}: {lg}.{k} digits differ")
                if Counter(CODE.findall(a)) != Counter(CODE.findall(b)): errs.append(f"{tag}: {lg}.{k} inline code differs")
    else:
        if len(o) != len(n): errs.append(f"{tag}: question count {len(o)} -> {len(n)}"); return
        for i, (a, b) in enumerate(zip(o, n)):
            if a.get("answer") != b.get("answer"): errs.append(f"{tag}: q{i} answer index changed")
            if len(a["options"]) != len(b["options"]): errs.append(f"{tag}: q{i} option count changed")
            for k in ("question", "explanation"):
                if Counter(DIGITS.findall(a.get(k, ""))) != Counter(DIGITS.findall(b.get(k, ""))): errs.append(f"{tag}: q{i}.{k} digits differ")
                if Counter(CODE.findall(a.get(k, ""))) != Counter(CODE.findall(b.get(k, ""))): errs.append(f"{tag}: q{i}.{k} inline code differs")
            for j, (x, y) in enumerate(zip(a["options"], b["options"])):
                if Counter(DIGITS.findall(x)) != Counter(DIGITS.findall(y)) or Counter(CODE.findall(x)) != Counter(CODE.findall(y)):
                    errs.append(f"{tag}: q{i} option {j} digits or code differ")


def main(argv):
    phases = [a for i, a in enumerate(argv) if i and argv[i - 1] == "--phase"]
    langs = [a for i, a in enumerate(argv) if i and argv[i - 1] == "--lang"] or ["en", "ko"]
    errs, changed, seen = [], 0, 0
    for old in sorted(BK.glob("phases/*/*/*")) + sorted(BK.glob("phases/*/*/docs/*.md")):
        if old.is_dir(): continue
        rel = old.relative_to(BK); new = ROOT / rel
        if phases and rel.parts[1][:2] not in phases: continue
        name = old.name
        if name.endswith(".md"):
            if name[:-3] not in langs: continue
            kind = "md"
        elif name == "fun.json": kind = "fun"
        elif name.startswith("quiz"):
            if (name == "quiz.json" and "en" not in langs) or (name == "quiz.ko.json" and "ko" not in langs): continue
            kind = "quiz"
        else: continue
        seen += 1
        a, b = old.read_text(), new.read_text()
        if a != b: changed += 1
        tag = "/".join(rel.parts[1:])
        if kind == "md": cmp_md(a, b, tag, errs)
        else:
            try: cmp_json(a, b, tag, errs, kind)
            except Exception as e: errs.append(f"{tag}: {type(e).__name__} {e}")
    print(f"checked {seen} files, {changed} changed, {len(errs)} problems")
    for e in errs[:80]: print(" -", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
