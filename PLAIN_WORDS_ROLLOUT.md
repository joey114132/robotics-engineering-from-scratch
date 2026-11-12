# In Plain Words rollout

This revision applies the review in `/tmp/rfs-cx/vis8.md` inside `/tmp/rfs-cx/t0`. It updates three bilingual openings and the two writing guides. The other 78 lessons are outside this revision. Existing source-code changes are preserved. Nothing is staged or committed.

## Writing rules

Write a short, connected explanation for a Senior High reader. Use familiar objects and address the reader directly where the scene calls for it. Verify the analogy against the lesson's equations, code and tests. Its force directions, changes in quantities and distinction between estimated and true state must agree with the lesson. Keep technical terms stable and explain them in everyday words. Korean uses natural spoken-polite language (~해요). Prefer 배식대의 쟁반 to 계산대. Use prose without company or product names, ASCII art, em-dash clauses, middle-dot noun chains or commas after Korean connective endings.

Apply these five rules in both languages.

1. An analogy must show the cause. Say what changes and what happens because of that change. A familiar scene alone is insufficient.
2. Explain the lesson's key mechanism before any closing question. In 08-01, explicitly show that planning and odometry use the same wrong values; the recorded route can then close while the real route does not.
3. Name the object a force acts on and its direction. Explain kp as the controller's response to a given error, rather than a vague degree of firmness.
4. Avoid dense English blocks and Korean paragraphs split after every sentence. Use two short English paragraphs when the block exceeds about 60 words. Group related Korean sentences into two or three paragraphs per block, normally two or three sentences together; do not split a connected explanation merely to isolate each sentence.
5. Do not force every lesson into the same opening order or a final question. Check English and Korean for natural flow separately. A closing question is optional and must follow an explanation that already makes sense.

| Do | Don't |
| --- | --- |
| "Your friend supports most of the tray's weight; the weight left on your arms makes them sag farther when you relax them." | "Relax your grip and gravity compensation stops the tray from sagging." |
| "A notebook records every corner as a right angle, so the drawn square closes even though your smaller turns leave you away from the start." | "A wrong stride length distorts distances." (This does not explain why the notebook can hide the error.) |
| "The showerhead pushes water away, so your hand feels a push in the opposite direction." | "A propeller's thrust points in the direction it blows air." |

The total English budget is 450 + 90 = 540 words outside fenced code, including headings and metadata.
The opening cap counts visible prose, including link labels. Korean has a mechanical ceiling of 90 whitespace-separated words and 600 characters, including spaces and paragraph breaks; match the English meaning rather than filling the ceiling.
Prefer words to equations in the opening. If a familiar number is needed for the causal scene, link it to a source or a lesson test. The 08-01 example keeps 90° / 90도 and links those labels to a verified definition of a right angle. Put detailed numeric examples and equations in the later sections.
Korean opening paragraphs may exceed the general 160-character paragraph guideline when needed to preserve a connected explanation; the block still has the 600-character ceiling. Source lines must stay within the checker's 160-character limit. A soft line break does not create a new paragraph.
Mechanical checks cannot establish that an analogy is physically correct, so reviewers must trace its causal chain.


### Corrected worked examples

These examples keep the lesson headings and caps. They show different ways to finish: a causal statement for 03-02 and 08-01, and a question after the explanation for 10-03.

#### 03-02 Gravity compensation

EN (79 words; 2 paragraphs).

```markdown
## In Plain Words

Gravity compensation lets a motor carry an arm's weight, much as a friend helps you carry a tray. At the cafeteria serving counter, you lift a heavy tray while your friend supports most of its weight.

Your friend's support is like gravity compensation. The position controller carries the remaining load. Its gain kp sets how strongly it pushes back for a given amount of sag. With a lower kp, the arm must sag farther to produce the same support.
```

KO (63 words; 283 characters including paragraph breaks; 3 paragraphs).

```markdown
## 쉽게 말하면

gravity compensation은 친구가 쟁반을 함께 받쳐 주듯 모터가 로봇 팔의 무게를 받치는 방법이에요.

배식대에서 친구와 무거운 쟁반을 들 때를 떠올려 보세요. 친구가 대부분 받쳐 줘도 팔에 무게가 남아서 힘을 풀수록 쟁반이 더 내려가요.

친구가 받쳐 주는 힘이 gravity compensation에 해당해요. position controller는 남은 무게를 버텨요. kp는 같은 정도로 처졌을 때 얼마나 강하게 밀어 올릴지 정해요. kp가 낮으면 같은 무게를 버티기까지 더 많이 처져요.
```

#### 08-01 Differential drive and odometry

Analogy must show the cause: before and after. The old walk-and-notebook scene described distortion but left the hidden-error mechanism to a question. The corrected scene gives the notebook an explicit wrong recording rule. The robot paragraph then maps that rule to the same incorrect geometry used in planning and odometry.

Before (EN and KO).

```markdown
## In Plain Words

Differential drive steers with unequal wheel speeds, and odometry estimates position from wheel motion. You draw your school walk in a notebook from counted steps and estimated turns. A wrong stride length distorts distances, and a misjudged turn sends the next line the wrong way. Wheel radius sets travel per rotation; wheelbase, the gap between wheels, converts travel differences into turns. If planning and odometry use the same wrong wheel radius or wheelbase, why can the map close while the robot misses the start?
```

```markdown
## 쉽게 말하면

differential drive는 양쪽 바퀴의 속도 차이로 방향을 바꾸는 방식이고 odometry는 바퀴가 움직인 거리로 위치를 추정하는 방법이에요.

학교 주변을 걸으며 걸음 수와 돈 각도를 기록해 공책에 길을 그려 보세요.

보폭을 잘못 잡으면 거리가 틀어지고 돈 각도를 잘못 잡으면 다음 선이 엉뚱한 방향으로 나가요.

wheel radius는 바퀴가 한 바퀴 돌 때 가는 거리를 정해요.

wheelbase는 양쪽 바퀴 사이의 간격으로 양쪽이 간 거리의 차이가 얼마나 큰 회전이 되는지 정해요.

경로 계획과 odometry가 똑같이 틀린 wheel radius나 wheelbase를 쓰면 지도에서는 제자리로 돌아와도 실제 로봇은 왜 출발점에 못 돌아올까요?
```

After (EN and KO). These labels link to a verified definition of a right angle; the visible wording and two-paragraph structure are verbatim from the approved review.

EN (84 words; 2 paragraphs).

```markdown
## In Plain Words

Differential drive turns a robot by running its wheels at different speeds. Imagine walking a square but turning slightly less than [90°](https://mathworld.wolfram.com/RightAngle.html) at each corner. A notebook that records every turn as [90°](https://mathworld.wolfram.com/RightAngle.html) draws a closed square, although you miss the start.

A robot can make the same mistake. Wheel radius and the distance between the wheels determine distances and turns from wheel rotations. If planning and odometry use the same wrong values, the recorded path can close while the robot misses the start.
```

KO (56 words; 248 characters including paragraph breaks; 2 paragraphs).

```markdown
## 쉽게 말하면

differential drive는 양쪽 바퀴의 속도 차이로 방향을 바꿔요.
사각형으로 걷는데 모서리마다 [90도](https://mathworld.wolfram.com/RightAngle.html)보다 조금 덜 돈다고 해 보세요.
공책에는 매번 [90도](https://mathworld.wolfram.com/RightAngle.html)로 그리면 사각형이 닫혀도 나는 출발점에 못 돌아와요.

로봇은 wheel radius와 양쪽 바퀴 사이 간격으로 이동 거리와 회전 각도를 계산해요.
계획할 때와 odometry로 이동을 기록할 때 같은 잘못된 값을 쓰면 기록상으로는 출발점에 돌아와도 실제로는 빗나갈 수 있어요.
```

#### 10-03 Quadrotor model

EN (85 words; 2 paragraphs).

```markdown
## In Plain Words

A quadrotor model predicts motion from a drone's tilt and thrust, the push it gets from its propellers. You rinse the bath with a showerhead and feel it push your hand opposite the water flow. When you tilt the showerhead, the push changes direction too.

An upright drone likewise pushes air down for upward thrust, then tilts to redirect that force. At the same total thrust, tilting reduces the upward force. How much more thrust does the drone need to stay at the same height?
```

KO (61 words; 271 characters including paragraph breaks; 3 paragraphs).

```markdown
## 쉽게 말하면

quadrotor model은 드론의 기울기와 프로펠러가 드론을 미는 힘인 thrust로 움직임을 예측하는 모델이에요.

샤워기를 손에 들고 욕조를 헹굴 때 물줄기 반대쪽으로 손이 밀리는 느낌을 떠올려 보세요. 샤워기를 기울이면 손을 미는 힘의 방향도 바뀌어요.

드론도 공기를 아래로 밀어 위로 힘을 받고 몸체를 기울여 그 힘의 방향을 바꿔요. thrust가 그대로인 상태에서 드론을 기울이면 위로 받치는 힘이 줄어들어요. 같은 높이를 유지하려면 thrust를 얼마나 늘려야 할까요?
```

## Causal checks

| Lesson | What the explanation must show |
| --- | --- |
| 03-02 | The friend supplies gravity compensation. The position controller carries the remaining load. Lower kp needs more sag to produce the same support. |
| 08-01 | The walker turns too little, but the notebook always records a right angle. Planning and odometry can share the same wrong geometry, so a closed record can hide a missed starting point. |
| 10-03 | Water pushes the hand opposite the flow. Tilting changes the push direction. A tilted drone has less upward force at the same total thrust. |

## Humanizer and backup policy

The supplied replacements are content edits, made before the humanizer passes. English is checked with humanizer-oneaway, kinncj-humanizer and no-ai-slop. Korean uses humanize-korean light, followed by its deterministic fidelity gates. Explicitly approved sentences stay fixed; unchanged text is a valid result.

Only the three lessons' six English/Korean documents in `/tmp/rfs-cx/t0/.board/humanize-backup/phases/` are refreshed to the corrected pre-humanizer drafts. No quiz, fun file or other baseline is refreshed. Original documents, original baselines, hash manifests, humanizer evidence and command logs are kept in `/tmp/rfs-cx/t0/.board/t0c/`. Korean shim files are in `/tmp/rfs-cx/t0/_workspace/2026-11-11-001/`.

## Verification

Requested checks and measured results are recorded in `/tmp/rfs-cx/t0c-report.md`. The build output is `/tmp/rfs-cx/site-t0c`. Counts in the worked examples exclude headings and strip evidence-link markup, so they count the text the reader sees.
