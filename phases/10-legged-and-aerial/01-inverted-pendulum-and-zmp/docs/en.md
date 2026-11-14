# Inverted Pendulum and ZMP

> A standing body falls like a balanced pencil, and the capture point tells you where the next foot must land.

**Type:** Build   **Prerequisites:** 03/04 PID and Tuning   **Time:** ~15 minutes

## In Plain Words

Someone shoves you from behind. Your body starts moving forward, and you can lean on your toes to hold yourself up. That works only for a small shove, because the spot where the floor pushes up (ZMP) can move only as far as your foot is long.

A bigger shove carries your body farther before it would stop. That stopping spot, the capture point, lies beyond your toes. Leaning cannot reach it, but a foot placed there stops you.

## The Problem

A walking robot is shoved from behind and its ankles push back hard, yet it keeps tipping forward. They only shift where the ground pushes inside the foot, so a big shove beats them. You need a model that says early whether a step is needed, and where.

## The Concept

![From a leg to one time constant](../assets/diagram-lipm-flow.png)

*Treat the body as one mass at height `h` on a massless leg, like a pencil on its tip. Its tipping speed becomes one number, `Tc`.*

`x` is the body's distance ahead of the ankle and `g` gravity. With the foot at `p`, the mass obeys `x'' = (g/h)(x - p)`: the farther the body is ahead of the foot, the harder gravity pulls it on (`x''` is its acceleration). Try `exp(t/Tc)`: its second derivative is `exp(t/Tc)/Tc^2`, so `1/Tc^2 = g/h`. For `h = 0.9 m`, `Tc = sqrt(h/g)` is about 0.30 s, and the tipping grows 2.7 times (e) every `Tc`.

Solved for `p`, it gives the zero-moment point (ZMP), where the ground's push acts under the foot: `p = x - (h/g) x''`. It cannot leave the foot, because the ground can only push. The capture point is the body's position plus its speed times `Tc`: `xi = x + v Tc`. It moves at `xi' = (xi - p)/Tc` (`xi'` is its speed), so a foot placed on `xi` freezes it and the body stops over that foot.

Example: a 10 cm foot lets the ground's push sit at most 0.05 m from the ankle. A shove gives the body `v = 0.4 m/s`, so `xi = 0.4 * 0.30 = 0.12 m`, beyond 0.05 m: the ankle alone fails. A shove of 0.1 m/s gives `xi = 0.03 m`, inside the foot, so the ankle holds.

![Two shoves, ankle only](../assets/clip-example.mp4)

*Purple post: the capture point. Grey posts: the ends of the foot (both drawn 3 times farther from the ankle). Green, 0.1 m/s: the purple post stays between them. Blue, 0.4 m/s: it leaves and the body topples.*

![Ankle torque or a step](../assets/diagram-capture-decision.png)

*Inside the foot the ankle can hold; outside, only a step helps.*

![A fall and a recovery from the same push](../assets/fig-fall-and-recovery.png)

*Ankle only: the body diverges. Waiting 0.1 s moves `xi` on to 0.15 m, so a step there stops the body at 0.15 m.*

## Build It

```python
def lipm_state(x0, v0, p, t, h, g=G):
    tc, a = time_constant(h, g), x0 - p
    c, s = np.cosh(t / tc), np.sinh(t / tc)
    return p + a * c + tc * v0 * s, a * s / tc + v0 * c

def capture_point(x, v, h, g=G):
    return x + v * time_constant(h, g)
```

`simulate()` steps the equation forward in time (RK4). `fall_or_recover()` clamps the ZMP to the foot and optionally steps.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp -q
python3 phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/code/main.py
```

## Use It

The last test checks `lipm_state` against SciPy's `solve_ivp`.

## Ship It

`outputs/skill-capture-point-check.md` reviews balance code for the ZMP, capture-point and step logic.

## Exercises

1. Raise `h` to 1.8 m; find the largest push the ankle alone absorbs.
2. Delay the step by 0.3 s; where must the foot land?
3. Add a foot width of 0.1 m; show the step target moves.
