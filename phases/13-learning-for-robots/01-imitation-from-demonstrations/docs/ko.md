# 시연으로부터의 모방 (Imitation from Demonstrations)

> 규칙을 쓰는 대신 예시를 보여 주면서 로봇을 가르치는 법을 배웁니다.

**유형:** 만들기   **선수 지식:** 없음   **시간:** 약 15분

## 쉽게 말하면

작은 로버가 기둥을 돌아 목표까지 가야 하는데 규칙은 아무도 써 두지 않았어요. 사람이 로버를 몇 번 직접 몰면서 위치마다 어느 쪽으로 방향을 틀었는지 기록해요.

그러면 로버는 가장 가까운 기록들을 찾아 사람이 했던 대로 움직여요.

## 핵심 용어

- **Imitation learning**: 전문가가 일하는 예시를 로봇에게 보여 주며 가르치는 방법입니다.
- **Observation**: 로봇이 감지하는 것입니다. 여기서는 바닥 위 자기 위치입니다.
- **Action**: 로봇이 다음에 하는 일입니다. 여기서는 주행 방향입니다.
- **Policy**: 관측을 행동으로 바꾸는 규칙입니다.
- **Least squares**: 모델이 예시에서 최대한 덜 벗어나도록 수치를 고르는 방법입니다. 여기서는 직선 규칙 하나가 나옵니다.
- **Nearest neighbours**: 가장 가까운 예시의 행동을 그대로 따라 하거나 평균하는 방법입니다.

## 문제

작은 로버를 어느 시작 위치에서든 기둥을 돌아가게 하고 싶습니다. 규칙이나 reward(얼마나 잘했는지 알려 주는 점수)를 쓰는 데는 며칠이 걸립니다. 손으로 몇 번 몰아 보는 것은 쉽고 비용도 적게 듭니다.

## 개념

로봇은 아무도 규칙을 써 두지 않은 상황을 만나곤 합니다. 그럴 때 사람은 올바른 동작을 그냥 보여 줄 수 있는 경우가 많습니다. 전문가가 지나간 위치마다 그때 한 동작을 저장하고 그 짝들에 맞는 규칙을 찾습니다.
직선 규칙 하나는 "왼쪽으로"와 "오른쪽으로"를 평균해서 "직진"으로 만들고 기둥에 부딪힙니다. 가장 가까운 예시를 따라 하면 훨씬 잘 됩니다.

![파이프라인](../assets/diagram-imitation-pipeline.png)

*전문가가 주행하고 우리는 그 동작을 저장합니다. 학습은 저장된 짝을 policy로 바꿉니다.*

![두 가지 규칙](../assets/diagram-imitation-fits.png)

*직선 규칙 하나는 기둥을 향해 곧장 갑니다. 가장 가까운 예시를 따라 하면 기둥을 돌아갑니다.*

![성공률](../assets/fig-imitation-success.png)

*왼쪽은 시연 수에 따라 주행이 성공하는 비율입니다. 가장 가까운 예시를 따르는 규칙은 열두 번쯤에서 전문가만큼 잘하고 직선 규칙은 오히려 나빠집니다. 오른쪽은 시험 주행 한 번입니다.*

![1개와 10개](../assets/clip-example.mp4)

*파랑 로버는 시연 하나만 보고 배워서 기둥에 부딪힙니다. 초록 로버는 열 개를 보고 배워서 기둥을 돌아갑니다.*

<details><summary>The math (optional)</summary>

policy는 로버의 위치 `x`를 속도로 바꿉니다. least squares는 직선 규칙 하나를 맞춥니다. 3-nearest-neighbours는 가장 가까운 기록 행동 3개를 평균합니다. 실제 로봇은 두 규칙을 신경망(학습으로 만든 큰 모델)으로 바꿉니다.
시작 위치 60개를 무작위로 뽑으면 성공률은 시연 1개에서 13%, 3개에서 92%, 10개에서 100%입니다. 주행은 장애물에 한 번도 들어가지 않고 목표 0.1 m 안에서 끝나야 성공으로 셉니다.

</details>

## 만들기

코드 속 가짜 전문가는 기둥 근처에서 옆으로 조향합니다. 코드는 예시를 저장하고 두 policy를 만듭니다.

```python
X, A = collect(rng, n_demos)        # stacked (position, velocity) pairs
policy = fit_knn(X, A, k=3)         # mean action of the 3 closest demo states
W = np.linalg.lstsq(feats, A)[0]    # or one linear rule, fit_linear
```

`success()`는 주행이 기둥을 한 번도 건드리지 않고 목표 근처에서 끝나는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/01-imitation-from-demonstrations -q
python3 phases/13-learning-for-robots/01-imitation-from-demonstrations/code/figure.py
```

## 실제 도구로 보기

테스트는 우리가 만든 이웃 탐색을 SciPy의 `cKDTree`와 대조합니다. 이 도구는 이미 만들어진 최근접 이웃 탐색기입니다.

출처: Ross, Gordon and Bagnell, arXiv:1011.0686(2026년 11월 9일 확인).

## 결과물

`outputs/skill-imitation-data-check.md`는 학습 전에 시연 데이터를 점검합니다.

## 연습 문제

1. 기둥을 하나 더 세우세요. 시연이 몇 개 필요한가요?
2. 평균을 내는 이웃의 수를 바꿔 보세요. 무슨 일이 생기나요?
3. 관측에 속도도 넣으세요. 직선 규칙은 여전히 실패하나요?
