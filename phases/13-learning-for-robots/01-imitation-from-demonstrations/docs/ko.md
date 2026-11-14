# 시연으로부터의 모방 (Imitation from Demonstrations)

> reward를 쓸 수 없으면 로봇에게 하는 법을 보여 주고 그 예시에 함수를 맞춥니다.

**유형:** 만들기   **선수 지식:** 03/02 중력 보상   **시간:** 약 15분

## 쉽게 말하면

작은 로버가 기둥을 돌아 목표까지 가야 하는데 규칙은 아무도 써 두지 않았어요. 대신 사람이 로버를 몇 번 직접 몰면서 위치마다 어느 방향으로 움직였는지 기록해요.

그러면 로버는 지금 위치에서 가장 가까운 기록들을 찾아 사람이 했던 대로 움직여요. 어떤 시연은 기둥 왼쪽으로 돌았고 어떤 시연은 오른쪽으로 돌았어도 괜찮아요. 하지만 직선 규칙 하나로 맞추면 왼쪽과 오른쪽을 평균해서 정면이 되고 로버는 기둥에 부딪혀요.

## 문제

로봇을 손으로 몰아 장애물을 돌아가게 하기는 쉽습니다. 하지만 어느 시작 위치에서든 그렇게 움직이는 제어기를 짜려면 며칠이 걸립니다.
학습 알고리즘에 줄 reward(얼마나 잘했는지 알려 주는 점수)를 쓰는 일도 쉽지 않습니다.
좋은 주행을 몇 번 녹화해서 학습시키면 비용이 적게 듭니다. 남는 질문은 시연이 몇 번 필요한지와 어떤 함수를 맞출지입니다.

## 개념

![전문가에서 정책까지](../assets/diagram-imitation-pipeline.png)

*번호를 따라가 보세요. 전문가가 움직이면 관측과 행동을 짝지어 저장하고 regression(곡선 맞추기)이 그 짝을 policy로 바꿉니다.*

이것은 예시마다 정답이 붙어 있는 supervised learning이고 여기서 정답은 전문가의 행동입니다.
관측은 평면 위 로버의 위치 `x`이고 행동은 그 자리에서 고른 속도입니다. policy는 관측을 행동으로 바꾸는 함수입니다.
전문가는 목표 쪽으로 당기면서 기둥 주위의 금지 원판을 돌아갑니다.

![같은 데이터를 맞추는 두 방법](../assets/diagram-imitation-fits.png)

*두 줄을 비교해 보세요. least squares는 직선 규칙 하나를 맞추기 때문에 "왼쪽으로"와 "오른쪽으로"를 평균해서 "직진"으로 만듭니다. nearest neighbours는 가장 가까운 기록 위치를 찾아 그 행동을 따라 합니다.*

![시연 수에 따른 성공률과 롤아웃](../assets/fig-imitation-success.png)

*왼쪽은 nearest neighbours가 시연 열두 번쯤에서 전문가 수준에 닿는 반면 least squares는 오히려 나빠지는 모습입니다. 오른쪽에서 rollout은 시험 주행 한 번이고 linear policy의 주행은 원판을 곧장 통과합니다.*

데이터만 늘려 본 결과입니다(`python3 code/main.py`를 한 번 돌린 것, 시작 위치 60개씩).
3-nearest-neighbours(가장 가까운 기록 행동 3개의 평균)의 성공률은 시연 1개에서 13%, 3개에서 92%, 10개에서 100%입니다.

![시연 1개로 배운 로버와 10개로 배운 로버](../assets/clip-example.mp4)

*두 로버가 기둥을 지나는 모습을 보세요. 파랑 로버는 파란 선 하나만 보고 배워서 기둥 옆에서 따라 할 기록이 없고 그대로 기둥에 부딪힙니다. 초록 로버는 초록 선 열 개를 보고 배워서 기둥을 돌아갑니다.*

## 만들기

전문가는 장애물 근처에서 swirl 항(장애물을 돌아가도록 옆으로 미는 항)을 더합니다. 코드는 짝을 모은 뒤 두 policy를 맞춥니다.

```python
X, A = collect(rng, n_demos)        # stacked (position, velocity) pairs
policy = fit_knn(X, A, k=3)         # mean action of the 3 closest demo states
W = np.linalg.lstsq(feats, A)[0]    # or one linear rule, fit_linear
```

`success()`는 장애물에 한 번도 들어가지 않고 목표 0.1 m 안에서 끝난 rollout만 성공으로 셉니다. 아래 명령으로 실행합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/01-imitation-from-demonstrations -q
python3 phases/13-learning-for-robots/01-imitation-from-demonstrations/code/figure.py
```

## 실제 도구로 보기

테스트 파일은 이웃 탐색을 `scipy.spatial.cKDTree`와 대조하고 SciPy가 없으면 건너뜁니다. 실제 시스템은 두 fit을 신경망으로 바꿉니다.

출처: Ross, Gordon and Bagnell, "A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning", arXiv:1011.0686.
초록을 2026년 11월 9일에 열어 확인했고 순차 예측이 통계 학습의 i.i.d. 가정을 깨뜨린다고 적혀 있습니다.

## 결과물

`outputs/skill-imitation-data-check.md`는 학습 전에 시연 데이터를 점검하는 체크리스트입니다.

## 연습 문제

1. 장애물을 하나 더 넣고 3-NN이 성공률 95%에 닿는 데 필요한 시연 수를 찾으세요.
2. `k=1`과 `k=15`로 바꾸고 성공률 변화를 설명하세요.
3. 관측에 속도 항을 넣어도 least squares가 여전히 실패하는지 확인하세요.
