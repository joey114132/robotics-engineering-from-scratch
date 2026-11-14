# AI-generated pictures

Made on 2026-11-12 with Higgsfield, using the Bolt mascot as a reference image (a screenshot of the 3D Bolt on the course home page). Nothing from the lessons was sent.

| Picture | Model | Notes |
|---|---|---|
| `hero-bolt.jpg` | Nano Banana 2, 16:9, 2k | Bolt in a toy robotics workshop; left third left empty for a title |
| `hero-bolt.webp` | Seedance 2.0, 1080p, 5 s | Image-to-video from `hero-bolt.jpg`; slow push-in, arm lifts a hex nut, Bolt waves. Cropped to the right 84%, scaled to 840 px, 12 fps, played forward then in reverse so the loop has no jump (ffmpeg, animated WebP). The README shows `hero-bolt.jpg` where WebP is not supported |
| `phases/00.jpg` to `16.jpg` | Nano Banana 2, 4:3, 2k | One cover per phase; 02, 08 and 12 were regenerated once |
| `social-card.png` | none | `hero-bolt.jpg` with the title set in HTML, so the text is real text |
| `phases-gallery.jpg` | none | The 17 covers laid out with captions in HTML |

Style sentence used for every phase cover:

> 3D toy render in the same style as the reference mascot Bolt (pearl-white shell, dark glass visor face with two cyan eyes, cyan trim, amber lightning-bolt antenna, short mitten arms). Bolt appears small in one corner as a friendly helper. Soft studio light, pastel pearl, cyan and warm amber palette, clean light background, shallow depth of field, one clear idea, centered subject, empty margin on the sides. No text, no letters, no numbers, no logos, no brand names.

Scene sentence per phase (placed before the style sentence):

| Phase | Scene |
|---|---|
| 00 | A tidy laptop with a terminal-like glowing screen, a toolbox and a small wrench on a clean desk, a tiny python-snake-shaped cable. |
| 01 | Three colorful glass coordinate axes floating, with a small cube rotating around them and a translucent rotated copy of the cube. |
| 02 | A glossy two-link robot arm made only of smooth tubes with plain round joints, reaching toward a small orange target sphere, with a faint circular reach range on the floor. |
| 03 | A robot arm holding a weight steady, with a small spring and a dial gauge beside it, soft glowing arcs showing the holding torque. |
| 04 | A small electric motor connected to a gearbox with visible gears and a round encoder disc with fine tick marks. |
| 05 | Several soft rounded node bubbles connected by glowing lines with tiny message envelopes traveling along them. |
| 06 | A toy camera looking at a checkerboard calibration pattern, with thin light rays from the camera to the board and a small point cloud nearby. |
| 07 | A cloud of noisy dots with a smooth glowing line passing through them, and a soft uncertainty ellipse. |
| 08 | A small wheeled robot with a spinning lidar on top driving on a floor grid, with a dotted path behind it. |
| 09 | A robot arm moving around a block obstacle along a smooth glowing path, with a branching tree of light lines on the floor. |
| 10 | A small two-legged walker robot taking a step beside a hovering quadrotor drone, with a footstep marker on the floor. |
| 11 | A two-finger gripper gently holding a small cube, and a peg about to slide into a hole in a block, with tiny force arrows. |
| 12 | A real small robot arm on the left and its translucent glowing blue digital twin on the right, linked by a thin bridge of light. |
| 13 | A small robot watching a floating screen, with a few stacked neural-network layers drawn as translucent glass slabs. |
| 14 | Six small identical wheeled robots in a neat flock formation on a floor, connected by thin light links. |
| 15 | A robot arm inside a soft glowing protective bubble, with a red emergency-stop button and a small shield. |
| 16 | A finished little robot built from many parts, standing on a podium with a small golden trophy, pastel confetti. |

## Phase opening clips

`phases/NN-*/opener.mp4` (and the poster `opener.jpg`) were made on 2026-11-13 with Higgsfield Kling 3.0 Turbo, image-to-video, 5 s, one per phase, each starting from that phase's cover above. They were scaled to 640 x 476 at 24 fps with ffmpeg (about 1.0 MB for all 17). The website plays one on the first lesson of each phase.

## What is not AI-generated

The lesson clips (`phases/*/*/assets/clip*.mp4`) are Blender renders from `code/clip*.py`, driven by the lesson's own `code/main.py` (see `scripts/blender/kit.py` and `scripts/build_clips.py`). Their look, including the "real" look with textures and the room, is made inside Blender. `scripts/restyle_clips.py` can restyle a clip with an AI video model, which writes a separate `*.real.mp4`; no such file ships with the course today.

The pictures and opening clips were checked by eye only. A Codex visual check is still pending.
