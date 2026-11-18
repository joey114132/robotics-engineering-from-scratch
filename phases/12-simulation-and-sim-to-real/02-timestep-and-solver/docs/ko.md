# Time Step과 Solver

> 시뮬레이션 속 공이 떨어진 높이보다 높이 튀는 이유와 한 줄짜리 해결법을 배웁니다.

**유형:** 만들기   **선수 지식:** 12/01 시뮬레이터가 근사하는 것   **시간:** 약 15분

## 쉽게 말하면

상자가 단단한 스프링 패드 위로 떨어져요. 눌린 패드가 상자를 위로 밀어 올리니 상자는 떨어뜨린 높이까지만 올라와야 해요. 컴퓨터는 이 움직임을 정해진 짧은 시간 간격으로 계산해요.
컴퓨터가 옛 속도로 상자를 옮기면 상자가 에너지(여분의 튐)를 공짜로 얻어서 너무 높이 튀어요. 속도를 먼저 갱신하면 대부분 해결돼요.

## 핵심 용어

- **Time step (`dt`)**: 한 번 갱신할 때 시간을 앞으로 넘기는 작은 간격입니다.
- **Integrator**: 시뮬레이션을 한 step 앞으로 보내는 규칙입니다.
- **Old-speed update**: 옛 속도로 움직이는 integrator입니다.
- **Speed-first update**: 속도를 먼저 갱신하고 새 속도로 움직이는 integrator입니다.
- **Energy drift**: 시뮬레이션 속 상자나 진자가 원래 없어야 할 튐이나 흔들림을 얻는 현상입니다.
- **Stiff contact**: 아주 단단한 접촉면입니다. 작은 step이 필요합니다.

## 문제

시뮬레이션에서 공을 떨어뜨렸더니 떨어진 높이보다 높이 튀거나 time step을 키우자 팔이 떨립니다. 물리는 그대로이고 계산만 바뀌었습니다.

## 개념

시뮬레이터는 시간을 한 step씩 앞으로 보내므로 step이 잘못되면 로봇 시험이 거짓말을 합니다. 옛 속도 갱신은 여분의 튐(에너지)을 공짜로 만들어 냅니다. 속도를 먼저 갱신하는 방식은 그렇지 않습니다.
그래도 step이 너무 크면 결과가 폭발할 수 있으므로 답이 더 변하지 않을 때까지 step을 줄이세요.

![갱신 순서](../assets/diagram-update-order.png)

*왼쪽은 옛 속도로 움직이고 오른쪽은 속도를 먼저 갱신한 뒤 움직입니다.*

![step 크기](../assets/diagram-dt-sweep.png)

*아주 작은 step에서 시작해 결과가 바뀔 때까지 키웁니다.*

![drift와 반발](../assets/fig-dt-sweep.png)

*왼쪽은 진자의 에너지입니다. 옛 속도 갱신에서는 오르고 속도 먼저 갱신에서는 평평합니다. 오른쪽은 step 크기에 따른 첫 반발의 높이입니다.*

![상자 셋](../assets/clip-example.mp4)

*같은 낙하를 step 크기 세 가지로 본 장면입니다. 가장 작은 step(초록)만 떨어뜨린 높이로 돌아옵니다.*

<details><summary>The math (optional)</summary>

옛 속도 갱신을 explicit Euler, 속도 먼저 갱신을 semi-implicit Euler라고 부릅니다. 스프링에 달린 질량의 위치를 `x`, 속도를 `v`, 주파수를 `w`라 합니다.
explicit Euler는 매 step 에너지에 `1 + (w*dt)^2`를 곱합니다. semi-implicit Euler는 `w*dt < 2`인 동안 안정합니다.
`dt` 0.01 s에서 10초 동안 explicit Euler는 39%, semi-implicit은 0.95% drift합니다. 1 kg 질량을 0.1 m 높이에서 10 kN/m 접촉면에 떨어뜨리면 0.1 m로 돌아와야 합니다.
explicit Euler는 3 ms에서 0.274 m로 2.7배 높고 0.1 ms에서 0.103 m입니다. semi-implicit은 3 ms까지 5% 안에 머물고 19 ms에서 0.65 m로 6배 높습니다.

</details>

## 만들기

step 함수 하나가 두 방법을 모두 맡습니다. 접촉은 바닥 아래에서만 위로 미는 스프링입니다.

```python
def step(method, x, v, acc, dt):
    if method == "euler":
        return x + dt * v, v + dt * acc(x)
    v = v + dt * acc(x)
    return x + dt * v, v
```

`pendulum_drift()`는 진자의 최악 에너지 오차를 재고 `rebound_height()`는 첫 반발의 꼭대기 높이를 잽니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/12-simulation-and-sim-to-real/02-timestep-and-solver -q
python3 phases/12-simulation-and-sim-to-real/02-timestep-and-solver/code/main.py
```

## 실제 도구로 보기

MuJoCo의 기본 integrator는 속도 먼저 갱신하는 방식입니다.

출처는 MuJoCo XML reference의 `option/timestep`과 `option/integrator`입니다(https://mujoco.readthedocs.io/en/stable/XMLreference.html, 2026년 11월 9일 확인).

## 결과물

`outputs/skill-timestep-sweep.md`는 시뮬레이션 결과가 `dt`에 따라 달라지지 않는지 확인합니다.

## 연습 문제

1. 접촉 stiffness를 절반으로 줄이세요. step을 얼마나 더 키울 수 있나요?
2. 진자 에너지 drift가 1% 아래인 가장 큰 step을 찾으세요.
3. 19 ms 실행은 너무 높이 튀지만 폭발하지는 않습니다. 왜일까요?
