# 지연 예산 (Latency Budget)

> loop의 모든 단계가 지연을 더하고 그 지연은 phase margin을 소모합니다. 남은 margin이 kd를 얼마나 키울 수 있는지 정합니다.

**유형:** 만들기   **선수 지식:** 04/03 Encoder와 양자화, 03/01 샘플링 한계   **시간:** 약 15분

## 쉽게 말하면

화면이 늦게 나오는 게임에서 cursor를 목표에 맞춰 보세요. 화면에는 아직 왼쪽에 있어서 오른쪽으로 계속 조작해요. 목표를 지난 모습이 보일 때는 이미 너무 멀리 보낸 뒤예요.

로봇 loop에서도 sensor와 filter와 통신의 지연이 더해져요. 보정이 더 빠르게 반복되면 같은 지연도 한 주기에서 더 큰 몫을 차지해요. damping을 키우다가 보정 주파수가 높아지면
지연을 버티는 여유가 줄 수 있어요. gain은 전체 latency budget에 맞아야 해요.

## 문제

관절이 bench에서는 `kd = 8`로 안정적인데 실제 controller에 올리면 떨기 시작합니다. gain은 하나도 바뀌지 않았습니다. 바뀐 것은 명령이 센서에서 drive까지 가는 데 몇 ms가 걸린다는 점입니다. 아무도 그 ms를 더해 보지 않았습니다.

## 개념

![지연 예산](../assets/diagram-latency-budget.png)

*단계마다 신호가 늦어지고 지연은 더해집니다. 유지된(hold) 명령은 반 주기만큼 더 늦습니다.*

관성 `J`에 PD loop를 건 경우, gain crossover `wc`는 `J^2 wc^4 = kd^2 wc^2 + kp^2`의 해입니다.

지연 `T`는 `wc*T`만큼의 위상 지연을 더하고 gain은 건드리지 않으므로 phase margin은 `PM - wc*T`로 줄어듭니다. delay margin은 `PM / wc`입니다.

![지연이 phase margin을 소모한다](../assets/diagram-delay-margin.png)

*지연은 margin을 0이 될 때까지 낮춥니다. 해결책은 crossover를 낮추는 것입니다.*

`kd`를 키우면 `wc`가 `PM`보다 빨리 올라가므로 어느 지점부터는 delay margin이 줄어듭니다. loop 지연이 정해지면 그래도 동작하는 가장 큰 `kd`가 있습니다.

![kd에 따른 delay margin과 시뮬레이션 응답](../assets/fig-latency-margin.png)

*왼쪽은 5.5 ms 예산이 약 14보다 큰 kd와 아주 작은 kd를 모두 막는 모습입니다. 오른쪽은 margin의 0.6배 지연에서는 가라앉고 1.5배에서는 커지는 모습입니다.*

## 만들기

```python
def crossover(kp, kd, J):
    return np.sqrt((kd**2 + np.sqrt(kd**4 + 4 * J**2 * kp**2)) / (2 * J**2))

def phase_margin(kp, kd, J, delay=0.0):
    wc = crossover(kp, kd, J)
    return np.arctan(kd * wc / kp) - wc * delay

def delay_margin(kp, kd, J):
    return phase_margin(kp, kd, J) / crossover(kp, kd, J)
```

`simulate()`는 지연이 있는 loop를 돌립니다. 테스트는 crossover를 수치로 구한 gain 1과 대조하고 `delay_margin()`의 0.6배에서 안정이고 1.5배에서 불안정함을 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/04-latency-budget -q
python3 phases/04-actuators-and-sensors/04-latency-budget/code/figure.py
```

## 실제 도구로 보기

delay margin은 Bode plot에서 읽은 phase margin을 crossover 주파수로 나눈 값입니다. 이 레슨에서 유도했습니다. 같은 loop를 `scipy.signal` 같은 주파수 응답 도구나 MATLAB 방식 Bode plot으로 그려서 결과를 비교해 보세요.

## 결과물

`outputs/skill-latency-budget-check.md`는 loop의 지연을 합산하고 안전한 가장 큰 `kd`를 돌려줍니다.

## 연습 문제

1. loop에 1차 필터를 넣고 margin을 수치로 다시 계산하세요.
2. `kd`를 고정하고 `kp`를 두 배로 할 때 delay margin을 구하세요.
3. 필터 지연을 2 ms에서 1 ms로 옮기고 새 최대 `kd`를 보고하세요.
