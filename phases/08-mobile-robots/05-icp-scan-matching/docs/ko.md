# ICP 스캔 정합 (Scan Matching with ICP)

> 두 스캔을 맞추려면 각 점의 짝이 가장 가까운 점이라고 추측하고 강체 이동 하나를 맞춘 뒤 오차가 줄지 않을 때까지 반복합니다.

**유형:** 만들기   **선수 지식:** 01/01 회전과 SE(3), 08/01 차동 구동과 오도메트리   **시간:** 약 15분

## 쉽게 말하면

점으로 그린 윤곽을 트레이싱지에 옮겨 원본 위에 놓아 보세요. 위쪽 점마다 가장 가까운 아래쪽 점을 짝지어요. 짝 사이가 가까워지도록 종이 전체를 밀고 돌린 뒤 다시 짝을 찾아요.

ICP는 어느 점끼리 진짜 짝인지 모르는 스캔을 이렇게 맞춰요. 처음부터 비슷하게 놓으면 짝을 찾기 쉬워요. 너무 어긋나면 엉뚱한 부분끼리 맞아서 점 사이 거리가 줄어도 추정한 이동은 틀릴 수 있어요.

## 문제

바퀴 오도메트리(08/01)는 표류합니다. 레이저 스캐너는 약간 다른 두 자세에서 같은 방을 두 번 봅니다. 두 스캔 사이의 이동을 알면 자세를 고칠 수 있습니다. 프로그램은 라벨 없는 점에서 쓸 수 있는 규칙이 필요합니다.

## 개념

![ICP는 짝을 추측하고 맞추고 반복합니다](../assets/diagram-icp-loop.png)

*매 회전마다 점을 짝짓고 그 짝에 강체 이동 하나를 맞춰 적용합니다.*

짝이 맞다면 가장 좋은 회전 `R`과 이동 `t`가 한 번에 나옵니다. 짝지은 점들은 중심을 뺀 두 구름의 cross-covariance를 SVD하면 `R`이 나옵니다. 마지막 특이 방향에 부호를 곱해 거울상을 막습니다. 이동은 `t = q_mean - R p_mean`입니다. ICP는 짝을 모르므로 최근접점을 추측으로 씁니다.

![시작 오차가 크면 틀린 답으로 끝나는 이유](../assets/diagram-icp-failure.png)

*두 스캔이 점 간격보다 멀리 떨어져 시작하면 최근접점이 틀린 짝이 되고 맞춤이 틀린 답에 고정됩니다.*

오차는 오르지 않습니다. 각 맞춤은 그 짝에서 최적이고 다시 짝지으면 거리가 줄기만 하기 때문입니다.

![ICP를 네 장으로 본 모습](../assets/fig-icp-basin.png)

*세 패널은 한 번의 수렴을 보여 줍니다. 마지막 패널은 시작 회전에 따른 최종 자세 오차입니다. 이 방에서는 약 65~70도까지 좋고 그 뒤에는 local minimum입니다. 점선은 점 간격 0.05 m입니다.*

이 데모의 residual 하한은 점 간격 정도입니다. 보편적인 하한은 아닙니다. 서로 다른 샘플도 정확히 맞을 수 있고 작은 residual에도 자세는 틀릴 수 있습니다. 직선 벽 하나는 벽을 따른 이동을 충분히 구속하지 못합니다.

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

`icp()`는 이것을 반복하고 전체 `R`, `t`와 오차 기록을 돌려줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/05-icp-scan-matching -q
python3 phases/08-mobile-robots/05-icp-scan-matching/code/main.py
```

## 실제 도구로 보기

Open3D의 ICP registration은 두 구름을 대략 맞추는 초기 변환을 받고 대응 찾기와 변환 갱신을 번갈아 합니다. `icp()`와 비교하고 오도메트리를 초기 추정으로 넣어 보세요.

출처는 Open3D의 ICP registration tutorial입니다(https://www.open3d.org/docs/latest/tutorial/pipelines/icp_registration.html, 2026년 11월 10일 확인).

## 결과물

`outputs/skill-icp-check.md`는 스캔 정합 단계의 나쁜 시작, 평평한 벽, 근거 없는 확신을 점검합니다.

## 연습 문제

1. 두 스캔에 2 cm 노이즈를 넣고 자세 오차를 점 간격과 비교하세요.
2. 오도메트리 추정에서 ICP를 시작해 고칠 수 있는 가장 큰 회전 표류를 찾으세요.
3. 가장 나쁜 짝 20%를 무시하는 trimmed 맞춤을 넣고 모서리가 빠진 경우로 테스트하세요.
