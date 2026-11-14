# 로봇 코드 테스트 (Testing Robot Code)

> 로봇 테스트는 시간을 통제하고 나쁜 명령을 거부하고 실제로 있었던 일을 다시 재생해야 합니다.

**유형:** 만들기   **선수 지식:** 15/01 고장 유형   **시간:** 약 15분

## 쉽게 말하면

타이머 앱을 시험할 때는 알람이 울릴 때까지 기다리지 않고 가짜 시계를 마감 시각 너머로 옮겨요. 로봇 테스트도 똑같아요. 가짜 시계를 손으로 돌리면 몇 초 동안의 팔 움직임이 실제 시간 없이 지나가요. 그다음
간단한 질문 하나를 던져요. 목표가 앞으로 뛰어 나갔을 때(step) 관절이 목표에 더 가까워지나요?

부호가 뒤집힌 controller는 팔을 반대로 밀어서 이 테스트가 바로 실패해요. mock joint, 곧 가짜 팔은 나쁜 torque를 거부해요. 녹화한 실행을 다시 재생하면 어떤 명령이 바뀌었는지 보여요.

## 문제

로봇 코드는 시계와 관절과 예측할 수 없는 입력에 의존합니다. 그래서 테스트가 몇 초씩 sleep하거나 하드웨어가 필요하거나 아무것도 검사하지 못합니다. 01 레슨의 wrong sign 결함이 그 증거입니다. 관절이 폭주해도 "숫자를 돌려준다"만 보는 테스트는 통과합니다.

## 개념

![세 가지 테스트와 세 가지 버그](../assets/diagram-test-kinds.png)

*unit은 가짜 시계를 돌리고 규칙 하나를 확인합니다("0.3초 뒤 더 가까운가?"). replay는 녹화한 측정값을 다시 넣어 토크를 비교합니다. property는 무작위 입력 수천 개를 규칙 하나에 던집니다.*

![테스트가 시계를 가집니다](../assets/diagram-fake-clock.png)

*controller는 객체를 통해 시간을 묻습니다. 운영에서는 진짜 시계를 받고 테스트에서는 테스트가 앞으로 돌리는 가짜 시계를 받습니다. 그래서 10초가 순식간에 지나고 결과가 흔들리지 않습니다.*

![두 테스트가 본 부호 버그](../assets/fig-sign-bug.png)

*왼쪽에서는 0.3초 뒤 관절이 목표에서 멀어 step 테스트가 실패합니다. 오른쪽은 녹화된 입력을 버그가 있는 controller에 재생했을 때 녹화 토크의 거울상이 나오는 모습입니다.*

replay 예시입니다. 1.0 rad step은 `kp * error = 40 * 1.0 = 40`을 만들고 `tau_max` 10으로 잘리므로 녹화된 첫 torque는 +10.0입니다. 부호가 뒤집힌 controller에 같은 녹화 측정값을 넣으면 첫 답은 -10.0이고 그 뒤에도 녹화 torque의 거울상이 이어집니다.

10 ms 간격의 샘플 80개가 모두 그렇습니다. replay 테스트는 첫 샘플에서 실패합니다.

![두 로봇 팔이 같은 녹화를 재생할 때 부호가 뒤집힌 controller는 반대로 밉니다](../assets/clip-example.mp4)

*두 팔 모두 녹화 하나를 재생합니다. 빨간 화살표는 각 controller의 torque입니다. 초록은 목표 쪽으로 밀고 부호가 뒤집힌 파란 쪽은 반대로 밉니다.*

![무작위 입력에서의 토크](../assets/fig-property-torque.png)

*property 테스트는 무작위 입력을 수천 개 뽑아 한 가지만 확인합니다. 토크는 유한하고 한계를 넘지 않는다는 것입니다.*

## 만들기

`FakeClock`은 `now()`와 `advance(dt)`를 가집니다. `MockJoint`는 단순한 plant를 적분하고 한계를 넘는 토크나 NaN(숫자가 아닌 값)을 받으면 예외를 냅니다.

`Controller`는 PD loop이며 update 간격이 timeout을 넘으면 토크 0을 냅니다.

`run()`은 trace를 `(q_meas, q_ref, tau)` 행으로 돌려줍니다.

```python
def test_step_direction_test_catches_the_sign_bug():
    with pytest.raises(AssertionError, match="moved away"):
        check_step_direction(polarity=-1)
```

`code/tests/golden_trace.json`은 믿을 수 있는 녹화본으로 정상 controller에서 얻었습니다. 유한값 검사가 없으면 property 테스트가 NaN 입력에서 실패합니다. 그래서 controller는 NaN과 무한대에 토크 0을 돌려줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/04-testing-robot-code -q
python3 phases/15-safety-and-deployment/04-testing-robot-code/code/main.py
```

## 실제 도구로 보기

ROS 2 노드에서도 시계를 같은 방식으로 주입하거나 simulated time을 씁니다. 정상 실행의 실제 bag을 녹화해 두고 배포 전마다 새 코드에 재생합니다. hypothesis 같은 property 테스트 라이브러리를 쓸 수 있습니다.

## 결과물

`outputs/skill-robot-test-plan.md`는 controller를 unit, replay, property 테스트 목록으로 바꿔 줍니다.

## 연습 문제

1. `kp`를 바꿔 replay 테스트가 실패하는 것을 보고 다시 녹화할지 판단하세요.
2. update가 끊긴(stale) controller가 항상 정확히 0을 돌려준다는 property 테스트를 쓰세요.
3. `q_meas`와 `q_ref` 인자 순서가 바뀐 경우를 잡는 테스트를 추가하세요.
