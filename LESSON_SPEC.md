# Lesson spec (short, visual, bilingual)

A lesson is a one-sitting study guide, about 15 minutes. The reader sees the idea in pictures before reading any math. The finished exemplar is `phases/03-dynamics-and-control/02-gravity-compensation`. Open its `docs/en.md`, `docs/ko.md`, `code/` and `assets/` and copy its shape.

## Folder

```text
phases/NN-slug/NN-lesson-slug/
  docs/en.md  docs/ko.md        required. Other languages: docs/<code>.md, optional, same structure
  code/main.py                  from-scratch implementation, at most 80 lines, one-line header comment
  code/diagram.py               builds assets/diagram-*.excalidraw with scripts/excal.py (2 or more diagrams)
  code/figure.py                builds assets/fig-*.png data plots with matplotlib (1 or more where there is data)
  code/tests/test_<slug>.py     pytest, 5+ tests, written first (red), unique file name
  assets/                       generated .excalidraw, .svg, .png. Commit them.
  quiz.json  quiz.ko.json       6 questions: 1 pre, 3 check, 2 post; same ids, same answer index
  outputs/skill-<slug>.md       English harness file, front matter name and description (when to call it)
```

## Doc shape (en.md): at most 450 words outside code blocks, at least 3 images

```text
# Title
> one-line idea
**Type:** Build | Learn   **Prerequisites:** ...   **Time:** ~15 minutes
## The Problem    3 sentences, a concrete failure the reader has felt
## The Concept    diagrams first. 2+ Excalidraw diagrams and 1+ data figure, each with a one-sentence italic caption
## Build It       at most 40 lines of code in steps, then the run command
## Use It         at most 6 lines: the production library and what to compare
## Ship It        what outputs/skill-<slug>.md does
## Exercises      3 one-line exercises
```

A reader who only looks at the pictures must get the idea. Put a picture where you would otherwise write a paragraph.

## Visuals

Build everything with `python3 scripts/build_figures.py <lesson-name-fragment>`. It runs `diagram*.py` and `figure*.py`, then renders every `.excalidraw` to `.svg` and `.png` with the real Excalidraw renderer. Docs link the `.png`.

Diagrams use `scripts/excal.py`:

```python
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram
d = Diagram()                                  # grid cells 300 x 170 px
d.title("Why a soft arm sags")
a = d.box("Model says\ngravity = ff", col=0, row=0, color="blue")   # colors: blue green yellow red purple gray
b = d.box("Residual", col=1, row=0.5, color="red", shape="rectangle")  # shapes: rectangle ellipse diamond
d.arrow(a, b, label="minus")                   # route="below" draws a feedback loop under the boxes
d.note("one-line takeaway", x, y)
d.save(OUT / "diagram-name.excalidraw")
```

- At most 8 boxes per diagram, 2 lines per box, short words. Colour carries meaning: blue input, yellow real world, red problem, purple transform, green result, gray neutral.
- Data figures (matplotlib, Agg backend): 1200x675 px or smaller, English labels only, axis names with units, a title that states the takeaway, colour-blind-safe colours (`#0072B2` blue, `#D55E00` orange, `#555555` gray), seeded, no external data.
- Captions live in each language's doc, so one image serves every language.
- Look at every PNG with the Read tool before reporting. Check clipped or overlapping text, crossing arrows, and whether the picture shows what the caption claims. Fix and rebuild.

## Content rules

- A number is derived in the lesson and tested, or it carries a source link found by a live search that day. No remembered vendor specs, prices or version claims.
- Lessons are simulation-only. No command that addresses a real motor ID or bus. No named company, robot product or vendor in the text.
- Original text and code. Do not copy from other courses or repos.
- Plain words first, then the term. Terminology stays English in every language.

## Korean (ko.md)

- Same headings, same number and order of code blocks and images as en.md. Images, code and tests are shared; only prose, captions and quiz text are translated. Code comments stay English.
- Polite style (`~합니다`), terms in English, particles attached (`PID를`, `kp가`).
- Keep Korean prose plain: no `—` joining clauses, no middle-dot chains of nouns in prose, no comma after a connective ending, no sentence ending in a colon, at most one bold per paragraph, no paragraph over 160 characters.

## Checks

```bash
cd robotics-engineering-from-scratch
python3 scripts/build_figures.py          # all lessons, or pass a name fragment
python3 scripts/check_lessons.py
python3 -m pytest phases -q
```
