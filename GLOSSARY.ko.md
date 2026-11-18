# 용어집

레슨의 핵심 용어를 알파벳순으로 모았습니다. 그 용어를 처음 소개하는 레슨이 함께 있습니다.

| Term | Meaning | Lesson |
|---|---|---|
| **A-star** | Dijkstra에 남은 걸음 수의 추측을 더해서 목표 쪽으로 향하는 탐색입니다. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/ko.md) |
| **Acceleration** | 1초 동안 속도가 얼마나 바뀌는지입니다. | [00-06](phases/00-start-here/06-time-steps/docs/ko.md) |
| **Accelerometer** | 미는 힘(가속도)을 재는 센서입니다. 중력도 느낍니다. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/ko.md) |
| **Action** | 로봇이 다음에 하는 일입니다. 여기서는 주행 방향입니다. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/ko.md) |
| **Action chunk** | 앞으로의 몇 개 행동을 한꺼번에 고른 짧은 묶음입니다. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/ko.md) |
| **Actuator** | 바퀴를 돌리는 모터처럼 움직임을 만드는 부품입니다. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/ko.md) |
| **Admissible** | 절대 부풀리지 않는 추측입니다. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/ko.md) |
| **Admittance layer** | 미는 힘을 재고 그만큼 목표를 옮겨서 관절이 부드럽게 움직이게 하는 코드입니다. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/ko.md) |
| **Agreement speed (`lambda2`)** | 이웃 표에서 읽어 낸 수 하나로, 로봇들이 얼마나 빨리 합의하는지를 정합니다. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/ko.md) |
| **Angle** | 어떤 것이 처음 방향에서 얼마나 돌았는지입니다. | [00-03](phases/00-start-here/03-angles-and-radians/docs/ko.md) |
| **Array shape** | 배열의 행과 열이 몇 개인지입니다. 예를 들어 5행 3열입니다. | [00-07](phases/00-start-here/07-python-env-and-numpy/docs/ko.md) |
| **Assignment** | 로봇과 일을 하나씩 짝짓는 것입니다. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/ko.md) |
| **At sign (`@`)** | numpy에서 표와 점을 곱할 때 쓰는 기호입니다. | [00-05](phases/00-start-here/05-turning-a-point/docs/ko.md) |
| **Attitude** | 드론이 공간에서 기울어진 모습입니다. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/ko.md) |
| **Back-EMF** | 도는 모터가 자기 전원에 맞서 만드는 전압입니다. 미는 힘을 약하게 합니다. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/ko.md) |
| **Baseline** | 좋은 움직임이 두드러지도록 점수에서 빼는 평균입니다. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/ko.md) |
| **Behaviour cloning** | 기록된 위치에서 전문가의 행동을 따라 해서 policy를 학습시키는 방법입니다. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/ko.md) |
| **Behaviour tree** | 작업을 단계의 tree로 적어 두고 매 주기 tick하는 방식입니다. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/ko.md) |
| **Belief** | 로봇이 각 장소가 얼마나 그럴듯하다고 믿는지입니다. 장소마다 확률 하나씩입니다. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/ko.md) |
| **Belief (`est`)** | 로버가 자기가 있다고 믿는 위치로, 실제 위치에서 벗어날 수 있습니다. | [16-02](phases/16-capstones/02-mobile-navigation-sim/docs/ko.md) |
| **Bias** | 늘 붙어 있는 작고 일정한 오차입니다. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/ko.md) |
| **Box constraint** | 미는 힘이 모두 허용된 가장 큰 힘의 ± 범위 안에 들어야 한다는 제약입니다. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/ko.md) |
| **Calibration** | 아는 표적으로 줌이나 중심 같은 카메라 자신의 값을 재는 일입니다. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/ko.md) |
| **Callback** | 메시지가 도착할 때마다 그것을 처리하는 함수입니다. | [05-01](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/ko.md) |
| **Callback group** | 함께 실행되는 방식을 정하는 규칙 하나를 공유하는 callback 묶음입니다. 예를 들면 서로 동시에 실행하지 않는다는 규칙입니다. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/ko.md) |
| **Capture point** | 발을 놓으면 넘어짐이 멈추는 지점입니다. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/ko.md) |
| **Cartesian space** | 관절 각도가 아니라 보통의 x, y, z 위치로 나타내는 공간입니다. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/ko.md) |
| **Cascade** | 바깥의 각도 루프가 안쪽의 회전 속도 루프에 속도를 명령하는 두 겹의 루프입니다. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/ko.md) |
| **Chamfer** | peg가 들어가도록 안내하는 비스듬한 구멍 모서리입니다. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/ko.md) |
| **Clamp** | 값을 허용 범위 안으로 잘라 내는 것입니다. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/ko.md) |
| **Clearance** | 경로와 장애물 사이에 남겨 두는 여유 거리입니다. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/ko.md) |
| **Clip** | 값을 범위 안으로 잘라 넣는 것입니다. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/ko.md) |
| **Clock offset** | 한 컴퓨터의 시계가 다른 컴퓨터보다 얼마나 앞서가는지입니다. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/ko.md) |
| **Collision checking** | 로봇의 자세나 움직임이 장애물에 닿는지 검사하는 일입니다. | [09-03](phases/09-motion-planning/03-collision-checking/docs/ko.md) |
| **Compliance** | 위치를 딱딱하게 고집하지 않고 힘을 받으면 비켜 주는 성질입니다. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/ko.md) |
| **Compounding error** | 작은 실수가 낯선 위치로 이어지고 거기서 더 큰 실수가 나는 현상입니다. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/ko.md) |
| **Computed torque** | 팔의 방정식으로 동역학을 상쇄하고 남은 것만 제어하는 방법입니다. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/ko.md) |
| **Consensus** | 로봇들이 이웃과만 통신해서 값 하나에 합의하는 것입니다. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/ko.md) |
| **Contact model** | 두 물체가 닿는 곳의 힘을 simulator가 계산하는 규칙입니다. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/ko.md) |
| **Control loop** | 센서를 읽고 계산해서 모터에 명령하는 일을 일정한 빠르기로 되풀이하는 코드입니다. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/ko.md) |
| **Control tick** | 모터를 움직이는 프로그램이 한 번 계산하는 간격입니다. 여기서는 0.002초입니다. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/ko.md) |
| **Controller** | 경로를 모터 명령으로 바꾸는 계층입니다. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/ko.md) |
| **Convention** | 표를 읽는 약속입니다. 같은 숫자도 convention에 따라 다르게 읽힙니다. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/ko.md) |
| **Converged** | 오차가 허용값 아래로 내려온 상태입니다. 여기서는 100만 분의 1 m입니다. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/ko.md) |
| **Convex hull** | 점들의 집합을 팽팽하게 감싼 껍질입니다. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/ko.md) |
| **Coordinates** | 가로로 얼마나 가고 세로로 얼마나 가는지 나타내는 숫자입니다. | [00-02](phases/00-start-here/02-points-as-numbers/docs/ko.md) |
| **Coriolis torque** | 링크가 빠르게 swing할 때 서로에게 가하는 당기는 힘입니다. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/ko.md) |
| **cos and sin** | 각도를 길이 1인 막대의 "옆으로 간 거리"와 "위로 간 거리"로 바꿔 주는 계산기 버튼 두 개입니다. | [00-04](phases/00-start-here/04-joints-and-links/docs/ko.md) |
| **Cost** | 계획이 얼마나 나쁜지 매기는 점수입니다. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/ko.md) |
| **Cost matrix `C`** | 로봇마다 일까지 얼마나 먼지 적은 표입니다. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/ko.md) |
| **Cost weights** | 오차와 노력에 벌점을 얼마나 줄지 정하는 숫자들입니다. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/ko.md) |
| **Count** | encoder가 알려 주는 한 단계입니다. 여기서는 홈 모서리 하나가 센서를 지나간 것입니다. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/ko.md) |
| **Counterexample** | 기울기가 양수인 상태 하나입니다. 이것이 안정하다는 주장을 깨뜨립니다. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/ko.md) |
| **Covariance (`P`)** | 추정이 얼마나 불확실한지입니다. 숫자 하나라면 퍼짐을 제곱한 값입니다. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/ko.md) |
| **CPR** | 한 바퀴당 count 수입니다. 한 바퀴가 몇 단계인지 알려 줍니다. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/ko.md) |
| **Crossover** | 변화의 빠르기를 초당 진동 수(Hz)로 나타냈을 때 gyro와 가속도계의 비중이 같아지는 지점입니다. | [07-04](phases/07-state-estimation/04-complementary-filter/docs/ko.md) |
| **Curvature (`k`)** | 경로가 얼마나 급하게 굽는지입니다. 급하게 돌수록 curvature가 큽니다. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/ko.md) |
| **DAgger** | learner가 달리면 전문가가 learner가 닿은 위치마다 맞는 움직임을 표시합니다. 그 표시를 학습 데이터에 합칩니다. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/ko.md) |
| **Damped least squares** | 작은 오차를 받아들여서 속도가 상한을 넘지 않게 하는 joint 속도 계산법입니다. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/ko.md) |
| **Damper** | 속도에 비례하는 torque로 속도를 거슬러 미는 브레이크입니다. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/ko.md) |
| **Damping (`D`)** | 속도를 거스르는 저항입니다. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/ko.md) |
| **Damping gain (`kd`)** | damper가 얼마나 세게 브레이크를 거는지입니다. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/ko.md) |
| **Damping ratio (`zeta`)** | damper가 관절을 얼마나 세게 가라앉히는지입니다. 1이면 미끄러지듯 멈추고 1보다 작으면 출렁입니다. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/ko.md) |
| **Damping term** | 속도가 클수록 세지는 브레이크라서 빠른 관절을 더 세게 제동합니다. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/ko.md) |
| **Deadbeat** | 한 걸음 만에 목표 속도에 이르고 그대로 유지하는 규칙입니다. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/ko.md) |
| **Deadline** | 한 cycle이 끝나야 하는 시각입니다. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/ko.md) |
| **Deadlock** | 로봇들이 고리로 서로를 기다려서 아무도 움직이지 못하는 상태입니다. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/ko.md) |
| **Deceleration `a`** | 제동하는 동안 속도가 줄어드는 빠르기입니다. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/ko.md) |
| **Deflection** | 힘에 밀려 관절이 원래 자세에서 움직인 거리입니다. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/ko.md) |
| **Degenerate views** | 같은 단서를 되풀이해서 풀 수 없는 시점들입니다. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/ko.md) |
| **Degree** | 한 바퀴를 똑같은 360조각으로 나눈 한 조각입니다. | [00-03](phases/00-start-here/03-angles-and-radians/docs/ko.md) |
| **Delay margin** | loop가 흔들리기 시작하기 전까지 견딜 수 있는 가장 긴 지연입니다. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/ko.md) |
| **Depth (`z`)** | 카메라 앞에서 점까지의 거리입니다. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/ko.md) |
| **Depth image** | 픽셀마다 색 대신 거리를 담은 사진입니다. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/ko.md) |
| **DH table** | Denavit-Hartenberg 표입니다. joint마다 숫자 네 개(길이 둘과 각도 둘)로 된 행이 하나씩 있어서 팔을 설명합니다. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/ko.md) |
| **Differential drive** | 두 바퀴를 서로 다른 속도로 돌려서 방향을 바꾸는 로봇입니다. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/ko.md) |
| **Dijkstra** | 그 칸까지 이미 쓴 걸음 수 순서로 칸을 확장하는 탐색입니다. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/ko.md) |
| **Discount (gamma)** | 나중 reward를 조금 덜 쳐 주는 1보다 작은 수입니다. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/ko.md) |
| **Distance** | 두 점 사이의 곧은 간격입니다. | [00-02](phases/00-start-here/02-points-as-numbers/docs/ko.md) |
| **Domain randomisation** | 수치를 무작위로 바꾼 여러 시뮬레이션 로봇에 걸쳐 controller를 튜닝하는 방법입니다. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/ko.md) |
| **Dot product** | 두 quaternion의 대응하는 숫자끼리 곱해 더한 값입니다. 양수면 서로 가깝고 음수면 멉니다. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/ko.md) |
| **Double integrator** | 가속도로 모는 자동차입니다. 위치는 속도로, 속도는 미는 힘으로 변합니다. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/ko.md) |
| **Drag (`b`)** | 속도가 클수록 커지는 저항입니다. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/ko.md) |
| **Drift** | 반올림된 숫자를 여러 번 곱하면서 쌓이는 느린 오차입니다. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/ko.md) |
| **Drive** | 모터에 전기를 보내고 제어하는 전자회로입니다. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/ko.md) |
| **Dynamics** | torque와 관절 운동을 이어 주는 방정식입니다. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/ko.md) |
| **Effective limit** | 가장 빡빡한 계층이 정해서 관절이 실제로 느끼는 한계입니다. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/ko.md) |
| **EKF** | extended Kalman filter로 로봇이 어디 있는지 추적하며 현재 추정값에서 직선 규칙을 쓰는 프로그램입니다. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/ko.md) |
| **Elbow down / elbow up** | 같은 목표에 닿는 두 가지 팔 모양입니다. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/ko.md) |
| **Encoder** | 축이 얼마나 돌았는지 정수 단계로 알려 주는 센서입니다. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/ko.md) |
| **Energy drift** | 시뮬레이션 속 상자나 진자가 원래 없어야 할 튐이나 흔들림을 얻는 현상입니다. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/ko.md) |
| **Entropy** | 불확실성의 점수입니다. 모든 장소가 똑같이 그럴듯하면 큽니다. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/ko.md) |
| **Epsilon** | 쥐기가 실패에서 얼마나 떨어져 있는지입니다. 0이면 실패합니다. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/ko.md) |
| **Euler angles** | 정해진 순서로 적용하는 회전 세 개로 roll, pitch, yaw라고 부릅니다. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/ko.md) |
| **Euler rates** | 각 고리가 돌고 있는 속도입니다. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/ko.md) |
| **Excitation** | 기록 속 움직임이 얼마나 다양한지입니다. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/ko.md) |
| **Executor** | 준비된 callback 중 무엇을 어느 thread에서 실행할지 정하는 ROS 2의 부분입니다. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/ko.md) |
| **Expanding a square** | 그 칸을 시도하는 일입니다. 이웃을 살펴보고 탐색에 더합니다. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/ko.md) |
| **Explicit / semi-implicit Euler** | 스텝을 밟는 두 방법입니다. explicit는 옛 속도를 쓰고 semi-implicit는 새 속도를 씁니다. Euler는 방법의 이름일 뿐입니다. | [00-08](phases/00-start-here/08-mujoco-hello-world/docs/ko.md) |
| **Extrapolate** | 마지막 움직임이 계속된다고 보고 가장 최신 샘플 너머의 값을 짐작하는 일입니다. | [05-06](phases/05-robot-software/06-transforms-at-a-time/docs/ko.md) |
| **Fake clock** | 테스트가 손으로 앞으로 돌리는 시계입니다. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/ko.md) |
| **Fallback** | 아래에 있는 단계들을 순서대로 시도하고 처음 성공에서 멈추는 단계입니다. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/ko.md) |
| **False alarm** | 장애물을 실제로는 피하는 경로에 충돌이라고 알리는 일입니다. | [09-03](phases/09-motion-planning/03-collision-checking/docs/ko.md) |
| **Fast-motion torques (`h`)** | 팔이 빠르게 움직일 때 나타나는 비트는 힘입니다. 자세에 따라 팔이 무겁게 느껴지는 정도가 달라지기 때문에 생깁니다. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/ko.md) |
| **Fault injection** | 어떻게 되는지 보려고 센서나 명령이나 타이밍을 일부러 망가뜨리는 일입니다. | [15-01](phases/15-safety-and-deployment/01-failure-modes/docs/ko.md) |
| **Feedback gain** | state를 미는 힘으로 바꾸는 숫자들입니다(미는 힘은 gain과 state를 곱한 값의 음수입니다). | [03-06](phases/03-dynamics-and-control/06-lqr/docs/ko.md) |
| **Feedforward** | 오차가 나타난 뒤가 아니라 팔이 움직이기 전에 미리 계산해 두는 힘입니다. | [16-01](phases/16-capstones/01-arm-pick-and-place-sim/docs/ko.md) |
| **Feedforward (`ff`)** | 오차가 생기기 전에 모델로 미리 더하는 torque입니다. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/ko.md) |
| **Finite difference** | 입력을 아주 조금 움직여 출력이 변하는 것을 보고 기울기를 추정하는 방법입니다. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/ko.md) |
| **Focal length (`fx, fy`)** | 렌즈가 가로와 세로로 얼마나 확대하는지입니다. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/ko.md) |
| **Foot placement** | 속도를 조절하려고 다음 발이 닿을 자리를 고르는 일입니다. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/ko.md) |
| **Force closure** | 접촉이 바깥에서 오는 어떤 밀기나 비틀림도 버틸 수 있는 상태입니다. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/ko.md) |
| **Force control** | 계획한 위치가 아니라 잰 힘에 따라 도구를 움직이는 제어입니다. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/ko.md) |
| **Forward kinematics (FK)** | 관절 각도로부터 손끝이 어디에 있는지 구하는 계산입니다. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/ko.md) |
| **Frame** | link나 방 같은 어떤 대상에 붙은 x, y, z축의 묶음입니다. | [00-09](phases/00-start-here/09-reading-a-urdf/docs/ko.md) |
| **Friction** | 움직임을 조금씩 빼앗는 마찰입니다. | [12-01](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/ko.md) |
| **Friction coefficient (`mu`)** | 표면이 얼마나 잘 붙는지를 나타내는 값입니다. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/ko.md) |
| **Friction cone** | 붙드는 한도, 즉 friction coefficient에 normal force를 곱한 값까지의 마찰력의 모음입니다. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/ko.md) |
| **Full turn** | 처음 향한 방향으로 돌아오는 한 바퀴입니다. | [00-03](phases/00-start-here/03-angles-and-radians/docs/ko.md) |
| **Fuzzing** | 코드가 깨지는지 보려고 무작위 입력을 마구 던지는 시험입니다. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/ko.md) |
| **Gain** | 컨트롤러가 얼마나 세게 반응하는지입니다. 예를 들어 오차 한 단위당 미는 힘입니다. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/ko.md) |
| **Gain (`ki`)** | 힘 오차를 도구 속도로 바꾸는 배율입니다. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/ko.md) |
| **Gains** | controller가 얼마나 세게 밀고 브레이크를 걸지 정하는 두 수입니다. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/ko.md) |
| **Gear ratio (`N`)** | 출력이 한 바퀴 돌 때 모터가 도는 바퀴 수입니다. 토크는 그 수만큼 커지고 속도는 그 수만큼 줄어듭니다. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/ko.md) |
| **Gimbal** | 어느 방향으로든 돌 수 있게 해 주는 겹쳐진 고리 세 개입니다. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/ko.md) |
| **Gimbal lock** | 고리 두 개가 나란해져서 돌릴 수 있는 방향 하나를 잃은 자세입니다. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/ko.md) |
| **Goal bias** | 무작위 지점을 목표 자체로 고르는 빈도입니다. 그 덕분에 나무가 목표 쪽으로 끌립니다. | [09-02](phases/09-motion-planning/02-rrt/docs/ko.md) |
| **Golden trace** | 정상 실행에서 얻은 믿을 수 있는 녹화본입니다. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/ko.md) |
| **Gradient** | cost가 가장 빨리 커지는 방향입니다. 반대쪽으로 한 걸음 가면 cost가 줄어듭니다. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/ko.md) |
| **Gradient descent** | gradient의 반대쪽으로 작은 걸음을 되풀이하는 방법입니다. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/ko.md) |
| **Gravity compensation** | 팔의 무게를 모델로 어림해서 torque로 미리 더해 주는 것입니다. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/ko.md) |
| **Greedy** | 앞을 내다보지 않고 지금 가장 좋아 보이는 것을 고르는 방식입니다. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/ko.md) |
| **Greedy policy** | 각 칸에서 점수가 가장 높은 행동을 고르는 policy입니다. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/ko.md) |
| **Guard** | 들어오는 숫자를 검사해서 나쁜 값을 분명한 오류로 멈추게 하는 검사입니다. | [00-07](phases/00-start-here/07-python-env-and-numpy/docs/ko.md) |
| **Gyro** | 얼마나 빨리 도는지를 재는 센서입니다. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/ko.md) |
| **Hand** | 마지막 link의 끝입니다. 우리가 원하는 곳에 놓고 싶은 지점입니다. | [00-04](phases/00-start-here/04-joints-and-links/docs/ko.md) |
| **Hand-eye calibration** | 카메라가 로봇 손(gripper)의 어디에 붙어 있는지 찾는 일입니다. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/ko.md) |
| **Hard stop** | 관절의 움직임 끝을 막는 블록입니다. | [15-01](phases/15-safety-and-deployment/01-failure-modes/docs/ko.md) |
| **Heading** | 로봇이 바라보는 방향입니다. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/ko.md) |
| **Heartbeat** | 관절에 명령을 보내는 프로그램이 규칙적으로 보내는 "아직 살아 있다"는 메시지입니다. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/ko.md) |
| **Heuristic (`h`)** | 목표까지 남은 걸음 수의 추측입니다. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/ko.md) |
| **Hold-and-wait** | 다음 칸을 기다리는 동안 자기 칸을 쥐고 있는 것입니다. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/ko.md) |
| **Homography (`H`)** | 평평한 보드 위의 한 지점을 pixel로 바꿔 주는 3x3 숫자 표입니다. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/ko.md) |
| **Horizon (`N`)** | 계획 하나가 몇 step 앞을 내다보는지입니다. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/ko.md) |
| **Host** | 컨트롤러 loop를 돌리는 컴퓨터입니다. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/ko.md) |
| **Hover** | 한 높이에 머무는 것입니다. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/ko.md) |
| **Hungarian method** | 전체 거리가 가장 낮은 배정을 차근차근 찾는 방법입니다. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/ko.md) |
| **Hybrid control** | 어떤 축은 위치 제어로, 나머지 축은 힘 제어로 다루는 방식입니다. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/ko.md) |
| **Hypotenuse** | 직각이 하나 있는 삼각형에서 비스듬한 가장 긴 변입니다. | [00-02](phases/00-start-here/02-points-as-numbers/docs/ko.md) |
| **ICP** | iterative closest point입니다. 가까운 점끼리 짝짓고 이동을 맞추는 일을 반복합니다. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/ko.md) |
| **Imitation learning** | 전문가가 일하는 예시를 로봇에게 보여 주며 가르치는 방법입니다. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/ko.md) |
| **Impedance** | 관절을 밀었을 때 spring과 damper처럼 되미는 방식입니다. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/ko.md) |
| **IMU** | gyro와 가속도계로 이루어진 움직임 센서입니다. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/ko.md) |
| **Inertia** | 물체를 돌려 속도를 올리기가 얼마나 어려운지입니다. 무거운 쇠바퀴는 값이 큽니다. | [04-01](phases/04-actuators-and-sensors/01-motor-and-gearbox/docs/ko.md) |
| **Inertia (`J`)** | 관절의 속도를 올리거나 줄이기가 얼마나 어려운지입니다. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/ko.md) |
| **Inertia matrix (`M`)** | 팔이 각 관절에 얼마나 무겁게 느껴지는지를 나타냅니다. 팔꿈치 각도에 따라 바뀝니다. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/ko.md) |
| **Inlier** | 평면 위에 있다고 볼 만큼 평면에 가까운 점입니다. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/ko.md) |
| **Innovation** | 놀라움입니다. 센서 값에서 필터가 기대한 값을 뺀 것입니다. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/ko.md) |
| **Integral** | 오차의 누적합입니다. 오차가 남아 있는 동안 계속 커집니다. | [10-04](phases/10-legged-and-aerial/04-cascaded-attitude-control/docs/ko.md) |
| **Integrate** | 읽은 값을 시간이 흐르는 동안 더하는 일입니다. 회전 속도는 각도로, 가속도는 속도로 바뀝니다. | [07-03](phases/07-state-estimation/03-imu-integration-and-drift/docs/ko.md) |
| **Integration** | 변화율을 시간에 따라 더해서 총량을 얻는 일입니다. 속도에서 거리를 얻는 것이 그 예입니다. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/ko.md) |
| **Integrator** | 시뮬레이션을 한 step 앞으로 보내는 규칙입니다. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/ko.md) |
| **Intent** | 한 단계가 이루어야 하는 일입니다. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/ko.md) |
| **Interpolate** | 알고 있는 두 샘플 사이의 값을 추정하는 일입니다. | [05-06](phases/05-robot-software/06-transforms-at-a-time/docs/ko.md) |
| **Intrinsics (`K`)** | 카메라 자신의 줌과 중심 값을 담은 matrix(숫자 표)입니다. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/ko.md) |
| **Inverse** | 다른 transform을 되돌리는 transform입니다. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/ko.md) |
| **Inverse kinematics (IK)** | 손이 목표에 놓이도록 joint 각도를 구하는 일입니다. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/ko.md) |
| **Inverted pendulum** | 다리 위에 균형 잡고 선 추입니다. 연필을 끝으로 세운 것과 같아서 잡아 주지 않으면 넘어집니다. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/ko.md) |
| **Jacobian** | 관절을 조금 움직였을 때 tip이 어떻게 움직일지 예측하는 숫자 표입니다. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/ko.md) |
| **Jacobian (`F`, `H`)** | 기울기 표(matrix)입니다. 로봇의 위치와 방향이 조금 변할 때 필터의 예측이 얼마나 변하는지 알려 줍니다. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/ko.md) |
| **Jacobian (`J`)** | 현재 자세에서 joint 속도를 tip의 속도와 방향으로 바꾸는 숫자 표입니다. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/ko.md) |
| **Jacobian inverse** | 원하는 손의 움직임을 다시 joint 속도로 바꾸는 표입니다. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/ko.md) |
| **Jam** | peg가 멈추고 더 세게 밀수록 더 단단히 박히는 상태입니다. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/ko.md) |
| **Jerk** | 가속도가 얼마나 빨리 바뀌는지입니다. 가속도가 뛰면 jerk가 뾰족해집니다. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/ko.md) |
| **Jitter** | 한 cycle의 실제 타이밍이 계획에서 벗어난 정도입니다. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/ko.md) |
| **Joint** | 돌아가는 경첩입니다. 얼마나 돌았는지는 각도로 나타냅니다. | [00-04](phases/00-start-here/04-joints-and-links/docs/ko.md) |
| **Joint angle (`q`)** | 관절이 각도가 0인 위치에서 얼마나 돌았는지입니다. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/ko.md) |
| **Joint angles (`q`)** | 각 관절이 얼마나 돌았는지입니다. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/ko.md) |
| **Joint limit** | 관절이 돌 수 있는 범위이고 거기서 관절이 멈춥니다. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/ko.md) |
| **Joint offset (`<origin>`)** | joint가 앞 부품에서 얼마나 떨어져 있고 얼마나 돌아가 있는지를 그 부품 자신의 방향으로 적은 값입니다. | [00-09](phases/00-start-here/09-reading-a-urdf/docs/ko.md) |
| **Joint offset (URDF origin)** | 로봇 설명 파일에서 joint가 앞 부품에서 얼마나 떨어져 있고 얼마나 돌아가 있는지입니다. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/ko.md) |
| **Kalman gain (`K`)** | 새 센서 값 쪽으로 추정이 얼마나 움직일지입니다. 0이면 무시하고 1이면 전부 믿습니다. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/ko.md) |
| **Kidnap** | 아무 말 없이 로봇을 들어서 다른 곳에 놓는 일입니다. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/ko.md) |
| **Kinetic energy** | 어떤 것이 움직이기 때문에 갖는 에너지입니다. | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/ko.md) |
| **Lag** | 조향 명령 뒤에 바퀴가 따라오기까지의 지연입니다. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/ko.md) |
| **Lagrange equation** | 팔의 움직임 에너지를 관절 torque로 바꾸는 규칙입니다(수학은 접힌 부분에 있습니다). | [03-07](phases/03-dynamics-and-control/07-deriving-arm-dynamics/docs/ko.md) |
| **Landmark** | 로봇이 재는 위치를 아는 기둥입니다. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/ko.md) |
| **Latency** | 무언가를 잰 뒤 모터가 그것에 반응하기까지 걸리는 지연입니다. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/ko.md) |
| **Law of cosines** | 삼각형의 세 변 길이로부터 각도를 구하는 규칙입니다. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/ko.md) |
| **Learned policy** | 로봇이 본 것을 행동으로 바꾸는 학습된 모델입니다. | [16-03](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/ko.md) |
| **Learner** | 학습 중인 policy입니다. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/ko.md) |
| **Least squares** | 모든 점이 평면을 당기는 best-fit 규칙입니다. 멀리 있는 점이 가장 세게 당깁니다. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/ko.md) |
| **Level set** | 에너지 같은 수가 같은 모든 상태를 곡선으로 그린 것입니다. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/ko.md) |
| **Likelihood** | 한 장소가 센서 값을 얼마나 잘 설명하는지입니다. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/ko.md) |
| **Linearise** | 곡선을 한 점에서의 직선 근사로 바꾸는 일입니다. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/ko.md) |
| **Link** | 두 joint 사이의 단단한 막대입니다. 휘거나 늘어나지 않습니다. | [00-04](phases/00-start-here/04-joints-and-links/docs/ko.md) |
| **Local minimum** | 작은 움직임으로는 오차가 더 줄지 않는 막다른 곳입니다. 답이 틀렸는데도 더는 줄지 않습니다. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/ko.md) |
| **Log-odds (`L`)** | 칸 하나의 증거 점수입니다. 양수면 막혀 있을 가능성이 높고 음수면 비어 있을 가능성이 높으며 0은 모른다는 뜻입니다. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/ko.md) |
| **Lookahead (`Ld`)** | 그 일정한 거리입니다. 조절하는 값은 이것 하나입니다. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/ko.md) |
| **Loop** | 계속 되풀이되는 단계입니다. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/ko.md) |
| **Loop closure** | 이미 지난 곳을 알아보는 일입니다. 스프링이 하나 더 생깁니다. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/ko.md) |
| **LQR** | 모델과 cost weights로부터 feedback gain을 계산하는 방법입니다. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/ko.md) |
| **Lyapunov function (`V`)** | 안정한(가라앉는) 시스템이 움직이는 동안 절대 오르지 않는 에너지 같은 수입니다. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/ko.md) |
| **Manhattan distance** | 벽을 무시하고 가로 칸 수와 세로 칸 수를 더한 값입니다. | [09-05](phases/09-motion-planning/05-grid-search-dijkstra-to-astar/docs/ko.md) |
| **Manipulability** | tip이 얼마나 자유롭게 움직일 수 있는지 나타내는 점수입니다. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/ko.md) |
| **MDP** | 칸, 행동, 각 결과의 확률, reward를 적어 둔 목록입니다. 이름은 그냥 이름표입니다. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/ko.md) |
| **Mean policy** | 가까운 시연의 움직임을 평균하는 규칙입니다. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/ko.md) |
| **Measurement noise (`R`)** | 센서가 얼마나 들쭉날쭉한지로, 센서 오차의 퍼짐을 제곱한 값입니다. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/ko.md) |
| **Mock joint** | 잘못된 힘(torque)을 거부하는 가짜 팔입니다. 숫자가 아닌 값(NaN)으로 미는 경우가 그 예입니다. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/ko.md) |
| **Model predictive control (MPC)** | 한계를 지키며 짧은 미래를 계획하고 첫 명령만 쓴 뒤 다시 계획하는 방법입니다. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/ko.md) |
| **Monitor** | controller가 볼 수 있는 신호로 경보를 내는 값싼 검사입니다. | [15-01](phases/15-safety-and-deployment/01-failure-modes/docs/ko.md) |
| **Motor lag** | 모터의 힘이 명령을 따라잡기까지 걸리는 지연입니다. | [12-01](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/ko.md) |
| **Motor lag (`Tm`)** | 명령 뒤에 모터의 힘이 얼마나 늦게 오는지입니다. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/ko.md) |
| **MuJoCo** | 우리 반복문과 비교할 완성된 무료 simulator입니다. | [00-08](phases/00-start-here/08-mujoco-hello-world/docs/ko.md) |
| **Multimodal** | 서로 다른 정답이 여럿 있는 것입니다. 각 정답을 mode라고 부릅니다. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/ko.md) |
| **Nearest neighbour** | 다른 스캔에서 가장 가까운 점입니다. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/ko.md) |
| **Nearest neighbours** | 가장 가까운 예시의 행동을 그대로 따라 하거나 평균하는 방법입니다. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/ko.md) |
| **NEES** | 필터의 불확실성이 실제 오차와 맞는지 보는 점수입니다. 정직한 필터는 추적하는 값의 개수만큼, 여기서는 약 3을 받습니다. | [07-05](phases/07-state-estimation/05-extended-kalman-filter/docs/ko.md) |
| **Neighbour table (`L`)** | 어느 로봇끼리 통신할 수 있는지 적어 둔 표입니다. 정식 이름은 graph Laplacian입니다. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/ko.md) |
| **Nested limits** | 계층마다 다음 계층보다 조금 덜 허용하는 구조이고 planner가 가장 빡빡합니다. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/ko.md) |
| **Node** | ROS 2 시스템에서 돌아가는 프로그램 하나입니다. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/ko.md) |
| **Normal force** | 면이 닿아 있는 물체를 면에 수직인 방향으로 밀어내는 힘입니다. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/ko.md) |
| **Not-a-number (`nan`)** | 코사인이 2인 각도를 구하라는 것처럼 답이 없는 계산이 내놓는 결과입니다. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/ko.md) |
| **Numerical IK** | 공식 대신 작은 수정을 반복해서 관절 각도를 찾는 방법입니다. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/ko.md) |
| **Observation** | 로봇이 감지하는 것입니다. 여기서는 바닥 위 자기 위치입니다. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/ko.md) |
| **Occupancy grid** | 지도를 작은 칸으로 나누고 칸마다 "여기 무언가 있다"는 점수를 담은 것입니다. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/ko.md) |
| **Odometry** | 바퀴가 돈 만큼을 더해서 얻는 위치 추정값입니다. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/ko.md) |
| **Old-speed update** | 옛 속도로 움직이는 integrator입니다. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/ko.md) |
| **Open-loop** | 센서로 확인해서 고치지 않고 명령만 보내는 방식입니다. | [12-01](phases/12-simulation-and-sim-to-real/01-what-a-simulator-approximates/docs/ko.md) |
| **Orientation** | 어떤 것이 어느 쪽을 보는지입니다. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/ko.md) |
| **Origin** | 모든 세기가 시작되는 구석이고 (0, 0)으로 적습니다. | [00-02](phases/00-start-here/02-points-as-numbers/docs/ko.md) |
| **Overshoot** | 최종 위치를 지나쳤다가 돌아오는 것입니다. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/ko.md) |
| **p99** | cycle의 99%가 넘지 않는 지연 값입니다. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/ko.md) |
| **Padding** | 검사가 안전한 쪽으로 틀리도록 장애물을 여유만큼 키우는 일입니다. | [09-03](phases/09-motion-planning/03-collision-checking/docs/ko.md) |
| **Particle** | 로봇이 어디에 있고 어느 쪽을 보는지에 대한 추측 하나입니다. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/ko.md) |
| **Particle filter** | particle 무리를 옮기고 측정으로 점수를 매긴 뒤 resampling하는 방식입니다. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/ko.md) |
| **PD control** | 각도에는 스프링을, 각속도(각도가 얼마나 빨리 변하는지)에는 브레이크를 거는 제어입니다. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/ko.md) |
| **PD controller** | 팔이 계획에서 벗어난 정도에 비례해서 밀고 속도에 비례해서 브레이크를 거는 컨트롤러입니다. | [03-05](phases/03-dynamics-and-control/05-computed-torque/docs/ko.md) |
| **PD loop** | 목표 쪽으로 끌어당기고 속도에 비례해 제동하는 제어 코드(controller)입니다. | [04-04](phases/04-actuators-and-sensors/04-latency-budget/docs/ko.md) |
| **Penalty** | waypoint가 장애물에 너무 가까워지면 더해지는 추가 cost입니다. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/ko.md) |
| **Pendulum** | 막대 끝에 달려 중력으로 흔들리는 추입니다. | [00-08](phases/00-start-here/08-mujoco-hello-world/docs/ko.md) |
| **Penetration** | simulator 안에서 물체가 면 속으로 파고든 깊이입니다. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/ko.md) |
| **Period** | 한 번 갔다가 돌아오는 데 걸리는 시간입니다. | [00-08](phases/00-start-here/08-mujoco-hello-world/docs/ko.md) |
| **Period (`T`)** | loop가 한 번 도는 데 계획한 시간입니다. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/ko.md) |
| **PID** | P(오차), I(시간에 따라 쌓은 오차), D(속도에 거는 브레이크) 세 부분으로 조종하는 방법입니다. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/ko.md) |
| **Pitch (`theta`)** | 드론 몸체가 기운 각도입니다. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/ko.md) |
| **Pixel** | 카메라 이미지의 점 하나입니다. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/ko.md) |
| **Planner** | 경로를 그리고 요청할 속도를 정하는 계층입니다. | [15-03](phases/15-safety-and-deployment/03-limits-at-every-layer/docs/ko.md) |
| **Point** | (2, 1.5) 같은 숫자 한 쌍으로 적는 자리 하나입니다. 3D에서는 숫자 세 개입니다. | [00-02](phases/00-start-here/02-points-as-numbers/docs/ko.md) |
| **Point cloud** | 3D 점의 모음입니다. 여기서는 depth 픽셀마다 3D 점으로 되돌려서 만듭니다. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/ko.md) |
| **Policy** | 관측을 행동으로 바꾸는 규칙입니다. | [13-01](phases/13-learning-for-robots/01-imitation-from-demonstrations/docs/ko.md) |
| **Policy gradient** | 평균보다 높은 점수를 받은 움직임 쪽으로 policy를 미는 방법입니다. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/ko.md) |
| **Pose** | 물체가 어느 쪽을 보는지와 어디에 있는지를 합친 것입니다. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/ko.md) |
| **Pose graph** | pose(위치와 그 위치에서 바라보는 방향)를 스프링처럼 작동하는 측정으로 이어 놓은 사슬입니다. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/ko.md) |
| **Position gain (`kp`)** | 각도 오차 1 rad당 모터가 팔을 얼마나 세게 되돌리는지입니다. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/ko.md) |
| **Position mode** | 프로그램은 목표 각도만 주고 토크는 drive 자신의 제어 코드(controller)가 정하는 방식입니다. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/ko.md) |
| **Predict** | 움직임만큼 belief를 밀고 퍼뜨려서 불확실성을 더하는 단계입니다. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/ko.md) |
| **Preemption** | 운영체제가 내 프로그램을 멈추고 다른 프로그램을 실행하는 일입니다. | [05-03](phases/05-robot-software/03-control-loop-jitter/docs/ko.md) |
| **Principal point (`cx, cy`)** | 카메라의 중심선이 닿는 pixel입니다. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/ko.md) |
| **Prior / posterior** | 센서 값을 보기 전의 belief와 본 뒤의 belief입니다. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/ko.md) |
| **Process noise (`Q`)** | 실제 움직임이 필터가 예측에 쓰는 규칙과 다를 수 있어서 한 단계마다 더하는 불확실성입니다. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/ko.md) |
| **Projection** | 3D 점을 pixel로 바꾸는 일입니다. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/ko.md) |
| **Property test** | 규칙 하나에 무작위 입력을 많이 던지는 테스트입니다. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/ko.md) |
| **Publisher / Subscriber** | topic에서 보내는 쪽과 듣는 쪽입니다. | [05-01](phases/05-robot-software/01-publish-subscribe-and-qos-mismatch/docs/ko.md) |
| **Pure pursuit** | 경로 위에서 일정 거리 앞의 점을 향해 로봇을 조향하는 방법입니다. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/ko.md) |
| **QoS** | quality of service의 약자로 메시지를 어떻게 보관하고 전달할지 정하는 설정입니다. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/ko.md) |
| **Quadratic** | 그릇 모양의 비용입니다. 최솟값을 찾기 쉽습니다. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/ko.md) |
| **Quadrotor** | 프로펠러가 네 개인 드론입니다. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/ko.md) |
| **Quantisation** | 부드러운 값을 정수 단계로 반올림하는 일입니다. 작은 변화는 보이지 않게 됩니다. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/ko.md) |
| **Quaternion** | 자세를 나타내는 숫자 네 개입니다. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/ko.md) |
| **Queue depth** | subscriber가 읽기 전까지 보관하는 메시지의 개수입니다. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/ko.md) |
| **Quintic** | 양 끝의 위치, 속도, 미는 힘이 모두 정해진 가장 간단한 곡선입니다. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/ko.md) |
| **rad/s** | 초당 radian으로 나타낸 회전 속도입니다. 한 바퀴는 약 6.28 radian입니다. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/ko.md) |
| **Radian** | 한 바퀴가 약 6.28인 각도 단위입니다. 코드는 이 단위를 씁니다. | [00-03](phases/00-start-here/03-angles-and-radians/docs/ko.md) |
| **Radian (rad)** | 각도의 단위로 한 바퀴가 약 6.28입니다. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/ko.md) |
| **RANSAC** | 무작위 점으로 평면을 여러 번 만들어 보고 가까운 점이 가장 많은 평면을 고르는 방법입니다. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/ko.md) |
| **Rate limit** | tick 한 번에 명령이 바뀔 수 있는 크기의 상한입니다. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/ko.md) |
| **Ray** | pixel을 지나는 시선입니다. 그 위의 모든 점이 같은 pixel에 찍힙니다. | [06-01](phases/06-perception-and-calibration/01-pinhole-camera/docs/ko.md) |
| **Reach band** | 팔이 닿을 수 있는 목표의 띠입니다. 두 link 길이의 차보다 가깝지 않고 합보다 멀지 않은 곳입니다. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/ko.md) |
| **Replay test** | 녹화를 다시 넣어 출력을 믿을 수 있는 녹화와 비교하는 테스트입니다. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/ko.md) |
| **Reprojection error** | 내 값으로 투영한 모서리가 실제로 본 모서리와 얼마나 떨어져 있는지입니다. | [06-02](phases/06-perception-and-calibration/02-camera-calibration/docs/ko.md) |
| **Resampling** | weight가 큰 particle은 복제하고 작은 것은 버리면서 개수는 그대로 둡니다. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/ko.md) |
| **Reservation** | 들어가기 전에 경로 전체를 먼저 잡는 것입니다. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/ko.md) |
| **Residual** | 모델의 오차, 곧 feedforward와 실제로 필요한 중력 torque의 차이입니다. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/ko.md) |
| **Return** | 시도(episode) 하나에서 받은 점수의 합입니다. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/ko.md) |
| **Reward-to-go** | 지금부터 시도가 끝날 때까지 모은 점수입니다. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/ko.md) |
| **Riccati recursion** | 모델과 가중치를 feedback gain으로 바꾸는 반복 계산입니다. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/ko.md) |
| **Rigid move** | 모양을 늘이거나 구부리지 않고 돌리고 밀기만 하는 움직임입니다. | [08-05](phases/08-mobile-robots/05-icp-scan-matching/docs/ko.md) |
| **rms error** | pose와 로봇이 실제로 있던 곳 사이의 전형적인 거리입니다. | [08-06](phases/08-mobile-robots/06-pose-graph-and-loop-closure/docs/ko.md) |
| **Robot** | 주변을 재고 할 일을 정해서 움직이는 일을 되풀이하는 기계입니다. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/ko.md) |
| **Robot frame** | 로봇과 함께 움직이는 좌표계입니다. x는 앞, y는 왼쪽입니다. | [08-04](phases/08-mobile-robots/04-path-following-pure-pursuit/docs/ko.md) |
| **Roll, pitch, yaw** | 앞쪽 축, 옆쪽 축, 수직 축을 도는 회전입니다. | [01-05](phases/01-math-foundations/05-euler-angles-and-gimbal-lock/docs/ko.md) |
| **Rollout** | 시작 위치에서 policy를 한 번 시험 주행해 보는 것입니다. | [13-02](phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/docs/ko.md) |
| **ROS 2** | 로봇을 작은 프로그램 여러 개로 나눠 서로 메시지를 주고받게 하는 로봇 소프트웨어입니다. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/ko.md) |
| **Rotate** | 점을 원점 둘레로 각도만큼 돌리는 것입니다. | [00-05](phases/00-start-here/05-turning-a-point/docs/ko.md) |
| **Rotation axis** | 회전이 도는 중심선입니다. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/ko.md) |
| **Rotation matrix** | 점과 곱하면 점을 돌려 주는 작은 숫자 표입니다. | [00-05](phases/00-start-here/05-turning-a-point/docs/ko.md) |
| **Round trip** | 요청이 나가고 응답이 돌아오는 데 걸리는 시간입니다. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/ko.md) |
| **RRT** | rapidly-exploring random tree입니다. 무작위 지점을 향해 짧은 걸음의 가지를 키우는 방법입니다. | [09-02](phases/09-motion-planning/02-rrt/docs/ko.md) |
| **Rub (`c`)** | 움직임의 반대 방향으로 일정하게 작용하는 저항입니다. | [12-03](phases/12-simulation-and-sim-to-real/03-system-identification/docs/ko.md) |
| **Safety wrapper** | policy와 모터 사이에 놓여 모든 명령을 제한하는 고정된 층입니다. | [13-04](phases/13-learning-for-robots/04-learned-policy-safety-wrapper/docs/ko.md) |
| **Sag** | 팔이 명령한 각도보다 얼마나 아래(또는 위)에 머무는지입니다. | [03-02](phases/03-dynamics-and-control/02-gravity-compensation/docs/ko.md) |
| **Sampler** | 평균 대신 시연 하나를 무작위로 고르는 방식입니다. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/ko.md) |
| **Saturation** | 모터가 토크 한계에 닿아서 더 세게 밀 수 없는 상태입니다. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/ko.md) |
| **Scan** | 레이저 빔을 한 번 훑는 것입니다. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/ko.md) |
| **Seed** | 한 번의 실행이 시작하는 자세입니다. | [02-05](phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/docs/ko.md) |
| **Segment** | 경로 위 두 점 사이의 곧은 구간입니다. | [09-03](phases/09-motion-planning/03-collision-checking/docs/ko.md) |
| **Selection matrix (`S`)** | 방향마다 힘 제어와 위치 제어 중 하나를 고르는 스위치입니다. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/ko.md) |
| **Sensor** | 벽까지의 거리처럼 무언가를 재는 부품입니다. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/ko.md) |
| **Sensor fusion** | 여러 센서의 값을 합쳐 하나의 추정값을 만드는 일입니다. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/ko.md) |
| **Sequence** | 아래에 있는 단계들을 순서대로 실행하고 처음 실패에서 멈추는 단계입니다. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/ko.md) |
| **Service** | 요청 하나에 응답 하나를 돌려주는 방식입니다. 끝없이 흐르는 topic과 다릅니다. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/ko.md) |
| **Settling** | 목표 가까이에 머무는 것입니다. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/ko.md) |
| **Shared parent** | 트리에서 두 frame의 위쪽으로 가장 가까운 frame입니다. 두 경로가 이곳에서 만납니다. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/ko.md) |
| **Shortcutting** | 경로의 일부를 직선 선분으로 바꾸는 일입니다. 그 선분이 비어 있어야 합니다. | [09-02](phases/09-motion-planning/02-rrt/docs/ko.md) |
| **Simulation** | 작은 스텝을 되풀이해서 움직임을 예측하는 프로그램입니다. | [00-06](phases/00-start-here/06-time-steps/docs/ko.md) |
| **Singularity** | 완전히 곧게 뻗은 팔처럼 tip이 움직일 수 있는 방향 하나를 잃은 자세입니다. | [02-04](phases/02-manipulator-kinematics/04-singularities/docs/ko.md) |
| **SLAM** | 지도를 그리면서 동시에 그 위에서 자기 위치를 찾는 방법입니다. | [08-03](phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/docs/ko.md) |
| **Slerp** | 두 자세 사이를 같은 속도로 매끄럽게 돌리는 방법입니다. | [01-03](phases/01-math-foundations/03-axis-angle-and-quaternions/docs/ko.md) |
| **Slope (`vdot`)** | 시스템이 움직이면서 에너지 같은 수가 얼마나 빨리 변하는지입니다. | [03-09](phases/03-dynamics-and-control/09-lyapunov-stability/docs/ko.md) |
| **Speed** | 1초 동안 얼마나 움직이는지입니다. | [00-06](phases/00-start-here/06-time-steps/docs/ko.md) |
| **Speed-first update** | 속도를 먼저 갱신하고 새 속도로 움직이는 integrator입니다. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/ko.md) |
| **Spread** | 움직임의 축들이 서로 얼마나 다른 쪽을 가리키는지입니다. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/ko.md) |
| **Stable** | 윙윙거리거나 폭주하지 않고 가라앉는 loop입니다. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/ko.md) |
| **Stale observation** | wrapper가 허용하는 것보다 오래된 카메라 화면입니다. | [16-03](phases/16-capstones/03-learned-policy-with-safety-wrapper/docs/ko.md) |
| **Stance** | 한 발이 땅에 닿아 있는 시간입니다. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/ko.md) |
| **Starvation** | 다른 callback이 thread를 쥐고 있어서 어떤 callback이 너무 오래 기다리는 일입니다. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/ko.md) |
| **State** | 위치와 속도처럼 앞으로의 움직임을 예측하는 데 필요한 값입니다. | [03-06](phases/03-dynamics-and-control/06-lqr/docs/ko.md) |
| **State (`x`)** | 필터가 추적하는 숫자들입니다. 여기서는 위치와 속도입니다. | [07-02](phases/07-state-estimation/02-kalman-filter/docs/ko.md) |
| **State machine** | 이름 붙은 상태들과 로봇이 상태를 바꾸게 하는 사건마다 그려 둔 화살표를 담은 표입니다. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/ko.md) |
| **Status** | 각 단계가 내놓는 답입니다. 성공했거나 실패했거나 아직 진행 중입니다. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/ko.md) |
| **Steady offset** | 어떤 힘이 관절을 계속 미는데 P와 D만 일할 때 남는 오차입니다. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/ko.md) |
| **Step size (`eps`)** | tick마다 이웃 쪽으로 움직이는 크기입니다. | [14-02](phases/14-multi-robot-and-swarms/02-consensus/docs/ko.md) |
| **Stick and slip** | 접촉의 두 상태입니다. 붙어서 멈춰 있거나 미끄러집니다. | [11-01](phases/11-contact-and-manipulation/01-contact-models/docs/ko.md) |
| **Stiff contact** | 아주 단단한 접촉면입니다. 작은 step이 필요합니다. | [12-02](phases/12-simulation-and-sim-to-real/02-timestep-and-solver/docs/ko.md) |
| **Stiffness (`K`)** | deflection 한 단위당 되미는 힘입니다. | [03-03](phases/03-dynamics-and-control/03-impedance-control/docs/ko.md) |
| **Stiffness (`ke`)** | 표면을 1 m 누르면 그 표면이 되미는 힘의 크기입니다. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/ko.md) |
| **Stiffness (`kx`)** | 손목이 옆으로 1 m 늘어났을 때 드는 옆힘입니다. | [11-04](phases/11-contact-and-manipulation/04-compliance-in-assembly/docs/ko.md) |
| **Sweep** | 모든 칸을 한 번씩 update하는 것입니다. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/ko.md) |
| **Task allocation** | 어느 로봇이 어느 일을 할지 정하는 일입니다. | [14-01](phases/14-multi-robot-and-swarms/01-task-allocation/docs/ko.md) |
| **Terminal cost** | 계획이 끝나는 자리에 매기는 값입니다. 덕분에 짧은 계획도 그 뒤의 일을 고려합니다. | [03-08](phases/03-dynamics-and-control/08-model-predictive-control/docs/ko.md) |
| **tf2** | transform 트리를 저장하는 ROS 2 라이브러리입니다. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/ko.md) |
| **Thread** | 프로그램 안의 일꾼 하나입니다. 한 번에 한 가지 일만 합니다. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/ko.md) |
| **Throughput** | 시간 한 단계당 끝낸 작업 수입니다. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/ko.md) |
| **Thrust (`T`)** | 프로펠러가 내는 위쪽 힘의 합입니다. | [10-03](phases/10-legged-and-aerial/03-quadrotor-model/docs/ko.md) |
| **Tick** | 작은 한 걸음입니다. tree에게 일을 조금 하고 보고하라고 시키는 것입니다. | [05-05](phases/05-robot-software/05-behaviour-trees-and-state-machines/docs/ko.md) |
| **Tick (`dt`)** | 제어 한 단계로 00/06의 time step과 같습니다. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/ko.md) |
| **Time constant** | 오차가 약 3분의 2만큼 줄어드는 데 걸리는 시간입니다. | [11-02](phases/11-contact-and-manipulation/02-force-and-hybrid-control/docs/ko.md) |
| **Time constant (`tau`)** | 가속도계가 넘겨받기 전까지 gyro를 믿는 시간입니다. | [07-04](phases/07-state-estimation/04-complementary-filter/docs/ko.md) |
| **Time constant (`Tc`)** | 몸이 얼마나 빨리 기우는지입니다. 01 레슨과 같은 값입니다. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/ko.md) |
| **Time stamp** | 값을 잰 컴퓨터의 시계가 그 값에 적어 넣은 시각입니다. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/ko.md) |
| **Time step** | loop를 한 번 돌고 다음 번을 돌기 전까지의 짧은 쉼입니다. 여기서는 0.1초입니다. | [00-01](phases/00-start-here/01-what-is-a-robot/docs/ko.md) |
| **Time step (`dt`)** | 컴퓨터가 한 번에 앞으로 넘기는 작은 시간 조각입니다. | [00-06](phases/00-start-here/06-time-steps/docs/ko.md) |
| **Timeout `T`** | watchdog이 작동하기 전까지 조용한 시간을 참아 주는 길이입니다. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/ko.md) |
| **Timing jitter** | 메시지 도착 시각이 흔들리는 정도입니다. | [15-02](phases/15-safety-and-deployment/02-watchdogs-and-stops/docs/ko.md) |
| **Tip** | 손이나 도구가 달린 팔의 끝입니다. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/ko.md) |
| **Tip pose** | 팔 끝이 어디에 있고 어느 쪽을 향하는지입니다. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/ko.md) |
| **Tolerance** | 반올림 잡음을 실패로 보지 않도록 허용하는 아주 작은 오차입니다. | [02-02](phases/02-manipulator-kinematics/02-inverse-kinematics-2link/docs/ko.md) |
| **Topic** | 이름 붙은 스트림입니다. 여기에 보내는 프로그램이 publisher이고 읽는 프로그램이 subscriber입니다. | [00-10](phases/00-start-here/10-ros2-in-one-page/docs/ko.md) |
| **Torque** | 모터가 관절을 돌리는 힘입니다. | [03-01](phases/03-dynamics-and-control/01-the-sampling-limit/docs/ko.md) |
| **Torque (`tau`)** | 비트는 힘입니다. 예를 들어 모터가 joint를 미는 힘입니다. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/ko.md) |
| **Torque mode** | 프로그램이 drive에 얼마나 세게 비틀지 알려 주면 drive가 그대로 따르는 방식입니다. | [04-02](phases/04-actuators-and-sensors/02-torque-vs-position-modes/docs/ko.md) |
| **Touchdown** | 공중에 있던 발이 땅에 닿는 순간입니다. | [10-02](phases/10-legged-and-aerial/02-walking-by-foot-placement/docs/ko.md) |
| **Trace** | 단계마다 기록 하나를 남기고 그 전후 상태를 담은 로그입니다. | [05-04](phases/05-robot-software/04-time-sync-and-traces/docs/ko.md) |
| **Track width (`b`)** | 두 바퀴 사이의 거리입니다. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/ko.md) |
| **Trajectory profile** | 두 자세 사이에서 관절의 위치가 시간에 따라 어떻게 바뀔지 정한 계획입니다. | [09-01](phases/09-motion-planning/01-trajectory-profiles/docs/ko.md) |
| **Transform** | 회전 하나와 이동 하나를 담은 4x4 숫자 표입니다. | [00-09](phases/00-start-here/09-reading-a-urdf/docs/ko.md) |
| **Transform (`T`)** | 회전과 이동을 한 표에 담은 4x4 행렬입니다. | [01-01](phases/01-math-foundations/01-rotations-and-se3/docs/ko.md) |
| **Transform (`X`)** | gripper를 기준으로 카메라가 어느 쪽으로 돌아 있고 얼마나 떨어져 있는지입니다. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/ko.md) |
| **Transform name (`T_to_from`)** | transform이 어느 frame에서 어느 frame으로 바꾸는지 알려 주는 이름입니다. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/ko.md) |
| **Transform tree** | 모든 frame이 부모 frame 하나에 매달린 지도입니다. | [01-04](phases/01-math-foundations/04-frames-and-transform-trees/docs/ko.md) |
| **Translation** | 돌림이 아니라 직선으로 옮기는 이동입니다. | [06-04](phases/06-perception-and-calibration/04-hand-eye-calibration/docs/ko.md) |
| **Transpose (`.T`)** | 행렬의 행과 열을 맞바꿉니다. | [00-07](phases/00-start-here/07-python-env-and-numpy/docs/ko.md) |
| **Transpose (`J^T`)** | 같은 행렬의 행과 열을 맞바꾼 것입니다. | [02-03](phases/02-manipulator-kinematics/03-jacobian-and-velocity/docs/ko.md) |
| **Tunnelling** | 검사 간격이 너무 넓어서 움직임이 얇은 장애물을 통과해 버리는 일입니다. | [09-03](phases/09-motion-planning/03-collision-checking/docs/ko.md) |
| **Twist (`alpha`)** | 다음 joint가 도는 선이 이 joint가 도는 선에 비해 얼마나 기울었는지입니다. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/ko.md) |
| **Unit test** | 가짜 시계를 돌리고 단순한 규칙 하나를 확인하는 테스트입니다. | [15-04](phases/15-safety-and-deployment/04-testing-robot-code/docs/ko.md) |
| **Update** | 각 장소가 센서 값을 얼마나 잘 설명하는지에 따라 belief의 가중치를 다시 매기는 단계입니다. | [07-01](phases/07-state-estimation/01-bayes-filter/docs/ko.md) |
| **URDF** | 로봇을 joint로 이어진 link로 설명하는 텍스트 파일입니다. | [00-09](phases/00-start-here/09-reading-a-urdf/docs/ko.md) |
| **Value `V(s)`** | 이후에 최선의 행동을 고른다고 할 때 그 칸에서 기대되는 reward입니다. | [13-05](phases/13-learning-for-robots/05-mdps-and-value-iteration/docs/ko.md) |
| **Variance** | 결과가 실행마다 튀는 정도입니다. | [13-03](phases/13-learning-for-robots/03-policy-gradients/docs/ko.md) |
| **venv** | 프로젝트 하나에 쓰는 Python 도구를 담는 전용 폴더입니다. | [00-07](phases/00-start-here/07-python-env-and-numpy/docs/ko.md) |
| **Voxel grid** | 공간을 작은 정육면체로 나눈 것입니다. 정육면체마다 평균 점 하나만 남기면 점이 줄어듭니다. | [06-03](phases/06-perception-and-calibration/03-depth-and-point-clouds/docs/ko.md) |
| **Wait-for graph** | 각 로봇에서 그 로봇이 기다리는 로봇으로 화살표를 그은 그림입니다. | [14-03](phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/docs/ko.md) |
| **Watchdog** | heartbeat가 늦으면 로봇을 세우는 감시 장치입니다. | [05-02](phases/05-robot-software/02-executors-and-callbacks/docs/ko.md) |
| **Waypoint** | 경로 위의 점 하나입니다. 경로는 이 점들의 사슬입니다. | [09-04](phases/09-motion-planning/04-trajectory-optimisation/docs/ko.md) |
| **Weight** | 이 추측이 맞다면 보였을 거리가 로봇이 실제로 잰 거리와 얼마나 가까운지를 나타내는 점수입니다. | [08-02](phases/08-mobile-robots/02-particle-filter-localisation/docs/ko.md) |
| **Wheel radius (`r`)** | 바퀴 중심에서 가장자리까지의 거리입니다. | [08-01](phases/08-mobile-robots/01-differential-drive-and-odometry/docs/ko.md) |
| **Width (`w`)** | 각 수치를 바꿀 수 있는 폭을 원래 값에 대한 비율로 나타낸 것입니다. | [12-04](phases/12-simulation-and-sim-to-real/04-domain-randomisation/docs/ko.md) |
| **Window** | 속도를 구하려고 빼는 두 count가 몇 번 읽기만큼 떨어져 있는지입니다. | [04-03](phases/04-actuators-and-sensors/03-encoders-and-quantisation/docs/ko.md) |
| **Windup** | 포화된 동안 I 부분이 계속 쌓였다가 overshoot를 일으키는 현상입니다. | [03-04](phases/03-dynamics-and-control/04-pid-and-tuning/docs/ko.md) |
| **Wobble (jitter)** | 스텝마다 행동이 바뀌는 크기입니다. 크면 흔들려 보입니다. | [13-06](phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/docs/ko.md) |
| **Workspace** | 손끝이 닿을 수 있는 모든 곳입니다. | [01-02](phases/01-math-foundations/02-forward-kinematics/docs/ko.md) |
| **Wrap** | 가리키는 방향은 그대로 두고 각도를 한 바퀴 안으로 되돌리는 일입니다. | [00-03](phases/00-start-here/03-angles-and-radians/docs/ko.md) |
| **Wrench** | 밀기와 비틀기를 함께 묶은 것입니다. 2차원에서는 세 숫자, 즉 좌우로 미는 힘, 위아래로 미는 힘, 비틀림입니다. | [11-03](phases/11-contact-and-manipulation/03-grasp-quality/docs/ko.md) |
| **Zero pose** | 모든 joint 각도가 0인 팔의 자세입니다. | [02-01](phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/docs/ko.md) |
| **ZMP** | zero-moment point입니다. 발 아래에서 지면의 미는 힘이 작용하는 점입니다. | [10-01](phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/docs/ko.md) |
