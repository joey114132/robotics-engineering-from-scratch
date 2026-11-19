# Contributing

Fork it, change it, run the checks, open a pull request. Small fixes (a typo, a wrong number, a clearer sentence) are as welcome as new lessons.

## Fork and run

```bash
git clone https://github.com/<you>/robotics-engineering-from-scratch
cd robotics-engineering-from-scratch
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 scripts/check_lessons.py
python3 -m pytest phases scripts/tests_robo -q
python3 scripts/robo.py        # read the course in the terminal
```

Nothing more is needed to read lessons, edit text, code or tests, or run a lesson's `code/main.py`: the rendered figures and clips are committed. On Windows, set `PYTHONUTF8=1` first, because the scripts read Korean text as UTF-8.

## Rebuilding figures and clips (only if you change one)

- **Figures** (`python3 scripts/build_figures.py <lesson fragment>`) run each lesson's `code/diagram*.py` and `code/figure*.py`, then render the Excalidraw files in a headless browser. That needs Node, `puppeteer` installed globally (`npm install -g puppeteer`), network access (the renderer loads Excalidraw from esm.sh) and Linux or macOS, because the script takes a file lock with `fcntl`.
- **Clips** (`python3 scripts/build_clips.py <lesson fragment>`) need Blender 5 and ffmpeg on your PATH, and also Linux or macOS. Commit the resulting `.mp4` and `.jpg`.

The same two checks run on every push through GitHub Actions, so your fork tells you if something broke.

## Ways to help

- **Fix a lesson.** Edit `phases/<phase>/<lesson>/docs/en.md` and `ko.md`. Keep the headings, code blocks and images the same in both languages.
- **Add a lesson.** Read [LESSON_SPEC.md](LESSON_SPEC.md) first: one folder per lesson, diagrams drawn with `scripts/excal.py`, a data figure, `code/main.py`, five or more tests written first, a six-question quiz, and a reusable `outputs/skill-*.md`.
- **Improve the Korean.** The Korean text was drafted and checked with tooling, not by a native editor. Plain corrections are the most useful contribution.
- **Translate.** Lessons accept `docs/<code>.md` files. `robo` currently switches between English and Korean only, so a third language needs a change in `scripts/robo/` as well. Open an issue first and we will plan it together.

## Rules that keep the course honest

- A number in a lesson is derived in the lesson (and tested) or carries a source link you opened. No remembered vendor specs or version claims.
- Original text and code. Do not copy from other courses or repositories.
- Lessons are simulation-only. No command that addresses a real motor or bus, and no company or robot product names.
- Look at every figure you generate before you open the pull request.

By contributing you agree your work is released under the repository's MIT license.
