# What a Simulator Approximates

> A simulator is the real joint with some effects deleted, and you can measure what each deletion costs.

**Type:** Build   **Prerequisites:** 03/02 Gravity Compensation   **Time:** ~15 minutes

## In Plain Words

Picture a metal arm hanging from a motor on a wall. You send the same pushes to the real arm and to a simulator that leaves out some real effects. The real hinge rubs, so every swing loses energy and shrinks. Without friction, the simulated arm swings farther.

Two quieter effects matter. The motor needs a moment to build its push, and the angle sensor reports where the arm just was. This lesson removes one effect at a time and measures which omission matters most.

## The Problem

A trajectory looks perfect in simulation, yet the real joint undershoots it, lags behind and stops short. Nobody changed the command. The simulator quietly left out things the hardware does, and you do not know which matters most.

## The Concept

![Real path and sim path](../assets/diagram-real-vs-sim.png)

*The real command (a torque, the motor's twisting push) passes through motor lag, a joint with friction and a delayed sensor. The simple sim skips three of those steps.*

One small plant (the thing controlled) serves the phase: a pendulum joint. Its parts are inertia `J` (hard to speed up), viscous damping `b` (drag that grows with speed), Coulomb friction `c` (a constant rub), gravity `k = m*g*l` (mass, g, arm length), a first-order motor lag `Tm` (torque follows the command slowly) and a sensor delay.

![Replay the same commands](../assets/diagram-replay-rank.png)

*Open-loop commands (no feedback) cannot correct themselves, so every difference between the plants shows up as divergence.*

![Trajectories, error, cost](../assets/fig-divergence.png)

*Top: the two trajectories separate. Bottom left: the error without friction swings up to 1 rad while lag and delay stay under 0.1 rad. Bottom right: RMS error (a typical gap, in radians) is 0.545 rad without friction, 0.042 rad without lag and 0.029 rad without delay.*

On the clip's 0.4 m arm, 0.545 rad (1 rad is about 57 degrees) is 31 degrees, a fingertip 22 cm off. Lag's 0.042 rad and delay's 0.029 rad are 2.4 and 1.7 degrees, 1 to 2 cm. Friction costs 13 times more than lag, so model it first.

![Three arms, one effect each](../assets/clip-example.mp4)

*Watch the ghosts. Blue is the real arm; each ghost misses one effect: friction, motor lag, sensor delay, left to right. Only the left ghost visibly separates.*

## Build It

Integrate `J*w' = tm - b*w - c*tanh(w/eps) - k*sin(q)` and `Tm*tm' = u - tm` with RK4. The measured angle is the true angle shifted by `delay`.

```python
def measured(p, u_fn, T):
    q, n = simulate(p, u_fn, T)[:, 0], round(p["delay"] / DT)
    return np.concatenate([np.full(n, q[0]), q[: len(q) - n]]) if n else q
```

`effect_costs()` removes one effect at a time from the sim, replays the same commands and returns the RMS angle error. A frictionless, lag-free joint conserves energy to 1e-6, so the integrator is not the cause.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates -q
python3 phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/code/main.py
```

## Use It

MuJoCo can switch these effects on one at a time: joint `frictionloss` for dry friction, actuator `dyntype="filter"` for first-order dynamics on the actuator activation (`act_dot = (ctrl - act) / dynprm[0]`), and actuator `delay` with `nsample` for a delayed control input. Add them and rerun the ranking.

Sources: MuJoCo XML reference, `joint/frictionloss`, `actuator/dyntype`, `actuator/delay` (https://mujoco.readthedocs.io/en/stable/XMLreference.html, opened 2026-11-09).

## Ship It

`outputs/skill-sim-gap-ranking.md` ranks which missing effect to model first.

## Exercises

1. Halve `c` in the real plant and see whether friction is still the biggest cost.
2. Make the command ten times faster and check whether delay overtakes friction.
3. Explain why "all three" is not the sum of the three single costs.
