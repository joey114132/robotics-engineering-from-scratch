# 샘플링 한계 (The Sampling Limit)

> 연속 시간에서는 맞는 damper도 컨트롤러가 명령을 한 tick 동안 붙잡고 있으면 불안정해질 수 있습니다.

**유형:** 만들기   **선수 지식:** 없음   **시간:** 약 15분

## 쉽게 말하면

친구가 미끄러지는 퍽을 보고 반대 방향으로 밀다가 다음에 볼 때까지 같은 힘을 유지해요. 퍽이 멈춘 뒤에도 계속 밀면 퍽이 반대로 움직이기 시작해요.

sampled damper도 이전 속도로 정한 torque를 joint에 계속 가해요. damping이 크거나 유지 시간이 길거나 inertia가 작으면 속도가 더 쉽게 뒤집혀요. 너무 세게 오래
밀면 방향이 바뀔 때마다 속도가 줄지 않고 커질 수 있어요.

## 문제

관절이 흔들리지 않게 하려고 damping gain `kd`를 올렸더니 이번에는 관절이 윙윙거립니다. gain은 무난해 보였습니다. host는 제어 주기마다 토크를 한 번 계산해서 붙잡고 있으므로 damper는 이미 한 tick 지난 속도를 상대로 힘을 냅니다.

## 개념

![붙잡힌 명령은 낡은 속도에 작용합니다](../assets/diagram-stale-command.png)

*토크는 tick 시작 시점의 속도로 계산되지만 tick 전체 동안 작용합니다.*

순수 관성 `J`에 `-kd * v` 토크를 `dt` 동안 붙잡고 있으면 한 tick 뒤 `v+ = v * (1 - r)`이 됩니다. 여기서 `r = dt * kd / J`입니다. 모든 것은 `1 - r`이라는 인자가 정합니다.

![r의 네 구간](../assets/diagram-r-zones.png)

*1보다 작으면 속도가 부드럽게 줄어듭니다. 정확히 1이면 한 tick 만에 0이 됩니다. 1과 2 사이에서는 부호가 뒤집히지만 여전히 줄어듭니다. 2 이상이면 줄지 않습니다.*

![tick별 속도와 인자 1 - r](../assets/fig-r-response.png)

*왼쪽은 `r` 네 값에 대한 속도입니다. 오른쪽은 인자 `1 - r`이 `r = 1`에서 0을, `r = 2`에서 -1을 지나는 모습입니다.*

비율 안에 `J`가 들어 있으므로 유효 관성이 가장 작은 관절(대개 손목)이 어깨에서는 무난하게 느껴지는 gain에서 먼저 선을 넘습니다.

## 만들기

```python
def step_damper(v, J, kd, dt):
    return v * (1.0 - dt * kd / J)

def classify(J, kd, dt):
    r = dt * kd / J
    return "smooth" if r <= 1 else "chatter" if r < 2 else "divergent"
```

테스트는 `J = 0.02`, `dt = 0.001`에서 각 경계의 양쪽을 확인합니다. 이때 한계는 `kd = 20`과 `kd = 40`입니다. 테스트 하나는 `r = 1`을 정확히 확인합니다. 속도는 한 tick 뒤 0이 되고 부호는 뒤집히지 않습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/01-the-sampling-limit -q
python3 phases/03-dynamics-and-control/01-the-sampling-limit/code/figure.py
```

## 실제 도구로 보기

많은 드라이브는 훨씬 빠른 내부 loop를 돌리므로 host loop의 한계가 사라집니다. damping을 host에 두어야 한다면 `kd`를 낮추거나 loop 주기를 올리거나, 관성이 가장 작은 자세의 값으로 gain의 상한을 정해야 합니다.

## 결과물

`outputs/skill-sampling-limit-check.md`는 gain 파일의 damping이 걸린 모든 관절에 대해 `r`을 계산합니다.

## 연습 문제

1. 스프링 항을 넣고 `(kp, kd)` 평면에서 안정 영역을 시뮬레이션으로 찾으세요.
2. 붙잡힌 명령에 한 tick 지연을 넣으세요. 한계는 어디로 움직입니까?
3. 레슨 03/02를 이용해 2링크 손목의 유효 관성을 추정하세요.
