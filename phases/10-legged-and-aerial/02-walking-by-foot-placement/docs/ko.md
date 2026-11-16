# 발 위치로 걷기

> 걷는 로봇이 발을 어디에 놓을지만 골라서 속도를 조절하는 방법을 알아봅니다.

**유형:** 만들기   **선수 지식:** 10/01 도립진자와 ZMP   **시간:** 약 15분

## 쉽게 말하면

걸을 때는 발을 어디에 놓느냐로 속도를 조절해요. 발을 몸보다 한참 앞에 놓으면 몸이 발 뒤에 있게 되어 중력이 몸을 뒤로 끌어서 느려져요. 발을 너무 가까이 놓으면 몸이 발 위를 지나쳐 가서 중력이 몸을 앞으로 끌어서 빨라져요.

보행 모델은 몸의 위치와 속도를 보고 발 놓을 자리를 골라요. 너무 짧은 걸음은 걸음마다 속도를 조금씩 더 키워요.

## 핵심 용어

- **Foot placement**: 속도를 조절하려고 다음 발이 닿을 자리를 고르는 일입니다.
- **Stance**: 한 발이 땅에 닿아 있는 시간입니다.
- **Touchdown**: 공중에 있던 발이 땅에 닿는 순간입니다.
- **Deadbeat**: 한 걸음 만에 목표에 이르고 그다음부터 정확히 유지하는 제어기입니다.
- **`Tc`**: 01 레슨에서 나온, 몸이 넘어지는 시간 규모입니다.
- **`sinh`, `cosh`**: `exp(t/Tc)`와 `exp(-t/Tc)`로 만든 곡선입니다. 넘어지는 몸을 나타냅니다.

## 문제

걷는 로봇에 0.6 m/s를 요구하면서 그럴듯한 고정 보폭을 준다고 상상해 보세요. 걸음마다 빨라져 몸이 발보다 한참 앞으로 나갑니다. 걸음이 조금 짧아서 중력이 몸을 계속 앞으로 밀었기 때문입니다.

## 개념

실제 보행 로봇에는 브레이크가 없고 발뿐이므로 발 위치가 속도를 올리고 내리는 방법입니다.

![발 위치 루프](../assets/diagram-foot-placement-loop.png)

*stance가 끝날 때마다 `x`와 `v`를 읽고 다음 발을 고릅니다.*

stance는 `T` 동안 이어지고 다음 발은 `p`에 놓입니다.
touchdown에 몸이 그 발보다 얼마나 앞에 있는지를 `u = x - p`라고 씁니다.
01 레슨의 `lipm_state`로 stance 끝의 속도를 구하면 `v' = (u/Tc) sinh(T/Tc) + v cosh(T/Tc)`입니다.
`v' = v_target`으로 두고 `u`를 풀면 발은 `p = x - u`입니다. 이것이 한 걸음 deadbeat입니다.

`v = 0.3 m/s`에서 출발하고 목표는 0.6 m/s입니다.
걸음마다 끝의 속도(m/s)는 deadbeat 걸음에서 0.31, 0.60, 0.60입니다(첫 발은 미리 놓여 있었습니다). deadbeat 길이의 1.5배인 걸음에서는 0.31, 0.42, 0.22, 0.67, -0.34입니다(음수는 뒤로 가는 속도입니다).

![보행자 둘](../assets/clip-example.mp4)

*파란 보행자(deadbeat의 1.5배 걸음)는 거의 나아가지 못하고 초록 보행자는 0.6 m/s로 걷습니다.*

![걸음 길이의 결과](../assets/diagram-step-length-outcomes.png)

*0.6배 걸음은 속도가 발산하고 1.5배 걸음은 속도가 요동치다가 뒤로 향합니다.*

`v_target`으로 일정하게 걸을 때 deadbeat 걸음 길이는 `2 Tc v tanh(T/2Tc)`입니다. `T = 0.4 s`, `h = 0.9 m`, `v = 0.6 m/s`이면 0.21 m입니다.

![무게중심](../assets/fig-com-over-steps.png)

*deadbeat 걸음은 2번째 걸음부터 속도를 0.6 m/s에 고정하고 60%로 줄인 걸음은 여섯 번째 걸음에 5 m/s에 이릅니다.*

## 만들기

```python
def next_foot(x, v, v_target, T, h):
    tc = time_constant(h)
    u = (v_target - v * np.cosh(T / tc)) * tc / np.sinh(T / tc)
    return x - u
```

`walk()`는 stance를 이어 붙입니다. `step_scale`은 걸음 길이에 곱해지므로 일부러 망가뜨려 볼 수 있습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/02-walking-by-foot-placement -q
python3 phases/10-legged-and-aerial/02-walking-by-foot-placement/code/main.py
```

## 실제 도구로 보기

마지막 테스트가 첫 stance를 SciPy의 적분기와 비교합니다. 실제 제어기는 걸음 시간도 고르고 발을 닿을 수 있는 위치로 자릅니다.

## 결과물

`outputs/skill-foot-placement-check.md`는 걸음 제어기의 deadbeat 일관성, 걸음 길이 배율, 도달 범위 제한을 검토합니다.

## 연습 문제

1. 걸음 길이를 0.15 m로 제한하고 걷는 모델이 유지할 수 있는 가장 빠른 속도를 찾으세요.
2. `T`를 0.6초로 바꾸고 정상 보행의 걸음 길이를 다시 계산하세요.
3. 측정한 `x`에 20 mm 오차를 넣고 속도가 목표에서 얼마나 벗어나는지 보세요.
