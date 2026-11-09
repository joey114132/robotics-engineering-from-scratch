# 임피던스 제어 (Impedance Control)

> 임피던스 제어는 위치를 추종하지 않습니다. 관절이 어떻게 밀어낼지를 정합니다.

**유형:** 만들기   **선수 지식:** 03/01 샘플링 한계, 03/02 중력 보상   **시간:** 약 15분

## 문제

뻣뻣한 position loop는 손이 닿을 때마다 최대 힘으로 맞섭니다. 컵을 건네주는 로봇에게는 반대가 필요합니다. 강성과 감쇠를 직접 고르면 밀었을 때 싸움이 아니라 예측 가능하고 한계가 있는 처짐이 생깁니다.

## 개념

![스프링, damper, 중력 feedforward가 한 관절에 작용합니다](../assets/diagram-impedance-structure.png)

*컨트롤러가 가상 스프링과 가상 damper, 중력 feedforward를 더합니다. 외부에서는 `F`로 밉니다.*

제어 법칙은 `tau = K (q_des - q) - D qd + tau_g`입니다. 일정한 힘 `F`로 밀면 관절은 `F / K`에서 멈춥니다. 감쇠비 `zeta = D / (2 sqrt(K J))`는 접근 모양을 정합니다.

`zeta = 1`이면 overshoot가 없고 `zeta < 1`이면 overshoot 비율은 `exp(-pi zeta / sqrt(1 - zeta^2))`입니다. `zeta = 0.2`에서는 약 0.53입니다.

![세 감쇠비의 step 응답과 K에 따른 처짐](../assets/fig-impedance-response.png)

*왼쪽은 같은 `K`와 세 가지 `zeta`가 모두 `F / K`에 멈추지만 overshoot는 감쇠만 바꾼다는 것을 보여 줍니다. 오른쪽은 `K`를 두 배로 하면 처짐이 절반이 되는 모습입니다.*

![K와 D를 고르는 네 단계](../assets/diagram-impedance-recipe.png)

*처짐 예산에서 `K`를, 감쇠비에서 `D`를 고른 뒤 레슨 03/01의 샘플링 한계를 확인합니다.*

## 만들기

```python
def impedance_torque(q, qd, q_des, K, D, tau_g):
    return K*(q_des - q) - D*qd + tau_g

def damping_for_zeta(K, J, zeta):
    return 2*zeta*np.sqrt(K*J)
```

`simulate()`는 semi-implicit Euler로 1자유도 관절을 일정한 외부 토크로 밉니다.

테스트는 처짐이 `F / K`와 1% 안에서 맞는지, `K`를 두 배로 하면 절반이 되는지, `zeta = 1`에서 overshoot가 없는지, `zeta = 0.2`가 공식과 3%p 안에서 맞는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/03-impedance-control -q
python3 phases/03-dynamics-and-control/03-impedance-control/code/figure.py
```

## 실제 도구로 보기

토크 제어 팔은 관절별 `K`와 `D`로 임피던스를 설정하게 해 주고 그 위에 Jacobian transpose로 Cartesian 임피던스를 얹기도 합니다. `K`는 예상되는 가장 큰 힘과 허용하는 가장 큰 처짐으로 고릅니다. `K = F_max / x_max`입니다.

## 결과물

`outputs/skill-impedance-check.md`는 `K`, `D` 선택을 처짐 예산과 샘플링 한계에 대해 점검합니다.

## 연습 문제

1. 마찰을 넣고 작은 힘에서 새 정상상태를 찾으세요.
2. 일정한 힘을 방향이 뒤집히는 step으로 바꾸세요. `zeta`가 0.7일 때와 1일 때의 settling time을 비교하세요.
3. 샘플링 한계 점검으로 `J = 0.05`일 때 1 kHz loop가 허용하는 가장 큰 `D`를 찾으세요.
