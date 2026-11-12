# Bolt 3D

## Contract and choices

Bolt is a small hover toy with a pearl shell, cyan trim and a dark glass face.
The head is about 60% of the head/body/pad silhouette; the antenna sits outside
that measurement. The short mitten arms have no fingers. Rosy cheek panels and an
amber lightning bulb keep the face readable without adding emoji.

Colors come from `/tmp/rfs-cx/cx3/scripts/build_site.py`: pearl `#f2f6f7`,
ink `#0e1a1f`, icon cyan `#41c8e6`, and amber `#ffb454`. Teal shading and rose
cheeks are material accents. Bolt keeps this palette across phase hues and themes.
A pale rim separates the visor and shell from dark backgrounds. Light ground
gets a soft dark shadow; dark ground gets a cyan contact halo (`#66b9ca40` fading
to transparent). Both stay at the fixed ground position and narrow during a hop.
An explicit page theme overrides the system color preference.

The implementation is `/tmp/rfs-cx/cx3/scripts/mascot3d.js`. It uses Canvas 2D
and its own perspective math. Ellipsoids are projected from rotated 3D bases,
lit with gradients, and sorted from back to front. The visor and its LEDs paint
as one clipped composite, with the LEDs above the glass. Rounded outlines sample
the head surface along straight edges as well as corners, at intervals no longer
than .06 model units. Facial parts never sort independently.
There is no dependency on M3D, GSAP, fonts or network data.
Analytic volumes were chosen over a triangle mesh to keep small instances cheap.
This is a miniature 3D character renderer, not a general mesh engine.

## Motion

The personality is Playful. Primary motion is the pose; the antenna and mittens
follow through; breathing and hover supply ambient motion. A hop lasts 900 ms:
120 ms of anticipation (deepest squash at 60 ms), an apex at 360 ms, landing at
600 ms, then a damped settle.
Squash/stretch preserves approximate volume. Drag release and antenna follow-through
use damped springs. Mood poses ease in over 240 ms rather than snapping.

| Mood | Pose and secondary motion |
| --- | --- |
| idle | Open LED eyes, breathing, small hover bob; random blink interval 3–5 s |
| cheer | Both mittens raised, curved happy eyes, one hop and a short spark burst |
| oops | Brief head shake, spiral eyes, three overlapping matte smoke puffs |
| sleepy | Drooping lids, lowered mittens, slow bob, floating letter z |
| wave | One raised mitten waves hello; the other stays beside the body |
| think | Head tilts, one mitten at the cheek, three thinking dots |

Cheer advances each mitten from Z `.16` by `.42 * cheer`, including its thumb.
A short rounded connector joins each shoulder to its mitten. Near mittens paint
over the cheek volumes. Cheer uses four upper-half spark anchors, with
`a = i * Math.PI / 3`, `x = 1.32 * Math.cos(a)`, `y = .34 + .82 * Math.sin(a)`
and Z `.1`. The original `.18` spark font scale and `.8` s burst stay intact.
The proposed X radius `1.02` overlapped the face at extreme yaw, so the anchors
move outward instead of reducing the effect. The original sheet's top crop did
not establish canvas clipping.

Face strokes have a `1.1` CSS px minimum; glyph fonts have an `8` CSS px minimum.
Sleepy z opacity stays at or above `.7`, with `#78d8e4` on dark ground and
`#27768a` on light ground. Smoke uses three plain translucent fills without rim
strokes, material gradients or specular marks. Successive puffs grow and fade
upward; each also expands, rises and fades through the `1.4` s reaction.

`window.BOLT3D.mount(el, {mood: 'idle', size: 88, interactive: true})`
returns `{setMood(name, holdMs), destroy()}`. Mounting twice returns the existing
handle. Unknown moods normalize to idle. A positive hold restores the previous
mood after that many visible milliseconds; another mood request cancels the hold.
Reduced motion uses a cancellable one-shot hold timer, paused while hidden.
`el.dataset.mood = 'cheer'` remains supported. Repeating setMood restarts
the reaction. Reduced motion keeps mood expressions but always uses the rest pose.

Auto-mount uses `[data-bolt3d]`, with optional `data-size` and `data-interactive`.
The page builder uses 88 px for the home hero and lesson hooks, 96 px for quiz
results. The header (36 px), quiz HUD (58 px) and path marker (46 px) retain SVG.
The SVG shares the toy's silhouette, visor, cheek panels and lightning bulb.

## Lifetime and input

One IntersectionObserver gates canvas creation and visibility. One shared
requestAnimationFrame loop advances only visible instances while the tab is open.
DPR is capped at 2. Hidden time does not advance holds, blinks or reactions.
Reduced motion creates one static frame on entry and repaints only for a discrete
mood, language, theme or size change; it schedules no animation frames.
The shared DOM observer mounts new quiz results and removes detached instances.
Single-file navigation explicitly mounts and disposes lesson instances too.

The host has a localized image label, no tabindex and no keyboard handler.
Pointer/touch gaze is optional. A horizontal drag turns the whole toy up to
about 41 degrees; inertia springs back to the front. `touch-action: pan-y`
preserves vertical scrolling. Pointer capture starts only after a horizontal
gesture wins a 6 px threshold. A tap starts the happy hop. Vertical gestures and
cancelled drags do not trigger a hop.

## Acceptance and limits

Tests precede implementation in `/tmp/rfs-cx/cx3/scripts/tests_robo/test_mascot3d.py`.
They execute the actual script in Node with DOM/Canvas command doubles. They check
API behavior, finite drawing commands, cleanup, visibility, reduced motion, input,
the 20,000-byte budget, offline source and builder integration. Regressions cover
each of the six visual-review repairs at drawing-command or coordinate level.
The spark sweep covers yaw -41 through +41 degrees in .5-degree steps and the
burst every 16 ms, including hop squash and lift, at 88 and 220 CSS px. A
conservative glyph box extends .6 em in each direction; it must remain inside
the canvas and outside the projected visor's bounding box, which includes the
mouth. This checks more than glyph anchor points alone. Reduced-motion repaints
compare complete paint commands at 0 and 5000 ms for all six moods, both sizes
and both themes. Pixel appearance
and real browser gestures cannot be established by these tests.

Run `python3 -m pytest scripts/tests_robo`, `python3 scripts/check_lessons.py`,
`python3 scripts/humanize_guard.py`, and build with
`SITE_OUT=/tmp/rfs-cx/site-mascot python3 scripts/build_site.py`, then run the
single-file builder with the same environment variable.

The target is at most 16 ms per frame at 4x CPU throttle. Rendering and browser
profiling are unavailable in this sandbox, so that target and visual appeal remain
unverified. The original screenshot matrix is in `/tmp/rfs-cx/mascot-report.md`;
repair evidence and remaining limits are in `/tmp/rfs-cx/mascot-fix-report.md`.
No commit or publication is part of this change.
