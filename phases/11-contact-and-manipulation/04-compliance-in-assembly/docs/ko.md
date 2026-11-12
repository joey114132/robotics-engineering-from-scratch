# 조립에서의 compliance (Compliance in Assembly)

> 도구가 너무 딱딱해 비켜 주지 못하면 펙이 jam됩니다. 그 도구가 만드는 옆힘이 펙을 붙드는 마찰을 키우기 때문입니다.

**유형:** 만들기   **선수 지식:** 11/01 접촉 모델, 11/02 힘 제어와 하이브리드 제어   **시간:** 약 15분

## 쉽게 말하면

기울어진 연필이 꼭 맞는 꽂이에 걸렸다고 해 보세요. 위쪽을 옆으로 어긋난 채 단단히 붙잡으면 연필이 벽을 세게 눌러요. 벽은 연필을 반대로 밀고 friction은 아래로 들어가는 움직임을 막아요.

compliance가 있으면 연필을 잡은 손이 옆으로 조금 움직여 벽을 누르는 힘을 줄여요. 그러면 연필이 곧게 서며 더 들어갈 수 있어요. 이 조립 모델은 접촉력이 손목의 밀기와 비틀기를 모두 상쇄할 수 있는지 봐요. 상쇄할 수
있으면 peg가 움직이지 않고 jam된 채 버틸 수 있어요.

## 문제

로봇이 빡빡하게 맞는 구멍에 펙을 끼웁니다. 1 mm도 안 되게 어긋나면 펙이 중간에서 멈추고 더 세게 밀수록 더 단단히 멈춥니다.

## 개념

![딱딱한 손목이 펙을 jam시키는 과정](../assets/diagram-jam-chain.png)

*딱딱한 손목은 작은 offset을 큰 옆힘으로 바꿉니다. 그 힘이 끝점을 벽에 눌러 마찰이 커지고 두 접촉이 펙을 붙들 수 있게 됩니다.*

![compliant 손목은 비켜 줍니다](../assets/diagram-comply.png)

*같은 offset에서 부드러운 손목은 작은 옆힘만 만들므로 펙이 미끄러져 내려가고 기울기가 줄어듭니다.*

펙은 기울어져 끝점이 한쪽 벽에, 구멍 모서리가 반대쪽에 닿으므로 자세가 끝점 깊이 하나로 정해집니다. 깊이마다 손목이 wrench를 가합니다. 두 마찰 cone 안에서 힘을 골라 그 wrench를 상쇄할 수 있으면 펙이 jam됩니다.

![손목 강성과 offset에 대한 jam 지도](../assets/fig-jam-map.png)

*주황색이 jam입니다. 딱딱한 손목은 약 0.7 mm 어긋남부터 jam되고 약 2.5e3 N/m보다 부드러운 손목은 그림의 모든 offset에서 삽입됩니다.*

![삽입 동안의 접촉력](../assets/fig-contact-forces.png)

*부드러운 손목은 끝점 힘을 미는 힘 근처에 둡니다. 딱딱한 손목은 벽에 수십 N을 주며 시작하고 옆힘의 부호가 바뀌는 곳에서 jam됩니다.*

## 만들기

깊이마다 손목 wrench(`wr`)와 cone 모서리 wrench 네 개가 나옵니다. `-wr`이 그중 세 개의 음이 아닌 조합이면 jam입니다.

```python
A = edges[list(idx)].T
if abs(np.linalg.det(A)) > 1e-12 and (np.linalg.solve(A, -wr) >= -1e-9).all():
    return True
```

가정은 폭이 0인 펙, chamfer 없는 날카로운 구멍, 준정적 운동, 끝점과 입구 모서리 두 곳의 접촉입니다.

손목은 횡 spring(`kx`)과 비틀림 spring과 일정한 미는 힘이고 마찰은 쿨롱 `mu`입니다. 모델은 이미 wedge가 된 상태에서 시작하므로 모서리에 얹히는 과정은 다루지 않습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/04-compliance-in-assembly -q
python3 phases/11-contact-and-manipulation/04-compliance-in-assembly/code/main.py
```

## 실제 도구로 보기

실제 셀은 remote center compliance 장치나 소프트웨어 compliance를 씁니다. 같은 원리가 Wikipedia 문서에 설명되어 있습니다. 쓰는 방법은 손목의 횡 강성을 여러분의 clearance와 `mu`에 대한 jam 지도와 비교합니다.

출처: Wikipedia "Remote center compliance"(2026년 11월 9일 열람). 어긋난 펙은 끝점에 옆힘을 받아 회전하다가 삽입이 멈춥니다. compliant 장치는 이를 악화시키지 않고 바로잡습니다.

## 결과물

`outputs/skill-assembly-compliance-check.md`는 미는 힘을 조정하기 전에 삽입의 jam 위험을 점검합니다.

## 연습 문제

1. `e = 1 mm`에서 여전히 삽입되는 가장 큰 `kx`를 찾으세요.
2. `mu`를 0.1에서 0.6까지 올리며 jam 경계가 어떻게 움직이는지 그리세요.
3. wedge를 더 얕은 깊이에서 시작해 chamfer를 흉내 내세요.
