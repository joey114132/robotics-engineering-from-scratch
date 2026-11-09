# CLAUDE.md — Robotics Engineering from Scratch

Robotics counterpart of rohitg00/ai-engineering-from-scratch (MIT). Same spine: every lesson has a "Build It" (raw math, stdlib + numpy) and a "Use It" (the production library), and ships one reusable artifact.

## Layout

```text
phases/NN-slug/NN-lesson-slug/
  docs/en.md        lesson (Problem, Concept, Build It, Use It, Ship It, Exercises)
  code/main.py      from-scratch implementation, one-line header comment
  code/tests/       pytest, 5+ tests, red first
  quiz.json         6 questions: 1 pre, 3 check, 2 post
  outputs/skill-*.md  reusable artifact
ROADMAP.md          phase and lesson status (source of truth for what exists)
scripts/check_lessons.py   structure + quiz + code-fence checks
```

## Commands

```bash
cd robotics-engineering-from-scratch
python3 scripts/check_lessons.py          # structure check, exit 1 on any violation
python3 -m pytest phases -q               # all lesson tests
```

## Rules

- No ASCII diagrams; Mermaid or tables. Every fenced block has a language tag.
- A number in a lesson is either derived in the lesson (and tested) or carries a source. No remembered vendor specs, no version claims without a check.
- Original implementations only. Do not copy lesson text or code from the upstream repo.
- Hardware commands in lessons are simulation-only. Never add a command that addresses a real motor ID or bus.
- No commit or push unless the user asks.
