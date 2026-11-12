# Roadmap

Scope: general robotics, not one robot and not one company's stack. Manipulators, wheeled and legged robots, aerial vehicles, perception, planning, learning, fleets and safety.

Status: all 17 phases are written, 81 lessons, each with code, tests, English and Korean docs, quizzes and a Ship It artifact.

## Sourcing rule

- Manipulator phases (02, 03, 08 partly, 11 partly) follow Craig, *Introduction to Robotics: Mechanics and Control*, 3rd ed.: Ch2 spatial descriptions, Ch3 kinematics, Ch4 inverse kinematics, Ch5 Jacobians, Ch6 dynamics, Ch7 trajectories, Ch9 to Ch11 control. Cite a chapter, and a section only when it was checked against the book's contents. Never quote page numbers or text. The book is not bundled.
- Mobile, legged, aerial, marine, perception and learning phases are outside Craig. Each lesson in them gets its sources from a live search on the day it is written, and carries the links. No remembered numbers.
- Every lesson is simulation-only and original text.

## Lessons

### Phase 00: setup and tooling

| Lesson | One-line idea |
|---|---|
| [01 Python Env and numpy](phases/00-setup-and-tooling/01-python-env-and-numpy/docs/en.md) · [한국어](phases/00-setup-and-tooling/01-python-env-and-numpy/docs/ko.md) | numpy never checks units or shapes for you, so a robot program has to check them itself. |
| [02 MuJoCo Hello World](phases/00-setup-and-tooling/02-mujoco-hello-world/docs/en.md) · [한국어](phases/00-setup-and-tooling/02-mujoco-hello-world/docs/ko.md) | A simulator is a loop that turns forces into a new state every `dt`, so write one before you trust one. |
| [03 Reading a URDF](phases/00-setup-and-tooling/03-reading-a-urdf/docs/en.md) · [한국어](phases/00-setup-and-tooling/03-reading-a-urdf/docs/ko.md) | A URDF is a tree of links joined by joints, and every joint origin is written in its parent link's frame. |
| [04 ROS 2 in One Page](phases/00-setup-and-tooling/04-ros2-in-one-page/docs/en.md) · [한국어](phases/00-setup-and-tooling/04-ros2-in-one-page/docs/ko.md) | Nodes exchange data over topics and services, and a queue depth decides what a slow subscriber loses. |

### Phase 01: math foundations

| Lesson | One-line idea |
|---|---|
| [01 Rotations and SE(3)](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) · [한국어](phases/01-math-foundations/01-rotations-and-se3/docs/ko.md) | A pose is a rotation and a position, and the order you multiply them in is the whole story. |
| [02 Forward Kinematics](phases/01-math-foundations/02-forward-kinematics/docs/en.md) · [한국어](phases/01-math-foundations/02-forward-kinematics/docs/ko.md) | Walk the chain: rotate about the joint, step along the link, repeat. |
| [03 Axis-Angle and Quaternions](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) · [한국어](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/ko.md) | Every rotation has two quaternions, and an interpolator that ignores this can spin a wrist a full turn. |
| [04 Frames and Transform Trees](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) · [한국어](phases/01-math-foundations/04-frames-and-transform-trees/docs/ko.md) | Name every transform `T_to_from`, and let the tree find the path between any two frames. |
| [05 Euler Angles and Gimbal Lock](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) · [한국어](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/ko.md) | Roll, pitch and yaw are three numbers in a fixed order, and near pitch 90 degrees that order has a hole. |

### Phase 02: manipulator kinematics

| Lesson | One-line idea |
|---|---|
| [01 DH Tables vs URDF Origins](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) · [한국어](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/ko.md) | The same arm can be written as a DH table or as joint origins, and a table fed to the wrong DH convention returns a wrong pose without any error. |
| [02 Inverse Kinematics of a Two-Link Arm](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) · [한국어](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/ko.md) | Reaching a point is a triangle with two valid answers and a hard edge, and the only honest test is to run FK on the answer. |
| [03 The Jacobian: Joint Speeds, Tip Speeds and Forces](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) · [한국어](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/ko.md) | One matrix turns joint speeds into tip speed, and its transpose turns tip force into joint torque. |
| [04 Singularities and Damped Least Squares](phases/02-manipulator-kinematics/04-singularities/docs/en.md) · [한국어](phases/02-manipulator-kinematics/04-singularities/docs/ko.md) | When the arm straightens, one direction of tip motion disappears, and the plain inverse answers with a joint speed that grows without limit. |
| [05 Numerical Inverse Kinematics](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) · [한국어](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/ko.md) | With no formula for the joints, nudge them toward the target with the Jacobian, clamp to the limits, and try several starting points. |

### Phase 03: dynamics and control

| Lesson | One-line idea |
|---|---|
| [01 The Sampling Limit](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) · [한국어](phases/03-dynamics-and-control/01-the-sampling-limit/docs/ko.md) | A damper that is correct in continuous time can still be unstable once the controller holds its command for one tick. |
| [02 Gravity Compensation](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) · [한국어](phases/03-dynamics-and-control/02-gravity-compensation/docs/ko.md) | A position loop pays for every error in your gravity model, and the bill is the residual divided by kp. |
| [03 Impedance Control](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) · [한국어](phases/03-dynamics-and-control/03-impedance-control/docs/ko.md) | Impedance control does not track a position. It decides how the joint pushes back. |
| [04 PID and Tuning](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) · [한국어](phases/03-dynamics-and-control/04-pid-and-tuning/docs/ko.md) | P pushes now, I remembers the past, D brakes. Each fixes one problem and causes another. |
| [05 Computed Torque](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) · [한국어](phases/03-dynamics-and-control/05-computed-torque/docs/ko.md) | If you know the arm's equations, use them to cancel the arm, then control what is left. |
| [06 LQR: Gains from Cost, Not from Guessing](phases/03-dynamics-and-control/06-lqr/docs/en.md) · [한국어](phases/03-dynamics-and-control/06-lqr/docs/ko.md) | Say how much you hate error against effort, and the Riccati recursion hands back the gain. |
| [07 Where M(q) Comes From: Deriving Arm Dynamics](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) · [한국어](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/ko.md) | Write the arm's kinetic energy once, and differentiation hands you the inertia matrix and every Coriolis term. |
| [08 Model Predictive Control](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) · [한국어](phases/03-dynamics-and-control/08-model-predictive-control/docs/ko.md) | Plan a short future with the limits written in, apply only the first command, then plan again. |
| [09 Lyapunov Stability by Checking](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) · [한국어](phases/03-dynamics-and-control/09-lyapunov-stability/docs/ko.md) | A stable system has an energy-like number that never rises, and you can test that on a computer. |

### Phase 04: actuators and sensors

| Lesson | One-line idea |
|---|---|
| [01 Motor and Gearbox](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) · [한국어](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/ko.md) | A motor is a torque source that weakens as it speeds up, and a gearbox makes the load almost invisible to it. |
| [02 Torque vs Position Modes](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/en.md) · [한국어](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/ko.md) | A position mode is a torque mode with someone else's PD gains, and those gains set how stiff your joint feels. |
| [03 Encoders and Quantisation](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) · [한국어](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/ko.md) | An encoder reports whole counts, so a slow joint reads as a jumpy velocity, and every filter that calms it makes it late. |
| [04 Latency Budget](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) · [한국어](phases/04-actuators-and-sensors/04-latency-budget/docs/ko.md) | Every stage of the loop adds delay, delay spends phase margin, and what is left decides how large kd may be. |

### Phase 05: robot software

| Lesson | One-line idea |
|---|---|
| [01 Publish-Subscribe and QoS Mismatch](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/en.md) · [한국어](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/ko.md) | A subscriber may not ask for more than the publisher offers, and when it does, nothing is delivered and nothing complains. |
| [02 Executors and Callbacks](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) · [한국어](phases/05-robot-software/02-executors-and-callbacks/docs/ko.md) | One thread runs one callback at a time, so a slow callback makes every other callback wait, whatever its period. |
| [03 Control Loop Jitter](phases/05-robot-software/03-control-loop-jitter/docs/en.md) · [한국어](phases/05-robot-software/03-control-loop-jitter/docs/ko.md) | The average period of a loop can be perfect while one late wake-up in a few thousand breaks the controller. |
| [04 Time Sync and Traces](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) · [한국어](phases/05-robot-software/04-time-sync-and-traces/docs/ko.md) | Two clocks that disagree by a few milliseconds put sensor data in the wrong order, and a trace with before and after states shows where a run first went wrong. |
| [05 Behaviour Trees and State Machines](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) · [한국어](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/ko.md) | A robot task is a tree that is ticked every cycle, and every node answers success, failure or running. |
| [06 Transforms at a Time](phases/05-robot-software/06-transforms-at-a-time/docs/en.md) · [한국어](phases/05-robot-software/06-transforms-at-a-time/docs/ko.md) | A transform lookup is a question about one instant, so the buffer must interpolate between samples or refuse to answer. |

### Phase 06: perception and calibration

| Lesson | One-line idea |
|---|---|
| [01 Pinhole Camera](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) · [한국어](phases/06-perception-and-calibration/01-pinhole-camera/docs/ko.md) | A pixel is a ray. Depth picks the point on it, so a depth error moves the point along the ray and the cost grows with distance. |
| [02 Camera Calibration](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) · [한국어](phases/06-perception-and-calibration/02-camera-calibration/docs/ko.md) | A flat grid seen from a few tilted views is enough to solve for `fx, fy, cx, cy` with linear algebra alone, but the answer is only as good as the views. |
| [03 Depth and Point Clouds](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) · [한국어](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/ko.md) | A depth image is a cloud waiting to be unprojected. Thin it with a voxel grid, then find the table with RANSAC because a plain least-squares plane believes every outlier. |
| [04 Hand-Eye Calibration](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) · [한국어](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/ko.md) | A camera bolted to a gripper gives two views of every motion. `A X = X B` finds where the camera sits, but only if the robot rotates about more than one axis. |

### Phase 07: state estimation

| Lesson | One-line idea |
|---|---|
| [01 Bayes Filter](phases/07-state-estimation/01-bayes-filter/docs/en.md) · [한국어](phases/07-state-estimation/01-bayes-filter/docs/ko.md) | A robot never knows where it is, only how likely each place is, and two steps keep that belief honest: predict adds doubt, update removes it. |
| [02 Kalman Filter](phases/07-state-estimation/02-kalman-filter/docs/en.md) · [한국어](phases/07-state-estimation/02-kalman-filter/docs/ko.md) | When a model and a noisy sensor disagree, the Kalman gain decides how far to move toward the sensor, and it also tells you how wrong the result still is. |
| [03 IMU Integration and Drift](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) · [한국어](phases/07-state-estimation/03-imu-integration-and-drift/docs/ko.md) | Integrating a sensor that has a tiny constant error turns that error into a line, a parabola or a cubic, and gravity is the channel that makes it cubic. |
| [04 Complementary Filter](phases/07-state-estimation/04-complementary-filter/docs/en.md) · [한국어](phases/07-state-estimation/04-complementary-filter/docs/ko.md) | The gyro is right about fast changes and wrong about the long run, the accelerometer is the opposite, and one time constant decides who is believed when. |
| [05 Extended Kalman Filter](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) · [한국어](phases/07-state-estimation/05-extended-kalman-filter/docs/ko.md) | Linearise the model at your current estimate and run a Kalman filter on that, which works only while the estimate is close enough to the truth. |

### Phase 08: mobile robots

| Lesson | One-line idea |
|---|---|
| [01 Differential Drive and Odometry](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) · [한국어](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/ko.md) | Wheel speeds give you a pose only if you know two lengths exactly, and the estimate cannot tell you when you do not. |
| [02 Particle Filter Localisation](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) · [한국어](phases/08-mobile-robots/02-particle-filter-localisation/docs/ko.md) | Keep many guesses of where you are, let the measurements kill the bad ones, and keep a few wild guesses for the day you are moved. |
| [03 Occupancy Grid and the SLAM Idea](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) · [한국어](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/ko.md) | A map is only as good as the poses you drew it from, which is why mapping and localising have to be solved together. |
| [04 Path Following with Pure Pursuit](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) · [한국어](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/ko.md) | Aim at a point a fixed distance ahead on the path, and let that one distance trade wobble against cut corners. |
| [05 Scan Matching with ICP](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) · [한국어](phases/08-mobile-robots/05-icp-scan-matching/docs/ko.md) | To line up two scans, guess that each point's partner is its nearest neighbour, fit one rigid move, and repeat until the error stops falling. |
| [06 Pose Graph and Loop Closure](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/en.md) · [한국어](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/ko.md) | Treat poses as unknowns and measurements as springs between them, and one late "we are back here" measurement bends the whole drifted trajectory shut. |

### Phase 09: motion planning

| Lesson | One-line idea |
|---|---|
| [01 Trajectory Profiles](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) · [한국어](phases/09-motion-planning/01-trajectory-profiles/docs/ko.md) | Picking a path between two points is easy. Picking one the motor can follow without a jerk takes six conditions, not four. |
| [02 RRT](phases/09-motion-planning/02-rrt/docs/en.md) · [한국어](phases/09-motion-planning/02-rrt/docs/ko.md) | Grow a tree of short, collision-free steps from the start until a branch touches the goal, then straighten the result. |
| [03 Collision Checking](phases/09-motion-planning/03-collision-checking/docs/en.md) · [한국어](phases/09-motion-planning/03-collision-checking/docs/ko.md) | A path that is checked only at sample points can tunnel through an obstacle thinner than the sample spacing. |
| [04 Trajectory Optimisation](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) · [한국어](phases/09-motion-planning/04-trajectory-optimisation/docs/ko.md) | A planner's path is feasible but jagged. Gradient descent on a smoothness cost and an obstacle penalty turns it into a path a robot can follow. |
| [05 Grid Search: Dijkstra to A*](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) · [한국어](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/ko.md) | A* is Dijkstra with a promise: a guess of the distance left that is never too big, which lets it skip cells that cannot be on the best path. |

### Phase 10: legged and aerial

| Lesson | One-line idea |
|---|---|
| [01 Inverted Pendulum and ZMP](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) · [한국어](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/ko.md) | A standing body falls like a pendulum balanced on its tip, and the capture point tells you where the next foot must land. |
| [02 Walking by Foot Placement](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) · [한국어](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/ko.md) | A walker steers its speed with its feet: the next foot position is solved from where the body is now. |
| [03 Quadrotor Model](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) · [한국어](phases/10-legged-and-aerial/03-quadrotor-model/docs/ko.md) | A quadrotor cannot push sideways. It tilts first, and the tilt turns thrust into sideways force. |
| [04 Cascaded Attitude Control](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/en.md) · [한국어](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/ko.md) | An angle loop outside a rate loop is the same as PD until you give the inner loop an integral, and then a gust stops costing you an angle error. |

### Phase 11: contact and manipulation

| Lesson | One-line idea |
|---|---|
| [01 Contact Models](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) · [한국어](phases/11-contact-and-manipulation/01-contact-models/docs/ko.md) | A block sticks on a tilted plane exactly when tan(theta) is at most mu, because friction can only push inside its cone. |
| [02 Force and Hybrid Control](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) · [한국어](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/ko.md) | Position control turns every error in your stiffness guess into a force error. A force loop measures the force, so the guess drops out. |
| [03 Grasp Quality](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) · [한국어](phases/11-contact-and-manipulation/03-grasp-quality/docs/ko.md) | A grasp holds if the friction-cone wrenches of its contacts can push in every direction, and the size of the hull tells you how well. |
| [04 Compliance in Assembly](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) · [한국어](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/ko.md) | A peg jams when the tool is too stiff to give way, because the side force it creates feeds the friction that holds the peg. |

### Phase 12: simulation and sim to real

| Lesson | One-line idea |
|---|---|
| [01 What a Simulator Approximates](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/en.md) · [한국어](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/ko.md) | A simulator is the real joint with some effects deleted, and you can measure what each deletion costs. |
| [02 Timestep and Solver](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) · [한국어](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/ko.md) | The step size and the integrator are part of the model, and a result that changes with them is not a result yet. |
| [03 System Identification](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) · [한국어](phases/12-simulation-and-sim-to-real/03-system-identification/docs/ko.md) | Fit the plant from a recording, and know that the recording decides which parameters you can learn. |
| [04 Domain Randomisation](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) · [한국어](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/ko.md) | Tune a fixed controller across a spread of plants that matches the real uncertainty, no wider and no narrower. |

### Phase 13: learning for robots

| Lesson | One-line idea |
|---|---|
| [01 Imitation from Demonstrations](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) · [한국어](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/ko.md) | If you cannot write the reward, show the robot what to do and fit a function to the examples. |
| [02 Behaviour Cloning Pitfalls](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) · [한국어](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/ko.md) | A cloned policy is accurate where the expert drove and wrong one step later, because its own mistakes put it somewhere the expert never was. |
| [03 Policy Gradients](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) · [한국어](phases/13-learning-for-robots/03-policy-gradients/docs/ko.md) | Nudge the policy toward actions that scored above average, and the only price is noise, which a baseline cuts. |
| [04 A Safety Wrapper for Learned Policies](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) · [한국어](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/ko.md) | A learned policy is a producer that can say anything. The layer after it must be deterministic and must not care what was said. |
| [05 MDPs and Value Iteration](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) · [한국어](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/ko.md) | The value of a state is the best action's reward plus the discounted value of where it leads, and a few sweeps are enough to find it. |
| [06 Multimodal Demonstrations and Action Chunks](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) · [한국어](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/ko.md) | When demonstrations disagree, a regression averages them into an action nobody demonstrated, and a short chunk of future actions commits to one. |

### Phase 14: multi robot and swarms

| Lesson | One-line idea |
|---|---|
| [01 Task Allocation](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) · [한국어](phases/14-multi-robot-and-swarms/01-task-allocation/docs/ko.md) | Assigning each robot its nearest task one at a time is fast and often wrong; the optimal assignment looks at all pairs at once. |
| [02 Consensus](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) · [한국어](phases/14-multi-robot-and-swarms/02-consensus/docs/ko.md) | Robots that only talk to neighbours can still agree on one number, and how fast they agree is set by the second-smallest eigenvalue of the graph Laplacian. |
| [03 Traffic and Deadlock](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) · [한국어](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/ko.md) | Single-lane crossings let robots block each other in a loop; draw who waits for whom, find the loop, and remove it by taking a whole route at once. |

### Phase 15: safety and deployment

| Lesson | One-line idea |
|---|---|
| [01 Failure Modes](phases/15-safety-and-deployment/01-failure-modes/docs/en.md) · [한국어](phases/15-safety-and-deployment/01-failure-modes/docs/ko.md) | Before you can guard a joint you have to know how it breaks, and the worst faults are the quiet ones. |
| [02 Watchdogs and Stops](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/en.md) · [한국어](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/ko.md) | A watchdog is only safe if the joint can stop in the room left after the timeout runs out. |
| [03 Limits at Every Layer](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) · [한국어](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/ko.md) | When two layers disagree about a limit, the tighter one wins and nothing reports it. |
| [04 Testing Robot Code](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) · [한국어](phases/15-safety-and-deployment/04-testing-robot-code/docs/ko.md) | A robot test must control time, refuse bad commands, and replay what really happened. |

### Phase 16: capstones

| Lesson | One-line idea |
|---|---|
| [01 Arm Pick and Place in Simulation](phases/16-capstones/01-arm-pick-and-place-sim/docs/en.md) · [한국어](phases/16-capstones/01-arm-pick-and-place-sim/docs/ko.md) | Four earlier ideas make one task, and removing the quietest one, gravity feedforward, makes the whole task fail. |
| [02 Mobile Navigation in Simulation](phases/16-capstones/02-mobile-navigation-sim/docs/en.md) · [한국어](phases/16-capstones/02-mobile-navigation-sim/docs/ko.md) | A planner draws the route, but the robot only follows where it believes it is, so a drifting odometry estimate turns a good plan into a crash. |
| [03 A Learned Policy with a Safety Wrapper](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/en.md) · [한국어](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/ko.md) | A learned policy is allowed to be wrong sometimes, so the code around it must make sure that being wrong is never dangerous. |
