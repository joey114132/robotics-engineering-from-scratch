# 발 위치로 걷기

> 걷는 로봇은 발로 속도를 조종합니다. 다음 발 위치는 지금 몸이 있는 곳에서 풀어 냅니다.

**유형:** 만들기   **선수 지식:** 10/01 도립진자와 ZMP   **시간:** 약 15분

## 문제

보행 모델에 0.6 m/s를 요구하면서 그럴듯한 고정 보폭을 줍니다. 몇 걸음은 괜찮아 보이다가, 걸음마다 속도가 빨라져 몸이 발보다 한참 앞으로 나갑니다. 보폭이 조금 짧았을 뿐인데 짧은 걸음은 속도를 줄이기는커녕 에너지를 밀어 넣습니다.

## 개념

![발 위치를 고르는 한 걸음](../assets/diagram-foot-placement-loop.png)

*stance가 끝날 때마다 제어기가 `x`와 `v`를 읽고 다음 발을 고릅니다. 이 루프가 걸음마다 반복됩니다.*

stance는 `T` 동안 이어지고 다음 발은 `p`에 놓입니다. touchdown 때 그 발에 대한 몸의 위치를 `u = x - p`라고 씁니다. 01 레슨의 닫힌 해로 stance 끝의 속도를 구합니다.

결과는 `v' = (u/Tc) sinh(T/Tc) + v cosh(T/Tc)`입니다.

`v' = v_target`으로 두고 `u`를 풀면 발은 `p = x - u`입니다. 이것이 한 걸음 deadbeat이라서 속도가 한 걸음 만에 정확히 맞습니다.

![걸음 길이가 속도에 미치는 영향](../assets/diagram-step-length-outcomes.png)

*올바른 걸음을 0.6배로 줄이면 속도가 발산합니다. 1.5배로 늘리면 속도가 요동치다 뒤집힙니다.*

`v_target`으로 정상 보행할 때 걸음은 `2 Tc v tanh(T/2Tc)`입니다. `T = 0.4 s`, `h = 0.9 m`, `v = 0.6 m/s`이면 0.21 m입니다.

![여섯 걸음 동안의 무게중심](../assets/fig-com-over-steps.png)

*출발과 목표가 같습니다. deadbeat 걸음은 두 번째 걸음부터 속도를 0.6 m/s에 고정합니다. 60%로 줄인 걸음은 여섯 번째 걸음에 5 m/s에 이릅니다.*

## 만들기

```python
def next_foot(x, v, v_target, T, h):
    tc = time_constant(h)
    u = (v_target - v * np.cosh(T / tc)) * tc / np.sinh(T / tc)
    return x - u
```

`walk()`는 01 레슨의 `lipm_state`로 stance를 이어 붙입니다. `step_scale`이 명령한 걸음 길이에 곱해지므로 일부러 망가뜨려 볼 수 있습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/02-walking-by-foot-placement -q
python3 phases/10-legged-and-aerial/02-walking-by-foot-placement/code/main.py
```

## 실제 도구로 보기

마지막 테스트가 첫 stance를 SciPy로 적분해 여기서 쓰는 닫힌 해와 비교합니다. 실제 제어기는 걸음 시간 선택, 유각 발의 제한, 도달 범위 제한을 더하고 발을 닿을 수 있는 위치로 자릅니다.

## 결과물

`outputs/skill-foot-placement-check.md`는 걸음 제어기의 deadbeat 일관성, 걸음 길이 배율, 도달 범위 제한을 검토합니다.

## 연습 문제

1. 걸음 길이를 0.15 m로 제한하고 걷는 모델이 유지할 수 있는 가장 빠른 속도를 찾으세요.
2. `T`를 0.6초로 바꾸고 정상 보행의 걸음 길이를 다시 계산하세요.
3. 측정한 `x`에 20 mm 오차를 넣고 속도가 목표에서 얼마나 벗어나는지 보세요.
