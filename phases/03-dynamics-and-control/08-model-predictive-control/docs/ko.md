# Model Predictive Control

> 컨트롤러가 모터의 한계를 지키면서 앞을 내다보고 계획하는 법을 알게 됩니다.

**유형:** 만들기   **선수 지식:** 03/06 LQR   **시간:** 약 15분

## 쉽게 말하면

장난감 자동차를 정지선에 세운다고 해 보세요. 브레이크가 약해요. 선에 와서야 브레이크를 잡으면 선을 지나치니까 일찍 잡아야 해요.

model predictive control은 그 브레이크 한계를 넣고 앞으로 몇 번 밀지를 계획해요. 첫 번째 힘만 쓰고 자동차를 다시 측정한 뒤 다시 계획해요.

## 핵심 용어

- **Model predictive control (MPC)**: 한계를 지키며 짧은 미래를 계획하고 첫 명령만 쓴 뒤 다시 계획하는 방법입니다.
- **Horizon (`N`)**: 계획 하나가 몇 step 앞을 내다보는지입니다.
- **Terminal cost**: 계획이 끝나는 자리에 매기는 값이라서 짧은 계획도 그 뒤의 일을 봅니다.
- **Quadratic**: 그릇 모양의 비용으로 최솟값을 찾기 쉽습니다.
- **Box constraint**: 모든 명령이 `-umax`와 `umax` 사이에 있어야 한다는 제약입니다.
- **Plant**: 제어 대상입니다.

## 문제

로봇의 모터는 낼 수 있는 힘에 한계가 있습니다. 컨트롤러가 그보다 큰 값을 요구하면 명령은 그냥 잘려 나가고 컨트롤러는 한계를 몰랐으므로 너무 늦게 제동해서 overshoot가 납니다.

## 개념

실제 모터에는 한계가 있고 그것을 알고 계획하는 쪽이 불가능한 값을 요구했다가 잘라 내는 것보다 낫습니다.

![receding horizon 루프](../assets/diagram-mpc-loop.png)

*매 tick마다 측정한 상태에서 계획을 새로 만듭니다. 계획의 첫 단계만 plant에 전달됩니다.*

다음 `N`개 상태를 `X = Phi x0 + Gam U`로 쌓습니다. `x0`는 측정한 상태이고 `U`는 앞으로 `N`번의 힘이며 `Phi`와 `Gam`은 레슨 06의 모델에서 나옵니다.

비용 `sum x'Qx + u'Ru`에 terminal cost를 더하면 `U`에 대한 quadratic이 되고 한계 `|u| <= umax`는 `U`에 대한 상자가 됩니다.

비용을 따라 내려가는 작은 이동(gradient step)을 하고 매번 상자 안으로 되돌리며 Nesterov momentum으로 빨리 수렴시킵니다. 종단 비용으로 LQR의 `P`를 쓰면 짧은 계획도 계획이 끝난 뒤를 봅니다.

![자르기와 한계를 알고 계획하기](../assets/diagram-mpc-clip.png)

*한계가 컨트롤러 뒤에 있느냐 안에 있느냐가 차이입니다.*

![MPC와 잘린 LQR gain](../assets/fig-mpc-vs-clip.png)

*4 m 떨어진 곳에서 `umax = 0.5`로 출발합니다. 잘린 gain은 1.28 m 넘치고 `N = 20`(`dt = 0.1`이므로 2초 앞)인 MPC는 0.31 m 넘칩니다. 오른쪽은 4초의 계획입니다.*

출발점은 같고 계획 길이만 바꿉니다. `N = 2`(0.2초 앞)이면 1.27 m 넘치고 `N = 10`이면 0.78 m, `N = 20`이면 0.31 m 넘칩니다.

![세 가지 계획 길이](../assets/clip-example.mp4)

*계획이 2, 10, 20 step인 차들입니다. 각 차 옆의 호박색 막대는 그 차가 선을 지나 미끄러진 거리입니다.*

## 만들기

```python
U_new = np.clip(Y - step * (H @ Y + f), -umax, umax)   # projected gradient
Y = U_new + (t - 1) / t_new * (U_new - U)               # momentum
```

`prediction()`이 `Phi`와 `Gam`을 만들고 `plan()`이 상자 제약 문제를 풀며 `simulate()`는 매 tick 다시 계획합니다. 테스트는 예측이 rollout을 재현하는지, 입력이 한계를 지키는지, 한계가 넉넉하면 MPC가 LQR과 같은지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/08-model-predictive-control -q
python3 phases/03-dynamics-and-control/08-model-predictive-control/code/figure.py
```

## 실제 도구로 보기

실제 MPC는 OSQP 같은 QP solver를 쓰고 직전 계획으로 warm start 합니다. 한 tick을 그것으로 풀어 첫 입력을 `plan()`과 비교하세요.

출처: [OSQP documentation](https://osqp.org/docs/), 2026년 11월 10일에 확인했습니다.

## 결과물

`outputs/skill-mpc-setup-check.md`는 horizon, 가중치, terminal cost, 풀이 시간을 검토합니다.

## 연습 문제

1. 속도 한계를 더하고 상자가 무엇이 되는지 설명하세요.
2. 비용이 `N = 30`의 1% 안에 드는 가장 작은 `N`을 찾으세요.
3. solver를 20번만 반복하게 하고 비용이 얼마나 오르는지 재세요.
