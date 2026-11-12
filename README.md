# Robotics Engineering from Scratch

Learn how robots work by building the math and control yourself, in plain numpy, with tests. Then see what the production library does.

81 lessons, 17 phases, English and Korean. Arms, wheeled and legged robots, drones, perception, planning, learning, fleets and safety. About 15 minutes each. The full list is in [ROADMAP.md](ROADMAP.md).

![Learning path: six stages from setup and math to fleets, safety and capstones](docs/img/roadmap.png)

## What a lesson gives you

- A short "In Plain Words" opening in everyday terms, before any math
- An animation, and for some lessons a toy you can drag or a 3D scene you can orbit (25 lessons so far)
- Diagrams and data figures
- Code that runs, with tests
- A six-question quiz and a one-page checklist you can reuse

Every lesson is simulation only. Nothing sends a command to real hardware.

<table>
<tr>
<td width="50%"><img src="docs/img/motion-scene.gif" alt="A damped pendulum arm settling while its angle trace shrinks into the target band"></td>
<td width="50%"><img src="docs/img/motion-singularity.gif" alt="A two-link arm stretching out while the plain inverse joint speed blows up and the damped one stays bounded"></td>
</tr>
<tr>
<td><em>Phase 3 opener: a damped swing settles.</em></td>
<td><em>Lesson 02-04: near full stretch the plain inverse blows up, damped least squares stays bounded.</em></td>
</tr>
</table>

<table>
<tr>
<td width="25%"><img src="docs/img/index-phone.png" alt="The course home page on a phone: Start button, mascot, level and XP"></td>
<td width="25%"><img src="docs/img/03-02-gravity-compensation-phone.png" alt="A lesson on a phone: data figures with captions, then the Build It code"></td>
<td width="50%"><img src="docs/img/cli-home.png" alt="The robo terminal home screen listing the 17 phases and the next lesson"></td>
</tr>
<tr>
<td><em>Website home on a phone.</em></td>
<td><em>Figures first, then a few lines of code.</em></td>
<td><em><code>robo</code> in the terminal, same lessons and progress.</em></td>
</tr>
</table>

## Start

```bash
cd robotics-engineering-from-scratch
python3 scripts/build_site.py      # build the website
xdg-open site/index.html           # read it (English/Korean, dark mode, quizzes)
python3 scripts/robo.py            # or read in the terminal (needs rich)
```

In the terminal, `robo read 03-02` opens a lesson, `robo quiz 03-02` runs a quiz and `robo daily` is a five-question review. Add `--lang ko` for Korean. Progress carries between the terminal and the website with a progress code on the home page.

## Check the code

```bash
python3 -m pytest phases scripts/tests_robo -q
python3 scripts/check_lessons.py
```

`python3 scripts/build_single.py` bundles everything into one file, `site-single/robotics-from-scratch.html`, for a phone or for sharing. The lesson format is in [LESSON_SPEC.md](LESSON_SPEC.md).

## Limits

- The Korean text was drafted and checked with tooling. No native editor has reviewed it, so corrections are welcome.
- The site caches pages for offline use through a service worker. The one-file bundle cannot, so it relies on the browser cache.
- Two `robo` quiz processes at the same moment can undercount XP.

## Contribute

Forks and pull requests are welcome, from a typo to a whole new lesson. Run the two checks above and see [CONTRIBUTING.md](CONTRIBUTING.md).

## License and credits

MIT, see [LICENSE](LICENSE). The lesson shape follows [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) (MIT). The text, code and figures here are original. The animations use GSAP 3.15.0, which keeps its own terms in `scripts/vendor/GSAP-LICENSE.txt`.

To regenerate the pictures above, run `python3 scripts/readme_roadmap.py`, `node scripts/render_excalidraw.cjs docs/img/roadmap.excalidraw` and `node scripts/readme_shots.cjs site|cli|gif` after building the site.
