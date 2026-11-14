# Lesson spec (short, visual, bilingual)

A lesson is a one-sitting study guide, about 15 minutes. The reader sees the idea in pictures before reading any math. The finished exemplar is `phases/03-dynamics-and-control/02-gravity-compensation`. Open its `docs/en.md`, `docs/ko.md`, `code/` and `assets/` and copy its shape.

## Folder

```text
phases/NN-slug/NN-lesson-slug/
  docs/en.md  docs/ko.md        required. Other languages: docs/<code>.md, optional, same structure
  code/main.py                  from-scratch implementation, at most 80 lines, one-line header comment
  code/diagram.py               builds assets/diagram-*.excalidraw with scripts/excal.py (2 or more diagrams)
  code/figure.py                builds assets/fig-*.png data plots with matplotlib (1 or more where there is data)
  code/clip.py                  builds assets/clip.mp4 and clip.jpg in Blender: the lesson's real object, moved by code/main.py
  code/clip-example.py          optional second clip for the worked example, linked from both docs
  code/tests/test_<slug>.py     pytest, 5+ tests, written first (red), unique file name
  assets/                       generated .excalidraw, .svg, .png. Commit them.
  quiz.json  quiz.ko.json       6 questions: 1 pre, 3 check, 2 post; same ids, same answer index
  outputs/skill-<slug>.md       English harness file, front matter name and description (when to call it)
  fun.json                      extras: en and ko text (hook, mission, clip caption), plus the names of the lesson's toy and three (3D scene); the separate website repo reads the last two
```

## Doc shape: at most 600 English words outside code blocks, at least 3 images

```text
# Title
> one-line idea
**Type:** Build | Learn   **Prerequisites:** ...   **Time:** ~15 minutes
## In Plain Words  at most 90 words; connected explanation with a causal everyday scene
## The Problem    3 sentences, a concrete failure the reader has felt
## The Concept    diagrams first. 2+ Excalidraw diagrams and 1+ data figure, each with a one-sentence italic caption
## Build It       at most 40 lines of code in steps, then the run command
## Use It         at most 6 lines: the production library and what to compare
## Ship It        what outputs/skill-<slug>.md does
## Exercises      3 one-line exercises
```

A reader who only looks at the pictures must get the idea. Put a picture where you would otherwise write a paragraph.

The Korean section sequence is `쉽게 말하면`, `문제`, `개념`, `만들기`, `실제 도구로 보기`, `결과물`, `연습 문제`.
Both languages put the opening section directly after the title, idea and Type metadata, before the Problem.

### In Plain Words style

Write a short, connected explanation for a Senior High reader. Use familiar objects and address the reader directly where the scene calls for it. Verify the analogy against the lesson's equations, code and tests. Its force directions, changes in quantities and distinction between estimated and true state must agree with the lesson. Keep technical terms stable and explain them in everyday words. Korean uses natural spoken-polite language (~해요). Prefer 배식대의 쟁반 to 계산대. Use prose without company or product names, ASCII art, em-dash clauses, middle-dot noun chains or commas after Korean connective endings.

Apply these five rules in both languages.

1. An analogy must show the cause. Say what changes and what happens because of that change. A familiar scene alone is insufficient.
2. Explain the lesson's key mechanism before any closing question. In 08-01, explicitly show that planning and odometry use the same wrong values; the recorded route can then close while the real route does not.
3. Name the object a force acts on and its direction. Explain kp as the controller's response to a given error, rather than a vague degree of firmness.
4. Avoid dense English blocks and Korean paragraphs split after every sentence. Use two short English paragraphs when the block exceeds about 60 words. Group related Korean sentences into two or three paragraphs per block, normally two or three sentences together; do not split a connected explanation merely to isolate each sentence.
5. Do not force every lesson into the same opening order or a final question. Check English and Korean for natural flow separately. A closing question is optional and must follow an explanation that already makes sense.

| Do | Don't |
| --- | --- |
| "Your friend supports most of the tray's weight; the weight left on your arms makes them sag farther when you relax them." | "Relax your grip and gravity compensation stops the tray from sagging." |
| "A notebook records every corner as a right angle, so the drawn square closes even though your smaller turns leave you away from the start." | "A wrong stride length distorts distances." (This does not explain why the notebook can hide the error.) |
| "The showerhead pushes water away, so your hand feels a push in the opposite direction." | "A propeller's thrust points in the direction it blows air." |

The total English budget is 450 + 90 + 60 = 600 words outside fenced code, including headings and metadata. The last 60 are for one worked example with the lesson's own numbers, which may carry a clip (see Visuals).
The opening cap counts visible prose, including link labels. Korean has a mechanical ceiling of 90 whitespace-separated words and 600 characters, including spaces and paragraph breaks; match the English meaning rather than filling the ceiling.
Prefer words to equations in the opening. If a familiar number is needed for the causal scene, link it to a source or a lesson test. The 08-01 example keeps 90° / 90도 and links those labels to a verified definition of a right angle. Put detailed numeric examples and equations in the later sections.
Korean opening paragraphs may exceed the general 160-character paragraph guideline when needed to preserve a connected explanation; the block still has the 600-character ceiling. Source lines must stay within the checker's 160-character limit. A soft line break does not create a new paragraph.
Mechanical checks cannot establish that an analogy is physically correct, so reviewers must trace its causal chain.

The terminal reader shows it before the lesson hook.
Glossary terms (`scripts/glossary.json`) follow the first-mention-per-section rule; the term taught by the lesson itself still has no redundant tooltip.

### Corrected worked examples

These examples keep the lesson headings and caps. They show different ways to finish: a causal statement for 03-02 and 08-01, and a question after the explanation for 10-03.

#### 03-02 Gravity compensation

EN (79 words; 2 paragraphs).

```markdown
## In Plain Words

Gravity compensation lets a motor carry an arm's weight, much as a friend helps you carry a tray. At the cafeteria serving counter, you lift a heavy tray while your friend supports most of its weight.

Your friend's support is like gravity compensation. The position controller carries the remaining load. Its gain kp sets how strongly it pushes back for a given amount of sag. With a lower kp, the arm must sag farther to produce the same support.
```

KO (63 words; 283 characters including paragraph breaks; 3 paragraphs).

```markdown
## 쉽게 말하면

gravity compensation은 친구가 쟁반을 함께 받쳐 주듯 모터가 로봇 팔의 무게를 받치는 방법이에요.

배식대에서 친구와 무거운 쟁반을 들 때를 떠올려 보세요. 친구가 대부분 받쳐 줘도 팔에 무게가 남아서 힘을 풀수록 쟁반이 더 내려가요.

친구가 받쳐 주는 힘이 gravity compensation에 해당해요. position controller는 남은 무게를 버텨요. kp는 같은 정도로 처졌을 때 얼마나 강하게 밀어 올릴지 정해요. kp가 낮으면 같은 무게를 버티기까지 더 많이 처져요.
```

#### 08-01 Differential drive and odometry

Analogy must show the cause: before and after. The old walk-and-notebook scene described distortion but left the hidden-error mechanism to a question. The corrected scene gives the notebook an explicit wrong recording rule. The robot paragraph then maps that rule to the same incorrect geometry used in planning and odometry.

Before (EN and KO).

```markdown
## In Plain Words

Differential drive steers with unequal wheel speeds, and odometry estimates position from wheel motion. You draw your school walk in a notebook from counted steps and estimated turns. A wrong stride length distorts distances, and a misjudged turn sends the next line the wrong way. Wheel radius sets travel per rotation; wheelbase, the gap between wheels, converts travel differences into turns. If planning and odometry use the same wrong wheel radius or wheelbase, why can the map close while the robot misses the start?
```

```markdown
## 쉽게 말하면

differential drive는 양쪽 바퀴의 속도 차이로 방향을 바꾸는 방식이고 odometry는 바퀴가 움직인 거리로 위치를 추정하는 방법이에요.

학교 주변을 걸으며 걸음 수와 돈 각도를 기록해 공책에 길을 그려 보세요.

보폭을 잘못 잡으면 거리가 틀어지고 돈 각도를 잘못 잡으면 다음 선이 엉뚱한 방향으로 나가요.

wheel radius는 바퀴가 한 바퀴 돌 때 가는 거리를 정해요.

wheelbase는 양쪽 바퀴 사이의 간격으로 양쪽이 간 거리의 차이가 얼마나 큰 회전이 되는지 정해요.

경로 계획과 odometry가 똑같이 틀린 wheel radius나 wheelbase를 쓰면 지도에서는 제자리로 돌아와도 실제 로봇은 왜 출발점에 못 돌아올까요?
```

After (EN and KO). These labels link to a verified definition of a right angle; the visible wording and two-paragraph structure are verbatim from the approved review.

EN (84 words; 2 paragraphs).

```markdown
## In Plain Words

Differential drive turns a robot by running its wheels at different speeds. Imagine walking a square but turning slightly less than [90°](https://mathworld.wolfram.com/RightAngle.html) at each corner. A notebook that records every turn as [90°](https://mathworld.wolfram.com/RightAngle.html) draws a closed square, although you miss the start.

A robot can make the same mistake. Wheel radius and the distance between the wheels determine distances and turns from wheel rotations. If planning and odometry use the same wrong values, the recorded path can close while the robot misses the start.
```

KO (56 words; 248 characters including paragraph breaks; 2 paragraphs).

```markdown
## 쉽게 말하면

differential drive는 양쪽 바퀴의 속도 차이로 방향을 바꿔요.
사각형으로 걷는데 모서리마다 [90도](https://mathworld.wolfram.com/RightAngle.html)보다 조금 덜 돈다고 해 보세요.
공책에는 매번 [90도](https://mathworld.wolfram.com/RightAngle.html)로 그리면 사각형이 닫혀도 나는 출발점에 못 돌아와요.

로봇은 wheel radius와 양쪽 바퀴 사이 간격으로 이동 거리와 회전 각도를 계산해요.
계획할 때와 odometry로 이동을 기록할 때 같은 잘못된 값을 쓰면 기록상으로는 출발점에 돌아와도 실제로는 빗나갈 수 있어요.
```

#### 10-03 Quadrotor model

EN (85 words; 2 paragraphs).

```markdown
## In Plain Words

A quadrotor model predicts motion from a drone's tilt and thrust, the push it gets from its propellers. You rinse the bath with a showerhead and feel it push your hand opposite the water flow. When you tilt the showerhead, the push changes direction too.

An upright drone likewise pushes air down for upward thrust, then tilts to redirect that force. At the same total thrust, tilting reduces the upward force. How much more thrust does the drone need to stay at the same height?
```

KO (61 words; 271 characters including paragraph breaks; 3 paragraphs).

```markdown
## 쉽게 말하면

quadrotor model은 드론의 기울기와 프로펠러가 드론을 미는 힘인 thrust로 움직임을 예측하는 모델이에요.

샤워기를 손에 들고 욕조를 헹굴 때 물줄기 반대쪽으로 손이 밀리는 느낌을 떠올려 보세요. 샤워기를 기울이면 손을 미는 힘의 방향도 바뀌어요.

드론도 공기를 아래로 밀어 위로 힘을 받고 몸체를 기울여 그 힘의 방향을 바꿔요. thrust가 그대로인 상태에서 드론을 기울이면 위로 받치는 힘이 줄어들어요. 같은 높이를 유지하려면 thrust를 얼마나 늘려야 할까요?
```

### Opening-section rollout and humanizers

Strict checking is the default now: `python3 scripts/check_lessons.py` and `python3 scripts/check_lessons.py --strict` require every opening block.
While the remaining lessons are being written, use `python3 scripts/check_lessons.py --allow-missing-plain-words`.
This flag permits absent blocks only; existing blocks still have to pass every cap, evidence and order check.
Remove the rollout flag from orchestration when every bilingual lesson is complete. No code default needs changing.

Add the bilingual blocks first, then refresh only that lesson's English and Korean files in `.board/humanize-backup/phases/.../docs/` before applying humanizers.
Never refresh the entire backup tree: it is the fact and structure baseline used by `scripts/humanize_guard.py`.
Run English through humanizer-oneaway followed by no-ai-slop, and Korean through humanize-korean fast/light. Change style only; preserve concepts, examples, numbers, identifiers, technical terms and all existing lesson content. Keep explicitly approved replacement sentences verbatim; a humanizer may make no edits when they already read naturally.
Run the guard afterward. Heading checks share `scripts/lesson_sections.py` with the checker and readers.

## Visuals

Build everything with `python3 scripts/build_figures.py <lesson-name-fragment>`. It runs `diagram*.py` and `figure*.py`, then renders every `.excalidraw` to `.svg` and `.png` with the real Excalidraw renderer. Docs link the `.png`. Next to each `diagram-<name>.png` the build also writes `diagram-<name>.anim.webp`: the same picture with short dashes flowing along every arrow from start to end (12 frames, about 14 a second, endless loop, usually under 110 KB). Boxes, text and labels do not move. A web page can show it unless the visitor asked for less motion; docs keep linking the `.png`.

Diagrams use `scripts/excal.py`. You say what connects to what; `save()` lays it out for a phone (a lesson column is about 350 px wide):

```python
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram
d = Diagram()                                  # Diagram(numbered=True) adds step badges
d.title("Why a soft arm sags")
a = d.box("Model says\ngravity = ff", col=0, row=0, color="blue")   # colors: blue green yellow red purple gray; shapes: rectangle ellipse diamond
b = d.box("Residual", col=1, row=0.5, color="red")
d.arrow(a, b, label="minus")                   # feedback arrows (route="below" in old files) are routed around the boxes by the engine
d.note("check units first", near=a, side="b")  # a note hung on a box; d.note(text, x, y) is a takeaway line under the picture
d.save(OUT / "diagram-name.excalidraw")
```

- `col` and `row` say what sits left of or above what, and which boxes share a lane. They are not pixels: the engine picks left to right, top to bottom, or a snake that wraps at 3 columns, whichever reads best, sizes the boxes to the text, and keeps the smallest text at about 12 px when the PNG is shown 350 px wide (the test requires 11). Do not set `w`, `h`, `size`, `dx` or `dy`; they are ignored.
- Arrows are straight orthogonal segments in a clear lane. They never cross a box or text. Both ends touch the shape's outline: a lone arrow meets the middle of a side, several arrows on one side are spread evenly and symmetrically about the middle, and two boxes level with each other (same row or column) are joined by one straight arrow through both middles. Bends leave and enter at right angles. A label sits in the middle of a straight stretch of its own arrow with a white background, so keep labels to a few words.
- `Diagram(numbered=True)` puts a number badge on each box in reading order (left to right by `col`, then by `row`). Use `box(..., step=n)` to set a number by hand. Use it when order matters, such as a procedure.
- `note(text, near=box, side="r"|"b"|"l"|"t")` puts a short note beside a box with a thin leader. The engine moves it to another side if that side is crowded or would widen the picture.
- At most 3 columns across and 8 boxes. Fonts are Nunito, 26 px in boxes and 24 px in labels and notes. Check the report in `d.warnings` after `save()`: it lists a label or note that found no clear spot.
- At most 2 lines per box and short words; the engine wraps longer text, but a word wider than about 200 px (for example `Counterexample`) forces wide boxes. Colour carries meaning: blue input, yellow real world, red problem, purple transform, green result, gray neutral.
- Data figures (matplotlib, Agg backend): 1200x675 px or smaller, English labels only, axis names with units, a title that states the takeaway, colour-blind-safe colours (`#0072B2` blue, `#D55E00` orange, `#555555` gray), seeded, no external data.
- Captions live in each language's doc, so one image serves every language.
- Every lesson has one 3D scene, which lives in the separate website repo. `fun.json` names it (`"three": "<name>-3d"`); this repo does not check the name.
- Every lesson has a lead clip. `code/clip.py` builds a small Blender scene from `scripts/blender/kit.py` (a toy car, a bench arm, a rover, a drone) and keys it with arrays from `kit.lesson_main(__file__)`, so what moves is what `code/main.py` computes. No text in the picture, 4 to 6 seconds, blue for the plain or failing case and green for the fixed one. Its caption is `clip` under `en` and `ko` in `fun.json`. A worked example may have its own clip, `code/clip-example.py`, linked in both docs as `![alt](../assets/clip-example.mp4)` with the usual italic caption line; the terminal reader shows its poster. Render with `python3 scripts/build_clips.py <lesson fragment>` (Blender 5 and ffmpeg on PATH; `CLIP_LOOK=real` for the ray-traced look; `--still N` for one frame). Commit the `.mp4` and `.jpg`.
- Look at every PNG with the Read tool before reporting. Check clipped or overlapping text, crossing arrows, and whether the picture shows what the caption claims. Fix and rebuild.

## Content rules

- A number is derived in the lesson and tested, or it carries a source link found by a live search that day. No remembered vendor specs, prices or version claims.
- Lessons are simulation-only. No command that addresses a real motor ID or bus. No named company, robot product or vendor in the text.
- Original text and code. Do not copy from other courses or repos.
- Plain words first, then the term. Terminology stays English in every language.

## Korean (ko.md)

- Same headings, same number and order of code blocks and images as en.md. Images, code and tests are shared; only prose, captions and quiz text are translated. Code comments stay English.
- Polite style (`~합니다`; the opening uses spoken-polite `~해요`), terms in English, particles attached (`PID를`, `kp가`).
- Keep Korean prose plain: no `—` joining clauses, no middle-dot chains of nouns in prose, no comma after a connective ending, no sentence ending in a colon, at most one bold per paragraph, no paragraph over 160 characters.

## Checks

```bash
cd robotics-engineering-from-scratch
python3 scripts/build_figures.py          # all lessons, or pass a name fragment
python3 scripts/check_lessons.py
python3 -m pytest phases -q
```
