# ICP 스캔 정합 (Scan Matching with ICP)

> 로봇이 같은 방을 찍은 레이저 스캔 두 장을 겹쳐서 얼마나 움직였는지 알아내는 방법을 알아봅니다.

**유형:** 만들기   **선수 지식:** 08/01 차동 구동과 Odometry   **시간:** 약 15분

## 쉽게 말하면

로버가 L자 방을 스캔해서 벽을 따라 점을 얻어요. 조금 움직인 뒤 다시 스캔하면 새 점들이 옛 점들과 겹치지 않아요.
ICP는 새 점마다 가장 가까운 옛 점을 짝짓고 새 점 전체를 밀고 돌려 짝 사이를 가깝게 한 뒤 이것을 반복해요.

두 번째 스캔이 멀리서 시작하면 가장 가까운 점이 엉뚱한 벽에 속해요. 점 사이 거리는 줄어도 추정한 이동은 틀려요.

## 핵심 용어

- **ICP**: iterative closest point입니다. 가까운 점끼리 짝짓고 이동을 맞추는 일을 반복합니다.
- **Rigid move**: 모양을 늘이거나 구부리지 않는, 돌리기와 밀기입니다.
- **Nearest neighbour**: 다른 스캔에서 가장 가까운 점입니다.

- **Local minimum**: 작은 움직임으로는 오차가 더 줄지 않는 막다른 곳입니다. 답이 틀려도 그렇습니다.

## 문제

로봇이 방을 스캔하고 조금 움직인 뒤 다시 스캔한다고 상상해 보세요. 바퀴 기록은 어긋나므로 점 구름일 뿐인 두 스캔만으로 실제 이동을 알고 싶습니다.

## 개념

로봇은 이것으로 바퀴가 준 추측을 스캐너가 실제로 본 것으로 바로잡습니다.

ICP는 새 점마다 가장 가까운 옛 점을 짝짓고 새 스캔 전체를 밀고 돌려 짝 사이를 가깝게 합니다. 짝 사이가 더는 가까워지지 않을 때까지 이것을 반복합니다.

![ICP 반복](../assets/diagram-icp-loop.png)

*짝짓고 옮기고 반복합니다.*

가깝게 시작하면 가장 가까운 점이 진짜 짝이라서 스캔이 맞물립니다. 멀리서 시작하면 가장 가까운 점이 엉뚱한 벽에 속해서 스캔이 갇힙니다.

![가깝게 시작과 멀리 시작](../assets/clip-example.mp4)

*초록은 맞습니다. 파랑은 엉뚱한 벽과 짝이 되어 갇힙니다.*

![큰 offset이 실패하는 이유](../assets/diagram-icp-failure.png)

*큰 어긋남은 점을 엉뚱한 벽과 짝짓습니다.*

![ICP를 네 장으로 본 모습](../assets/fig-icp-basin.png)

*작은 시작 오차에서는 괜찮고 큰 시작 오차에서는 갇힙니다.*

<details><summary>The math (optional)</summary>

두 점 집합의 중심을 각자의 평균에 맞춥니다.
짝지은 점들이 어떻게 겹치는지를 SVD(표준 행렬 도구)로 분해하면 가장 좋은 회전 `R`이 나오고 거울상은 부호를 바로잡아 막습니다.
이동은 `t = q_mean - R p_mean`입니다.
점은 0.05 m 간격입니다.
0.2 rad 어긋나게 시작하면 가장 가까운 옛 점까지의 평균 거리가 0.39 m이고 12번 반복하면 0.016 m가 됩니다.
2.6 rad 어긋나게 시작하면 4.07 m이고 25번 반복해도 0.54 m에서 멈추며 스캔은 여전히 2.5 rad 틀어져 있습니다.
오차는 오르지 않습니다.
각 맞춤은 그 짝에서 최적이기 때문입니다.
이 방에서는 시작 회전이 약 65~70도까지 좋고 100도에서는 local minimum입니다.
직선 벽 하나는 벽을 따른 이동을 고정하지 못합니다.

</details>

## 만들기

```python
def kabsch(P, Q):
    pc, qc = P.mean(0), Q.mean(0)
    U, _, Vt = np.linalg.svd((P - pc).T @ (Q - qc))
    D = np.diag([1.0, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, qc - R @ pc

match = dst[nearest(cur, dst)]
dR, dt = kabsch(cur, match)
cur = cur @ dR.T + dt
```

`icp()`는 이것을 반복하고 전체 회전, 이동, 오차 기록을 돌려줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/05-icp-scan-matching -q
python3 phases/08-mobile-robots/05-icp-scan-matching/code/main.py
```

## 실제 도구로 보기

Open3D는 3D 라이브러리이고 대략적인 시작 추측도 받는 완성된 ICP가 있습니다. `icp()`와 비교해 보세요.

출처는 Open3D의 ICP registration tutorial입니다(https://www.open3d.org/docs/latest/tutorial/pipelines/icp_registration.html, 2026년 11월 10일 확인).

## 결과물

`outputs/skill-icp-check.md`는 스캔 정합 단계의 나쁜 시작, 평평한 벽, 근거 없는 확신을 점검합니다.

## 연습 문제

1. 두 스캔에 노이즈를 조금 넣고 답이 어떻게 바뀌는지 보세요.
2. 어떤 회전만큼 틀린 추측에서 ICP를 시작하세요. ICP가 실패할 때까지 그 회전을 키워 보세요.
3. 방의 모서리 하나를 빼고 어떻게 되는지 보세요.
