// Phase 05: timestamp에 맞는 interpolated transform과 latest transform을 비교한다.
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  // 05/06 __main__: endpoint poses (2t,0,0), quaternion (cos(t/2),0,0,sin(t/2)).
  const q0 = [1, 0, 0, 0], q1 = [Math.cos(.5), 0, 0, Math.sin(.5)];
  function model(stamp) {
    const om = Math.acos(q1[0]);
    const a = Math.sin((1 - stamp) * om) / Math.sin(om), b = Math.sin(stamp * om) / Math.sin(om);
    const q = q0.map((v, i) => a * v + b * q1[i]);
    const yaw = 2 * Math.atan2(q[3], q[0]), p = [2 * stamp, 0, 0];
    const point = R.add(p, [Math.cos(yaw), Math.sin(yaw), 0]);
    const latest = [2 + Math.cos(1), Math.sin(1), 0];
    return { p, q, yaw, point, latest, error: Math.hypot(...R.sub(point, latest)) };
  }
  const endpoint = model(1);
  window.MOTION.three('timestamp-frames-3d', {
    en: 'A timestamped sensor point goes to two different places when the lookup time is wrong',
    ko: 'Sensor point의 timestamp와 다른 시각으로 transform을 조회하면 위치가 어긋납니다',
    cap: ['The buffer stores t=0 and t=1 s with p=(2t,0,0) and yaw=t rad, as in the lesson. Position uses lerp and orientation uses slerp. A unit point (1,0,0) in the sensor frame uses its own timestamp (green); using the newest pose puts it at the orange point. All lookups stay inside the stored interval.',
      '수업처럼 buffer에 t=0과 t=1 s의 p=(2t,0,0), yaw=t rad를 저장합니다. 위치는 lerp, 방향은 slerp로 보간합니다. Sensor frame의 단위 점 (1,0,0)에 자신의 timestamp를 쓰면 초록색 위치가 됩니다. Latest pose를 쓰면 주황색 위치로 어긋납니다. 조회는 저장된 시간 범위 안에서만 합니다.'],
    period: 12, rest: 6, H: 340, unit: 110, look: [1.3, .3, .05], oy: 45,
    cam: { yaw: .15, pitch: .65, dist: 8 }, model,
    controls: [{ id: 'stamp', en: 'point timestamp', ko: '점의 timestamp', min: 0, max: 1, step: .01, dec: 2, unit: '\u00a0s', auto: t => Math.min(1, Math.max(0, (t - 1) / 10)) }],
  }, (s, t, m) => {
    const a = model(s.v.stamp), rot = R.rz(a.yaw);
    for (let i = 0; i <= 3; i++) {
      s.line([i, -.45, -.06], [i, 1.15, -.06], '--line', 1);
      s.label([i, -.45, -.06], `${i} m`, '--mut', 15, 'center', 0, 20);
    }
    s.line([0, 0, 0], [2, 0, 0], '--mut', 2, { dash: [4, 4] });
    s.wire([2, 0, .08], [.17, .12, .08], R.rz(1), '--mut', 2, { dash: [4, 4] });
    s.box(R.add(a.p, [0, 0, .08]), [.17, .12, .08], rot, '--pf');
    // Sensor origins coincide with robot origins in this lesson's buffer.
    for (const [p, rotation, scale] of [[a.p, rot, .4], [endpoint.p, R.rz(1), .25]]) {
      for (let k = 0; k < 3; k++) {
        const e = [0, 0, 0]; e[k] = scale;
        s.arrow(p, R.add(p, R.mv(rotation, e)), ['--bad', '--ok', '--pd'][k], 2);
      }
    }
    s.line(a.p, a.point, '--ok', 3); s.dot(a.point, '--ok', 8, { ring: true, front: true });
    s.line(endpoint.p, a.latest, '--bad', 2, { dash: [4, 4] });
    s.dot(a.latest, '--bad', 7, { ring: true, front: true });
    s.line(a.point, a.latest, '--bad', 2, { dash: [3, 4] });
    s.text(14, 24, m.t(`point stamp ${s.v.stamp.toFixed(2)} s`, `점의 timestamp ${s.v.stamp.toFixed(2)} s`), '--ok', 16);
    s.text(14, 46, m.t('orange: lookup at latest (1 s)', '주황: latest(1 s)로 조회'), '--bad', 15);
    s.text(14, 68, m.t(`position error ${a.error.toFixed(3)} m`, `위치 오차 ${a.error.toFixed(3)} m`), '--fg', 16);
  });
})();
// 05단계 3D (wave 3d): qos-queue-3d, executor-lanes-3d, loop-jitter-belt-3d, clock-offset-3d, behaviour-tree-fetch-3d

// 05/01: keep-last queue. A burst of 8 messages meets a subscriber queue of depth d (lesson: run(Qos(), Qos(depth=d), [8] + [0]*9)).
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], BURST = 8, STEP = 0.3;
  window.MOTION.three('qos-queue-3d', {
    en: 'A burst of 8 messages reaches a subscriber whose queue holds only a few; the oldest crates fall off the belt',
    ko: '메시지 8개가 한꺼번에 도착하는데 구독자 queue에 몇 개만 들어가면, 가장 오래된 상자부터 벨트 밖으로 떨어집니다',
    cap: ['Each crate is one message. The publisher sends 8 in a single tick, the subscriber takes one per tick (lesson run(Qos(), Qos(depth=d), [8] + [0]*9)). A keep-last queue of depth d keeps the newest d crates and drops 8 − d, so depth 1 delivers 1 and drops 7. The toggle shows a QoS mismatch (publisher best_effort, subscriber reliable): the pair never connects, nothing is delivered and nothing is reported. The belt and crates are a picture of the queue, not a transport model.',
      '상자 하나가 메시지 하나입니다. Publisher가 한 tick에 8개를 보내고 subscriber는 tick마다 1개씩 꺼냅니다(수업의 run(Qos(), Qos(depth=d), [8] + [0]*9)). Depth d인 keep-last queue는 최신 d개만 남기고 8 − d개를 버리므로 depth 1이면 1개를 전달하고 7개를 버립니다. 토글은 QoS mismatch(publisher best_effort, subscriber reliable)를 보여 줍니다. 연결이 되지 않아 아무것도 전달되지 않고 아무 오류도 나오지 않습니다. 벨트와 상자는 queue를 그림으로 옮긴 것이며 실제 전송 모델이 아닙니다.'],
    period: 12, rest: 6, H: 320, unit: 58, look: [1.0, 0, .1], oy: 30, cam: {yaw: .3, pitch: .75, dist: 8},
    controls: [
      {id: 'depth', en: 'subscriber queue depth', ko: '구독자 queue depth', min: 1, max: 10, step: 1, auto: t => [1, 3, 8, 8][Math.floor(t / 3) % 4]},
      {id: 'bad', toggle: true, en: 'QoS mismatch (best_effort vs reliable)', ko: 'QoS mismatch (best_effort vs reliable)', auto: t => Math.floor(t / 3) % 4 === 3},
    ],
  }, (s, t, m) => {
    const d = s.v.depth, bad = s.v.bad, PX = i => 3.06 - .34 * i, kept = Math.min(BURST, d), dropped = bad ? 0 : BURST - kept;
    const got = bad ? 0 : Math.min(kept, Math.floor((t % 3) / STEP));
    const bx = PX(d - 1) - .2; s.poly([[-1.9, -.35, -.02], [bx, -.35, -.02], [bx, .35, -.02], [-1.9, .35, -.02]], '--line', {a: .35});
    for (let i = 0; i < d; i++) { const x = PX(i); s.poly([[x - .16, -.18, -.01], [x + .16, -.18, -.01], [x + .16, .18, -.01], [x - .16, .18, -.01]], '--pf', {a: .22, edge: '--line', w: 1}); }
    s.box([-2.2, 0, .3], [.3, .3, .3], I, '--pd'); s.box([-1.85, 0, .3], [.06, .12, .12], I, '--fg');
    s.box([4.0, 0, .3], [.3, .3, .3], I, '--pl');
    if (bad) {
      s.box([-.3, 0, .3], [.04, .4, .3], I, '--bad');
      for (let k = 0; k < BURST; k++) s.box([-1.5 + .32 * (k % 4), 0, .15 + .32 * Math.floor(k / 4)], [.15, .15, .15], I, '--pf');
      s.label([-.3, .8, .3], m.t('no connection', '연결 안 됨'), '--bad', 15, 'center');
    } else {
      for (let k = 0; k < BURST - kept; k++) s.box([-1.5 + .32 * k, -.75, .15], [.15, .15, .15], R.rz(.35 * k), '--bad', {a: .75});
      for (let j = 0; j < kept; j++) if (j >= got) s.box([PX(j - got), 0, .15], [.15, .15, .15], I, '--pf');
      if (got) s.box([4.0, 0, .75], [.15, .15, .15], I, '--ok');
    }
    if (BURST - kept > 0 && !bad) s.label([-.7, -1.15, 0], m.t(`dropped ${dropped}`, `버려짐 ${dropped}`), '--bad', 14, 'center');
    s.text(14, 24, bad ? m.t('delivered 0 of 8, and no error is shown', '8개 중 0개 전달, 오류 표시도 없음') : m.t(`published 8 · dropped ${dropped}`, `발행 8 · 버려짐 ${dropped}`), bad ? '--bad' : '--fg', 15);
    s.text(14, 44, bad ? m.t('the two ends never connect', '두 끝이 연결되지 않음') : m.t(`delivered so far ${got} of ${kept}`, `지금까지 전달 ${got} / ${kept}`), bad ? '--bad' : '--ok', 15);
    s.text(14, 64, m.t(`queue depth ${d}`, `queue depth ${d}`), '--mut', 14);
  });
})();

// 05/02: one thread vs two threads with mutually exclusive groups (lesson simulate(), callbacks timer 10/1 ms group fast first=1, slow 100/60 ms group slow first=0).
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], K = .022, CBS = [['timer', 10, 1, 'fast', 1], ['slow', 100, 60, 'slow', 0]], cache = {};
  function simulate(cbs, threads, horizon) {   // port of main.py simulate(): FIFO of released jobs, a free thread takes the oldest job whose group is idle
    const pending = [], log = []; let running = [];
    for (let t = 0; t < horizon; t++) {
      for (const [name, period, dur, group, first] of cbs) if (t >= first && (t - first) % period === 0) pending.push([name, t, dur, group]);
      running = running.filter(r => r[0] > t);
      while (running.length < threads) {
        const busy = new Set(running.map(r => r[1]).filter(g => g !== null)), k = pending.findIndex(j => j[3] === null || !busy.has(j[3]));
        if (k < 0) break;
        const job = pending.splice(k, 1)[0]; running.push([t + job[2], job[3]]); log.push([job[0], job[1], t, t + job[2]]);
      }
    }
    return log;
  }
  function model(n) {
    if (cache[n]) return cache[n];
    const log = simulate(CBS, n, 1000), waits = log.filter(j => j[0] === 'timer').map(j => j[2] - j[1]);
    return cache[n] = {log, worst: Math.max(...waits), late: waits.filter(w => w >= 10).length};
  }
  window.MOTION.three('executor-lanes-3d', {
    en: 'A slow callback blocks a 10 ms timer on one thread; a second thread in a different group lets the timer run on time',
    ko: 'Thread가 하나면 느린 callback이 10 ms timer를 막고, 다른 group의 thread가 하나 더 있으면 timer가 제때 돕니다',
    cap: ['Time runs along the floor (0 to 200 ms). Blue boxes are the 60 ms slow callback every 100 ms; thin boxes are the 1 ms timer every 10 ms (drawn wider than 1 ms so you can see them). Red lines on the back rail run from the moment a timer job is released to the moment it starts. With one thread the first timer waits 59 ms and the worst wait over 1000 ms is 59 ms with 60 late ticks; with two threads and separate mutually exclusive groups the worst wait is 0 ms (lesson simulate(), 1 ms steps).',
      '시간은 바닥을 따라 0~200 ms로 흐릅니다. 파란 상자는 100 ms마다 도는 60 ms짜리 느린 callback이고 얇은 상자는 10 ms마다 도는 1 ms짜리 timer입니다(보이도록 1 ms보다 넓게 그렸습니다). 뒤쪽 레일의 빨간 선은 timer job이 release된 순간부터 시작되는 순간까지의 대기입니다. Thread가 하나면 첫 timer가 59 ms 기다리고 1000 ms 동안 최악 대기가 59 ms, 늦은 tick이 60번입니다. Thread가 둘이고 group이 서로 다른 mutually exclusive면 최악 대기는 0 ms입니다(수업의 simulate(), 1 ms 단위).'],
    period: 12, rest: 3, H: 320, unit: 72, look: [1.9, 0, .1], oy: 30, cam: {yaw: .3, pitch: .6, dist: 8},
    controls: [{id: 'n', en: 'executor threads', ko: 'executor thread 수', min: 1, max: 2, step: 1, auto: t => t % 12 < 6 ? 1 : 2}],
  }, (s, t, m) => {
    const n = s.v.n, M = model(n), free = [0, 0], YR = .95;
    s.poly([[0, -1.2, -.02], [4.4, -1.2, -.02], [4.4, 1.2, -.02], [0, 1.2, -.02]], '--line', {a: .3});
    for (let ms = 0; ms <= 200; ms += 50) { s.line([ms * K, -1.2, 0], [ms * K, 1.2, 0], '--line', 1); s.label([ms * K, -1.2, 0], `${ms} ms`, '--mut', 14, 'center', 0, 6); }
    for (const [name, rel, st, en] of M.log) {
      if (rel >= 200) continue;
      if (name === 'timer' && st > rel) s.line([rel * K, YR, .04 + .02 * ((rel - 1) / 10 % 8)], [st * K, YR, .04 + .02 * ((rel - 1) / 10 % 8)], '--bad', 2);
      if (st >= 200) continue;
      let lane = free[0] <= st ? 0 : 1; if (n === 1) lane = 0; free[lane] = en;
      const len = Math.max((en - st) * K, .06);
      s.box([st * K + len / 2, -.3 - .6 * lane, .09], [len / 2, .17, .09], I, name === 'slow' ? '--pd' : '--pf');
    }
    s.label([0, -.3, 0], m.t('thread 1', 'thread 1'), '--mut', 14, 'right', -8, 4);
    if (n > 1) s.label([0, -.9, 0], m.t('thread 2', 'thread 2'), '--mut', 14, 'right', -8, 4);
    s.label([0, YR, 0], m.t('timer waits', 'timer 대기'), '--bad', 14, 'right', -8, 4);
    const cx = ((t % 12) / 12) * 200 * K; s.line([cx, -1.2, 0], [cx, 1.2, .3], '--ok', 2);
    s.text(14, 24, m.t(`${n} thread${n > 1 ? 's' : ''}`, `thread ${n}개`), '--fg', 16);
    s.text(14, 44, m.t(`worst timer wait ${M.worst} ms`, `timer 최악 대기 ${M.worst} ms`), M.worst ? '--bad' : '--ok', 15);
    s.text(14, 64, m.t(`late ticks in 1000 ms: ${M.late}`, `1000 ms 동안 늦은 tick: ${M.late}`), '--fg', 15);
  });
})();

// 05/03: a fixed-rate loop on a conveyor. Model of main.py simulate(): T = 1 ms, work 0.2 ms, exponential wake latency (scale 20 us), rare spikes of 0.5 to 1.5 periods.
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], N = 40, T = 1e-3, WORK = 2e-4, LAT = 2e-5, DX = .12;
  const rng = seed => () => { seed = seed + 0x6D2B79F5 | 0; let x = Math.imul(seed ^ seed >>> 15, 1 | seed); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; };
  const rnd = rng(11), E = [], U = [], S = [];   // fixed draws: the slider only moves the threshold on U, so a spike appears and grows with it
  for (let i = 0; i < N; i++) { E.push(-Math.log(1 - rnd())); U.push(rnd()); S.push(.5 + rnd()); }
  function sim(p, rel) {
    const s = [], d = []; let done = 0;
    for (let i = 0; i < N; i++) {
      const lat = E[i] * LAT + (U[i] < p ? S[i] * T : 0), wake = (rel ? done + T : i * T) + lat;
      s.push(Math.max(wake, done)); d.push(done = s[i] + WORK);
    }
    let worst = 0, miss = 0;
    for (let i = 1; i < N; i++) worst = Math.max(worst, Math.abs(s[i] - s[i - 1] - T));
    for (let i = 0; i < N - 1; i++) if (d[i] > (i + 1) * T) miss++;
    return {s, d, worst, miss};
  }
  window.MOTION.three('loop-jitter-belt-3d', {
    en: 'A machine drops a crate every millisecond. The tall posts show how late each drop was; a sleep-after-work loop drifts further every cycle',
    ko: '기계가 1 ms마다 상자를 하나씩 떨어뜨립니다. 기둥은 각 상자가 얼마나 늦었는지 보여 주고, 일을 마친 뒤 쉬는 방식의 loop는 주기마다 더 밀립니다',
    cap: ['Each crate is one loop iteration; the post above it is how late it started compared with its slot i × 1 ms (1 unit of height = 1 ms, capped at 2.2). Model from the lesson: T = 1 ms, work 0.2 ms, wake-up latency exponential with scale 20 µs, and a rare spike of 0.5 to 1.5 periods. The slider is the spike chance per iteration; the lesson uses 0.002 to 0.003 over 5000 iterations, so this view goes up to 0.1 to make a spike appear in 40 iterations. Random numbers are a fixed JavaScript sequence, not the lesson’s numpy seed. The toggle sleeps T after the work (relative): the period becomes T + work and the lateness grows every cycle. Red dots mark an iteration that finishes after the next deadline.',
      '상자 하나가 loop 한 번입니다. 위의 기둥은 그 상자가 자기 slot i × 1 ms보다 얼마나 늦게 시작했는지입니다(높이 1이 1 ms, 최대 2.2). 수업의 모델을 씁니다. T = 1 ms, 일 0.2 ms, 깨어나는 지연은 scale 20 µs의 지수분포이고 가끔 0.5~1.5 주기짜리 spike가 끼어듭니다. 슬라이더는 iteration마다 spike가 날 확률입니다. 수업은 5000번 도는 동안 0.002~0.003을 쓰므로, 여기서는 40번 안에 spike가 보이도록 0.1까지 올립니다. 난수는 수업의 numpy seed가 아니라 고정된 JavaScript 수열입니다. 토글을 켜면 일을 마친 뒤 T만큼 쉬는 방식(relative)이 되어 주기가 T + 일이 되고 늦음이 주기마다 쌓입니다. 빨간 점은 다음 deadline 뒤에 끝난 iteration입니다.'],
    period: 12, rest: 5, H: 320, unit: 72, look: [2.1, 0, 1], oy: 25, cam: {yaw: .2, pitch: .35, dist: 8},
    controls: [
      {id: 'p', en: 'spike chance per iteration', ko: 'iteration당 spike 확률', min: 0, max: .1, step: .002, dec: 3, auto: t => .1 * (.5 - .5 * Math.cos(2 * Math.PI * t / 12))},
      {id: 'rel', toggle: true, en: 'sleep T after work (relative)', ko: '일 끝난 뒤 T 쉬기 (relative)', auto: t => t % 12 > 8.5},
    ],
  }, (s, t, m) => {
    const r = sim(s.v.p, s.v.rel);
    s.poly([[-.15, -.4, -.02], [N * DX, -.4, -.02], [N * DX, .4, -.02], [-.15, .4, -.02]], '--line', {a: .4});
    for (let i = 0; i < N; i++) {
      const x = i * DX, late = (r.s[i] - i * T) * 1000, h = Math.min(2.2, Math.max(.02, late));
      s.box([x, 0, .06], [.04, .1, .06], I, '--pf');
      if (i % 5 === 0) s.label([x, -.4, 0], `${i}`, '--mut', 13, 'center', 0, 16);
      s.line([x, .25, 0], [x, .25, h], late < .5 ? '--ok' : '--bad', 3);
      if (i < N - 1 && r.d[i] > (i + 1) * T) s.dot([x, 0, .3], '--bad', 5, {ring: true});
    }
    s.label([-.15, .25, .05], '0 ms', '--mut', 13, 'right', -6, 4); s.label([-.15, .25, 1], '1 ms', '--mut', 13, 'right', -6, 4);
    s.line([-.1, .25, 1], [N * DX, .25, 1], '--line', 1, {dash: [3, 4]});
    s.text(14, 24, m.t(`worst period error ${(r.worst * 1e6).toFixed(0)} µs`, `최대 주기 오차 ${(r.worst * 1e6).toFixed(0)} µs`), r.worst > 5e-4 ? '--bad' : '--ok', 15);
    s.text(14, 44, m.t(`missed deadlines ${r.miss} of ${N - 1}`, `놓친 deadline ${r.miss} / ${N - 1}`), r.miss ? '--bad' : '--ok', 15);
    s.text(466, 24, s.v.rel ? m.t('sleep T after work', '일 끝난 뒤 T 쉬기') : m.t('sleep until i × T', 'i × T까지 쉬기'), '--mut', 14, 'right');
  });
})();

// 05/04: NTP-style clock offset from one request/reply (lesson exchange() and estimate(); offset 0.123 s, d_back 0.01 s, forward delay is the slider).
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], OFF = .123, DB = .01, ZS = 25, XC = -1.5, XS = 1.5;
  window.MOTION.three('clock-offset-3d', {
    en: 'Two wall clocks exchange one request and reply; unequal travel times make the offset estimate wrong by half the difference',
    ko: '벽시계 두 개가 요청과 응답을 한 번 주고받습니다. 가는 시간과 오는 시간이 다르면 offset 추정이 그 차이의 절반만큼 틀립니다',
    cap: ['Height is true time (1 unit = 40 ms). The server clock runs 0.123 s ahead of the client, and the reply takes 0.01 s as in the lesson’s exchange(0.123, 0.03, 0.01). The estimate ((t1 − t0) + (t2 − t3)) / 2 assumes both trips take the same time, so it puts the server’s reading at the midpoint of the round trip (red ring); the real moment is the green dot. The gap is (forward − back) / 2 and the round-trip delay is forward + back. The slider is the forward delay, 0.03 s is the lesson’s value. The processing time is 0 as in the lesson.',
      '높이는 실제 시간입니다(1 단위 = 40 ms). 서버 시계는 client보다 0.123 s 앞서 있고, 응답에는 수업의 exchange(0.123, 0.03, 0.01)처럼 0.01 s가 걸립니다. 추정식 ((t1 − t0) + (t2 − t3)) / 2는 가는 시간과 오는 시간이 같다고 보고 서버가 읽힌 순간을 왕복의 한가운데(빨간 고리)에 놓습니다. 실제 순간은 초록 점입니다. 그 차이가 (forward − back) / 2이고 round-trip delay는 forward + back입니다. 슬라이더는 가는 시간이며 수업의 값은 0.03 s입니다. 처리 시간은 수업처럼 0입니다.'],
    period: 12, rest: 5, H: 340, unit: 64, look: [0, 0, 1.2], oy: 60, cam: {yaw: .45, pitch: .22, dist: 8},
    controls: [{id: 'df', en: 'forward delay', ko: '가는 시간', min: .01, max: .06, step: .005, dec: 3, unit: ' s', auto: t => .035 + .025 * Math.sin(2 * Math.PI * t / 12)}],
  }, (s, t, m) => {
    const df = s.v.df, t0 = 0, t1 = df + OFF, t2 = t1, t3 = df + DB;
    const est = ((t1 - t0) + (t2 - t3)) / 2, err = est - OFF, rtt = (t3 - t0) - (t2 - t1);
    const zTrue = df * ZS, zMid = (df + DB) / 2 * ZS, zEnd = (df + DB) * ZS;
    s.poly([[-2.4, -.8, -.02], [2.4, -.8, -.02], [2.4, .8, -.02], [-2.4, .8, -.02]], '--line', {a: .3});
    for (const [x, c, who] of [[XC, '--pf', m.t('client clock', 'client 시계')], [XS, '--pl', m.t('server clock', 'server 시계')]]) {
      s.box([x, 0, 1.1], [.04, .04, 1.1], I, '--line');
      s.box([x, 0, 2.6], [.4, .08, .4], I, c); s.dot([x, -.1, 2.6], '--card', 5);
      const a = (x === XS ? (zTrue / ZS + OFF) : 0) * 20; s.line([x, -.1, 2.6], [x + .3 * Math.sin(a), -.1, 2.6 + .3 * Math.cos(a)], '--fg', 2, {front: true});
      s.label([x, 0, 3.15], who, '--fg', 14, 'center');
    }
    s.arrow([XC, 0, 0], [XS, 0, zTrue], '--pf', 3, {front: true});
    s.arrow([XS, 0, zTrue], [XC, 0, zEnd], '--pl', 3, {front: true});
    s.dot([XC, 0, 0], '--fg', 5, {ring: true}); s.dot([XC, 0, zEnd], '--fg', 5, {ring: true});
    s.label([XC, 0, 0], 't0 0.000', '--mut', 13, 'right', -12, 4); s.label([XC, 0, zEnd], `t3 ${t3.toFixed(3)}`, '--mut', 13, 'right', -12, 4);
    s.label([XS, 0, zTrue], `t1 = t2 ${t1.toFixed(3)}`, '--mut', 13, 'left', 14, 4);
    s.dot([XS, 0, zTrue], '--ok', 7, {ring: true, front: true});
    s.dot([XS, 0, zMid], '--bad', 7, {ring: true, front: true}); s.line([XS, 0, zTrue], [XS, 0, zMid], '--bad', 3, {front: true});
    s.line([XC, 0, zMid], [XS, 0, zMid], '--bad', 1, {dash: [3, 4]});
    s.text(14, 24, m.t(`estimated offset ${est.toFixed(3)} s (true ${OFF})`, `추정 offset ${est.toFixed(3)} s (실제 ${OFF})`), '--fg', 15);
    s.text(14, 44, m.t(`error ${(err * 1000).toFixed(1)} ms`, `오차 ${(err * 1000).toFixed(1)} ms`), Math.abs(err) < 1e-9 ? '--ok' : '--bad', 15);
    s.text(14, 64, m.t(`round trip ${(rtt * 1000).toFixed(0)} ms`, `왕복 ${(rtt * 1000).toFixed(0)} ms`), '--mut', 15);
  });
})();

// 05/05: the fetch tree of the lesson, ticked six times (fetch_task() and run(): go object RUNNING x2, grasp FAILURE x2 then SUCCESS inside Retry(3), go bin RUNNING then SUCCESS, release).
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  // log of run(fetch_task()[0]) in lesson order, one entry per tick: [node, status]
  const LOG = [
    [['go object', 'running'], ['fetch', 'running']],
    [['go object', 'running'], ['fetch', 'running']],
    [['go object', 'success'], ['grasp', 'failure'], ['retry', 'running'], ['fetch', 'running']],
    [['grasp', 'failure'], ['retry', 'running'], ['fetch', 'running']],
    [['grasp', 'success'], ['retry', 'success'], ['go bin', 'running'], ['fetch', 'running']],
    [['go bin', 'success'], ['release', 'success'], ['fetch', 'success']],
  ];
  const X = [-1.47, -.73, 0, 0, 1.1, 2.2], NODES = [['fetch', 0], ['go object', 1], ['retry', 1], ['grasp', 2], ['go bin', 1], ['release', 1]];
  const COL = {success: '--ok', failure: '--bad', running: '--pl'};
  window.MOTION.three('behaviour-tree-fetch-3d', {
    en: 'A floor robot ticks a behaviour tree: it drives to the object, fails to grasp twice, retries, then carries it to the bin',
    ko: 'Floor robot이 behaviour tree를 tick합니다. 물건까지 가고, grasp에 두 번 실패하고, 재시도한 뒤 상자로 옮깁니다',
    cap: ['Step through the six ticks of the lesson’s fetch tree. Sequence runs its children in order and resumes the child that said RUNNING; Retry(3) turns the first two grasp FAILUREs into RUNNING and lets the third SUCCESS through. The status lines on the left are the real log of run(fetch_task()[0]); a node that is not listed was not ticked on that tick. Robot position per tick is a picture (one third of the way to the object per RUNNING tick), not a measured path.',
      '수업 fetch tree의 여섯 tick을 하나씩 따라갑니다. Sequence는 자식을 차례로 실행하고 RUNNING이라고 답한 자식에서 다시 시작합니다. Retry(3)는 grasp의 첫 두 FAILURE를 RUNNING으로 바꾸고 세 번째 SUCCESS는 통과시킵니다. 왼쪽 상태 줄은 run(fetch_task()[0])의 실제 log이며 목록에 없는 node는 그 tick에 실행되지 않은 것입니다. Tick마다의 robot 위치는 RUNNING 한 번에 물건까지의 3분의 1씩 가는 그림이며 측정한 경로가 아닙니다.'],
    period: 12, rest: 7, H: 360, unit: 76, look: [.15, 0, 0], oy: 100, cam: {yaw: .3, pitch: .5, dist: 8},
    controls: [{id: 'tick', en: 'tick', ko: 'tick', min: 1, max: 6, step: 1, auto: t => 1 + Math.floor(t / 2) % 6}],
  }, (s, t, m) => {
    const k = s.v.tick, log = LOG[k - 1], x = X[k - 1], carry = k === 5, inBin = k === 6;
    NODES.forEach(([name, depth], i) => {
      const e = log.find(q => q[0] === name), c = e ? COL[e[1]] : '--mut';
      s.text(14 + 14 * depth, 24 + 19 * i, name + '  ' + (e ? e[1] : m.t('(not ticked)', '(tick 안 됨)')), c, 14);
    });
    s.text(466, 24, m.t(`grasp tries: ${k < 3 ? 0 : Math.min(k - 2, 3)} of 3`, `grasp 시도: ${k < 3 ? 0 : Math.min(k - 2, 3)} / 3`), '--mut', 14, 'right');
    s.poly([[-2.6, -1.1, -.02], [2.9, -1.1, -.02], [2.9, 1.1, -.02], [-2.6, 1.1, -.02]], '--line', {a: .3});
    s.wire([2.2, 0, .1], [.3, .3, .1], I, '--fg', 2); s.poly([[1.9, -.3, 0], [2.5, -.3, 0], [2.5, .3, 0], [1.9, .3, 0]], '--pd', {a: .3});
    s.box([x, 0, .17], [.3, .25, .17], I, '--pl'); s.box([x, 0, .5], [.06, .06, .16], I, '--pd');
    const g = k === 3 || k === 4 ? .02 : .12;
    s.box([x - g, 0, .72], [.03, .05, .06], I, '--fg'); s.box([x + g, 0, .72], [.03, .05, .06], I, '--fg');
    s.box(inBin ? [2.2, 0, .1] : carry ? [x, 0, .55] : [0, 0, .1], [.1, .1, .1], I, '--bad');
    s.label([0, 0, -.02], m.t('object', '물건'), '--mut', 13, 'center', 0, 18); s.label([2.2, 0, -.02], m.t('bin', '상자'), '--mut', 13, 'center', 0, 18);
    if (k === 3 || k === 4) s.label([x, 0, 1], m.t('grasp failed, retry', 'grasp 실패, 재시도'), '--bad', 14, 'center');
  });
})();
