# Glossary

Every term from the lessons' Key Terms, A to Z, with the lesson that introduces it.

| Term | Meaning | Lesson |
|---|---|---|
| **`<origin>`** | a joint's position (`xyz`) and rotation (`rpy`) relative to its parent link. | [00-03](phases/00-setup-and-tooling/03-reading-a-urdf/docs/en.md) |
| **A-star** | Dijkstra plus a guess of the cost still to go, so it heads toward the goal. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Acceleration** | how fast the speed changes; the motor's push follows it. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) |
| **Acceleration (`x''`)** | how fast the speed changes; here, how hard gravity pulls the body on. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) |
| **Accelerometer** | measures push (acceleration), and also feels gravity. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Action** | what the robot does at that moment. Here it is a velocity. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **Action chunk** | a short run of the next `H` actions, chosen together. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **Admissible** | a heuristic that never guesses more than the true remaining cost. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Admittance layer** | code that measures a push and moves the target so the joint acts soft. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/en.md) |
| **Array shape** | how many rows and columns an array has, such as 5 rows by 3 columns. | [00-01](phases/00-setup-and-tooling/01-python-env-and-numpy/docs/en.md) |
| **Assignment** | a one-to-one pairing of robots to tasks. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **Attitude** | how the drone is tilted in space. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/en.md) |
| **Augmenting path** | a chain of swaps that rearranges matches to fit one more pair. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **Axis-angle** | a rotation given as a line to turn about plus an angle. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Back-EMF** | the voltage a spinning motor makes against its own supply, which cuts the current and the push. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) |
| **Backup** | recomputing one state's value from its actions' rewards and next values. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Baseline** | an average subtracted from the return to calm the estimate. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **Behaviour cloning** | training a policy by copying an expert's actions at recorded states. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Behaviour tree** | a task written as a tree of steps and ticked every cycle. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Belief** | how likely the robot thinks each place is, one probability per place. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Belief (`est`)** | where the rover thinks it is, which can drift from the true pose. | [16-02](phases/16-capstones/02-mobile-navigation-sim/docs/en.md) |
| **Bias** | a small steady error that is always there. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Box constraint** | every command must stay between `-umax` and `umax`. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **Calibration** | measuring a camera's own numbers, such as zoom and centre, from a target you know. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Callback** | the function that handles each arriving message. | [05-01](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/en.md) |
| **Callback group** | a set of callbacks that share one overlap rule, such as never running together. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **Capture point** | where the body would stop if the foot were placed there. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) |
| **Cartesian space** | ordinary x, y, z positions, as opposed to joint angles. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Cascade** | two loops, an angle loop outside that commands a turning speed to a rate loop inside. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/en.md) |
| **Cell** | one square of the occupancy grid. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) |
| **Chamfer** | a bevelled hole edge that guides the peg in. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) |
| **Chord** | the part of a segment that lies inside a circle. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Clamp** | cut a value back to the allowed range. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Clearance** | the spare distance kept between the path and an obstacle. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Clip** | cut a value so it stays inside a range. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) |
| **Clock offset** | how far one computer's clock runs ahead of another's. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Collision checking** | testing whether a robot pose or motion touches an obstacle. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Common ancestor** | the nearest frame above two frames on the tree, where their paths meet. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) |
| **Compliance** | the ability to give way under a force instead of holding a position rigidly. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) |
| **Compounding error** | a small mistake leads to an unfamiliar state, which causes a bigger mistake. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Computed torque** | using the arm's equations to cancel its dynamics, then controlling what is left. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **Consensus** | all robots agreeing on one value by talking only to neighbours. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) |
| **Contact model** | the rule a simulator uses to compute the forces where two bodies touch. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Control loop** | code that repeats at a fixed rate to read sensors, compute and command the motors. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Control tick** | one step of the controller; here 0.002 s. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) |
| **Controller** | the layer that turns the path into motor commands. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) |
| **Convention** | an agreed rule for reading a table; two conventions can read the same numbers differently. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **Converged** | the error has fallen below the tolerance, here 1e-6 m. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Convex hull** | the tight wrapping around a set of points. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) |
| **Coriolis and centripetal torques (`h`)** | speed-dependent torques that exist because `M` changes with the pose. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) |
| **Coriolis torque** | the pull links exert on each other when they swing fast. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **Cost** | a single number scoring how bad a route is; lower is better. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Cost matrix `C`** | a table of the distance from each robot to each task. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **Cost weights (`Q`, `R`)** | how much error (`Q`) and effort (`R`) hurt. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Coulomb friction (`c`)** | a constant rub against the motion. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) |
| **Count** | one step an encoder reports, here one slot edge passing the reader. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Counterexample** | one state where `vdot` is positive, which breaks the stability claim. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **Covariance (`P`)** | how unsure the estimate is. For one number it is the variance, the spread squared. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **CPR** | counts per revolution, the number of steps in one full turn. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Crossover** | the frequency (cycles per second, Hz) where both paths carry equal weight. | [07-04](phases/07-state-estimation/04-complementary-filter/docs/en.md) |
| **Crossover (`wc`)** | the rate in rad/s (radians per second, an angular speed) where the loop stops amplifying a signal. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) |
| **Curvature (`k`)** | how sharply a path bends. It is `1 / R` for a circle of radius `R`. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **Cycle** | a loop in which a frame becomes its own ancestor. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) |
| **DAgger** | dataset aggregation. The learner drives, the expert labels the visited states, and the labels join the data. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Damped least squares** | an inverse that accepts a small error, set by `lam`, to keep joint speeds bounded. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **Damper** | a brake that pushes against speed with a torque proportional to it. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Damping (`D`)** | resistance to speed. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **Damping gain (`kd`)** | how strongly the damper brakes. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Damping ratio (`zeta`)** | how strongly the damper settles the joint; 1 glides in, below 1 rings. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **Damping term** | `kd * velocity`, a brake that grows with speed. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Dead reckoning** | tracking position by adding up each small movement from a known start. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Deadbeat** | a controller that reaches the target in one step and then stays exact. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Deadline** | the time by which a turn must finish. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Deadlock** | robots waiting on each other in a loop, so none can move. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Deceleration `a`** | how fast the speed drops while braking, in rad/s^2. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/en.md) |
| **Deflection** | how far a push moves the joint from its rest pose. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **Degenerate views** | views that repeat the same clue, so they cannot be solved. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Delay margin** | the longest delay the loop survives, the phase margin divided by the crossover. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) |
| **Depth (`z`)** | how far a point is in front of the camera. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Depth image** | a photo whose pixels store a distance instead of a colour. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Determinant (`det J`)** | one number from a matrix that falls to 0 when the matrix loses a direction. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **Determinant (`det`)** | one number computed from a matrix; zero means the matrix flattens space. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **DH table** | a Denavit-Hartenberg table, one row of four numbers per joint, describing an arm. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **Differential drive** | a robot that steers by spinning its two wheels at different speeds. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Dijkstra** | a search that expands cells in order of the cost already spent reaching them. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Discount (gamma)** | a factor below one that shrinks later rewards, since sooner is better. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Domain randomisation** | tuning a controller across many simulated plants with randomly scaled parameters. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) |
| **Dot product** | multiply matching entries of two lists and add them up; it scores how alike two quaternions are. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Dot product (`.`)** | multiply matching entries of two lists and add them up. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Double integrator** | a car steered by acceleration; position changes by speed, speed by push. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Drift** | a slow error that builds up as rounded numbers are multiplied many times. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) |
| **Drive** | the electronics that power and control the motor. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) |
| **Dynamics** | the equations linking torques to joint motion. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **Effective limit** | the limit the joint really feels, set by the tightest layer. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) |
| **Eigenvalue** | a number for how much one motion pattern is multiplied per tick; the loop is stable if all are below 1 in size. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **EKF** | extended Kalman filter, a Kalman filter that straightens the model at the current estimate. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Elbow down / elbow up** | the two arm shapes that reach the same target. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Encoder** | a sensor that reports how far a shaft has turned, in whole steps. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Energy drift** | simulated energy that creeps up when it should stay constant. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Entropy** | a score of doubt, high when all places look equally likely. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Episode** | one try from start to finish. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **Epsilon** | the grasp's margin: the smallest distance from the hull's inside to its surface. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) |
| **Equilibrium** | a state where nothing moves, such as the arm at rest. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **Euler angles** | three turns applied in a fixed order, named roll, pitch and yaw. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **Euler rates** | how fast each ring is turning. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **Excitation** | how varied the motion in a recording is. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) |
| **Executor** | the part of ROS 2 that decides which ready callback runs next, and on which thread. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **`exp`** | the exponential function, which grows by the same factor in equal time steps. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) |
| **Expanding a cell** | checking that cell's neighbours and adding them to the search. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Explicit / semi-implicit Euler** | two ways to take a step. Explicit moves with the old speed; semi-implicit moves with the new one. | [00-02](phases/00-setup-and-tooling/02-mujoco-hello-world/docs/en.md) |
| **Explicit Euler** | an integrator that moves with the old velocity. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Extrapolate** | guess a value past the newest sample by continuing the last motion. | [05-06](phases/05-robot-software/06-transforms-at-a-time/docs/en.md) |
| **Fake clock** | a clock the test advances by hand. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Fallback** | a parent that tries its children in order and stops at the first success. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **False alarm** | a hit reported for a path that actually clears the obstacle. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Fault injection** | deliberately breaking a sensor, command or timing to see what happens. | [15-01](phases/15-safety-and-deployment/01-failure-modes/docs/en.md) |
| **Feedback gain (`K`)** | the numbers that turn the state into a push, `u = -Kx`. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Feedforward** | a push added in advance from a model, instead of waiting for error. | [16-01](phases/16-capstones/01-arm-pick-and-place-sim/docs/en.md) |
| **Feedforward (`ff`)** | torque added in advance from a model, before any error appears. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Finite difference** | estimating a slope by nudging an input a small step and watching the output. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Focal length (`fx, fy`)** | how strongly the lens zooms in, measured in pixels. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Foot placement** | choosing where the next foot lands in order to control speed. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Force closure** | the contacts can resist a load from any direction. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) |
| **Force control** | moving the tool according to the measured force, not a planned position. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Forward kinematics (FK)** | finding where the tip is from the joint angles. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Frame** | a set of x, y, z axes attached to something, such as a link or the room. | [00-03](phases/00-setup-and-tooling/03-reading-a-urdf/docs/en.md) |
| **Friction** | a rubbing force that drains motion energy. | [12-01](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/en.md) |
| **Friction cone** | all friction forces that do not exceed `mu` times the normal force. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Fuzzing** | throwing many random inputs at code to find breaks. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) |
| **Gain** | a multiplier such as `kp` that sets how strongly a controller reacts. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/en.md) |
| **Gain (`ki`)** | the factor that turns a force error into a tool speed. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Gains** | the numbers `kp` and `kd` that set how hard the controller pushes and brakes. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) |
| **Gauss-Newton** | a method that repeats the step that most reduces the cost, treating residuals as straight lines. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/en.md) |
| **Gaussian kernel** | a weight that is larger for demonstration states nearer the current one. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **Gear ratio (`N`)** | how many motor turns make one output turn. Torque grows `N` times and speed shrinks `N` times. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) |
| **Gimbal lock** | a pose where two rings line up and one direction of turning is lost. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **Goal bias** | the share of samples that are the goal itself, tilting the tree toward it. | [09-02](phases/09-motion-planning/02-rrt/docs/en.md) |
| **Golden trace** | a trusted recording from a healthy run. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Gradient** | the direction in which the cost rises fastest. Stepping against it lowers the cost. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Gradient descent** | repeating small steps against the gradient. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Graph Laplacian `L`** | the matrix `D - A` that encodes who talks to whom. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) |
| **Gravity compensation** | adding a model's estimate of the arm's weight as torque in advance. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Greedy** | choosing the best-looking option at each step without looking ahead. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **Greedy policy** | in each state, take the action with the best score. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Guard** | a check where data enters your code that stops bad data with a clear error. | [00-01](phases/00-setup-and-tooling/01-python-env-and-numpy/docs/en.md) |
| **Gyro** | a sensor that measures how fast something turns. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Hand-eye calibration** | finding where a camera sits relative to the gripper it is mounted on. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) |
| **Hard stop** | a block that ends the joint's travel. | [15-01](phases/15-safety-and-deployment/01-failure-modes/docs/en.md) |
| **Heading** | the direction the robot faces. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Heartbeat** | the regular "still here" message from the program that commands the joint. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/en.md) |
| **Held-out data** | examples kept aside from training to test a model. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Heuristic (`h`)** | the guess of the remaining cost to the goal. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **High-pass / low-pass** | a filter that keeps fast changes, or one that keeps the slow average. | [07-04](phases/07-state-estimation/04-complementary-filter/docs/en.md) |
| **Hold-and-wait** | holding a cell while waiting for the next one. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Homography (`H`)** | a 3x3 matrix that maps points on the flat board to pixels. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Horizon (`N`)** | how many steps ahead each plan looks. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **Host** | the computer that runs the controller loop. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Hover** | staying at one height with zero acceleration. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Hungarian method** | an algorithm that finds the assignment with the lowest total cost. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **Hybrid control** | position control on some axes and force control on the others. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Hz** | times per second. | [00-04](phases/00-setup-and-tooling/04-ros2-in-one-page/docs/en.md) |
| **ICP** | iterative closest point, the loop of pairing nearest dots and fitting a move. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) |
| **Imitation learning** | teaching a robot by fitting a function to examples of an expert's behaviour. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **Impedance** | how a joint pushes back when pushed, like a spring plus a damper. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **IMU** | a motion sensor made of a gyro and an accelerometer. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Inertia** | how hard something is to spin up. A heavy flywheel has a lot. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) |
| **Inertia (`J`)** | how hard a joint is to speed up or slow down. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Inertia matrix (`M`)** | how heavy the arm feels to each joint; it changes with the elbow angle. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **Inlier** | a point close enough to a plane to count as lying on it. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Innovation** | the surprise `z - H x`, the reading minus what the model expected. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **Integral** | a running total of the error; it keeps growing while any error remains. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/en.md) |
| **Integrate** | add readings up over time, turning turn speed into angle or acceleration into speed. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Integration** | adding up a rate over time to get a total, like speed to distance. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Integrator** | the update rule that turns force and speed into the next position. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Intent** | what a step is supposed to achieve. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Interpolate** | estimate a value between two known samples. | [05-06](phases/05-robot-software/06-transforms-at-a-time/docs/en.md) |
| **Interpolator** | code that moves smoothly between a start value and a target value. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Intrinsics (`K`)** | the matrix (a grid of numbers) holding `fx, fy, cx, cy`. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Inverse** | the transform that undoes another one. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) |
| **Inverse kinematics (IK)** | finding joint angles that put the hand on a target. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Inverted pendulum** | a mass balanced on top of a leg, like a pencil on its tip; it falls if not held. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) |
| **Jacobian** | the matrix that predicts how the tip moves for a small joint change. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Jacobian (`F`, `H`)** | the matrix of slopes that says how a small change in the state changes the output. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Jacobian (`J`)** | a matrix that turns joint speeds into tip velocity for the current pose. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Jacobian inverse** | the matrix that turns a wanted tip velocity back into joint speeds. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **Jam** | the peg stops and pushing harder only holds it more firmly. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) |
| **Jerk** | how fast the acceleration changes. A jump in acceleration is a spike in jerk. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) |
| **Jitter** | how far a turn's real timing is from the plan. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Joint** | the connection that lets a child link move relative to its parent link. | [00-03](phases/00-setup-and-tooling/03-reading-a-urdf/docs/en.md) |
| **Joint angle (`q`)** | how far a joint is turned from its zero position. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Joint limit** | how far a joint may turn; the joint stops there. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Kalman gain (`K`)** | how far the estimate moves toward a new reading, from 0 (ignore it) to 1 (trust it fully). | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **Kidnap** | the robot is picked up and put somewhere else without being told. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **Kinetic energy (`T`)** | the energy of motion; for an arm `T = 1/2 qd' M qd`, where `qd'` is the speed list written sideways. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) |
| **Lag** | the delay before the wheels follow a steering command. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **Lagrange equation** | a rule that turns kinetic energy into joint torques by differentiating. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) |
| **`lambda2`** | the second-smallest eigenvalue of `L`. It sets the agreement speed. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) |
| **Landmark** | a post at a known place that the robot measures. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Latency** | the delay between measuring something and the motor acting on it. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) |
| **Law of cosines** | a rule that gives a triangle's angle from its three side lengths. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Learned policy** | a trained model that maps what the robot sees to an action. | [16-03](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/en.md) |
| **Learner** | the policy being trained. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Least squares** | a fit that minimises the sum of squared distances, so far points pull hard. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Level set** | all states with the same value of `V`, drawn as a curve. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **Likelihood** | how well a place explains a sensor reading. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Linearise** | replace a curve by its straight-line approximation at one point. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Link** | one rigid part of the robot, such as an upper arm. | [00-03](phases/00-setup-and-tooling/03-reading-a-urdf/docs/en.md) |
| **Local minimum** | a dead end where small moves no longer reduce the error, although the answer is wrong. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) |
| **Log-odds (`L`)** | a cell's evidence score. Positive means probably occupied, negative probably free, and 0 unknown. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) |
| **Lookahead (`Ld`)** | that fixed distance; the one knob you tune. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **Loop closure** | recognising a place already visited, which adds one more spring. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/en.md) |
| **Low-pass filter** | a smoother that blurs fast changes. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **LQR** | a method that computes a feedback gain from a model and a cost for error and effort. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Lyapunov function (`V`)** | an energy-like number that never rises along the motion of a stable system. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **Manhattan distance** | cells across plus cells down, ignoring walls. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Manipulability** | a score, `sqrt(det(J J^T))`, for how freely the tip can move; it peaks at a right-angle elbow. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **MDP** | Markov decision process. States, actions, transition chances and rewards. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Mean policy** | a policy that predicts the average action of nearby demonstrations. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **Measurement noise (`R`)** | the variance of the sensor's error. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **Mock joint** | a pretend arm that refuses bad torque. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Mode** | one independent pattern of disagreement. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) |
| **Model predictive control (MPC)** | plan a short future under the limits, apply the first command, then plan again. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **Monitor** | a cheap check on signals the controller can see that raises an alarm. | [15-01](phases/15-safety-and-deployment/01-failure-modes/docs/en.md) |
| **Motor lag** | the delay before the motor's push catches up with the command. | [12-01](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/en.md) |
| **`mu`** | the friction coefficient; how grippy the surfaces are. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **MuJoCo** | a free physics engine, a ready-made simulator we compare our loop against. | [00-02](phases/00-setup-and-tooling/02-mujoco-hello-world/docs/en.md) |
| **Multimodal** | having several different correct answers, called modes. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **`nan`** | "not a number", the result of an impossible calculation such as `acos` of a value above 1. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Nearest neighbour** | the closest dot in the other scan. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) |
| **Nearest neighbours** | a fit that copies the actions of the closest recorded examples. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **Nearest-neighbour policy** | averages the actions of the closest recorded demonstrations. | [16-03](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/en.md) |
| **NEES** | the error in units of the filter's own claimed uncertainty. It should average the state size. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Nested limits** | each layer allows no more than the next layer. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) |
| **Newton-Euler** | a second method that adds up each link's forces and moments instead of using energy. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) |
| **Node** | one running program in a ROS 2 system. | [00-04](phases/00-setup-and-tooling/04-ros2-in-one-page/docs/en.md) |
| **Nominal plant** | the simulated arm with unscaled, average parameters. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) |
| **Normal force** | the push of a surface straight out of itself, perpendicular to the surface. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Numerical IK** | finding joint angles by repeated small corrections instead of a formula. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Observation** | what the robot senses. Here it is its position `x` on a plane. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **Occupancy grid** | a map split into small squares, each holding a score for "something is here". | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) |
| **Odometry** | a position guess made by adding up how far the wheels turned. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Open-loop** | sending commands without sensor feedback to correct them. | [12-01](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/en.md) |
| **Overshoot** | passing the final position before coming back. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **p99** | the delay that 99% of cycles stay under. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Padding** | growing the obstacle by a margin so the check errs on the safe side. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Particle** | one guess of the robot's pose, `(x, y, heading)`. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **Particle filter** | a crowd of particles that is moved, scored by measurements and resampled. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **PD control** | a spring on the angle plus a brake on the rate. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **PD controller** | pushes by the error and brakes by the speed. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **PD loop** | a controller that pulls toward a target with `kp` and brakes with `kd`. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) |
| **Penalty** | extra cost added when a waypoint gets too close to an obstacle. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Pendulum** | a weight on a rod that swings under gravity; the simplest test for a simulator. | [00-02](phases/00-setup-and-tooling/02-mujoco-hello-world/docs/en.md) |
| **Penetration** | how far a simulated body sinks into a surface. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Period** | the time for one full swing out and back. | [00-02](phases/00-setup-and-tooling/02-mujoco-hello-world/docs/en.md) |
| **Period (`T`)** | the planned time between two turns of the loop. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Phase margin** | how much lag, as an angle, the loop absorbs at crossover before it oscillates. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) |
| **PID** | a controller that adds a P term (the error), an I term (the error summed over time) and a D term (a speed brake). | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Pitch (`theta`)** | the tilt angle of the drone body. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Pixel** | one dot of a camera image. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Planner** | the layer that draws the path and sets the speed it asks for. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) |
| **Plant** | the thing being controlled, here the joint and motor. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Point cloud** | a set of 3D points, here made by unprojecting every depth pixel. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Policy** | the function that maps an observation to an action. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **Policy gradient** | nudging the policy's numbers toward actions that earned above-average return. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **Pose** | an object's orientation plus its position. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) |
| **Pose graph** | poses as unknowns, joined by measurements that act like springs. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/en.md) |
| **Position gain (`kp`)** | how hard the motor pushes the arm back per radian of error. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Position mode** | your program gives a target angle, and the drive's own controller picks the torque. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/en.md) |
| **Positive definite** | every motion has positive kinetic energy. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) |
| **Predict** | the step that slides and blurs the belief by the move, adding doubt. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Preemption** | the operating system pausing your program to run another one. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Principal point (`cx, cy`)** | the pixel where the camera's centre line lands. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Prior / posterior** | the belief before and after a reading. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Process noise (`Q`)** | doubt added each step because the real motion may differ from the model. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **Projection** | turning a 3D point into a pixel. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Property test** | throws many random inputs at one rule. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Publisher / Subscriber** | the sender and the listener on a topic. | [05-01](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/en.md) |
| **Pure pursuit** | steering a robot toward a point on the path a fixed distance ahead. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **QoS** | quality of service, the settings that decide how messages are kept and delivered. | [00-04](phases/00-setup-and-tooling/04-ros2-in-one-page/docs/en.md) |
| **Quadratic** | a cost shaped like a bowl, easy to minimise. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **Quadrotor** | a drone with four propellers. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Quantisation** | rounding a smooth value to whole steps, so small changes stay invisible. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Quasi-static** | moving so slowly that speeds and inertia can be ignored. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) |
| **Quaternion** | four numbers that name an orientation; a unit quaternion has length one. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Queue depth** | how many messages a subscriber keeps while it waits to read them. | [00-04](phases/00-setup-and-tooling/04-ros2-in-one-page/docs/en.md) |
| **Quintic** | a polynomial of degree 5, the lowest that can fix position, speed and acceleration at both ends. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) |
| **rad/s** | radians per second, a spin speed. One full turn is about 6.28 radians. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Radian** | a unit of angle where one full turn is about 6.28. Degrees use 360 for a full turn. | [00-01](phases/00-setup-and-tooling/01-python-env-and-numpy/docs/en.md) |
| **Radian (rad)** | an angle unit where one full turn is about 6.28. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Rank** | the number of independent directions the wrenches span. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) |
| **RANSAC** | try planes from random points and keep the one with the most points near it. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Rate limit** | a cap on how much a command may change per tick. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) |
| **Ray** | the line of sight through a pixel. Every point on it lands on that pixel. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Reach band** | the ring of targets the arm can touch, between `/L1 - L2/` and `L1 + L2` from the base. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Reference** | the planned path the arm should follow. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **Replay test** | feeds recorded readings back and compares the torque. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Reprojection error** | how far corners projected with your numbers land from the corners seen. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Resampling** | copying high-weight particles and dropping low-weight ones, keeping the count fixed. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **Reservation** | claiming a whole route before entering it. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Residual** | the model's error, the gap between `ff` and the torque gravity really needs. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Return** | the total reward of one episode. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **Reward-to-go** | the rewards from the current step to the end of the episode. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **Riccati recursion** | a repeated calculation that turns the model and weights into the gain `K`. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Rigid move** | a turn plus a slide that keeps all distances inside the shape unchanged. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) |
| **rms error** | root mean square, the typical distance of a pose from the truth. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/en.md) |
| **Robot frame** | coordinates that move with the robot, x forward and y left. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **Roll, pitch, yaw** | turns about the forward axis, the side axis and the vertical axis. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **Rollout** | one test drive of a policy from a start state. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Rotation axis** | the line a rotation spins about. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) |
| **Rotation matrix** | a small grid of numbers that turns a point around an axis. | [00-01](phases/00-setup-and-tooling/01-python-env-and-numpy/docs/en.md) |
| **Round trip** | the time a request takes to go out plus its reply to come back. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **RRT** | rapidly-exploring random tree, a planner that grows a tree of short steps by random sampling. | [09-02](phases/09-motion-planning/02-rrt/docs/en.md) |
| **Safety wrapper** | a fixed layer between a policy and the motor that limits every command. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) |
| **Sag** | how far the arm ends up below (or above) its commanded angle. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Sampler** | picks one demonstration at random instead of averaging. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **Saturation** | the motor is at its torque limit and cannot push harder. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Seed** | the starting pose of one run. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Segment** | the straight stretch between two path points. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Selection matrix (`S`)** | a switch per axis choosing force law or position law. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Semi-implicit Euler** | an integrator that updates velocity first, then moves with the new one. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Sensor fusion** | merging readings from several sensors into one estimate. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Sequence** | a parent that runs its children in order and stops at the first failure. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Service** | a request with one reply, unlike a topic's endless stream. | [00-04](phases/00-setup-and-tooling/04-ros2-in-one-page/docs/en.md) |
| **Settling** | staying within a small band around the target. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) |
| **Shortcutting** | replacing part of a path with a straight segment when that segment is free. | [09-02](phases/09-motion-planning/02-rrt/docs/en.md) |
| **Simulation** | a program that predicts how something moves by repeating one small time step many times. | [00-02](phases/00-setup-and-tooling/02-mujoco-hello-world/docs/en.md) |
| **Singular value** | how much a matrix stretches one direction; a small one means a nearly lost direction. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **Singularity** | a pose where the arm loses a direction of tip motion, such as a fully straight arm. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **`sinh`, `cosh`** | curves built from `exp(t/Tc)` and `exp(-t/Tc)`; they describe the falling body. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **SLAM** | mapping and locating at once, because each needs the other. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) |
| **Slerp** | a smooth, even-speed turn between two orientations. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Spread** | the half-angle of the cone that the motions' axes fill. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) |
| **Stable** | a disturbance dies out instead of growing. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/en.md) |
| **Stale observation** | a camera picture older than the wrapper allows. | [16-03](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/en.md) |
| **Stall torque** | the push a motor gives when held still, its strongest. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) |
| **Stance** | the time one foot stays on the ground. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Starvation** | a callback waits too long because another one holds the thread. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **State** | the values that predict future motion, such as position and speed. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **State (`x`)** | the numbers the filter tracks, here position and velocity. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **State machine** | a table of named states with an arrow for each event. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Status** | the answer a node gives, `success`, `failure` or `running`. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Steady offset** | the error left when a constant load pushes against P+D alone. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Step size `eps`** | how far each robot moves toward its neighbours per tick. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) |
| **Stick and slip** | two states of a contact; holding still, or sliding. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Stiff contact** | a very hard surface that needs small steps. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Stiffness (`K`)** | push back per unit of deflection. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **Stiffness (`ke`)** | the newtons a surface pushes back per metre squeezed. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Stiffness (`kx`)** | the sideways force per metre the wrist is stretched. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) |
| **SVD** | a matrix tool. Its smallest singular vector solves "make this product as close to zero as possible". | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Sweep** | one backup of every state. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **System identification** | fitting a model's unknown numbers to a recording of the real system. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) |
| **`T_to_from`** | a transform that converts coordinates from the `from` frame into the `to` frame. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) |
| **Task allocation** | deciding which robot does which task. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **`Tc`** | the time scale of the body's fall, from lesson 01. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Terminal cost** | a price on where the plan ends, so a short plan still sees what comes after. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **tf2** | the ROS 2 library that stores a transform tree. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) |
| **Thread** | one worker inside a program, doing one job at a time. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **Throughput** | the number of jobs finished per tick. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Thrust (`T`)** | the total upward push of the propellers. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Tick** | one small step, where the tree is asked to do a little work and report. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Tick (`dt`)** | one control step, the time between two controller readings. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Time constant** | the time in which an error shrinks by about two thirds. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Time constant (`tau`)** | how long the gyro is trusted before the accelerometer takes over. | [07-04](phases/07-state-estimation/04-complementary-filter/docs/en.md) |
| **Time constant (`Tc`)** | the time in which tipping grows by a factor of 2.7. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) |
| **Time stamp** | the time written on a reading by the clock of the computer that took it. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Time step (`dt`)** | how far the simulation jumps forward in time on each step, here a few hundredths of a second. | [00-02](phases/00-setup-and-tooling/02-mujoco-hello-world/docs/en.md) |
| **Timeout `T`** | how long silence is tolerated before the watchdog trips. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/en.md) |
| **Tip** | the end of the arm, where the hand or tool sits. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Tip pose** | the position and orientation of the end of the arm. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Tolerance** | a tiny allowed error, so rounding noise is not treated as a failure. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Topic** | a named stream that publishers send to and subscribers read from. | [00-04](phases/00-setup-and-tooling/04-ros2-in-one-page/docs/en.md) |
| **Torque** | the twisting force a motor applies to a joint. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Torque (`tau`)** | a twisting force, such as a motor's push on a joint. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Torque mode** | your program tells the drive how hard to twist, and the drive obeys. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/en.md) |
| **Touchdown** | the moment a swinging foot lands. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Trace** | a log with one record per step, holding the state before and after. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Track width (`b`)** | the distance between the two wheels. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Trajectory profile** | the plan of how a joint's position changes over time between two poses. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) |
| **Transform** | a 4x4 table of numbers holding one turn and one shift. | [00-03](phases/00-setup-and-tooling/03-reading-a-urdf/docs/en.md) |
| **Transform (`T`)** | a 4x4 matrix that stores a rotation and a shift in one table. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) |
| **Transform (`X`)** | the rotation and shift that take one frame to another, here camera to gripper. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) |
| **Transform tree** | a map where each frame hangs off exactly one parent frame. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) |
| **Transpose (`.T`)** | swaps the rows and columns of a matrix. | [00-01](phases/00-setup-and-tooling/01-python-env-and-numpy/docs/en.md) |
| **Transpose (`J^T`)** | the same matrix with its rows and columns swapped. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Tunnelling** | a motion slipping through a thin obstacle because the checks are too far apart. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Twist (`alpha`)** | how far the next joint axis tilts relative to this one. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **Unit test** | steps the fake clock and checks one rule. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Update** | the step that reweights the belief by how well each place explains a reading. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **URDF** | a text file that describes a robot as links joined by joints. | [00-03](phases/00-setup-and-tooling/03-reading-a-urdf/docs/en.md) |
| **URDF origin** | in the robot file ROS reads, a joint's position (`xyz`) and rotation (`rpy`: roll, pitch, yaw) relative to its parent. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **Value `V(s)`** | the expected reward-to-go from state s, assuming the best actions afterwards. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Variance** | how much an estimate jumps around between runs. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **`vdot` (`dV/dt`)** | how fast `V` changes as the system moves. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **venv** | a private folder of packages for one project. | [00-01](phases/00-setup-and-tooling/01-python-env-and-numpy/docs/en.md) |
| **Viscous damping (`b`)** | a drag that grows with speed. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) |
| **Voxel grid** | small cubes cutting up space. Keeping one averaged point per cube thins the cloud. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Wait-for graph** | arrows from each robot to the robot it waits for. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Watchdog** | a guard that stops the robot when a heartbeat is late. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **Waypoint** | one point on the route; the route is a chain of them. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Weight** | a score for how well a particle's predicted distances match the measured ones. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **Wheel radius (`r`)** | the distance from a wheel's center to its edge. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Width (`w`)** | how far each parameter may be scaled, as a fraction. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) |
| **Window** | the number of samples between the two counts you compare to get a speed. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Windup** | the integral keeps growing while saturated, then causes overshoot. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Workspace** | every place the tip can reach. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Wrench** | a push and a twist packed together; in 2-D, three numbers `(fx, fy, torque)`. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) |
| **Zero pose** | the arm with every joint angle at 0. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **ZMP** | zero-moment point, the spot under the foot where the ground's push acts. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) |
