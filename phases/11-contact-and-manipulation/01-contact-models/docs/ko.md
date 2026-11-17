# 접촉 모델 (Contact Models)

> 손목을 기울이면 잡은 부품이 왜 미끄러져 빠지는지, 미끄러지기 시작하는 각도를 예측하는 방법을 알아봅니다.

**유형:** 만들기   **선수 지식:** 없음   **시간:** 약 15분

## 쉽게 말하면

교과서 위에 지우개를 놓고 책을 천천히 기울여 보세요. 중력은 지우개를 경사 아래로 당겨요. 면 사이의 달라붙는 힘인 마찰력은 지우개를 위쪽으로 잡아 줘요.

마찰력에는 상한이 있어요. 지우개를 책에 누르는 힘에 `mu`를 곱한 값까지만 낼 수 있어요. 이 상한 안에 드는 마찰력의 모음이 friction cone이에요. 필요한 마찰력이 상한을 넘으면 지우개는 미끄러져요.

## 핵심 용어

- **Contact model**: 두 물체가 닿는 곳의 힘을 simulator가 계산하는 규칙입니다.
- **Normal force**: 면이 면에 수직으로 밀어내는 힘입니다.
- **Friction coefficient (`mu`)**: 표면이 얼마나 잘 붙는지를 나타내는 값입니다.
- **Friction cone**: 붙드는 한도, 즉 friction coefficient에 normal force를 곱한 값까지의 마찰력의 모음입니다.
- **Stick and slip**: 접촉의 두 상태입니다. 붙어서 멈춰 있거나 미끄러집니다.
- **Penetration**: simulator 안에서 물체가 면 속으로 파고든 깊이입니다.

## 문제

로봇 손이 부품을 잡고 있다고 상상해 보세요. 손목을 몇 도 기울이자 부품이 미끄러져 빠지지만 조금 더 평평하게 들었다면 붙어 있었을 것입니다.

## 개념

실제 gripper는 마찰이 모자라면 부품을 떨어뜨리므로 그 각도를 알아야 합니다.

책 위에 지우개를 놓고 기울여 보세요. 경사가 너무 가팔라지기 전까지는 마찰이 지우개를 잡고 그 뒤에는 미끄러집니다. 마찰은 한도까지만 되밀 수 있고 그 한도는 두 면이 얼마나 세게 눌리는지와 얼마나 잘 붙는지에 달려 있습니다.

![층](../assets/diagram-penalty-layers.png)

*simulator 안의 블록은 면 속으로 아주 조금 파고듭니다. 깊이 파고들수록 마찰이 더 세게 붙들 수 있습니다.*

![기울어지는 판자](../assets/clip-example.mp4)

*블록은 판자가 표시를 지나는 순간부터 미끄러집니다.*

![stick인가 slip인가](../assets/diagram-stick-slip.png)

*필요한 마찰력이 cone 안에 들어가는가?*

![cone](../assets/fig-stick-slip.png)

*붙어 있는 블록은 cone 안에 머물고 미끄러지는 블록은 cone의 모서리를 탑니다.*



<details><summary>The math (optional)</summary>

기울기를 `theta`, 질량을 `m`, 중력가속도를 `g`라고 하면 중력은 블록을 면 안쪽으로 `fn = m g cos(theta)`로 누르고 경사 아래로 `m g sin(theta)`로 당깁니다.
붙어 있으려면 마찰 `ft = m g sin(theta)`가 필요하므로 `ft / fn = tan(theta)`이고 friction cone은 `mu`까지 허용합니다.
`mu = 0.5`이면 블록은 약 26.6도를 넘으면 미끄러집니다.
25도 경사는 필요한 값이 0.47이라 붙어 있고 35도 경사는 0.70이라 미끄러지며 가속도는 `g (sin(theta) - mu cos(theta))`로 약 1.6 m/s²입니다.
질량은 약분되므로 두 배로 해도 달라지지 않습니다.

</details>

## 만들기

스프링과 완충기가 침투에 맞서 밀어냅니다. 마찰은 옆 방향 스프링이고 `mu`에 normal force를 곱한 값에서 잘립니다.

```python
fn = max(K * pen - C * nv, 0.0)
ft = -KT * (s - anchor) - CT * v
if abs(ft) > mu * fn:
    ft = np.sign(ft) * mu * fn
    anchor = s + ft / KT
```

가정은 점 블록, 접촉 하나, 평면 경사, 고정된 spring 상수, 작은 시간 스텝(0.1 ms)입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/01-contact-models -q
python3 phases/11-contact-and-manipulation/01-contact-models/code/main.py
```

## 실제 도구로 보기

MuJoCo는 물리 simulator이고 마찬가지로 침투에 맞서 밀어내며 `mu`로 마찰을 제한합니다. 같은 블록을 거기에 만들고 미끄러지기 시작하는 각도를 비교하세요.

출처: MuJoCo 문서 Computation 장(2026년 11월 9일 열람).

## 결과물

`outputs/skill-contact-model-check.md`는 로봇의 제어 코드를 탓하기 전에 접촉 설정에서 stick/slip 문제가 없는지 점검합니다.

## 연습 문제

1. 판자를 조금씩 기울여서 블록이 미끄러지기 시작하는 각도를 찾으세요.
2. 표면이 더 잘 붙거나 덜 붙게 만들고 각도가 움직이는 것을 보세요.
3. 블록을 경사를 따라 옆으로 밀어 보고 위로 미끄러지게 하는 힘을 찾으세요.
