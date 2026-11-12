// Bolt: perspective Canvas toy with a shared visible-only clock.
(function () {
  'use strict';
  if (window.BOLT3D) return;
  const TAU = Math.PI * 2, clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const moods = ['idle', 'cheer', 'oops', 'sleepy', 'wave', 'think'];
  const valid = m => moods.includes(m) ? m : 'idle';
  const instances = new Map(), motion = matchMedia('(prefers-reduced-motion: reduce)');
  const dark = matchMedia('(prefers-color-scheme: dark)');
  let raf = 0, last = null;
  const canRun = s => s.visible && s.el.isConnected && !document.hidden;
  function pauseHold(s) {
    clearTimeout(s.timer); s.timer = 0;
    if (s.holdStart !== null) {s.age += Math.max(0, performance.now() - s.holdStart) / 1000;s.holdStart = null;}
  }
  function armHold(s) {
    if (motion.matches && s.hold && canRun(s)) {
      s.holdStart = performance.now();
      s.timer = setTimeout(() => {s.timer=0;s.holdStart=null;change(s,s.returnMood);}, Math.max(0, (s.hold-s.age)*1000));
    }
  }
  function schedule() {
    const running = !motion.matches && [...instances.values()].some(canRun);
    if (running && !raf) raf = requestAnimationFrame(frame);
    if (!running && raf) { cancelAnimationFrame(raf); raf = 0; last = null; }
  }
  function frame(now) {
    raf = 0;
    const dt = last === null ? 0 : clamp((now - last) / 1000, 0, .04);
    last = now;
    instances.forEach(s => {
      if (!s.el.isConnected) s.api.destroy();
      else if (canRun(s)) { step(s, dt); draw(s, false); }
    });
    schedule();
  }
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      const s = instances.get(e.target);
      if (!s) return;
      pauseHold(s);
      s.visible = e.isIntersecting;
      if (canRun(s)) { init(s); if (motion.matches) draw(s, true); }
      armHold(s);
      if (!s.visible) { s.skip = true; endDrag(s, true); }
    });
    schedule();
  }, {threshold: 0});
  function label(s) {
    const ko = document.documentElement.lang.startsWith('ko');
    s.el.setAttribute('aria-label', ko ? '작은 로봇 Bolt' : 'Bolt, a little robot');
  }
  function init(s) {
    if (s.canvas) return;
    const c = document.createElement('canvas');
    c.setAttribute('aria-hidden', 'true');
    c.style.width = '100%'; c.style.height = '100%'; c.style.display = 'block';
    s.canvas = c; s.ctx = c.getContext('2d');
    s.el.appendChild(c); resize(s);
  }
  function resize(s) {
    if (!s.canvas) return;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const n = Math.round(s.size * dpr);
    if (s.canvas.width !== n || s.canvas.height !== n) {
      s.canvas.width = s.canvas.height = n;
      s.ctx.setTransform(n, 0, 0, n, 0, 0);
    }
  }
  function change(s, mood, holdMs) {
    if (s.dead) return;
    pauseHold(s);
    const previous = s.mood;
    s.mood = valid(mood); s.age = 0;
    s.hold = Number.isFinite(holdMs) && holdMs > 0 ? holdMs / 1000 : 0;
    s.returnMood = previous;
    s.el.dataset.mood = s.mood;
    if (s.mood === 'cheer' && !motion.matches) s.hop = 0;
    if (motion.matches && canRun(s)) { init(s); draw(s, true); }
    armHold(s);
    schedule();
  }
  function step(s, dt) {
    if (s.skip) { dt = 0; s.skip = false; }
    s.time += dt; s.age += dt; s.hop += dt;
    if (s.hold && s.age >= s.hold) change(s, s.returnMood);
    if (s.time >= s.nextBlink) { s.blink = 0; s.nextBlink = s.time + 3 + Math.random() * 2; }
    s.blink += dt;
    // Substeps stabilize springs after late frames.
    for (let left = dt; left > 0; left -= .008) {
      const h = Math.min(.008, left);
      if (!s.drag || !s.drag.horizontal) {
        s.velocity += (-42 * s.yaw - 7.5 * s.velocity) * h;
        s.yaw = clamp(s.yaw + s.velocity * h, -.72, .72);
      }
      const target = -.12 * s.velocity + .035 * Math.sin(s.time * 2.2);
      s.antV += (65 * (target - s.ant) - 8 * s.antV) * h;
      s.ant += s.antV * h;
    }
    const f = 1 - Math.exp(-dt * 12);
    s.lookX += (s.targetX - s.lookX) * f; s.lookY += (s.targetY - s.lookY) * f;
    moods.forEach((m, i) => s.weights[i] += ((s.mood === m ? 1 : 0) - s.weights[i]) * f);
  }
  function endDrag(s, cancelled, e) {
    const d = s.drag;
    if (!d || (e && e.pointerId !== d.id)) return;
    s.drag = null;
    if (performance.now() - d.last > 100) s.velocity = 0;
    if (s.el.hasPointerCapture(d.id)) s.el.releasePointerCapture(d.id);
    window.removeEventListener('pointermove', s.move);
    window.removeEventListener('pointerup', s.up);
    window.removeEventListener('pointercancel', s.cancel);
    const moved = e && Math.hypot(e.clientX - d.x, e.clientY - d.y) > 6;
    if (!cancelled && !d.horizontal && !d.scrolled && !moved && !motion.matches) change(s, 'cheer', 1100);
  }
  function mount(el, opts = {}) {
    if (instances.has(el)) return instances.get(el).api;
    const requested = Number(opts.size || el.dataset.size || 88);
    const s = {el, size: Number.isFinite(requested) ? clamp(requested, 32, 512) : 88,
      mood: valid(opts.mood || el.dataset.mood), visible: false, dead: false,
      time: 0, age: 0, hop: 10, blink: 10, nextBlink: 3 + Math.random() * 2,
      yaw: 0, velocity: 0, ant: 0, antV: 0, lookX: 0, lookY: 0, targetX: 0, targetY: 0,
      hold: 0, timer: 0, holdStart: null, skip: true, weights: moods.map(m => +(m === valid(opts.mood || el.dataset.mood)))};
    const styles = ['width', 'height', 'display', 'flexShrink', 'touchAction'];
    const saved = styles.map(k => el.style[k]);
    const attrs = ['role', 'aria-label', 'data-mood'].map(k => [k, el.getAttribute(k)]);
    el.style.width = el.style.height = s.size + 'px';
    el.style.display = 'inline-block'; el.style.flexShrink = '0';
    el.setAttribute('role', 'img'); el.dataset.mood = s.mood; label(s);
    const interactive = opts.interactive === undefined ? el.dataset.interactive !== 'false' : !!opts.interactive;
    s.move = e => {
      const d = s.drag;
      if (!d || d.id !== e.pointerId) return;
      const dx = e.clientX - d.x, dy = e.clientY - d.y;
      if (!d.horizontal) {
        if (Math.abs(dy) > 6 && Math.abs(dy) >= Math.abs(dx)) { d.scrolled = true; endDrag(s, true, e); return; }
        if (Math.abs(dx) > 6 && Math.abs(dx) > Math.abs(dy) * 1.3) {
          d.horizontal = true; el.setPointerCapture(d.id);
        }
      }
      if (d.horizontal) {
        const y = clamp(d.yaw + dx / s.size * 1.6, -.72, .72);
        s.velocity = clamp((y - s.yaw) / Math.max(.016, (performance.now() - d.last) / 1000), -4, 4);
        s.yaw = y; d.last = performance.now();
      }
    };
    s.up = e => endDrag(s, false, e); s.cancel = e => endDrag(s, true, e);
    s.down = e => {
      if (s.drag || motion.matches || !canRun(s) || e.isPrimary === false || e.button !== 0) return;
      s.drag = {id: e.pointerId, x: e.clientX, y: e.clientY, yaw: s.yaw, last: performance.now()};
      window.addEventListener('pointermove', s.move, {passive: true});
      window.addEventListener('pointerup', s.up, {passive: true});
      window.addEventListener('pointercancel', s.cancel, {passive: true});
    };
    s.lost = e => endDrag(s, true, e);
    if (interactive) {
      el.style.touchAction = 'pan-y';
      el.addEventListener('pointerdown', s.down, {passive: true});
      el.addEventListener('lostpointercapture', s.lost);
    }
    s.interactive = interactive;
    s.api = {setMood: (name, holdMs) => change(s, name, holdMs), destroy() {
      if (s.dead) return;
      s.dead = true; pauseHold(s); endDrag(s, true); observer.unobserve(el); instances.delete(el);
      el.removeEventListener('pointerdown', s.down); el.removeEventListener('lostpointercapture', s.lost);
      if (s.canvas) s.canvas.remove();
      styles.forEach((k, i) => el.style[k] = saved[i]);
      attrs.forEach(([k, v]) => v === null ? el.removeAttribute(k) : el.setAttribute(k, v));
      schedule();
    }};
    instances.set(el, s); observer.observe(el);
    if (s.mood === 'cheer') s.hop = 0;
    return s.api;
  }

  // Y-up, +Z forward.
  function draw(s, rest) {
    if (!s.ctx) return;
    const c = s.ctx, w = rest ? moods.map(m => +(m === s.mood)) : s.weights;
    const [, cheer, oops, sleepy, wave, think] = w;
    const t = rest ? 0 : s.time, age = rest ? 2 : s.age;
    let hop = 0, squash = 1;
    const h = rest ? 10 : s.hop;
    if (h < .12) squash = 1 - .12 * Math.sin(h / .12 * Math.PI) ** 2;
    else if (h < .6) { const u = (h - .12) / .48; hop = .32 * Math.sin(Math.PI * u) ** 2; squash = 1 + .1 * Math.sin(TAU * u) * Math.sin(Math.PI * u); }
    else if (h < .9) {const d=h-.6;squash=1-.14*Math.exp(-d*10)*Math.sin(d*23)*(1-Math.exp(-d*25));}
    const breath = rest ? 0 : .012 * Math.sin(t * 2.1);
    const bob = rest ? 0 : .035 * Math.sin(t * (2.4 - 1.5 * sleepy));
    const lift = hop + bob, yaw = rest ? 0 : s.yaw;
    const tilt = .18 * think - .09 * sleepy;
    const shake = rest ? 0 : oops * .16 * Math.sin(age * 24) * Math.exp(-age * 3);
    const cy = Math.cos(yaw), sy = Math.sin(yaw), ct = Math.cos(tilt), st = Math.sin(tilt);
    const cp = .993, sp = .118;
    const project = (p, head = false, fixed = false) => {
      let [x, y, z] = p;
      if (head) {
        const a = x; x = x * Math.cos(shake) + z * Math.sin(shake); z = -a * Math.sin(shake) + z * Math.cos(shake);
        const b = x; x = x * ct - (y - .34) * st; y = b * st + (y - .34) * ct + .34;
      }
      if (!fixed) { x /= Math.sqrt(squash); y = (y + .8) * squash - .8 + lift; z /= Math.sqrt(squash); }
      const a = x; x = x * cy + z * sy; z = -a * sy + z * cy;
      const b = y; y = y * cp - z * sp; z = b * sp + z * cp;
      const k = 5 / (5 - z), scale = k / 3.45;
      return [.5 + x * scale, .56 - y * scale, z, scale];
    };
    const queue = []; let add = (z, paint) => queue.push({z, paint});
    const path = pts => { c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); };
    function poly(pts, fill, stroke, head = false, fixed = false) {
      const pp = pts.map(p => project(p, head, fixed));
      add(pp.reduce((v,p)=>v+p[2],0)/pp.length, () => {
        path(pp); c.fillStyle = fill; c.fill();
        if (stroke) { c.strokeStyle = stroke; c.lineWidth = .003; c.stroke(); }
      });
    }
    function volume(p, radii, colors, head = false, alpha = 0) {
      const a = project(p, head), axes = radii.map((r, i) => {
        const q = p.slice(); q[i] += r; const b = project(q, head); return [b[0] - a[0], b[1] - a[1]];
      });
      const xx = axes.reduce((v, b) => v + b[0] * b[0], 0), yy = axes.reduce((v, b) => v + b[1] * b[1], 0);
      const xy = axes.reduce((v, b) => v + b[0] * b[1], 0), d = Math.hypot(xx - yy, 2 * xy);
      const rx = Math.sqrt((xx + yy + d) / 2), ry = Math.sqrt(Math.max(.000001, (xx + yy - d) / 2));
      const angle = .5 * Math.atan2(2 * xy, xx - yy);
      add(a[2], () => {
        c.save(); c.translate(a[0], a[1]); c.rotate(angle); c.scale(rx, ry);
        const lx = -.34 * Math.cos(angle) - .46 * Math.sin(angle), ly = .34 * Math.sin(angle) - .46 * Math.cos(angle);
        if (alpha) {c.globalAlpha = alpha; c.fillStyle = colors;}
        else {
          const g = c.createRadialGradient(lx, ly, .06, lx*.2, ly*.2, 1.25);
          g.addColorStop(0, colors[0]); g.addColorStop(.48, colors[1]); g.addColorStop(1, colors[2]); c.fillStyle = g;
        }
        c.beginPath(); c.arc(0, 0, 1, 0, TAU); c.fill();
        if (!alpha) {
          c.strokeStyle = '#c5eff0'; c.lineWidth = .025; c.stroke();
          c.beginPath(); c.ellipse(lx, ly, .33, .13, -angle, 0, TAU); c.fillStyle = '#ffffff65'; c.fill();
        }
        c.restore();
      });
    }
    const shell = ['#ffffff', '#d8eef0', '#378799'], teal = ['#b0f1ec', '#41c8e6', '#176579'];
    const rose = ['#ffe0d7', '#ed9e9b', '#b95664'];
    c.clearRect(0, 0, 1, 1); resize(s);
    const night = (document.documentElement.dataset.theme || (dark.matches ? 'dark' : 'light')) === 'dark';
    const ground = project([0, -1.19, 0], false, true);
    c.save(); c.translate(ground[0], ground[1]); c.scale(.19 - hop * .06, .029 - hop * .01);
    const shadow = c.createRadialGradient(0, 0, 0, 0, 0, 1);
    shadow.addColorStop(0, night ? '#66b9ca40' : '#0e1a1f65'); shadow.addColorStop(1, night ? '#66b9ca00' : '#0e1a1f00');
    c.fillStyle = shadow; c.beginPath(); c.arc(0, 0, 1, 0, TAU); c.fill(); c.restore();
    volume([0, -.97, 0], [.43, .12, .36], teal);
    volume([0, -.56, 0], [.4, .36 + breath, .3], shell);
    volume([0, -.59, .29], [.12, .12, .035], teal);
    volume([0, -.21, 0], [.27, .045, .24], ['#b0f1ec','#227789','#124351']);
    [-1, 1].forEach(side => {
      const up = cheer * .66 + (side === -1 ? wave * (.48 + .08 * Math.sin(age * 9)) : think * .42);
      const x = side * (.49 + cheer * .09 + (side === -1 ? wave * .07 : -think * .05));
      const hand = [x, -.59 + up, .16 + .42 * cheer + think * (side === 1 ? .29 : 0)];
      volume([side * .4, -.4, 0], [.13, .15, .13], teal);
      const arm = [[side*.4,-.4,.04],hand].map(p=>project(p));
      add((arm[0][2]+arm[1][2])/2,()=>{c.beginPath();c.moveTo(...arm[0].slice(0,2));c.lineTo(...arm[1].slice(0,2));c.strokeStyle='#227789';c.lineWidth=.055;c.lineCap='round';c.stroke();});
      volume(hand, [.16, .21, .17], shell);
      volume([x - side * .1, -.56 + up, hand[2]+.09], [.075, .1, .075], shell);
    });
    volume([0, .34, 0], [.83, .6, .54], shell, true);
    const surface = (x, y, bump = 0) => [x, y + .34, .54 * Math.sqrt(Math.max(.05, 1 - (x / .83) ** 2 - (y / .6) ** 2)) + bump];
    const rounded = (x, y, ww, hh, r, bump) => {
      const out = [];
      [[x+ww-r,y+r,-Math.PI/2],[x+ww-r,y+hh-r,0],[x+r,y+hh-r,Math.PI/2],[x+r,y+r,Math.PI]].forEach(([cx,cy,a]) => {
        for (let j=0;j<=4;j++) {const ang=a+j*Math.PI/8;out.push([cx+r*Math.cos(ang),cy+r*Math.sin(ang)]);}
      }); return out.flatMap((p,i)=>{const q=out[(i+1)%out.length],n=Math.ceil(Math.hypot(q[0]-p[0],q[1]-p[1])/.06);
        return Array.from({length:n},(_,j)=>surface(p[0]+(q[0]-p[0])*j/n,p[1]+(q[1]-p[1])*j/n,bump));});
    };
    const glass = c.createLinearGradient(.3, .3, .7, .6);
    glass.addColorStop(0, '#365565'); glass.addColorStop(.4, '#0e1a1f'); glass.addColorStop(1, '#08151d');
    [-1, 1].forEach(side => volume(surface(side * .57, -.33, .045), [.1, .045, .04], rose, true));
    // One clipped face layer keeps LEDs above glass.
    const visor=rounded(-.65,-.32,1.3,.7,.22,-.02), face=[], enqueue=add;
    add=(z,paint)=>face.push(paint);
    poly(visor, glass, '#78c5d3', true);
    poly(rounded(-.49, .2, .7, .05, .025, .044), '#e6ffff35', null, true);
    const closed = rest ? 0 : s.blink < .16 ? Math.sin(s.blink / .16 * Math.PI) ** 2 : 0;
    const faceMood = moods[w.indexOf(Math.max(...w))];
    function faceLine(points, width = .035, color = '#8ff8ed') {
      const pp = points.map(([x, y]) => project(surface(x, y, .055), true));
      add(0, () => {
        c.beginPath(); pp.forEach((p,i)=>i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]));
        c.lineWidth = Math.max(width / 3.45, 1.1 / s.size); c.lineCap = 'round'; c.lineJoin = 'round'; c.strokeStyle = color; c.stroke();
      });
    }
    [-1, 1].forEach(side => {
      const x = side * .275 + (rest ? 0 : s.lookX * .055), y = .025 + (rest ? 0 : s.lookY * .035);
      if (faceMood === 'oops') {
        const spiral=[];for(let i=0;i<25;i++){const a=i/24*TAU*1.7,r=.006+i/24*.105;spiral.push([x+Math.cos(a)*r,y+Math.sin(a)*r]);}
        faceLine(spiral, .026);
      } else if (faceMood === 'cheer') faceLine([[x-.105,y-.035],[x,y+.085],[x+.105,y-.035]], .045);
      else {
        const lid = sleepy * .68 + closed * (1 - sleepy * .68);
        poly(rounded(x-.085, y-.13, .17, Math.max(.018,.27*(1-lid)), .008+ .055*(1-lid), .055), '#8ff8ed', null, true);
        if (lid < .5) poly(rounded(x-.045,y+.035,.035,.065,.014,.065),'#eaffff',null,true);
      }
    });
    faceLine([[-.08,-.21],[0,-.23],[.08,-.21]], .022, '#41c8e6');
    add=enqueue;
    add(project([0,.34,.54],true)[2],()=>{c.save();path(visor.map(p=>project(p,true)));c.clip();face.forEach(paint=>paint());c.restore();});
    const ax = rest ? 0 : s.ant;
    const stem = [[0,.89,-.03],[ax*.5,1.02,-.03],[ax,1.16,-.03]];
    const pp = stem.map(p => project(p,true));
    add(pp[1][2],()=>{c.beginPath();pp.forEach((p,i)=>i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]));c.lineWidth=.017;c.strokeStyle='#227789';c.lineCap='round';c.stroke();});
    const bulb = [[ax+.02,1.39,.1],[ax-.09,1.22,.1],[ax-.015,1.22,.1],[ax-.04,1.08,.1],[ax+.1,1.27,.1],[ax+.025,1.27,.1]];
    const back = bulb.map(([x,y])=>[x,y,-.055]), glow=project([ax,1.23,0],true);
    add(glow[2]-.1,()=>{const g=c.createRadialGradient(glow[0],glow[1],0,glow[0],glow[1],.075);
      g.addColorStop(0,'#ffcc7066');g.addColorStop(1,'#ffcc7000');c.fillStyle=g;c.beginPath();c.arc(glow[0],glow[1],.075,0,TAU);c.fill();});
    poly(back,'#d58124',null,true);
    bulb.forEach((p,i)=>{const j=(i+1)%bulb.length;poly([p,back[i],back[j],bulb[j]],'#d9943e',null,true);});
    poly(bulb,'#ffdd86','#fff6c4',true);
    function glyph(text, p, alpha, size, color) {
      const q=project(p);add(q[2]+.5,()=>{c.globalAlpha=alpha;c.font=`600 ${Math.max(size/3.45,8/s.size)}px ui-sans-serif,system-ui,sans-serif`;c.textAlign='center';c.textBaseline='middle';c.fillStyle=color;c.fillText(text,q[0],q[1]);c.globalAlpha=1;});
    }
    if (sleepy > .01) for(let i=0;i<2;i++){const u=rest?.35:((t*.25+i*.5)%1);glyph('z',[.72+u*.12,.65+u*.65,.1],Math.max(.7,sleepy*(1-u)),.2,night?'#78d8e4':'#27768a');}
    if (think > .01) for(let i=0;i<3;i++) {const r=.03+.012*(.5+.5*Math.sin(t*4-i));volume([.78+i*.12,.99+Math.sin(i)*.08,0],[r,r,r],teal,true);}
    if (cheer > .01 && age < .8) for(let i=0;i<4;i++) {
      const a=i*Math.PI/3, u=age/.8;
      glyph('+',[1.32*Math.cos(a),.34+.82*Math.sin(a),.1],cheer*(1-u),.18,'#e6a33f');
    }
    if (oops > .01 && age < 1.4) {
      const u=age/1.4;
      for(let i=0;i<3;i++){const r=.065+u*.06+i*.018;
        volume([.65+u*.1+i*.04,.99+u*.3+i*.09,-.05],[r,r*.8,r],'#a5bbc4',true,oops*(1-u)*(.5-i*.1));}
    }
    queue.sort((a,b)=>a.z-b.z).forEach(item=>item.paint());
  }

  function refresh() {
    instances.forEach(s => {pauseHold(s);label(s); if(canRun(s)) {init(s);resize(s);if(motion.matches)draw(s,true);} armHold(s);s.skip=true;});
    schedule();
  }
  document.addEventListener('visibilitychange', () => {
    instances.forEach(s => {s.skip=true;if(document.hidden)endDrag(s,true);});refresh();
  });
  motion.addEventListener('change', () => {
    last=null;instances.forEach(s=>{endDrag(s,true);s.yaw=s.velocity=s.ant=s.antV=0;});refresh();
  });
  dark.addEventListener('change', refresh);
  window.addEventListener('resize', refresh, {passive:true});
  window.addEventListener('pointermove', e => {
    if(motion.matches)return;
    instances.forEach(s=>{if(!s.interactive||!canRun(s))return;const r=s.el.getBoundingClientRect();
      s.targetX=clamp((e.clientX-r.left-r.width/2)/Math.max(1,r.width),-1,1);
      s.targetY=clamp(-(e.clientY-r.top-r.height/2)/Math.max(1,r.height),-1,1);
    });
  }, {passive:true});
  function scan(root) {
    if(root.matches && root.matches('[data-bolt3d]'))mount(root);
    root.querySelectorAll('[data-bolt3d]').forEach(el=>mount(el));
  }
  const mutations = new MutationObserver(records => {
    records.forEach(r=>{
      if(r.type==='childList')r.addedNodes.forEach(n=>{if(n.querySelectorAll)scan(n);});
      else if(r.target===document.documentElement)refresh();
      else {const s=instances.get(r.target);if(s&&s.el.dataset.mood!==s.mood)change(s,s.el.dataset.mood);}
    });
    instances.forEach(s=>{if(!s.el.isConnected)s.api.destroy();});
  });
  function boot() {
    scan(document);
    mutations.observe(document.documentElement,{childList:true,subtree:true,attributes:true,attributeFilter:['data-mood','lang','data-theme']});
  }
  window.BOLT3D = {mount};
  if(document.readyState==='loading')window.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
