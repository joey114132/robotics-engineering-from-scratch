# Roadmap

Scope: general robotics, not one robot and not one company's stack. Manipulators, wheeled and legged robots, aerial vehicles, perception, planning, learning, fleets and safety.

Status: all 17 phases are written, 87 lessons, each with code, tests, English and Korean docs, quizzes and a Ship It artifact.

## Sourcing rule

- Manipulator phases (02, 03, 08 partly, 11 partly) follow Craig, *Introduction to Robotics: Mechanics and Control*, 3rd ed.: Ch2 spatial descriptions, Ch3 kinematics, Ch4 inverse kinematics, Ch5 Jacobians, Ch6 dynamics, Ch7 trajectories, Ch9 to Ch11 control. Cite a chapter, and a section only when it was checked against the book's contents. Never quote page numbers or text. The book is not bundled.
- Mobile, legged, aerial, marine, perception and learning phases are outside Craig. Each lesson in them gets its sources from a live search on the day it is written, and carries the links. No remembered numbers.
- Every lesson is simulation-only and original text.

## Lessons

### Phase 00: start here

| Lesson | What you will learn |
|---|---|
| [01 What Is a Robot](phases/00-start-here/01-what-is-a-robot/docs/en.md) · [한국어](phases/00-start-here/01-what-is-a-robot/docs/ko.md) | Learn that a robot is a machine that keeps repeating three steps: sense, think, act. |
| [02 Points as Numbers](phases/00-start-here/02-points-as-numbers/docs/en.md) · [한국어](phases/00-start-here/02-points-as-numbers/docs/ko.md) | Learn that a place is just a pair of numbers counted from a corner, and how to measure the distance between two places. |
| [03 Angles and Radians](phases/00-start-here/03-angles-and-radians/docs/en.md) · [한국어](phases/00-start-here/03-angles-and-radians/docs/ko.md) | Learn that an angle can be counted in degrees or radians, and that code always wants radians. |
| [04 Joints and Links](phases/00-start-here/04-joints-and-links/docs/en.md) · [한국어](phases/00-start-here/04-joints-and-links/docs/ko.md) | Learn how a joint angle and a link length tell you where an arm's hand is. |
| [05 Turning a Point](phases/00-start-here/05-turning-a-point/docs/en.md) · [한국어](phases/00-start-here/05-turning-a-point/docs/ko.md) | Learn how to turn a point around the origin by an angle, first with plain math, then with a small table of numbers. |
| [06 Time Steps](phases/00-start-here/06-time-steps/docs/en.md) · [한국어](phases/00-start-here/06-time-steps/docs/ko.md) | Learn how a computer moves things by repeating tiny steps, and why smaller steps follow real motion better. |
| [07 Python Env and numpy](phases/00-start-here/07-python-env-and-numpy/docs/en.md) · [한국어](phases/00-start-here/07-python-env-and-numpy/docs/ko.md) | See how a wrong unit or array shape quietly gives a wrong answer, and how to catch it. |
| [08 MuJoCo Hello World](phases/00-start-here/08-mujoco-hello-world/docs/en.md) · [한국어](phases/00-start-here/08-mujoco-hello-world/docs/ko.md) | Learn how a simulator moves things in tiny time steps, why a wrong step adds energy out of nowhere, and the one-line fix. |
| [09 Reading a URDF](phases/00-start-here/09-reading-a-urdf/docs/en.md) · [한국어](phases/00-start-here/09-reading-a-urdf/docs/ko.md) | Learn to read a robot's description file, and why each joint's offset is measured from the part before it. |
| [10 ROS 2 in One Page](phases/00-start-here/10-ros2-in-one-page/docs/en.md) · [한국어](phases/00-start-here/10-ros2-in-one-page/docs/ko.md) | Learn how robot programs pass data to each other, and why a longer waiting line can make a robot react late. |

### Phase 01: math foundations

| Lesson | What you will learn |
|---|---|
| [01 Rotations and SE(3)](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) · [한국어](phases/01-math-foundations/01-rotations-and-se3/docs/ko.md) | Learn how to describe where something is and which way it faces, and why the order of two turns matters. |
| [02 Forward Kinematics](phases/01-math-foundations/02-forward-kinematics/docs/en.md) · [한국어](phases/01-math-foundations/02-forward-kinematics/docs/ko.md) | Learn how to turn a robot arm's joint angles into the position of its hand. |
| [03 Axis-Angle and Quaternions](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) · [한국어](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/ko.md) | Learn why a robot wrist can spin a whole turn the long way round, and the one-line check that stops it. |
| [04 Frames and Transform Trees](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) · [한국어](phases/01-math-foundations/04-frames-and-transform-trees/docs/ko.md) | Learn a naming habit that stops you mixing up which part's view a position is measured from. |
| [05 Euler Angles and Gimbal Lock](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) · [한국어](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/ko.md) | Learn why roll, pitch and yaw numbers suddenly jump when a tool tilts straight down. |

### Phase 02: manipulator kinematics

| Lesson | What you will learn |
|---|---|
| [01 DH Tables vs URDF Origins](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) · [한국어](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/ko.md) | Learn why a robot-arm table copied from a book can give wrong positions with no warning. |
| [02 Inverse Kinematics of a Two-Link Arm](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) · [한국어](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/ko.md) | Learn how to find the joint angles that put an arm's hand on a point, or learn that it cannot reach. |
| [03 The Jacobian: Joint Speeds, Tip Speeds and Forces](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) · [한국어](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/ko.md) | Learn how joint speeds set the hand's speed, and how a push on the hand turns into motor torque. |
| [04 Singularities and Damped Least Squares](phases/02-manipulator-kinematics/04-singularities/docs/en.md) · [한국어](phases/02-manipulator-kinematics/04-singularities/docs/ko.md) | Learn why a nearly straight arm makes joints spin wildly, and the small trick that calms them. |
| [05 Numerical Inverse Kinematics](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) · [한국어](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/ko.md) | Learn how to find joint angles by trial and correction when no formula exists. |

### Phase 03: dynamics and control

| Lesson | What you will learn |
|---|---|
| [01 The Sampling Limit](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) · [한국어](phases/03-dynamics-and-control/01-the-sampling-limit/docs/ko.md) | Learn why a brake that works on paper can make a robot joint buzz, and how to tell in advance. |
| [02 Gravity Compensation](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) · [한국어](phases/03-dynamics-and-control/02-gravity-compensation/docs/ko.md) | Learn why a soft robot arm sags, and how the error in your weight guess decides how far. |
| [03 Impedance Control](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) · [한국어](phases/03-dynamics-and-control/03-impedance-control/docs/ko.md) | Learn how to make a robot joint push back like a spring and damper, so a touch is gentle. |
| [04 PID and Tuning](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) · [한국어](phases/03-dynamics-and-control/04-pid-and-tuning/docs/ko.md) | Learn how the three parts of the most common controller work, and what goes wrong when you turn them up. |
| [05 Computed Torque](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) · [한국어](phases/03-dynamics-and-control/05-computed-torque/docs/ko.md) | Learn how to cancel an arm's own swing forces in advance, so a fast motion stays on track. |
| [06 LQR: Gains from Cost, Not from Guessing](phases/03-dynamics-and-control/06-lqr/docs/en.md) · [한국어](phases/03-dynamics-and-control/06-lqr/docs/ko.md) | Learn how to get controller gains by saying how much you mind error and effort, instead of guessing. |
| [07 Where M(q) Comes From: Deriving Arm Dynamics](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) · [한국어](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/ko.md) | Learn where an arm's inertia numbers come from, so you can rebuild them when the robot changes. |
| [08 Model Predictive Control](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) · [한국어](phases/03-dynamics-and-control/08-model-predictive-control/docs/ko.md) | Learn how a controller can plan ahead while respecting a motor's limits. |
| [09 Lyapunov Stability by Checking](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) · [한국어](phases/03-dynamics-and-control/09-lyapunov-stability/docs/ko.md) | Learn how to check that a controller is stable from every starting state with one energy-like number. |

### Phase 04: actuators and sensors

| Lesson | What you will learn |
|---|---|
| [01 Motor and Gearbox](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) · [한국어](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/ko.md) | Learn why a gearbox makes a heavy load feel almost weightless to the motor. |
| [02 Torque vs Position Modes](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/en.md) · [한국어](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/ko.md) | Learn why a robot joint can stay stiff when you ask it to be soft, and what fixes that. |
| [03 Encoders and Quantisation](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) · [한국어](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/ko.md) | Learn why a slow joint gives a jumpy speed reading, and why smoothing it makes it late. |
| [04 Latency Budget](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) · [한국어](phases/04-actuators-and-sensors/04-latency-budget/docs/ko.md) | Learn why a controller that is smooth on the bench can buzz on the real robot, and how much delay it can take. |

### Phase 05: robot software

| Lesson | What you will learn |
|---|---|
| [01 Publish-Subscribe and QoS Mismatch](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/en.md) · [한국어](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/ko.md) | Learn why two ROS programs can both run fine and still never exchange a message. |
| [02 Executors and Callbacks](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) · [한국어](phases/05-robot-software/02-executors-and-callbacks/docs/ko.md) | Learn why one slow task can freeze a robot's other tasks even when the processor is idle. |
| [03 Control Loop Jitter](phases/05-robot-software/03-control-loop-jitter/docs/en.md) · [한국어](phases/05-robot-software/03-control-loop-jitter/docs/ko.md) | Learn why a control loop with a perfect average timing can still make a robot arm twitch. |
| [04 Time Sync and Traces](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) · [한국어](phases/05-robot-software/04-time-sync-and-traces/docs/ko.md) | Learn how to line up two clocks, and how a step-by-step log shows where a run first went wrong. |
| [05 Behaviour Trees and State Machines](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) · [한국어](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/ko.md) | Learn how a robot task can remember where it is, so a failed step is retried instead of restarted. |
| [06 Transforms at a Time](phases/05-robot-software/06-transforms-at-a-time/docs/en.md) · [한국어](phases/05-robot-software/06-transforms-at-a-time/docs/ko.md) | Learn why a turning robot's laser scan bends a straight wall, and how timestamps fix it. |

### Phase 06: perception and calibration

| Lesson | What you will learn |
|---|---|
| [01 Pinhole Camera](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) · [한국어](phases/06-perception-and-calibration/01-pinhole-camera/docs/ko.md) | Learn why a camera gives the direction of a cup but not its distance, and what that costs. |
| [02 Camera Calibration](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) · [한국어](phases/06-perception-and-calibration/02-camera-calibration/docs/ko.md) | Learn how to measure a camera's own zoom and centre from a checkerboard and a few tilted photos. |
| [03 Depth and Point Clouds](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) · [한국어](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/ko.md) | Learn how a robot finds a flat table in a messy 3D scan, even with a box and stray dots. |
| [04 Hand-Eye Calibration](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) · [한국어](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/ko.md) | Learn how to find where a camera is mounted on a robot's hand, and why the arm must turn about different axes. |

### Phase 07: state estimation

| Lesson | What you will learn |
|---|---|
| [01 Bayes Filter](phases/07-state-estimation/01-bayes-filter/docs/en.md) · [한국어](phases/07-state-estimation/01-bayes-filter/docs/ko.md) | Learn how a robot keeps track of where it is when its wheels slip and its sensors are vague. |
| [02 Kalman Filter](phases/07-state-estimation/02-kalman-filter/docs/en.md) · [한국어](phases/07-state-estimation/02-kalman-filter/docs/ko.md) | Learn how to blend a noisy sensor with a motion prediction into a steadier estimate. |
| [03 IMU Integration and Drift](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) · [한국어](phases/07-state-estimation/03-imu-integration-and-drift/docs/ko.md) | Learn why a robot that adds up tiny sensor errors thinks it is rolling away while standing still. |
| [04 Complementary Filter](phases/07-state-estimation/04-complementary-filter/docs/en.md) · [한국어](phases/07-state-estimation/04-complementary-filter/docs/ko.md) | Learn how to combine a smooth-but-drifting sensor with a jittery-but-honest one to track tilt. |
| [05 Extended Kalman Filter](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) · [한국어](phases/07-state-estimation/05-extended-kalman-filter/docs/ko.md) | Learn how a robot that drives in curves tracks its position, and why a wrong start can leave it confidently wrong. |

### Phase 08: mobile robots

| Lesson | What you will learn |
|---|---|
| [01 Differential Drive and Odometry](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) · [한국어](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/ko.md) | Learn why a robot can say it came home when it did not, and what causes it. |
| [02 Particle Filter Localisation](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) · [한국어](phases/08-mobile-robots/02-particle-filter-localisation/docs/ko.md) | Learn how a lost robot, even one picked up and moved, finds where it is by keeping many guesses. |
| [03 Occupancy Grid and the SLAM Idea](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) · [한국어](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/ko.md) | Learn how a robot draws a room map from laser beams, and why a small heading error ruins it. |
| [04 Path Following with Pure Pursuit](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) · [한국어](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/ko.md) | Learn how a robot follows a path by aiming ahead, and how one number trades wobble for cut corners. |
| [05 Scan Matching with ICP](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) · [한국어](phases/08-mobile-robots/05-icp-scan-matching/docs/ko.md) | Learn how a robot lines up two laser scans to work out how far it moved. |
| [06 Pose Graph and Loop Closure](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/en.md) · [한국어](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/ko.md) | Learn how recognising a place you have been before can straighten a whole drifted trip at once. |

### Phase 09: motion planning

| Lesson | What you will learn |
|---|---|
| [01 Trajectory Profiles](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) · [한국어](phases/09-motion-planning/01-trajectory-profiles/docs/ko.md) | Learn why a smooth-looking move can still jolt a robot arm, and how to plan a gentler one. |
| [02 RRT](phases/09-motion-planning/02-rrt/docs/en.md) · [한국어](phases/09-motion-planning/02-rrt/docs/ko.md) | Learn how a robot finds a way around obstacles by trial and error, then straightens the route. |
| [03 Collision Checking](phases/09-motion-planning/03-collision-checking/docs/en.md) · [한국어](phases/09-motion-planning/03-collision-checking/docs/ko.md) | Learn why checking a path at only a few spots can miss a thin obstacle, and how to check safely. |
| [04 Trajectory Optimisation](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) · [한국어](phases/09-motion-planning/04-trajectory-optimisation/docs/ko.md) | Learn how to smooth a zigzag path without pushing it back into an obstacle. |
| [05 Grid Search: Dijkstra to A*](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) · [한국어](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/ko.md) | Learn how a robot finds the shortest route on a map without checking every square. |

### Phase 10: legged and aerial

| Lesson | What you will learn |
|---|---|
| [01 Inverted Pendulum and ZMP](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) · [한국어](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/ko.md) | Learn how a walking robot knows early that it will fall, and where to step. |
| [02 Walking by Foot Placement](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) · [한국어](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/ko.md) | Learn how a walking robot controls its speed just by choosing where each foot lands. |
| [03 Quadrotor Model](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) · [한국어](phases/10-legged-and-aerial/03-quadrotor-model/docs/ko.md) | Learn why a drone must tilt to move sideways, and why tilting makes it sink. |
| [04 Cascaded Attitude Control](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/en.md) · [한국어](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/ko.md) | Learn how a drone stays level against steady wind, with a controller that remembers. |

### Phase 11: contact and manipulation

| Lesson | What you will learn |
|---|---|
| [01 Contact Models](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) · [한국어](phases/11-contact-and-manipulation/01-contact-models/docs/ko.md) | Learn why a gripped part slides out when the wrist tilts, and how to predict the angle. |
| [02 Force and Hybrid Control](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) · [한국어](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/ko.md) | Learn how a robot presses with the right force on a surface of unknown softness. |
| [03 Grasp Quality](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) · [한국어](phases/11-contact-and-manipulation/03-grasp-quality/docs/ko.md) | Learn how to tell whether a robot hand's grip will hold, and how much margin it has. |
| [04 Compliance in Assembly](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) · [한국어](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/ko.md) | Learn why a stiff robot jams a peg in a tight hole, and why a gentler wrist slides it in. |

### Phase 12: simulation and sim to real

| Lesson | What you will learn |
|---|---|
| [01 What a Simulator Approximates](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/en.md) · [한국어](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/ko.md) | Find out which things a simulator leaves out of a real joint, and which one costs you most. |
| [02 Timestep and Solver](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) · [한국어](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/ko.md) | Learn why a simulated ball can bounce higher than it fell, and the one-line fix. |
| [03 System Identification](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) · [한국어](phases/12-simulation-and-sim-to-real/03-system-identification/docs/ko.md) | Learn how to measure a robot joint's hidden numbers from a recording, and why a boring recording fails. |
| [04 Domain Randomisation](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) · [한국어](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/ko.md) | Learn how to tune a robot's controller so it works on many slightly different robots, not just one. |

### Phase 13: learning for robots

| Lesson | What you will learn |
|---|---|
| [01 Imitation from Demonstrations](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) · [한국어](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/ko.md) | Learn how to teach a robot by showing it examples instead of writing rules. |
| [02 Behaviour Cloning Pitfalls](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) · [한국어](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/ko.md) | Learn why a robot that copies an expert works at first and then drifts off, and how to fix it. |
| [03 Policy Gradients](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) · [한국어](phases/13-learning-for-robots/03-policy-gradients/docs/ko.md) | Learn how a robot can improve from points alone, with no teacher, and why the learning wobbles. |
| [04 A Safety Wrapper for Learned Policies](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) · [한국어](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/ko.md) | Learn how to put a simple, checkable guard between a learned model and a motor. |
| [05 MDPs and Value Iteration](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) · [한국어](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/ko.md) | Learn how a robot can work out the best move in every square of a small slippery world. |
| [06 Multimodal Demonstrations and Action Chunks](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) · [한국어](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/ko.md) | Learn why a robot trained on two different good answers can pick a bad middle one, and how to make it pick one. |

### Phase 14: multi robot and swarms

| Lesson | What you will learn |
|---|---|
| [01 Task Allocation](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) · [한국어](phases/14-multi-robot-and-swarms/01-task-allocation/docs/ko.md) | Learn how to hand out jobs to a team of robots so the total travel is smallest. |
| [02 Consensus](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) · [한국어](phases/14-multi-robot-and-swarms/02-consensus/docs/ko.md) | Learn how robots that only talk to their neighbours can still agree on one number, and what makes it slow. |
| [03 Traffic and Deadlock](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) · [한국어](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/ko.md) | Learn why robots can block each other forever at a crossing, and a simple rule that prevents it. |

### Phase 15: safety and deployment

| Lesson | What you will learn |
|---|---|
| [01 Failure Modes](phases/15-safety-and-deployment/01-failure-modes/docs/en.md) · [한국어](phases/15-safety-and-deployment/01-failure-modes/docs/ko.md) | Learn the ways a robot joint can fail quietly, and how to spot each one early. |
| [02 Watchdogs and Stops](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/en.md) · [한국어](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/ko.md) | Learn how to make a robot stop safely when its control program crashes. |
| [03 Limits at Every Layer](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) · [한국어](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/ko.md) | Learn why a robot can quietly move slower than you asked, and how to catch it at startup. |
| [04 Testing Robot Code](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) · [한국어](phases/15-safety-and-deployment/04-testing-robot-code/docs/ko.md) | Learn how to test robot code without waiting for real time and without risking a real robot. |

### Phase 16: capstones

| Lesson | What you will learn |
|---|---|
| [01 Arm Pick and Place in Simulation](phases/16-capstones/01-arm-pick-and-place-sim/docs/en.md) · [한국어](phases/16-capstones/01-arm-pick-and-place-sim/docs/ko.md) | Put four earlier ideas together to make a robot arm move a ball, and see what breaks when one is missing. |
| [02 Mobile Navigation in Simulation](phases/16-capstones/02-mobile-navigation-sim/docs/en.md) · [한국어](phases/16-capstones/02-mobile-navigation-sim/docs/ko.md) | Drive a simulated rover to a goal and see why a drifting position estimate leads it into a wall. |
| [03 A Learned Policy with a Safety Wrapper](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/en.md) · [한국어](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/ko.md) | Put a plain safety layer around a learned model and see it keep a robot arm inside its limits. |
