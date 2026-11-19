# Glossary

Every term from the lessons' Key Terms, A to Z, with the lesson that introduces it.

| Term | Meaning | Lesson |
|---|---|---|
| **A-star** | Dijkstra plus a guess of the steps still to go, so it heads toward the goal. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Acceleration** | how much the speed changes in one second. | [00-06](phases/00-start-here/06-time-steps/docs/en.md) |
| **Accelerometer** | measures push (acceleration), and also feels gravity. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Action** | what the robot does next. Here it is a driving direction. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **Action chunk** | the next few actions, chosen together. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **Actuator** | a part that makes motion, such as a motor that turns a wheel. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/en.md) |
| **Admissible** | a guess that never exaggerates. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Admittance layer** | code that measures a push and moves the target so the joint acts soft. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/en.md) |
| **Agreement speed (`lambda2`)** | one number, read off the neighbour table, that sets how fast the robots agree. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) |
| **Angle** | how much something has turned from its starting direction. | [00-03](phases/00-start-here/03-angles-and-radians/docs/en.md) |
| **Array shape** | how many rows and columns an array has, such as 5 rows by 3 columns. | [00-07](phases/00-start-here/07-python-env-and-numpy/docs/en.md) |
| **Assignment** | a one-to-one pairing of robots and jobs. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **At sign (`@`)** | the symbol numpy uses to multiply a table by a point. | [00-05](phases/00-start-here/05-turning-a-point/docs/en.md) |
| **Attitude** | how the drone is tilted in space. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/en.md) |
| **Back-EMF** | the voltage a spinning motor makes against its own supply. It weakens the push. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) |
| **Baseline** | an average subtracted from the score so good moves stand out. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **Behaviour cloning** | training a policy to copy an expert's actions at recorded spots. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Behaviour tree** | a task written as a tree of steps and ticked every cycle. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Belief** | how likely the robot thinks each place is, one probability per place. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Belief (`est`)** | where the rover thinks it is, which can drift from the truth. | [16-02](phases/16-capstones/02-mobile-navigation-sim/docs/en.md) |
| **Bias** | a small steady error that is always there. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Box constraint** | every push must stay within plus or minus the biggest allowed push. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **Calibration** | measuring a camera's own numbers, such as zoom and centre, from a target you know. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Callback** | the function that handles each arriving message. | [05-01](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/en.md) |
| **Callback group** | a set of callbacks with one shared rule about running together, such as never at the same time. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **Capture point** | the spot where placing the foot stops the fall. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) |
| **Cartesian space** | ordinary x, y, z positions, as opposed to joint angles. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Cascade** | two loops, an angle loop outside that commands a turning speed to a rate loop inside. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/en.md) |
| **Chamfer** | a slanted hole edge that guides the peg in. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) |
| **Clamp** | cut a value back to the allowed range. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Clearance** | the spare distance kept between the path and an obstacle. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Clip** | cut a value so it stays inside a range. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) |
| **Clock offset** | how far one computer's clock runs ahead of another's. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Collision checking** | testing whether a robot pose or motion touches an obstacle. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Compliance** | the ability to give way under a force instead of holding a position rigidly. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) |
| **Compounding error** | a small slip leads to an unfamiliar spot, which causes a bigger slip. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Computed torque** | using the arm's equations to cancel its dynamics, then controlling what is left. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **Consensus** | all robots agreeing on one value by talking only to neighbours. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) |
| **Contact model** | the rule a simulator uses to compute the forces where two bodies touch. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Control loop** | code that repeats at a fixed rate to read sensors, compute and command the motors. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Control tick** | one step of the program that drives the motor; here 0.002 s. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) |
| **Controller** | the layer that turns the path into motor commands. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) |
| **Convention** | an agreed rule for reading a table; two conventions can read the same numbers differently. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **Converged** | the error has fallen below the tolerance, here one millionth of a metre. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Convex hull** | the tight wrapping around a set of points. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) |
| **Coordinates** | the numbers that name a point: how far across and how far up. | [00-02](phases/00-start-here/02-points-as-numbers/docs/en.md) |
| **Coriolis torque** | the pull links exert on each other when they swing fast. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **cos and sin** | two calculator buttons that turn an angle into "how far across" and "how far up" for a bar of length one. | [00-04](phases/00-start-here/04-joints-and-links/docs/en.md) |
| **Cost** | a score for how bad a plan is. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **Cost matrix `C`** | a table of how far each robot is from each job. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **Cost weights** | numbers saying how much error hurts and how much effort hurts. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Count** | one step an encoder reports, here one slot edge passing the reader. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Counterexample** | one state where the slope is positive, so this energy-like number fails the test. Another number might still work. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **Covariance (`P`)** | how unsure the estimate is. For one number it is the spread squared. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **CPR** | counts per revolution, the number of steps in one full turn. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Crossover** | the speed of change, in cycles per second (Hz), where gyro and accelerometer count equally. | [07-04](phases/07-state-estimation/04-complementary-filter/docs/en.md) |
| **Curvature (`k`)** | how sharply a path bends. A tight turn has a large curvature. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **DAgger** | the learner drives, the expert marks the right move at the spots it reached, and the marks join the training data. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Damped least squares** | a way of finding joint speeds that allows a small error so the speeds never pass a cap. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **Damper** | a brake that pushes against speed with a torque proportional to it. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Damping (`D`)** | resistance to speed. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **Damping gain (`kd`)** | how strongly the damper brakes. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Damping ratio (`zeta`)** | how strongly the damper calms the joint: at 1 it glides in, below 1 it wobbles. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **Damping term** | a brake that grows with speed, so a fast joint is braked harder. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Deadbeat** | a rule that hits the target speed in one step and stays there. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Deadline** | the time by which a cycle must finish. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Deadlock** | robots waiting on each other in a loop, so none can move. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Deceleration `a`** | how fast the speed drops while braking. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/en.md) |
| **Deflection** | how far a push moves the joint from its rest pose. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **Degenerate views** | views that repeat the same clue, so they cannot be solved. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Degree** | one slice when a full turn is cut into 360 equal slices. | [00-03](phases/00-start-here/03-angles-and-radians/docs/en.md) |
| **Delay margin** | the longest delay the loop can take before it starts to swing. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) |
| **Depth (`z`)** | how far a point is in front of the camera. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Depth image** | a photo whose pixels store a distance instead of a colour. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **DH table** | a Denavit-Hartenberg table, one row of four numbers (two lengths and two angles) per joint, describing an arm. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **Differential drive** | a robot that steers by spinning its two wheels at different speeds. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Dijkstra** | a search that expands squares in order of the steps already spent reaching them. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Discount (gamma)** | a number below one that makes later rewards count a little less. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Distance** | the straight-line gap between two points. | [00-02](phases/00-start-here/02-points-as-numbers/docs/en.md) |
| **Domain randomisation** | tuning a controller across many simulated robots whose numbers are randomly changed. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) |
| **Dot product** | multiply matching numbers of two quaternions and add them up. Negative means the smooth turn between them would take the long way round. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Double integrator** | a car steered by acceleration; position changes by speed, speed by push. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Drag (`b`)** | a push-back that grows with speed. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) |
| **Drift** | a slow error that builds up as rounded numbers are multiplied many times. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) |
| **Drive** | the electronics that power and control the motor. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) |
| **Dynamics** | the equations linking torques to joint motion. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **Effective limit** | the limit the joint really feels, set by the tightest layer. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) |
| **EKF** | extended Kalman filter, a program that tracks where the robot is, using a straight-line rule at its current guess. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Elbow down / elbow up** | the two arm shapes that reach the same target. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Encoder** | a sensor that reports how far a shaft has turned, in whole steps. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Energy drift** | a simulated crate or pendulum gaining bounce or swing that it should not have. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Entropy** | a score of doubt, high when all places look equally likely. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Epsilon** | how far the grasp is from failing; zero means it fails. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) |
| **Euler angles** | three turns applied in a fixed order, named roll, pitch and yaw. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **Euler rates** | how fast each ring is turning. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **Excitation** | how varied the motion in a recording is. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) |
| **Executor** | the part of ROS 2 that decides which ready callback runs next, and on which thread. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **Expanding a square** | trying that square: checking its neighbours and adding them to the search. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Explicit / semi-implicit Euler** | two ways to take a step. Explicit uses the old speed; semi-implicit uses the new speed. Euler is a name. | [00-08](phases/00-start-here/08-mujoco-hello-world/docs/en.md) |
| **Extrapolate** | guess a value past the newest sample by continuing the last motion. | [05-06](phases/05-robot-software/06-transforms-at-a-time/docs/en.md) |
| **Fake clock** | a clock the test moves forward by hand. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Fallback** | a step that tries the steps under it in order and stops at the first success. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **False alarm** | a hit reported for a path that actually clears the obstacle. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Fast-motion torques (`h`)** | twisting pushes that appear when the arm moves fast, because how heavy it feels changes with its pose. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) |
| **Fault injection** | deliberately breaking a sensor, command or timing to see what happens. | [15-01](phases/15-safety-and-deployment/01-failure-modes/docs/en.md) |
| **Feedback gain** | the numbers that turn the state into a push (the push is minus the gain times the state). | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Feedforward** | a push worked out before the arm moves, not after an error shows. | [16-01](phases/16-capstones/01-arm-pick-and-place-sim/docs/en.md) |
| **Feedforward (`ff`)** | torque added in advance from a model, before any error appears. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Finite difference** | estimating a slope by nudging an input a small step and watching the output. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Focal length (`fx, fy`)** | how strongly the lens zooms in, across and up. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Foot placement** | choosing where the next foot lands in order to control speed. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Force closure** | the contacts can resist any outside push or twist. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) |
| **Force control** | moving the tool according to the measured force, not a planned position. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Forward kinematics (FK)** | finding where the tip is from the joint angles. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Frame** | a set of x, y, z axes attached to something, such as a link or the room. | [00-09](phases/00-start-here/09-reading-a-urdf/docs/en.md) |
| **Friction** | rubbing that slowly drains movement. | [12-01](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/en.md) |
| **Friction coefficient (`mu`)** | how grippy the surfaces are. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Friction cone** | the allowed combinations of normal force and sideways friction force at a contact. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Full turn** | one complete trip around, back to the direction you started in. | [00-03](phases/00-start-here/03-angles-and-radians/docs/en.md) |
| **Fuzzing** | throwing many random inputs at code to see if it breaks. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) |
| **Gain** | how strongly a controller reacts, such as push per unit of error. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Gain (`ki`)** | the factor that turns a force error into a tool speed. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Gains** | the two numbers that set how hard the controller pushes and brakes. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) |
| **Gear ratio (`N`)** | how many motor turns make one output turn. Torque grows by that number and speed shrinks by it. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) |
| **Gimbal** | three nested rings that let something turn in any direction. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **Gimbal lock** | a pose where two rings line up and one direction of turning is lost. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **Goal bias** | how often the random spot is chosen to be the goal, which pulls the tree toward it. | [09-02](phases/09-motion-planning/02-rrt/docs/en.md) |
| **Golden trace** | a trusted recording from a healthy run. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Gradient** | the direction in which the cost rises fastest. Step the opposite way and the cost drops. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Gradient descent** | repeating small steps the opposite way to the gradient. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Gravity compensation** | adding a model's estimate of the arm's weight as torque in advance. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Greedy** | picking what looks best right now without looking ahead. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **Greedy policy** | at each square, take the move with the best score. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Guard** | a check on numbers as they arrive that stops bad ones with a clear error. | [00-07](phases/00-start-here/07-python-env-and-numpy/docs/en.md) |
| **Gyro** | a sensor that measures how fast something turns. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Hand** | the tip of the last link, the point we want to place. | [00-04](phases/00-start-here/04-joints-and-links/docs/en.md) |
| **Hand-eye calibration** | finding where a camera sits on the robot's hand (its gripper). | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) |
| **Hard stop** | a block that ends the joint's travel. | [15-01](phases/15-safety-and-deployment/01-failure-modes/docs/en.md) |
| **Heading** | the direction the robot faces. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Heartbeat** | a regular "still here" message from the program that commands the joint. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/en.md) |
| **Heuristic (`h`)** | the guess of the steps remaining to the goal. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Hold-and-wait** | keeping your square while waiting for the next one. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Homography (`H`)** | a 3x3 table of numbers that turns a spot on the flat board into a pixel. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Horizon (`N`)** | how many steps ahead each plan looks. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **Host** | the computer that runs the controller loop. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Hover** | staying at one height. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Hungarian method** | a step-by-step way to find the assignment with the lowest total distance. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **Hybrid control** | position control on some axes and force control on the others. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Hypotenuse** | the slanted long side of a triangle that has one square corner. | [00-02](phases/00-start-here/02-points-as-numbers/docs/en.md) |
| **ICP** | iterative closest point, the loop of pairing nearest dots and fitting a move. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) |
| **Imitation learning** | teaching a robot by showing it examples of an expert doing the task. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **Impedance** | how a joint pushes back when pushed, like a spring plus a damper. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **IMU** | a motion sensor made of a gyro and an accelerometer. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Inertia** | how hard something is to spin up. A heavy wheel has a lot. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/en.md) |
| **Inertia (`J`)** | how hard a joint is to speed up or slow down. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Inertia matrix (`M`)** | how heavy the arm feels to each joint; it changes with the elbow angle. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **Inlier** | a point close enough to a plane to count as lying on it. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Innovation** | the surprise, the reading minus what the filter expected. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **Integral** | a running total of the error; it keeps growing while any error remains. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/en.md) |
| **Integrate** | add readings up over time, turning turn speed into angle or acceleration into speed. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/en.md) |
| **Integration** | adding up a rate over time to get a total, like speed to distance. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Integrator** | the rule that moves the simulation forward by one step. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Intent** | what a step is supposed to achieve. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Interpolate** | estimate a value between two known samples. | [05-06](phases/05-robot-software/06-transforms-at-a-time/docs/en.md) |
| **Intrinsics (`K`)** | the matrix (a table of numbers) holding a camera's own zoom and centre values. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Inverse** | the transform that undoes another one. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) |
| **Inverse kinematics (IK)** | finding joint angles that put the hand on a target. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Inverted pendulum** | a weight balanced on top of a leg, like a pencil on its tip; it falls if not held. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) |
| **Jacobian** | a table of numbers that predicts how the tip moves for a small joint change. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Jacobian (`F`, `H`)** | a table of slopes. It says how much the filter's prediction changes when the robot's position and heading change a little. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Jacobian (`J`)** | a table of numbers that turns joint speeds into the tip's speed and direction for the current pose. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Jacobian inverse** | the table that turns a wanted hand motion back into joint speeds. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **Jam** | the peg stops because wall friction holds against the push. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) |
| **Jerk** | how fast the acceleration changes. A jump in acceleration is a spike in jerk. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) |
| **Jitter** | how far a cycle's real timing is from the plan. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Joint** | a hinge that turns. How far it has turned is an angle. | [00-04](phases/00-start-here/04-joints-and-links/docs/en.md) |
| **Joint angle (`q`)** | how far a joint is turned from the position where its angle is 0. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Joint angles (`q`)** | how far each joint has turned. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) |
| **Joint limit** | how far a joint may turn; the joint stops there. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Joint offset (`<origin>`)** | how far a joint sits from the part before it and how much it is turned, in that part's own directions. | [00-09](phases/00-start-here/09-reading-a-urdf/docs/en.md) |
| **Joint offset (URDF origin)** | in the robot description file, how far a joint sits from the part before it and how much it is turned. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **Kalman gain (`K`)** | how far the estimate moves toward a new reading, from 0 (ignore it) to 1 (trust it fully). | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **Kidnap** | the robot is picked up and put somewhere else without being told. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **Kinetic energy** | the energy something has because it is moving. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) |
| **Lag** | the delay before the wheels follow a steering command. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **Lagrange equation** | a rule that turns the arm's energy of motion into joint torques (the maths is in the fold). | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/en.md) |
| **Landmark** | a post at a known place that the robot measures. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Latency** | the delay between measuring something and the motor acting on it. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) |
| **Law of cosines** | a rule that gives a triangle's angle from its three side lengths. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Learned policy** | a trained model that turns what the robot sees into an action. | [16-03](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/en.md) |
| **Learner** | the policy being trained. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **Least squares** | a best-fit rule where every point pulls on the plane, and far points pull hardest. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Level set** | all states with the same energy-like number, drawn as a curve. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **Likelihood** | how well a place explains a sensor reading. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Linearise** | replace a curve by its straight-line approximation at one point. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Link** | a stiff bar between two joints. It never bends or stretches. | [00-04](phases/00-start-here/04-joints-and-links/docs/en.md) |
| **Local minimum** | a dead end where small moves no longer reduce the error, although the answer is wrong. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) |
| **Log-odds (`L`)** | a square's evidence score. Positive means probably occupied, negative probably free, and 0 unknown. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) |
| **Lookahead (`Ld`)** | the least straight-line distance from the robot to the aim point; the one knob you tune. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **Loop** | steps that repeat over and over. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/en.md) |
| **Loop closure** | recognising a place already visited, which adds one more spring. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/en.md) |
| **LQR** | a method that computes a feedback gain from a model and the cost weights. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Lyapunov function (`V`)** | an energy-like number, zero at the goal and positive elsewhere. If it never rises, a start near the goal stays near it. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **Manhattan distance** | squares across plus squares down, ignoring walls. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/en.md) |
| **Manipulability** | a score for how freely the tip can move. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **MDP** | a list of squares, moves, the chances of each outcome, and rewards. The name is just a label. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Mean policy** | a rule that takes the average of the nearby demonstrated moves. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **Measurement noise (`R`)** | how jumpy the sensor is, as the spread of its error squared. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **Mock joint** | a pretend arm that refuses a bad push (torque), such as a push that is not a real number (NaN). | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Model predictive control (MPC)** | plan a short future under the limits, apply the first command, then plan again. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **Monitor** | a cheap check on signals the controller can see that raises an alarm. | [15-01](phases/15-safety-and-deployment/01-failure-modes/docs/en.md) |
| **Motor lag** | the delay before the motor's push catches up with the command. | [12-01](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/en.md) |
| **Motor lag (`Tm`)** | how late the motor's push arrives after the command. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) |
| **MuJoCo** | a free ready-made simulator we compare our loop against. | [00-08](phases/00-start-here/08-mujoco-hello-world/docs/en.md) |
| **Multimodal** | having several different correct answers, called modes. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **Nearest neighbour** | the closest dot in the other scan. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) |
| **Nearest neighbours** | a method that copies, or averages, the actions of the closest examples. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **NEES** | a score for whether the filter's doubt matches its real error. An honest filter scores about 3 here, one per value it tracks. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/en.md) |
| **Neighbour table (`L`)** | a table of which robots can talk to each other. Its proper name is the graph Laplacian. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) |
| **Nested limits** | each layer allows a little less than the next, so the planner is the strictest. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) |
| **Node** | one running program in a ROS 2 system. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/en.md) |
| **Normal force** | the push of a surface straight out of itself, perpendicular to the surface. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Not-a-number (`nan`)** | what a calculation gives when it has no answer, such as asking for the angle whose cosine is 2. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Numerical IK** | finding joint angles by repeated small corrections instead of a formula. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Observation** | what the robot senses. Here it is its spot on the floor. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **Occupancy grid** | a map split into small squares, each holding a score for "something is here". | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) |
| **Odometry** | a position guess made by adding up how far the wheels turned. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Old-speed update** | an integrator that moves using the old speed. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Open-loop** | sending commands without checking sensors to correct them. | [12-01](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/en.md) |
| **Orientation** | which way something faces. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Origin** | the corner all counting starts from, written (0, 0). | [00-02](phases/00-start-here/02-points-as-numbers/docs/en.md) |
| **Overshoot** | passing the final position before coming back. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **p99** | the delay that 99% of cycles stay under. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Padding** | growing the obstacle by a margin so the check errs on the safe side. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Particle** | one guess of where the robot is and which way it faces. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **Particle filter** | a crowd of particles that is moved, scored by measurements and resampled. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **PD control** | a spring on the angle plus a brake on the rate (how fast the angle is changing). | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **PD controller** | pushes in proportion to how far the arm is from its plan, and brakes in proportion to its speed. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/en.md) |
| **PD loop** | control code that pulls toward a target and brakes in proportion to speed. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/en.md) |
| **Penalty** | extra cost added when a waypoint gets too close to an obstacle. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Pendulum** | a weight on a rod that swings under gravity. | [00-08](phases/00-start-here/08-mujoco-hello-world/docs/en.md) |
| **Penetration** | how far a simulated body sinks into a surface. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Period** | the time for one full swing out and back. | [00-08](phases/00-start-here/08-mujoco-hello-world/docs/en.md) |
| **Period (`T`)** | the planned time between two cycles of the loop. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **PID** | a way to steer something with three parts: P (the error), I (the error added up over time) and D (a brake on speed). | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Pitch (`theta`)** | the tilt angle of the drone body. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Pixel** | one dot of a camera image. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Planner** | the layer that draws the path and sets the speed it asks for. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/en.md) |
| **Point** | one place, written as a pair of numbers such as (2, 1.5), or three numbers in 3D. | [00-02](phases/00-start-here/02-points-as-numbers/docs/en.md) |
| **Point cloud** | a set of 3D points, here made by turning every depth pixel back into a 3D point. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Policy** | the rule that turns an observation into an action. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/en.md) |
| **Policy gradient** | nudging the policy toward moves that scored above average. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **Pose** | which way an object faces plus where it is. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) |
| **Pose graph** | a chain of poses (a position plus the direction it faces) joined by measurements that act like springs. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/en.md) |
| **Position gain (`kp`)** | how hard the motor pulls the arm back per radian of error. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Position mode** | your program gives a target angle, and the drive's own control code picks the torque. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/en.md) |
| **Predict** | the step that slides and blurs the belief by the move, adding doubt. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Preemption** | the operating system pausing your program to run another one. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/en.md) |
| **Principal point (`cx, cy`)** | the pixel where the camera's centre line lands. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Prior / posterior** | the belief before and after a reading. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **Process noise (`Q`)** | doubt added each step because the real motion may differ from the rule the filter uses to predict. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **Projection** | turning a 3D point into a pixel. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Property test** | throws many random inputs at one rule. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Publisher / Subscriber** | the sender and the listener on a topic. | [05-01](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/en.md) |
| **Pure pursuit** | steering a robot toward a point on the path a fixed distance ahead. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **QoS** | quality of service, the settings that decide how messages are kept and delivered. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/en.md) |
| **Quadratic** | a cost shaped like a bowl, easy to minimise. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **Quadrotor** | a drone with four propellers. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Quantisation** | rounding a smooth value to whole steps, so small changes stay invisible. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Quaternion** | four numbers, with squares adding up to one, that name an orientation. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Queue depth** | how many messages a subscriber keeps while it waits to read them. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/en.md) |
| **Quintic** | the simplest curve whose position, speed and acceleration are all set at both ends. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) |
| **rad/s** | radians per second, a spin speed. One full turn is about 6.28 radians. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Radian** | an angle unit where a full turn is about 6.28. Code uses this unit. | [00-03](phases/00-start-here/03-angles-and-radians/docs/en.md) |
| **Radian (rad)** | an angle unit where one full turn is about 6.28. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **RANSAC** | try planes from random points and keep the one with the most points near it. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Rate limit** | a cap on how much a command may change in one tick. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) |
| **Ray** | the line of sight through a pixel. Every point on it lands on that pixel. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/en.md) |
| **Reach band** | the ring of targets the arm can touch: no closer than the difference of the two link lengths and no farther than their sum. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Replay test** | feeds a recording back in and compares the output with the trusted recording. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Reprojection error** | how far corners projected with your numbers land from the corners seen. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/en.md) |
| **Resampling** | copying high-weight particles and dropping low-weight ones, keeping the count fixed. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **Reservation** | claiming a whole route before entering it. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Residual** | the model's error, the gap between the feedforward and the torque gravity really needs. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Return** | the total points of one try (an episode). | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **Reward-to-go** | the points collected from now until the end of the try. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **Riccati recursion** | a repeated calculation that turns the model and the weights into the feedback gain. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **Rigid move** | a turn plus a slide that does not stretch or bend the shape. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/en.md) |
| **rms error** | the typical distance between a pose and where the robot really was. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/en.md) |
| **Robot** | a machine that senses its surroundings, decides what to do, and moves, again and again. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/en.md) |
| **Robot frame** | coordinates that move with the robot, x forward and y left. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/en.md) |
| **Roll, pitch, yaw** | turns about the forward axis, the side axis and the vertical axis. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/en.md) |
| **Rollout** | one test drive of a policy from a start spot. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/en.md) |
| **ROS 2** | robot software that splits a robot into small programs that pass messages to each other. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/en.md) |
| **Rotate** | turn a point around the origin by an angle. | [00-05](phases/00-start-here/05-turning-a-point/docs/en.md) |
| **Rotation axis** | the line a rotation spins about. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) |
| **Rotation matrix** | a small table of numbers that turns a point when you multiply the two. | [00-05](phases/00-start-here/05-turning-a-point/docs/en.md) |
| **Round trip** | the time a request takes to go out plus its reply to come back. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **RRT** | rapidly-exploring random tree, a method that grows branches of short steps toward random spots. | [09-02](phases/09-motion-planning/02-rrt/docs/en.md) |
| **Rub (`c`)** | a constant push-back against the motion. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/en.md) |
| **Safety wrapper** | a fixed layer between a policy and the motor that limits every command. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/en.md) |
| **Sag** | how far the arm ends up below (or above) its commanded angle. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/en.md) |
| **Sampler** | picks one demonstration at random instead of averaging. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **Saturation** | the motor is at its torque limit and cannot push harder. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Scan** | one sweep of laser beams. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) |
| **Seed** | the starting pose of one run. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/en.md) |
| **Segment** | the straight stretch between two path points. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Selection matrix (`S`)** | a switch for each direction that chooses force control or position control. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Sensor** | a part that measures something, such as the distance to a wall. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/en.md) |
| **Sensor fusion** | merging readings from several sensors into one estimate. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Sequence** | a step that runs the steps under it in order and stops at the first failure. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Service** | a request with one reply, unlike a topic's endless stream. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/en.md) |
| **Settling** | staying close to the target. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) |
| **Shared parent** | the nearest frame above two frames on the tree, where their paths meet. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) |
| **Shortcutting** | replacing part of a path with a straight segment when that segment is free. | [09-02](phases/09-motion-planning/02-rrt/docs/en.md) |
| **Simulation** | a program that predicts motion by repeating small steps. | [00-06](phases/00-start-here/06-time-steps/docs/en.md) |
| **Singularity** | a pose where the arm loses a direction of tip motion, such as a fully straight arm. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/en.md) |
| **SLAM** | drawing the map and finding your place on it at the same time. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/en.md) |
| **Slerp** | a smooth, even-speed turn between two orientations. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/en.md) |
| **Slope (`vdot`)** | how fast the energy-like number changes as the system moves. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/en.md) |
| **Speed** | how far something moves in one second. | [00-06](phases/00-start-here/06-time-steps/docs/en.md) |
| **Speed-first update** | an integrator that updates the speed first, then moves using the new speed. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Spread** | how far apart the motions' axes point. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) |
| **Stable** | a loop that settles instead of buzzing or blowing up. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Stale observation** | a camera picture older than the wrapper allows. | [16-03](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/en.md) |
| **Stance** | the time one foot stays on the ground. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Starvation** | a callback waits too long because another one holds the thread. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **State** | the values that predict future motion, such as position and speed. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/en.md) |
| **State (`x`)** | the numbers the filter tracks, here position and velocity. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/en.md) |
| **State machine** | a table of named states, with an arrow for each thing that makes the robot switch. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Status** | the answer each step gives: it worked, it failed, or it is still running. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Steady offset** | the error left when something pushes on the joint all the time and only P and D are working. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Step size (`eps`)** | how far each robot moves toward its neighbours per tick. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/en.md) |
| **Stick and slip** | two states of a contact; holding still, or sliding. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/en.md) |
| **Stiff contact** | a very hard surface, which needs small steps. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/en.md) |
| **Stiffness (`K`)** | push back per unit of deflection. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/en.md) |
| **Stiffness (`ke`)** | how much force a surface pushes back for each metre you squeeze it. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Stiffness (`kx`)** | the sideways force per metre the wrist is stretched. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/en.md) |
| **Sweep** | one update of every square. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Task allocation** | deciding which robot does which job. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/en.md) |
| **Terminal cost** | a price on where the plan ends, so a short plan still sees what comes after. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/en.md) |
| **tf2** | the ROS 2 library that stores a transform tree. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) |
| **Thread** | one worker inside a program, doing one job at a time. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **Throughput** | the number of jobs finished per time step. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Thrust (`T`)** | the total push of the propellers along the drone's body axis; it tilts with the drone. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/en.md) |
| **Tick** | one small step, where the tree is asked to do a little work and report. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/en.md) |
| **Tick (`dt`)** | one control step, the same as the time step in 00/06. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Time constant** | the time in which an error shrinks by about two thirds. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/en.md) |
| **Time constant (`tau`)** | how long the gyro is trusted before the accelerometer takes over. | [07-04](phases/07-state-estimation/04-complementary-filter/docs/en.md) |
| **Time constant (`Tc`)** | how quickly the body tips over, the same number as in lesson 01. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Time stamp** | the time written on a reading by the clock of the computer that took it. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Time step** | the time from the start of one pass of the loop to the start of the next, here a tenth of a second. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/en.md) |
| **Time step (`dt`)** | the small slice of time the computer jumps forward each time. | [00-06](phases/00-start-here/06-time-steps/docs/en.md) |
| **Timeout `T`** | how long silence is tolerated before the watchdog acts. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/en.md) |
| **Timing jitter** | how much message arrival times wobble. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/en.md) |
| **Tip** | the end of the arm, where the hand or tool sits. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Tip pose** | where the end of the arm is and which way it points. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Tolerance** | a tiny allowed error, so rounding noise is not treated as a failure. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/en.md) |
| **Topic** | a named stream. A program that sends into it is a publisher; a program that reads from it is a subscriber. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/en.md) |
| **Torque** | the twisting force a motor applies to a joint. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/en.md) |
| **Torque (`tau`)** | a twisting force, such as a motor's push on a joint. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Torque mode** | your program tells the drive how hard to twist, and the drive obeys. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/en.md) |
| **Touchdown** | the moment a swinging foot lands. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/en.md) |
| **Trace** | a log with one record per step, holding the state before and after. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/en.md) |
| **Track width (`b`)** | the distance between the two wheels. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Trajectory profile** | the plan of how a joint's position changes over time between two poses. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/en.md) |
| **Transform** | a 4x4 table of numbers holding one turn and one shift. | [00-09](phases/00-start-here/09-reading-a-urdf/docs/en.md) |
| **Transform (`T`)** | a 4x4 matrix that stores a rotation and a shift in one table. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/en.md) |
| **Transform (`X`)** | how the camera is turned and shifted relative to the gripper. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) |
| **Transform name (`T_to_from`)** | a name that tells which frame a transform converts from and which it converts into. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) |
| **Transform tree** | a map where each frame hangs off exactly one parent frame. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/en.md) |
| **Translation** | a straight-line shift, as opposed to a turn. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/en.md) |
| **Transpose (`.T`)** | swaps the rows and columns of a matrix. | [00-07](phases/00-start-here/07-python-env-and-numpy/docs/en.md) |
| **Transpose (`J^T`)** | the same matrix with its rows and columns swapped. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/en.md) |
| **Tunnelling** | a motion slipping through a thin obstacle because the checks are too far apart. | [09-03](phases/09-motion-planning/03-collision-checking/docs/en.md) |
| **Twist (`alpha`)** | how far the line the next joint turns about is tilted compared with this one's. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **Unit test** | moves the fake clock and checks one simple rule. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/en.md) |
| **Update** | the step that reweights the belief by how well each place explains a reading. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/en.md) |
| **URDF** | a text file that describes a robot as links joined by joints. | [00-09](phases/00-start-here/09-reading-a-urdf/docs/en.md) |
| **Value `V(s)`** | how much reward you can expect from a square if you play the best moves afterwards. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/en.md) |
| **Variance** | how much a result jumps around between runs. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/en.md) |
| **venv** | a private folder holding the Python add-ons for one project. | [00-07](phases/00-start-here/07-python-env-and-numpy/docs/en.md) |
| **Voxel grid** | small cubes cutting up space. Keeping one averaged point per cube thins the cloud. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/en.md) |
| **Wait-for graph** | a drawing with an arrow from each robot to the robot it is waiting for. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/en.md) |
| **Watchdog** | a guard that stops the robot when a heartbeat is late. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/en.md) |
| **Waypoint** | one point on the route; the route is a chain of them. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/en.md) |
| **Weight** | a score for how closely the distances this guess would see match the distances the robot measured. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/en.md) |
| **Wheel radius (`r`)** | the distance from a wheel's center to its edge. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/en.md) |
| **Width (`w`)** | how far each number may be changed, as a fraction of its plain value. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/en.md) |
| **Window** | how many readings apart the two counts are that you subtract to get a speed. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/en.md) |
| **Windup** | the I part keeps growing during saturation, then causes overshoot. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/en.md) |
| **Wobble (jitter)** | how much the action changes from step to step. High wobble looks shaky. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/en.md) |
| **Workspace** | every place the tip can reach. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/en.md) |
| **Wrap** | bring an angle back into one full turn without changing the direction it points. | [00-03](phases/00-start-here/03-angles-and-radians/docs/en.md) |
| **Wrench** | a push and a twist packed together. In 2-D that is three numbers: push left-right, push up-down and twist. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/en.md) |
| **Zero pose** | the arm with every joint angle at 0. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/en.md) |
| **ZMP** | zero-moment point, the spot under the foot where the ground's push acts. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/en.md) |
