# 파지 품질 (Grasp Quality)

> 로봇 손의 쥐기가 버틸지, 여유가 얼마나 되는지 알아내는 방법을 알아봅니다.

**유형:** 만들기   **선수 지식:** 11/01 접촉 모델   **시간:** 약 15분

## 쉽게 말하면

grasp quality는 접촉이 밀림과 비틀림을 모두 버틸 수 있는지 봐요. 작은 상자의 양옆을 손끝으로 집고 한쪽 손가락을 위로 옮겨 보세요. 같은 힘으로 눌러도 안쪽으로 미는 힘이 상자를 비틀어요.

friction 덕분에 손끝은 표면을 따라서도 힘을 낼 수 있지만 상한이 있어요. 가능한 힘과 비틀림으로 모든 방향의 외란에 맞설 수 없으면 force closure가 없어요.

## 핵심 용어

- **Wrench**: 밀기와 비틀기를 함께 묶은 것입니다. 2차원에서는 세 숫자 `(fx, fy, torque)`입니다.
- **Friction cone**: 손끝이 미끄러지지 않고 낼 수 있는 모든 힘입니다.
- **Convex hull**: 점들의 집합을 팽팽하게 감싼 껍질입니다.
- **Force closure**: 접촉들이 어느 방향의 하중도 버틸 수 있는 상태입니다.
- **Epsilon**: 파지의 여유입니다. hull의 안쪽에서 표면까지의 가장 짧은 거리입니다.
- **Rank**: wrench들이 펼치는 서로 독립인 방향의 수입니다.

## 문제

손가락 두 개로 상자를 집었다고 상상해 보세요. 한 손가락을 위로 밀면 쥐는 힘은 같은데도 상자가 돌아 빠집니다. 접촉이 모두 쥐고 있어도 함께는 어떤 방향의 하중을 견디지 못합니다.

## 개념

실제 로봇 손은 쥐기가 괜찮아 보여도 여유가 없으면 물건을 떨어뜨리므로 그 여유를 나타내는 숫자가 필요합니다.

손끝은 마찰 cone 안의 어떤 힘으로도 밀 수 있으므로 cone의 두 모서리 wrench가 그 양 끝입니다.
이런 밀기들을 적당히 섞어(당기는 힘은 없습니다) 어떤 하중도 상쇄할 수 있으면 파지가 버팁니다.
그것은 원점(알짜 밀기와 비틀기가 없는 상태)이 모든 모서리 wrench를 감싼 hull의 안쪽에 있다는 뜻입니다.

![closure 과정](../assets/diagram-closure-pipeline.png)

*접촉마다 모서리 wrench 두 개가 더해지고 그 hull이 원점을 안쪽에 품으면 파지가 닫힙니다.*

폭이 2인 상자와 `mu = 0.3`을 생각해 봅니다.
오른쪽 jaw가 왼쪽보다 `offset`만큼 높습니다.
두 접촉을 잇는 선이 두 cone 안에 있는 동안에만 접촉이 서로 균형을 잡으므로 `offset / 2 <= mu`, 즉 `offset <= 0.6`이어야 합니다.
offset 0.4는 epsilon 0.07(`epsilon()` 결과)로 닫히고 0.8은 0이 됩니다.

![올라가는 jaw](../assets/clip-example.mp4)

*offset 0.6까지는 상자가 버티다가 그 뒤로 돕니다.*

![필요한 마찰](../assets/diagram-friction-needed.png)

*마찰이 없으면 마주 보는 접촉 두 개는 한 직선 위의 wrench 두 개뿐이어서 비틀림을 견디지 못합니다.*

![파지 모음](../assets/fig-grasp-gallery.png)

*파란색은 닫히고 주황색은 닫히지 않습니다.*

![offset과 품질](../assets/fig-epsilon-vs-offset.png)

*epsilon은 직선으로 줄어 offset = 2 mu에서 0이 됩니다.*

## 만들기

hull의 면은 wrench 세 개를 지나고 나머지가 모두 한쪽에 있는 평면입니다. epsilon은 원점에서 면까지의 최소 거리이며 원점이 밖에 있거나 rank가 3보다 작으면 0입니다.

```python
n = np.cross(W[j] - W[i], W[k] - W[i]); n /= np.linalg.norm(n)
side = W @ n - n @ W[i]
if np.all(side <= tol): h.append(n @ W[i])
```

가정은 강체, 점 접촉, 하나의 쿨롱 `mu`, 토크를 길이 `rho`로 나누는 것입니다. closure 여부는 `rho`에 무관하지만 epsilon은 `rho`에 따라 달라집니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/03-grasp-quality -q
python3 phases/11-contact-and-manipulation/03-grasp-quality/code/main.py
```

## 실제 도구로 보기

SciPy로 같은 wrench에 대한 closure 선형계획을 풉니다. 테스트가 무작위 손가락 세 개 파지에서 둘을 비교합니다.

출처: Lynch와 Park, *Modern Robotics*, 2017년 5월 preprint, 12.2.3절(2026년 11월 9일 열람).

## 결과물

`outputs/skill-grasp-closure-check.md`는 파지가 닫히는지와 여유가 작은지를 점검합니다.

## 연습 문제

1. 열린 파지에 세 번째 접촉을 더하고 닫히는 가장 작은 `mu`를 찾으세요.
2. epsilon은 `rho`에 따라 변하지만 closure는 변하지 않는다는 것을 보이세요.
3. 원 위의 세 접촉을 돌려 가며 epsilon이 가장 큰 배치를 찾으세요.
