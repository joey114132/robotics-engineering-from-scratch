# GLOSSARY.md 생성: 첫 레슨의 정의가 이기고 알파벳순이며 레슨 링크가 붙는다.
import build_glossary as g


def test_first_lesson_wins_and_sorted(tmp_path, monkeypatch):
    for ph, ls, body in [("00-a", "01-x", "- **Zeta**: last.\n- **alpha**: first def."),
                         ("01-b", "02-y", "- **Alpha**: second def.")]:
        d = tmp_path / "phases" / ph / ls / "docs"
        d.mkdir(parents=True)
        (d / "en.md").write_text(f"# T\n\n## Key Terms\n\n{body}\n\n## The Problem\n\nx\n")
    monkeypatch.setattr(g, "ROOT", tmp_path)
    rows = [l for l in g.render("en").splitlines() if l.startswith("| **")]
    assert rows[0].startswith("| **alpha** | first def. | [00-01](phases/00-a/01-x/docs/en.md)")
    assert rows[1].startswith("| **Zeta**")
    assert len(rows) == 2
