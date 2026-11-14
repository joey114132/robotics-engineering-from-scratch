# Model Predictive Control

> 한계를 식에 넣고 짧은 미래를 계획하고 첫 명령만 쓰고 다시 계획합니다.

**유형:** 만들기   **선수 지식:** 03/06 LQR   **시간:** 약 15분

## 쉽게 말하면

장난감 자동차를 정지선에 세운다고 해 보세요. 브레이크가 약해요. 선에 와서야 브레이크를 잡으면 선을 지나쳐요. 속도를 보고 멈추는 데 얼마나 걸릴지 가늠해서 일찍 잡아야 해요.

model predictive control은 그 브레이크 한계를 넣고 앞으로 몇 번 밀지를 계획해요. 첫 번째 힘만 쓰고 자동차를 다시 측정한 뒤 다시 계획해요. 한계를 무시하고 큰 힘을 요구한 뒤 잘라 내는 것보다 한계를 넣고 계획하면 덜 지나쳐요.

## 문제

컨트롤러가 모터가 낼 수 있는 토크보다 큰 값을 요구하고 그 명령은 그냥 잘려 나갑니다. 컨트롤러는 한계를 몰랐으므로 너무 늦게 제동해서 overshoot가 납니다. 그러면 오차가 반대로 밀어서 팔이 목표를 다시 가로질러 흔들립니다.

## 개념

![receding horizon 루프](../assets/diagram-mpc-loop.png)

*번호를 따라가 보세요. 매 tick마다 측정한 상태에서 계획을 새로 만듭니다. 계획의 첫 단계만 plant, 즉 제어 대상에 전달됩니다.*

다음 `N`개 상태(horizon)를 `X = Phi x0 + Gam U`로 쌓습니다. `x0`는 측정한 상태이고 `U`는 앞으로 `N`번의 힘을 담으며 `Phi`와 `Gam`은 레슨 06의 모델에서 나옵니다.

비용 `sum x'Qx + u'Ru`에 종단 비용(계획이 끝나는 자리에 매기는 값)을 더하면 `U`에 대한 이차식, 즉 최솟값을 찾기 쉬운 그릇 모양이 됩니다. 한계 `|u| <= umax`는 `U`에 대한 상자입니다.

모든 힘이 한계 안에 있어야 한다는 뜻입니다.

이것을 풀려면 비용을 따라 내려가는 작은 이동(gradient step)을 하고 매번 상자 안으로 되돌리며 Nesterov momentum으로 빨리 수렴시킵니다. 종단 비용으로 LQR의 `P`를 쓰면 짧은 계획도 계획이 끝난 뒤의 비용까지 봅니다.

![자르기와 한계를 알고 계획하기](../assets/diagram-mpc-clip.png)

*차이는 한계가 컨트롤러 뒤에 있느냐 안에 있느냐입니다.*

![MPC와 잘린 LQR gain](../assets/fig-mpc-vs-clip.png)

*이중 적분기가 4 m 떨어진 곳에서 `umax = 0.5`로 출발합니다. 잘린 gain은 1.28 m 넘치고 `N = 20`(`dt = 0.1`이므로 2초 앞)인 MPC는 0.31 m 넘칩니다. 오른쪽은 4 s의 계획이 2 s를 내다보고 첫 단계만 쓰는 모습입니다.*

예: 출발점과 `umax = 0.5`는 같고 계획 길이만 바꿉니다. `N = 2`(0.2초 앞)이면 자동차가 1.27 m 넘치고 `N = 10`이면 0.78 m, `N = 20`이면 0.31 m 넘칩니다.

![세 가지 계획 길이](../assets/clip-example.mp4)

*계획이 2, 10, 20 step인 차들입니다(초록 차는 2초 앞을 봅니다). 각 차가 선을 지나 얼마나 미끄러지는지 보세요. 2배속으로 재생합니다.*

## 만들기

```python
U_new = np.clip(Y - step * (H @ Y + f), -umax, umax)   # projected gradient
Y = U_new + (t - 1) / t_new * (U_new - U)               # momentum
```

`prediction()`이 `Phi`와 `Gam`을 만들고 `plan()`이 상자 제약 문제를 풉니다. `simulate()`는 매 tick 다시 계획합니다. 테스트는 예측이 rollout을 재현하는지, 적용된 입력이 모두 한계를 지키는지, 한계가 넉넉하면 MPC가 LQR과 같은지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/08-model-predictive-control -q
python3 phases/03-dynamics-and-control/08-model-predictive-control/code/figure.py
```

## 실제 도구로 보기

실제 MPC는 OSQP 같은 전용 QP solver를 쓰고 직전 계획으로 warm start 합니다. 한 tick을 그것으로 풀어 첫 입력을 `plan()`과 비교하세요. horizon은 비용과 계산량 사이의 손잡이입니다.

출처: [OSQP documentation](https://osqp.org/docs/), 2026년 11월 10일에 확인했습니다.

## 결과물

`outputs/skill-mpc-setup-check.md`는 horizon, 가중치, 종단 비용, 풀이 시간을 검토합니다.

## 연습 문제

1. 속도 한계를 두 번째 제약으로 더하고 상자가 무엇이 되는지 설명하세요.
2. 비용이 `N = 30`의 1% 안에 드는 가장 작은 `N`을 찾으세요.
3. solver를 20번만 반복하게 하고 비용이 얼마나 오르는지 재세요.
