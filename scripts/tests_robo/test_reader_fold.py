# terminal reader: the optional math fold shows its title as bold text and drops the closing tag, never inside code.
from robo import reader


def test_fold_becomes_bold_title_and_close_tag_is_dropped():
    out = reader.split_blocks("a\n<details><summary>The math (optional)</summary>\n\nx = 1\n\n</details>\nb")
    assert out == [("md", "a\n**The math (optional)**\n\nx = 1\n\nb")]


def test_fold_tags_inside_code_are_kept():
    body = "```html\n<details><summary>S</summary>\n</details>\n```"
    assert reader.split_blocks(body) == [("md", body)]
