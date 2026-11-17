# What a Simulator Approximates

> Find out which things a simulator leaves out of a real joint, and which one costs you most.

**Type:** Build   **Prerequisites:** 03/02 Gravity Compensation   **Time:** ~15 minutes

## In Plain Words

A metal arm hangs from a motor on a wall. The real hinge rubs, so each swing shrinks. A simulator with no friction swings farther.

The motor is also slow to push and the sensor is late. This lesson removes one effect at a time and measures which hurts most.

## Key Terms

- **Plant**: the thing being controlled. Here it is one swinging arm joint.
- **Torque**: the twisting push a motor gives a joint.
- **Friction**: rubbing that slowly drains movement.
- **Motor lag**: the delay before the motor's push catches up with the command.
- **Open-loop**: sending commands without checking sensors to correct them.
- **RMS error**: one number for how far apart two curves are, on average.

## The Problem

You test an arm in simulation and it looks perfect. On the real robot the same commands lag and stop short. The simulator left out something the hardware does.

## The Concept

A simulator is where you test robot code safely, so you need to know how far to trust it. We give a real arm and a simulated copy the same commands, then delete one real effect at a time from the copy and see how far it drifts.

![Real vs sim](../assets/diagram-real-vs-sim.png)

*The real command goes through a slow motor, a rubbing joint and a late sensor. The simple simulator skips all three.*

![Replay](../assets/diagram-replay-rank.png)

*Both get the same commands with no feedback, so any difference keeps growing.*

![Divergence](../assets/fig-divergence.png)

*The copy without friction drifts far from the real arm. Missing lag or delay barely matters.*

Friction matters far more than the delays, so model it first.

![Three arms](../assets/clip-example.mp4)

*Blue is the real arm. Each ghost misses one effect: friction, motor lag, sensor delay. Only the left one drifts.*

<details><summary>The math (optional)</summary>

The model is `J*w' = tm - b*w - c*tanh(w/eps) - k*sin(q)` and `Tm*tm' = u - tm`, stepped with RK4. `J` is how hard the arm is to speed up, `b` a drag that grows with speed, `c` a constant rub, `k = m*g*l` gravity's pull and `Tm` the motor lag. RMS error is 0.545 rad without friction, 0.042 rad without lag and 0.029 rad without delay (1 rad is about 57 degrees). On a 0.4 m arm 0.545 rad is a fingertip 22 cm off, while lag and delay cost 1 to 2 cm, so friction costs 13 times more than lag. A joint with no friction and no lag keeps its energy to 1e-6.

</details>

## Build It

The model is a swinging arm with friction, a slow motor and a late sensor.

```python
def measured(p, u_fn, T):
    q, n = simulate(p, u_fn, T)[:, 0], round(p["delay"] / DT)
    return np.concatenate([np.full(n, q[0]), q[: len(q) - n]]) if n else q
```

`effect_costs()` removes one effect at a time and returns the error.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates -q
python3 phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/code/main.py
```

## Use It

MuJoCo can switch these effects on one at a time: dry friction, a slow actuator and a delayed command.

Sources: MuJoCo XML reference, `joint/frictionloss`, `actuator/dyntype`, `actuator/delay` (https://mujoco.readthedocs.io/en/stable/XMLreference.html, opened 2026-11-09).

## Ship It

`outputs/skill-sim-gap-ranking.md` ranks which missing effect to model first.

## Exercises

1. Halve the friction. Is it still the biggest cost?
2. Make the commands ten times faster. Does delay matter more now?
3. Remove all three effects at once. Is the cost the sum of the single costs?
