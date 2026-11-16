# Builds GLOSSARY.md and GLOSSARY.ko.md from every lesson's Key Terms section (first lesson that defines a term wins).
from pathlib import Path

from lesson_sections import key_terms

ROOT = Path(__file__).resolve().parents[1]
TITLE = {"en": ("Glossary", "Every term from the lessons' Key Terms, A to Z, with the lesson that introduces it."),
         "ko": ("용어집", "레슨의 핵심 용어를 알파벳순으로 모았습니다. 그 용어를 처음 소개하는 레슨이 함께 있습니다.")}


def collect(lang):
    seen = {}
    for doc in sorted(ROOT.glob(f"phases/*/*/docs/{lang}.md")):
        lesson = doc.parents[1]
        tag = f"{lesson.parent.name[:2]}-{lesson.name[:2]}"
        for term, definition in key_terms(doc.read_text(), lang):
            seen.setdefault(term.lower(), (term, definition, tag, doc.relative_to(ROOT).as_posix()))
    return sorted(seen.values(), key=lambda x: x[0].lower().strip("`"))


def render(lang):
    title, intro = TITLE[lang]
    lines = [f"# {title}", "", intro, "", "| Term | Meaning | Lesson |", "|---|---|---|"]
    for term, definition, tag, path in collect(lang):
        lines.append(f"| **{term}** | {definition.replace('|', '/')} | [{tag}]({path}) |")
    return "\n".join(lines) + "\n"


def main():
    (ROOT / "GLOSSARY.md").write_text(render("en"))
    (ROOT / "GLOSSARY.ko.md").write_text(render("ko"))


if __name__ == "__main__":
    main()
