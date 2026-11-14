# Multimodal 시연과 Action Chunk

> 시연들이 서로 다른 답을 주면 regression은 그것을 평균해서 아무도 시연하지 않은 행동을 만들고 짧은 미래 행동 묶음(chunk)은 하나를 골라 끝까지 갑니다.

**유형:** 만들기   **선수 지식:** 13/01 모방, 13/02 복제의 함정   **시간:** 약 15분

## 쉽게 말하면

시연의 절반은 로버를 그림에서 기둥의 위쪽으로 보내고 나머지 절반은 아래쪽으로 보내요. 둘 다 잘 통하지만 두 답을 평균하는 규칙은 기둥 정면으로 몰고 가서 로버가 기둥에 부딪혀요.

chunk는 시연 하나에서 그대로 가져온 앞으로의 몇 걸음이라서 로버가 한쪽을 골라 끝까지 가요. 새 chunk가 이전 chunk와 겹칠 때는 아직 하지 않은 걸음과 맞아야 해요. 그렇지 않으면 섞는 순간 우회가 지워져요.

## 문제

시연의 절반은 로버를 그림에서 기둥 위쪽으로 보내고 절반은 아래쪽으로 보냅니다. 시연은 모두 좋은데 학습된 policy는 기둥 정면으로 달려갑니다. 첫 행동부터 유효한 답 둘을 평균하기 때문입니다.
13/02에서는 먼저 push가 policy를 시연에서 밀어내야 했습니다. 여기서는 첫 행동부터 이미 틀립니다.

## 개념

![평균할까 하나를 고를까](../assets/diagram-average-or-commit.png)

*시작점에서는 두 답이 모두 맞지만 둘의 평균은 틀립니다. sampler는 시연 하나를 골라 그대로 따라갑니다.*

regression(least squares나 가까운 시연들의 가중 평균)은 평균 행동을 예측합니다. "위"와 "아래" 시연의 평균은 "정면"입니다. 시작점에서 두 시연은 옆으로 +0.054와 -0.054씩 움직이므로 평균은 0입니다.
대신 표본을 뽑으면 시연 하나의 행동을 무작위로 골라 따라 합니다. 지금 위치 가까이를 지나는 시연이 더 잘 뽑히므로 두 mode가 그대로 남습니다.
스텝마다 새로 뽑으면 반대쪽으로 넘어갈 수 있습니다. 그래서 sampler는 다음 `H`개 행동을 한 묶음(chunk)으로 돌려줍니다.

![chunk 겹침](../assets/diagram-chunk-overlap.png)

*새 chunk는 이전 chunk가 끝나기 전에 시작합니다. 겹치는 스텝은 이전에서 새것으로 가중치가 넘어가는 가중 평균으로 섞고 새 chunk는 이전 chunk와 맞는 것으로 고릅니다.*

![rollout 부채꼴과 chunk 길이](../assets/fig-chunk-fan.png)

*왼쪽은 mean policy가 곧바로 가로지르는 모습입니다. 가운데는 표본 rollout 40개가 두 갈래로 나뉘는 모습입니다.
오른쪽은 H = 2부터 jitter, 즉 스텝마다 행동이 바뀌는 크기가 한 스텝 표본의 절반 아래로 떨어지고 rollout 60개가 모두 원판을 피하는 모습입니다.*

`python3 code/main.py`를 50번 돌린 결과입니다. 한 스텝씩 표본을 뽑으면 기둥을 피하는 비율은 98%이지만 jitter는 스텝당 0.034입니다.
길이 8이고 4스텝마다 새로 시작하는(겹침 4) chunk는 100% 피하고 jitter는 0.011로 3분의 1입니다.

![한 걸음씩 고르는 로버와 chunk를 따라가는 로버](../assets/clip-example.mp4)

*파랑 로버는 걸음마다 시연을 골라서 흔들립니다. 초록 로버는 8걸음짜리 chunk를 따라가서 매끄럽게 갑니다.*

## 만들기

`mean_policy`는 가까운 시연 행동을 Gaussian kernel로 가중합니다. `sample_chunk`는 같은 kernel로 시연 하나를 고르고 그 시연의 다음 `H`개 행동을 돌려줍니다.

```python
j = ((P[:, :-1] - x) ** 2).sum(2).argmin(1)            # nearest state in each demo
logw -= ((chunks[:, :len(prefix)] - prefix) ** 2).sum((1, 2)) / (2 * SIGMA_A**2)
a = w * new[k] + (1 - w) * old[k + stride]             # blend while chunks overlap
```

`prefix`가 없으면 새 chunk가 반대쪽을 고를 수 있고 그러면 섞인 값이 원판 정면으로 향합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks -q
python3 phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/code/figure.py
```

## 실제 도구로 보기

실제 policy는 조회 대신 chunk를 출력하는 network를 쓰고 겹치는 예측은 실행할 때 섞습니다. chunk가 길수록 그 사이에 생기는 일에 늦게 반응하므로 그 비용은 직접 재야 합니다.

출처: Zhao 외, "Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware", arXiv:2304.13705의 초록을 2026년 11월 10일에 열어 봤습니다. 행동 시퀀스에 대한 생성 모델을 학습한다고 적혀 있습니다.
Chi 외, "Diffusion Policy", arXiv:2303.04137의 초록도 같은 날 열어 봤습니다. multimodal 행동 분포를 다룬다고 적혀 있습니다.

## 결과물

`outputs/skill-multimodal-demo-check.md`는 mean policy가 뭉개 버릴 mode가 시연 세트에 있는지 점검합니다.

## 연습 문제

1. 시연을 5 대 1로 갈라서 mean policy가 어떻게 되는지 찾으세요.
2. `SIGMA_A`를 크게 키우고 원판에 부딪히는 rollout 수를 세세요.
3. 스텝마다 행동 노이즈를 넣고 jitter가 더는 줄지 않는 chunk 길이를 찾으세요.
