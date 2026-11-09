# 도립진자와 ZMP

> 서 있는 몸은 끝으로 선 진자처럼 넘어지고 capture point는 다음 발이 어디에 닿아야 하는지 알려 줍니다.

**유형:** 만들기   **선수 지식:** 03/04 PID와 튜닝   **시간:** 약 15분

## 문제

뒤에서 밀린 biped가 발목으로 최대한 버티는데도 계속 앞으로 기웁니다. 발목은 힘이 닿는 점을 발바닥 안에서만 옮길 수 있어서, 충분히 큰 밀침은 발목의 능력 밖입니다. 넘어지기 전에 걸음이 필요한지 필요하다면 어디인지를 알려 주는 작은 모델이 있어야 합니다.

## 개념

![다리에서 시상수 하나가 나오기까지](../assets/diagram-lipm-flow.png)

*몸을 높이 `h`의 질점 하나로 보고 다리는 질량이 없다고 둡니다. 그러면 넘어지는 속도가 `Tc`라는 숫자 하나로 모입니다.*

발이 `p`에 있으면 질점은 `x'' = (g/h)(x - p)`를 따릅니다. `exp(t/Tc)`를 대입하면 `1/Tc^2 = g/h`이므로 `Tc = sqrt(h/g)`입니다. 일반해는 `x = p + (x0-p) cosh(t/Tc) + Tc v0 sinh(t/Tc)`입니다.

`h = 0.9 m`이면 `Tc`는 약 0.30초입니다.

zero-moment point(ZMP)는 지면 반력이 작용하는 점으로 `p = x - (h/g) x''`입니다. 이 점은 발 밖으로 나갈 수 없습니다.

capture point `xi = x + v Tc`는 `xi' = (xi - p)/Tc`를 따르므로 발을 `xi`에 놓으면 그 값이 멈추고 몸은 그 발 위에서 정지합니다.

![발목 토크인가 걸음인가](../assets/diagram-capture-decision.png)

*`xi`가 발 안에 있으면 발목으로 버틸 수 있습니다. 밖에 있으면 걸음만 해결책입니다.*

![같은 밀침에서 넘어지는 경우와 회복하는 경우](../assets/fig-fall-and-recovery.png)

*같은 0.4 m/s 밀침이고 capture point는 0.12 m, 발 반길이는 0.05 m입니다. 발목만 쓰면 몸이 발산합니다. 0.1초에 `xi`로 걸으면 0.15 m에서 멈춥니다.*

## 만들기

```python
def lipm_state(x0, v0, p, t, h, g=G):
    tc, a = time_constant(h, g), x0 - p
    c, s = np.cosh(t / tc), np.sinh(t / tc)
    return p + a * c + tc * v0 * s, a * s / tc + v0 * c

def capture_point(x, v, h, g=G):
    return x + v * time_constant(h, g)
```

`simulate()`는 같은 식을 RK4로 적분하고 테스트가 닫힌 해와 비교합니다. `fall_or_recover()`는 ZMP를 발 안으로 제한하고 필요하면 걸음을 냅니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp -q
python3 phases/10-legged-and-aerial/01-inverted-pendulum-and-zmp/code/main.py
```

## 실제 도구로 보기

SciPy의 `solve_ivp`가 같은 ODE를 적분하고 마지막 테스트가 닫힌 해와 비교합니다. 전신 제어기는 질점 대신 전신의 무게중심을 쓰지만 capture point 검사는 같습니다.

## 결과물

`outputs/skill-capture-point-check.md`는 균형 코드에서 ZMP 제한, capture point 검사, 걸음 trigger를 검토합니다.

## 연습 문제

1. `h`를 1.8 m로 올리고 발목만으로 받을 수 있는 가장 큰 밀침을 찾으세요.
2. 걸음을 0.3초 늦추고 발이 어디에 닿아야 하는지 구하세요.
3. 발 폭 0.1 m를 넣고 걸음 목표가 움직이는 것을 보이세요.
