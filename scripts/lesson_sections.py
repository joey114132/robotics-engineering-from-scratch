# 레슨의 공통 heading과 쉬운 설명 경계를 모든 출력 도구에 제공한다.
import re

PLAIN_HEADINGS = {"en": "## In Plain Words", "ko": "## 쉽게 말하면"}
SECTIONS = {
    "en": [PLAIN_HEADINGS["en"], "## The Problem", "## The Concept", "## Build It", "## Use It", "## Ship It", "## Exercises"],
    "ko": [PLAIN_HEADINGS["ko"], "## 문제", "## 개념", "## 만들기", "## 실제 도구로 보기", "## 결과물", "## 연습 문제"],
}


def headings(text, level=None):
    """Return heading matches with source offsets; fenced code cannot create sections."""
    masked, fence, size = [], None, 0
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        inside = fence is not None
        if marker:
            ch, n = marker[1][0], len(marker[1])
            if fence is None:
                fence, size = ch, n
            elif ch == fence and n >= size:
                fence = None
        masked.append(re.sub(r"[^\r\n]", " ", line) if inside or marker else line)
    pattern = r"^#{1,6} [^\r\n]+" if level is None else rf"^#{{{level}}} [^\r\n]+"
    return list(re.finditer(pattern, "".join(masked), re.M))


def split_plain_words(text):
    """Return prelude, opening section (including heading), remainder; preserve bytes."""
    hs = headings(text, 2)
    for i, h in enumerate(hs):
        if h[0].strip() in PLAIN_HEADINGS.values():
            end = hs[i + 1].start() if i + 1 < len(hs) else len(text)
            return text[:h.start()], text[h.start():end], text[end:]
    return text, "", ""
