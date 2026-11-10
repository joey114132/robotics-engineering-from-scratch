# Contributing

Fork it, change it, run the checks, open a pull request. Small fixes (a typo, a wrong number, a clearer sentence) are as welcome as new lessons.

## Fork and run

```bash
git clone https://github.com/<you>/robotics-engineering-from-scratch
cd robotics-engineering-from-scratch
pip install -r requirements.txt
python scripts/check_lessons.py
python -m pytest phases scripts/tests_robo -q
python scripts/build_site.py && xdg-open site/index.html
```

The same two checks run on every push through GitHub Actions, so your fork tells you if something broke. To put your fork's site online, set Settings > Pages > Source to "GitHub Actions" and run the `site` workflow by hand.

## Ways to help

- **Fix a lesson.** Edit `phases/<phase>/<lesson>/docs/en.md` and `ko.md`. Keep the headings, code blocks and images the same in both languages.
- **Add a lesson.** Read [LESSON_SPEC.md](LESSON_SPEC.md) first: one folder per lesson, diagrams drawn with `scripts/excal.py`, a data figure, `code/main.py`, five or more tests written first, a six-question quiz, and a reusable `outputs/skill-*.md`.
- **Improve the Korean.** The Korean text was drafted and checked with tooling, not by a native editor. Plain corrections are the most useful contribution.
- **Translate.** Lessons accept `docs/<code>.md` files. The website and `robo` currently switch between English and Korean only, so a third language needs a change in `scripts/build_site.py` as well. Open an issue first and we will plan it together.

## Rules that keep the course honest

- A number in a lesson is derived in the lesson (and tested) or carries a source link you opened. No remembered vendor specs or version claims.
- Original text and code. Do not copy from other courses or repositories.
- Lessons are simulation-only. No command that addresses a real motor or bus, and no company or robot product names.
- Look at every figure you generate before you open the pull request.

By contributing you agree your work is released under the repository's MIT license.
