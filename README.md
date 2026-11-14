# Robotics Engineering from Scratch

<picture>
  <source srcset="docs/img/hero-bolt.webp" type="image/webp">
  <img src="docs/img/hero-bolt.jpg" alt="Bolt, the course mascot, waves in a toy robotics workshop while a small arm lifts a hex nut and a drone drifts past">
</picture>

Learn how robots work by building the math and control yourself, in plain numpy, with tests. Then see what the production library does.

81 lessons, 17 phases, English and Korean. Arms, wheeled and legged robots, drones, perception, planning, learning, fleets and safety. About 15 minutes each. The full list is in [ROADMAP.md](ROADMAP.md).

![Learning path: six stages from setup and math to fleets, safety and capstones](docs/img/roadmap.png)

<details>
<summary>See all 17 phases</summary>

![The 17 phases as toy-render covers: setup, math, kinematics, dynamics and control, actuators, software, perception, estimation, mobile robots, planning, legged and aerial, contact, simulation, learning, swarms, safety and capstones](docs/img/phases-gallery.jpg)

</details>

## What a lesson gives you

- A short "In Plain Words" opening in everyday terms, before any math
- A short rendered clip of a real object (a toy car, a bench arm, a rover, a drone) that acts out the lesson, computed by the lesson's own code
- Diagrams and data figures
- Code that runs, with tests
- A six-question quiz and a one-page checklist you can reuse

Every lesson is simulation only. Nothing sends a command to real hardware.

## Clips

Each lesson opens with a short clip rendered in Blender. The motion comes from the lesson's `code/main.py`, so what you see is the lesson's result, not an illustration of it. Blue is the plain or failing case, green the fixed one. Many lessons have a second clip next to their worked example.

<table>
<tr>
<td width="50%"><img src="docs/img/clip-pid.gif" alt="Two toy cars drive to a stop line with the same PID; the blue one rolls past the line, the green one with anti-windup settles near it"></td>
<td width="50%"><img src="docs/img/clip-quadrotor.gif" alt="Two quadrotors: the blue one gets more thrust and only climbs, the green one gets a small pitch torque, tilts first and then moves sideways"></td>
</tr>
<tr>
<td><em>Lesson 03-04: integral windup, and the clamp that fixes it.</em></td>
<td><em>Lesson 10-03: a drone must tilt before it can move sideways.</em></td>
</tr>
</table>

## In the terminal

![The robo terminal home screen listing the 17 phases and the next lesson](docs/img/cli-home.png)

*`robo` in the terminal: lessons, quizzes, clip posters and your progress.*

## Start

```bash
cd robotics-engineering-from-scratch
pip install -r requirements.txt
python3 scripts/robo.py            # read in the terminal (needs rich)
```

In the terminal, `robo read 03-02` opens a lesson, `robo quiz 03-02` runs a quiz and `robo daily` is a five-question review. Add `--lang ko` for Korean.

## Check the code

```bash
python3 -m pytest phases scripts/tests_robo -q
python3 scripts/check_lessons.py
```

The lesson format is in [LESSON_SPEC.md](LESSON_SPEC.md).

## Limits

- The Korean text was drafted and checked with tooling. No native editor has reviewed it, so corrections are welcome.
- Two `robo` quiz processes at the same moment can undercount XP.

## Contribute

Forks and pull requests are welcome, from a typo to a whole new lesson. Run the two checks above and see [CONTRIBUTING.md](CONTRIBUTING.md).

## License and credits

MIT, see [LICENSE](LICENSE). The lesson shape follows [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) (MIT). The text, code and figures here are original. The banner, the 17 phase covers, the social card background and the Bolt animation are AI-generated (Higgsfield), from the Bolt mascot. Models and prompts are in [docs/img/AI-ART.md](docs/img/AI-ART.md). The lesson figures are drawn in code, not generated.

To regenerate the pictures above, run `python3 scripts/readme_roadmap.py`, `node scripts/render_excalidraw.cjs docs/img/roadmap.excalidraw` and `node scripts/readme_shots.cjs cli`.
