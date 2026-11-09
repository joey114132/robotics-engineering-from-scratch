# Robotics Engineering from Scratch

Build the math and control behind a robot arm from raw numpy, test it, then see what the production library does. Every lesson ends with a skill you can reuse.

Modelled on the lesson shape of [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) (MIT). The text and code here are original.

Scope: robotics in general. Manipulators, wheeled and legged robots, aerial vehicles, perception, planning, learning, fleets and safety.

Status: 67 lessons in 17 phases, English and Korean. Every lesson has diagrams drawn in Excalidraw, a data figure, runnable code with tests, a six-question quiz and a reusable checklist skill. The lesson list is in [ROADMAP.md](ROADMAP.md).

## Read it as a website

```bash
cd robotics-engineering-from-scratch
python3 scripts/build_site.py
xdg-open site/index.html
```

The site has an English and Korean toggle, a dark mode, and a clickable quiz at the end of every lesson.

## Run the code

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases -q
python3 scripts/check_lessons.py
python3 scripts/build_figures.py
```

`build_figures.py` rebuilds every diagram and figure. Lessons are simulation-only and none sends a command to real hardware. The lesson format is in [LESSON_SPEC.md](LESSON_SPEC.md).

## Read it in the terminal

`robo` is a terminal reader and tutor (needs `rich`; `Pillow` draws figures).

```bash
cd robotics-engineering-from-scratch
python3 scripts/robo.py              # home: XP, level, phases, next lesson
python3 scripts/robo.py read 03-02   # the lesson, with figures and Bolt's hook
python3 scripts/robo.py quiz 03-02   # game-style quiz round (+10 XP per right answer)
python3 scripts/robo.py daily        # Daily 5 review (+5 XP each, 25 XP a day)
python3 scripts/robo.py play pd-step --kp 30 --kd 4
python3 scripts/robo.py sync export  # move progress to the website and back
```

Add `--lang ko`, `--plain` (no colour, for pipes) or `--no-pager`. Progress is a JSON file under `$XDG_STATE_HOME/robotics-course/`; the website keeps the same data in your browser and the two exchange it with a progress code (home page, "Take your progress along").

## One-file build

`python3 scripts/build_single.py` bundles all 67 lessons into `site-single/robotics-from-scratch.html` (images as WebP), for phones or sharing. Tests: `python3 -m pytest phases scripts/tests_robo -q`.

## Offline use and known limits

The multi-page site registers a service worker on http(s) and caches pages and figures on the reader's device (Clear local data is in the sync panel). Nothing leaves the device. The one-file bundle and the shared Artifact cannot register a worker, so they rely on the browser cache only. Known limits: two `robo` quiz processes running at the same moment can undercount XP (the last save wins on XP, answers are merged); the service worker handles one offline pack download at a time; terminals narrower than 60 columns may wrap.


## License and credits

MIT, see [LICENSE](LICENSE). The lesson shape follows rohitg00/ai-engineering-from-scratch (MIT); the text, code and figures here are original. The site's animations use GSAP 3.15.0 (`scripts/vendor/gsap.min.js`), which keeps its own terms in `scripts/vendor/GSAP-LICENSE.txt`. The Korean text was drafted and checked with tooling and has not been reviewed by a native editor, so corrections are welcome.
