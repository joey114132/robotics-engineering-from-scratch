# 레슨 읽기: 마크다운을 터미널에 맞게 렌더(제목 블록, Bolt 말풍선, 표, 코드 하이라이트, 인라인 그림)
import re
from pathlib import Path

from rich import box
from rich.cells import cell_len
from rich.markdown import CodeBlock, Heading, Markdown, TableElement
from rich.padding import Padding
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from . import figures
from . import progress as P
from . import ui as U

_IMG = re.compile(r"^!\[(.*?)\]\((.+?)\)\s*$")
_CAP = re.compile(r"^\*(?!\*)(.+?)\*\s*$")
_META = re.compile(r"\*\*(.+?):\*\*\s*(.+?)(?=\s{2,}\*\*|$)")


class _Heading(Heading):
    def __rich_console__(self, console, options):
        t, tag = self.text, self.tag
        plain = console.no_color
        if tag == "h1":
            yield t
        elif tag == "h2":
            yield Text("")
            yield Text("▍ ", style="markdown.h2") + t if not plain else Text("## ") + t
        else:
            yield Text("")
            yield (Text("### ") + t) if plain else t


class _Code(CodeBlock):
    def __rich_console__(self, console, options):
        code = str(self.text).rstrip()
        if self.lexer_name == "mermaid":
            yield Text("diagram (mermaid), open the lesson in the browser to see it drawn", style="muted")
        elif self.lexer_name not in ("text", "txt", ""):
            yield Text(self.lexer_name, style="muted")
        yield Padding(Syntax(code, self.lexer_name, theme=self.theme, word_wrap=True, background_color="default"), (0, 0, 0, 2))


class _Table(TableElement):
    def __rich_console__(self, console, options):
        plain = console.no_color
        table = Table(box=box.MARKDOWN if plain else box.SIMPLE_HEAD, header_style="bold", pad_edge=False, show_edge=False)
        if self.header is not None and self.header.row is not None:
            for column in self.header.row.cells:
                table.add_column(column.content)
        if self.body is not None:
            for row in self.body.rows:
                table.add_row(*[el.content for el in row.cells])
        yield table


class _Markdown(Markdown):
    elements = {**Markdown.elements, "heading_open": _Heading, "fence": _Code, "code_block": _Code, "table_open": _Table}


def make_markdown(u, text):
    md = _Markdown(text, code_theme="ansi_light" if u.dark is False else "ansi_dark", hyperlinks=False)
    if u.plain:                      # plain 에서는 `인라인 코드` 의 백틱이 마지막 단서이므로 남긴다
        for tok in md.parsed:
            for c in tok.children or []:
                if c.type == "code_inline":
                    c.content = f"`{c.content}`"
    return md


def split_doc(md):
    """제목, 한 줄 요약, 메타 줄, 나머지 본문으로 나눈다."""
    lines = md.splitlines()
    i, title, tagline, meta = 0, "", "", []
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    if i < len(lines):
        title = lines[i][2:].strip()
        i += 1
    rest = lines[i:]
    j = 0
    while j < len(rest) and not rest[j].strip():
        j += 1
    if j < len(rest) and rest[j].startswith(">"):
        tagline = rest[j].lstrip("> ").strip()
        j += 1
    while j < len(rest) and not rest[j].strip():
        j += 1
    if j < len(rest) and rest[j].startswith("**") and _META.search(rest[j]):
        meta = _META.findall(rest[j])
        j += 1
    return title, tagline, meta, "\n".join(rest[j:])


def split_blocks(body):
    """본문을 ('md', 텍스트) 와 ('img', alt, 경로, 캡션) 조각으로 나눈다. 코드 펜스 안의 줄은 건드리지 않는다."""
    out, buf, fence = [], [], False
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("```"):
            fence = not fence
        m = None if fence else _IMG.match(ln.strip())
        if m:
            if buf:
                out.append(("md", "\n".join(buf)))
                buf = []
            k = i + 1
            while k < len(lines) and not lines[k].strip():
                k += 1
            cap = _CAP.match(lines[k].strip()) if k < len(lines) else None
            out.append(("img", m[1], m[2], cap[1] if cap else m[1]))
            i = k + 1 if cap else i + 1
            continue
        buf.append(ln)
        i += 1
    if buf:
        out.append(("md", "\n".join(buf)))
    return out


def print_lesson(u, lesson, state, mode, root=None):
    doc = lesson.doc_path(u.lang)
    title, tagline, meta, body = split_doc(doc.read_text(encoding="utf-8"))
    w = u.read_width
    u.print()
    t = Text("  ")
    t.append(lesson.short + "  ", style="muted")
    t.append(title or lesson.title(u.lang), style="bold accent")
    u.print(t)
    if tagline:
        u.print(Padding(Text(tagline, style="italic"), (0, 0, 0, 2)), width=w)
    if meta:
        m = Text("  ")
        for k, v in meta:
            m.append(k + " ", style="muted"), m.append(v.strip() + "   ")
        u.para(m)
    hook = lesson.fun(u.lang).get("hook")
    if hook:
        u.print()
        for line in U.bolt_says(u, hook, "idle", w - 2):
            u.print(line, no_wrap=True, overflow="crop")
    for part in split_blocks(body):
        if part[0] == "md":
            if part[1].strip():
                u.print(Padding(make_markdown(u, part[1]), (0, 0, 0, 2)), width=w)
        else:
            _, alt, src, cap = part
            path = (doc.parent / src).resolve() if not src.startswith("http") else Path(src)
            u.print()
            full = mode == "full"
            lines = figures.render_figure(path, cap if u.plain else cap.replace("`", ""), min(w - 4, 96 if full else figures.MAX_COLS),
                                          mode=mode, rel_to=root, max_rows=None if full else figures.MAX_ROWS)
            if mode == "plain":
                u.print(Padding(lines[0], (0, 0, 0, 2)), width=w)
            else:
                for line in lines[:-1]:
                    u.print(Text("  ") + line, no_wrap=True, overflow="crop")
                u.print(Padding(lines[-1], (0, 0, 0, 2)), width=w)
            u.print()
    u.print()
    u.rule(width=w)
    if lesson.assets():
        u.print(Padding(Text(u.t("Figures at full size: ", "그림 원본: ") + str((lesson.path / "assets").relative_to(root) if root else lesson.path / "assets"), style="muted"), (0, 0, 0, 2)), width=w)
    answered = len(state["q"].get(lesson.id, {}))
    foot = Text("  ")
    foot.append(u.t(f"quiz {answered}/{P.QUESTIONS_PER_LESSON}", f"퀴즈 {answered}/{P.QUESTIONS_PER_LESSON}"), style="muted")
    foot.append("   " + (u.t("mission done", "미션 완료") if state["m"].get(lesson.id) else u.t("mission open", "미션 남음")), style="muted")
    foot.append(f"      robo quiz {lesson.short}   robo mission {lesson.short}", style="accent" if not u.plain else "")
    u.print(foot)
