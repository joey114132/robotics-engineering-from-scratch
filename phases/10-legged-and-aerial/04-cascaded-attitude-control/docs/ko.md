# 캐스케이드 자세 제어

> 각도 루프가 회전 속도 루프를 감싼 구조는 PD와 같습니다. 안쪽 루프에 적분을 주면 돌풍이 각도 오차를 남기지 않습니다.

**유형:** 만들기   **선수 지식:** 10/03 쿼드로터 모델   **시간:** 약 15분

## 쉽게 말하면

일정한 돌풍이 드론의 앞머리를 밀면 드론은 맞서야 해요. 단순한 제어기는 기울어진 만큼 비례해서 되밀기 때문에 돌풍만큼 세게 밀려면 드론이 기울어진 채로 있어야 해요.

cascaded attitude(자세, 기울기) control은 제어기에 기억을 더해요. 드론이 수평으로 멈추기 전까지는 되미는 힘이 조금씩 더 쌓여요. 그 힘이 돌풍과 같아지면 드론은 다시 수평이 되고 여전히 버텨요.

## 문제

돌풍이 드론을 1초 동안 밀고 PD pitch 루프(기울기에는 `kp`, 회전 속도에는 `kd`의 세기로 되미는 루프)는 그 내내 일정한 기울기를 유지하고 그 기울기 때문에 드론이 흘러갑니다. `kp`를 올리면 기울기는 줄지만 작은 오차마다 더 큰 토크를 요구합니다.

## 개념

![한 루프: 각도에 대한 PD](../assets/diagram-single-pd.png)

*단일 루프는 각도 오차를 토크로 바꿉니다. 일정한 돌풍 토크 `d`는 `kp * error = d`가 필요하므로 오차가 `d / kp`로 남습니다.*

바깥 루프는 각도 오차 `e`를 회전 속도 명령 `omega_ref = k_theta * e`로 바꿉니다(`omega`는 회전 속도이고 `k_theta`는 각도 gain입니다). 안쪽 루프는 회전 속도 오차를 토크로 바꿉니다. 안쪽이 P이고 rate gain이 `k_w`이면 `tau = k_w (k_theta e - omega)`이고 이것은 `kp = k_w k_theta`, `kd = k_w`인 PD와 똑같습니다.

![두 루프: 바깥은 각도, 안쪽은 회전 속도](../assets/diagram-cascade.png)

*바깥 gain은 그대로이고 회전 속도 오차에 적분(기억, 오차의 누적합, gain `k_i`)이 붙습니다. 적분은 회전 속도 오차가 0일 때만 자라기를 멈추므로 돌풍과 같아진 채 멈추고 각도 오차는 필요 없습니다.*

안정성은 `I s^3 + k_w s^2 + (k_w k_theta + k_i) s + k_i k_theta = 0`의 근에 달려 있습니다. 안정하다는 것은 외란이 사라진다는 뜻이고 모든 근의 실수부가 음수여야 합니다. 예제 gain은 이를 만족합니다.

예(`I = 0.004`, `kp = 0.9`, `kd = 0.084`, `k_i = 0.5`): 0.1 Nm 돌풍은 PD 루프를 `0.1 / 0.9 = 0.11 rad`(6.4도)에 붙잡아 둡니다. 캐스케이드는 약 4도까지 기울었다가 돌풍이 0.5초 지났을 때는 같은 0.1 Nm로 되밀면서 0.5도입니다.

![같은 되미는 힘, 다른 기울기](../assets/clip-example.mp4)

*주황 화살표(되미는 힘)와 빨간 화살표(돌풍)를 보세요. 두 드론 모두 0.1 Nm로 되밀지만 파란 PD 드론은 기운 채로 있어야 그 힘을 내고 초록 캐스케이드 드론은 수평으로 돌아옵니다. 기울기는 3배 크게 그렸습니다.*

![두 루프에 가한 1초 돌풍](../assets/fig-gust-response.png)

*PD 루프는 돌풍 내내 6.4도에 머뭅니다. 캐스케이드는 약 4도에서 정점을 찍고 돌풍이 끝나기 전에 0 가까이 돌아옵니다. 돌풍이 멈추면 쌓인 적분 때문에 반대쪽으로 약 4도 흔들립니다.*

## 만들기

```python
def cascade(k_theta, k_w, k_i):
    z = [0.0]
    def ctrl(ref, th, w, dt):
        e_w = k_theta * (ref - th) - w
        z[0] += e_w * dt
        return k_w * e_w + k_i * z[0]
    return ctrl
```

`k_i = 0`이면 P-P 캐스케이드이고 `pd(kp, kd)`와 같습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/04-cascaded-attitude-control -q
python3 phases/10-legged-and-aerial/04-cascaded-attitude-control/code/main.py
```

## 실제 도구로 보기

마지막 테스트가 `cascade_poles()`를 SciPy의 `TransferFunction`과 비교합니다. 실제 제어기는 gyro(회전 속도 센서)를 필터링하고 windup이 생기지 않게 적분을 제한합니다.

## 결과물

`outputs/skill-cascade-loop-check.md`는 자세 캐스케이드에서 회전 속도 루프의 적분, windup 제한, 루프 대역폭 순서를 검토합니다.

## 연습 문제

1. `k_i`를 2로 올리고 돌풍 뒤의 반대쪽 흔들림을 `k_i = 0.5`와 비교하세요.
2. 토크를 0.15 Nm로 제한하고 적분이 어떻게 되는지 보세요.
3. `k_w = 0.02`, `k_i = 2`의 같은 gain 분할이 불안정함을 보이세요.
