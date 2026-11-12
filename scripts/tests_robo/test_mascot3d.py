# Bolt의 standalone API와 lifecycle을 실제 JS 실행으로 검증한다.
import json
from pathlib import Path
import re
import runpy
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts/mascot3d.js"
MOODS = ("idle", "cheer", "oops", "sleepy", "wave", "think")

# Command recorder only: this is not pixel rendering or a performance benchmark.
HARNESS = r"""
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
let clock=0,frames=0,next=0,raf=new Map(),timers=new Map(),ios=[],mos=[],calls=[],paints=[];
const listeners=new Map();
function events(o){o.addEventListener=(n,f)=>{if(!listeners.has(o))listeners.set(o,{});(listeners.get(o)[n]??=new Set()).add(f)};
o.removeEventListener=(n,f)=>listeners.get(o)?.[n]?.delete(f);
o.emit=(n,e={})=>[...(listeners.get(o)?.[n]||[])].forEach(f=>f(e));return o}
let pen=[],clips=[],matrix=[1,0,0,1,0,0],stack=[];
const ctx=new Proxy({globalAlpha:1}, {get:(o,k)=>o[k]??((...a)=>{
 if(k==='clearRect')frames++;calls.push([k,...a]);
 for(const x of a)if(typeof x==='number')assert(Number.isFinite(x),k);
 if(k.startsWith('create'))return {stops:[],addColorStop(...stop){this.stops.push(stop)}};
 if(k==='save')stack.push([{...o},matrix.slice(),clips.slice()]);
 if(k==='restore'){const [props,m,c]=stack.pop();for(const key of Object.keys(o))delete o[key];Object.assign(o,props);matrix=m;clips=c}
 if(k==='translate'){matrix[4]+=matrix[0]*a[0]+matrix[2]*a[1];matrix[5]+=matrix[1]*a[0]+matrix[3]*a[1]}
 if(k==='scale'){matrix[0]*=a[0];matrix[1]*=a[0];matrix[2]*=a[1];matrix[3]*=a[1]}
 if(k==='rotate'){const [x,y,u,v]=matrix,c=Math.cos(a[0]),s=Math.sin(a[0]);matrix.splice(0,4,x*c+u*s,y*c+v*s,u*c-x*s,v*c-y*s)}
 if(k==='beginPath')pen=[];
 if(['moveTo','lineTo','arc','ellipse','closePath'].includes(k))pen.push([k,...a]);
 if(k==='clip')clips.push(pen.slice());
 if(['fill','stroke','fillText'].includes(k))paints.push({kind:k,args:a,path:pen.slice(),clips:clips.slice(),matrix:matrix.slice(),...o});
}),set:(o,k,v)=>(o[k]=v,true)});
class El {constructor(tag='span'){events(this);this.tagName=tag.toUpperCase();this.attrs={};this.style={};this.children=[];this.isConnected=true;this.captured=0;
 this.dataset=new Proxy({}, {set:(o,k,v)=>{o[k]=String(v);this.attrs['data-'+k.replace(/[A-Z]/g,x=>'-'+x.toLowerCase())]=String(v);return true}})}
 setAttribute(k,v){this.attrs[k]=String(v);if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v}
 getAttribute(k){return this.attrs[k]??null} removeAttribute(k){delete this.attrs[k]}
 appendChild(e){this.children.push(e);e.parentNode=this;return e} append(e){return this.appendChild(e)}
 remove(){this.isConnected=false;if(this.parentNode)this.parentNode.children=this.parentNode.children.filter(e=>e!==this)}
 getContext(){return ctx} getBoundingClientRect(){return {left:0,top:0,width:88,height:88}}
 querySelectorAll(){return []} matches(s){return s==='[data-bolt3d]'&&this.getAttribute('data-bolt3d')!==null}
 setPointerCapture(){this.captured++} releasePointerCapture(){} hasPointerCapture(){return this.captured>0}
}
const root=new El('html');root.lang='en';
const doc=events({documentElement:root,readyState:'complete',hidden:false,createElement:t=>new El(t),querySelectorAll:()=>[],contains:e=>e.isConnected});
const media=events({matches:REDUCED});
const darkMedia=events({matches:false});
const win=events({devicePixelRatio:3});Object.assign(win,{document:doc});
Object.assign(global,{window:win,document:doc,performance:{now:()=>clock},matchMedia:q=>q.includes('reduced-motion')?media:darkMedia,
 requestAnimationFrame:f=>{raf.set(++next,f);return next},cancelAnimationFrame:id=>raf.delete(id),
 setTimeout:(f,ms)=>{timers.set(++next,{f,at:clock+ms});return next},clearTimeout:id=>timers.delete(id),
 IntersectionObserver:class{constructor(cb){this.cb=cb;this.targets=new Set();ios.push(this)}observe(e){this.targets.add(e)}unobserve(e){this.targets.delete(e)}},
 MutationObserver:class{constructor(cb){this.cb=cb;mos.push(this)}observe(){}disconnect(){}}});
win.matchMedia=matchMedia;win.requestAnimationFrame=requestAnimationFrame;win.cancelAnimationFrame=cancelAnimationFrame;
Math.random=()=>.5;
// Expose the real draw function only inside this VM; production has no test API.
vm.runInThisContext(fs.readFileSync('scripts/mascot3d.js','utf8').replace('window.BOLT3D = {mount};',
 'window.__bolt={instances,draw};window.BOLT3D = {mount};'));
function enter(el,on=true){ios.forEach(io=>{if(io.targets.has(el))io.cb([{target:el,isIntersecting:on,intersectionRatio:on?1:0}])})}
function mutate(el,attributeName){mos.forEach(m=>m.cb([{type:'attributes',target:el,attributeName}]))}
function tick(ms=16){clock+=ms;for(const [id,v] of [...timers])if(v.at<=clock){timers.delete(id);v.f()}
const work=[...raf.values()];raf.clear();work.forEach(f=>f(clock))}
function run(ms){for(let n=0;n<ms;n+=16)tick(Math.min(16,ms-n))}
function mount(opts={}){const el=new El();const api=win.BOLT3D.mount(el,opts);return {el,api}}
function fixture(opts={}){const item=mount(opts);enter(item.el);const s=win.__bolt.instances.get(item.el);
 return {...item,s,shot(pose={}){Object.assign(s,pose);calls=[];paints=[];win.__bolt.draw(s,media.matches);return paints}}}
const color=(p,c)=>p.fillStyle===c||p.fillStyle?.stops?.some(s=>s[1]===c);
const polygon=p=>p.path.filter(c=>c[0]==='moveTo'||c[0]==='lineTo').map(c=>c.slice(1));
function inside(p,poly){let hit=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){
 const [x,y]=poly[i],[u,v]=poly[j];if((y>p[1])!==(v>p[1])&&p[0]<(u-x)*(p[1]-y)/(v-y)+x)hit=!hit}return hit}
"""


def js(body, reduced=False):
    assert SOURCE.exists(), "standalone mascot renderer is missing"
    result = subprocess.run(
        ["node", "-e", HARNESS.replace("REDUCED", str(reduced).lower()) + body],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_syntax_budget_and_offline():
    assert SOURCE.exists()
    subprocess.run(["node", "--check", str(SOURCE)], check=True, capture_output=True)
    code = SOURCE.read_text()
    assert SOURCE.stat().st_size < 20_000
    assert not re.search(r"https?://|fetch\s*\(|XMLHttpRequest|\bimport\s|require\s*\(", code)


def test_lazy_api_and_shared_loop_cleanup():
    js(r"""
const a=mount(),b=mount({size:220});
assert.deepEqual(Object.keys(a.api).sort(),['destroy','setMood']);
assert.equal(win.BOLT3D.mount(a.el),a.api);assert.equal(a.el.children.length,0);assert.equal(raf.size,0);
enter(a.el);enter(b.el);assert.equal(a.el.children.length,1);assert.equal(b.el.children.length,1);
assert.equal(a.el.children[0].width,176);assert.equal(b.el.children[0].width,440);
assert.equal(raf.size,1);run(100);assert(frames>0);
enter(a.el,false);enter(b.el,false);const n=frames;run(100);assert.equal(frames,n);assert.equal(raf.size,0);
enter(a.el);doc.hidden=true;doc.emit('visibilitychange');assert.equal(raf.size,0);
doc.hidden=false;doc.emit('visibilitychange');assert.equal(raf.size,1);
a.api.destroy();b.api.destroy();a.api.destroy();assert.equal(raf.size,0);assert.equal(a.el.children.length,0);
for(const target of [a.el,b.el])for(const set of Object.values(listeners.get(target)||{}))assert.equal(set.size,0);
""")


@pytest.mark.parametrize("mood", MOODS)
def test_moods_hold_and_data_contract(mood):
    js(r"""
const {el,api}=mount();enter(el);run(16);
api.setMood(MOOD,100);assert.equal(el.dataset.mood,MOOD);run(48);
enter(el,false);run(500);assert.equal(el.dataset.mood,MOOD);
enter(el);run(160);assert.equal(el.dataset.mood,'idle');
el.dataset.mood=MOOD;mutate(el,'data-mood');run(260);
api.setMood('not-a-mood');assert.equal(el.dataset.mood,'idle');api.destroy();
""".replace("MOOD", json.dumps(mood)))


def test_reduced_motion_draws_once_and_never_hops():
    js(r"""
const {el,api}=mount({mood:'cheer'});assert.equal(frames,0);enter(el);assert.equal(frames,1);assert.equal(raf.size,0);
run(5000);assert.equal(frames,1);
el.emit('pointerdown',{pointerId:1,clientX:40,clientY:40,button:0,isPrimary:true});
win.emit('pointerup',{pointerId:1,clientX:40,clientY:40});run(1000);assert.equal(frames,1);assert.equal(raf.size,0);
api.setMood('sleepy');assert.equal(frames,2);assert.equal(raf.size,0);api.destroy();
""", reduced=True)


def test_reduced_motion_hold_pauses_and_is_cancelled_on_destroy():
    js(r"""
const {el,api}=mount();enter(el);api.setMood('cheer',100);assert.equal(timers.size,1);
run(40);enter(el,false);assert.equal(timers.size,0);run(500);assert.equal(el.dataset.mood,'cheer');
enter(el);run(80);assert.equal(el.dataset.mood,'idle');assert.equal(raf.size,0);
api.setMood('wave',100);api.setMood('think',200);run(120);assert.equal(el.dataset.mood,'think');
api.destroy();assert.equal(timers.size,0);run(500);assert.equal(el.children.length,0);
""", reduced=True)


@pytest.mark.parametrize("size", [88, 220])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_each_mood_changes_real_drawing_commands_and_rest_is_stable(size, theme):
    js(r"""
const shapes=[];
root.dataset.theme=THEME;
for(const mood of ['idle','cheer','oops','sleepy','wave','think']){
 const geometry=()=>JSON.stringify(paints.map(p=>[p.kind,p.path,p.matrix,p.clips,p.globalAlpha,
  p.kind==='stroke'?[p.strokeStyle,p.lineWidth]:[p.fillStyle,p.kind==='fillText'?[p.font,p.args]:null]]));
 const {el,api}=mount({mood,size:SIZE});calls=[];paints=[];enter(el);const pose=geometry();shapes.push(pose);
 // A discrete repaint in rest mode must produce identical geometry at any time.
 run(5000);calls=[];paints=[];mutate(root,'data-theme');assert(geometry()===pose,'rest geometry changed for '+mood);api.destroy();
}
assert.equal(new Set(shapes).size,6);
""".replace("THEME", json.dumps(theme)).replace("SIZE", str(size)), reduced=True)


def test_hop_projection_is_continuous_at_anticipation_and_landing():
    js(r"""
// Compare the projected pad, independently of facial changes or secondary parts.
function padAt(t){const {el,api}=mount({mood:'cheer'});enter(el);tick(0);run(t-0.1);
 calls=[];tick(.1);const positions=calls.filter(c=>c[0]==='translate').slice(1,5);api.destroy();return positions}
for(const boundary of [120,600]){
 const a=padAt(boundary-.05),b=padAt(boundary+.05);
 for(let i=0;i<a.length;i++)assert(Math.hypot(a[i][1]-b[i][1],a[i][2]-b[i][2])<.001);
}
""")


def test_language_resize_and_live_motion_preference():
    js(r"""
const {el,api}=mount();enter(el);assert.equal(el.getAttribute('role'),'img');assert(!el.getAttribute('tabindex'));
assert(el.getAttribute('aria-label').includes('Bolt'));
root.lang='ko';mutate(root,'lang');assert(/[가-힣]/.test(el.getAttribute('aria-label')));
media.matches=true;media.emit('change');assert.equal(raf.size,0);const n=frames;run(1000);assert.equal(frames,n);
media.matches=false;media.emit('change');assert.equal(raf.size,1);api.destroy();
""")


def test_touch_scroll_horizontal_capture_and_cancel():
    js(r"""
const {el,api}=mount();enter(el);assert.equal(el.style.touchAction,'pan-y');
const down=(x,y)=>el.emit('pointerdown',{pointerId:1,clientX:x,clientY:y,button:0,isPrimary:true,pointerType:'touch'});
const move=(x,y)=>win.emit('pointermove',{pointerId:1,clientX:x,clientY:y});
down(40,40);move(42,70);assert.equal(el.captured,0);win.emit('pointerup',{pointerId:1,clientX:42,clientY:70});assert.equal(el.dataset.mood,'idle');
down(40,40);move(65,42);assert.equal(el.captured,1);win.emit('pointercancel',{pointerId:1});assert.equal(el.dataset.mood,'idle');
down(40,40);win.emit('pointerup',{pointerId:1,clientX:40,clientY:40});assert.equal(el.dataset.mood,'cheer');api.destroy();
""")


@pytest.mark.parametrize("degrees", [-30, 30, 40])
def test_visor_contour_stays_inside_rendered_shell_silhouette(degrees):
    js(r"""
const f=fixture(),p=f.shot({yaw:DEGREES*Math.PI/180});
const area=p=>Math.abs(p.matrix[0]*p.matrix[3]-p.matrix[1]*p.matrix[2]);
// The head is the largest white volume; use its actual Canvas ellipse transform.
const shell=p.filter(p=>p.kind==='fill'&&color(p,'#d8eef0')).sort((a,b)=>area(b)-area(a))[0];
assert(shell&&area(shell)>0,'rendered shell is missing');
const visor=polygon(p.find(p=>p.kind==='fill'&&color(p,'#08151d')));
assert(visor.length>40,'visor contour is missing');
const [a,b,c,d,x,y]=shell.matrix,det=a*d-b*c;
// Invert the ellipse transform: every contour vertex must lie in the unit disk.
// The disk is convex, so this also contains every straight contour segment.
for(const [vx,vy] of visor){
 const dx=vx-x,dy=vy-y,u=(d*dx-c*dy)/det,v=(a*dy-b*dx)/det;
 assert(u*u+v*v<=1+1e-10,`visor outside shell at DEGREESdeg: ${u*u+v*v}`);
}
f.api.destroy();
""".replace("DEGREES", str(degrees)))


def test_visor_is_one_clipped_composite_with_curved_edges():
    js(r"""
const f=fixture();
for(const degrees of [-41,-40,-30,0,30,40,41]){
 const p=f.shot({yaw:degrees*Math.PI/180}),glass=p.findIndex(p=>color(p,'#08151d'));
 const leds=p.map((p,i)=>({p,i})).filter(({p})=>p.kind==='fill'&&p.fillStyle==='#8ff8ed');
 assert.equal(leds.length,2);assert(glass>=0);
 const edge=polygon(p[glass]);assert(edge.length>40,'long visor edges need surface samples');
 for(const {p:eye,i} of leds){
  assert(i>glass,'glass covered a LED');assert.equal(eye.clips.length,1,'LED escaped visor composite');
  assert.deepEqual(polygon({path:eye.clips[0]}),edge);
  for(const point of polygon(eye))assert(inside(point,edge),'far eye cut by visor');
 }
 const highlights=p.filter(p=>p.kind==='fill'&&p.fillStyle==='#eaffff');
 assert.equal(highlights.length,2);assert(highlights.every(p=>p.clips.length===1));
 const first=leds[0].i,last=p.findLastIndex(p=>p.fillStyle==='#eaffff');
 assert(p.slice(first,last+1).every(p=>p.clips.length===1),'foreign depth-sorted part split LEDs');
}
f.api.destroy();
""")


def test_cheer_mittens_move_in_front_and_have_shoulder_connectors():
    js(r"""
const f=fixture({mood:'cheer'}),p=f.shot();
const cheeks=p.map((p,i)=>({p,i})).filter(({p})=>p.kind==='fill'&&color(p,'#ed9e9b'));
const q=5/(5-(.07*.118+.58*.993))/3.45;
for(const side of [-1,1]){
 const expected=[.5+side*.58*q,.56-(.07*.993-.58*.118)*q];
 const hand=p.findIndex(p=>p.kind==='fill'&&color(p,'#d8eef0')&&Math.hypot(p.matrix[4]-expected[0],p.matrix[5]-expected[1])<1e-7);
 assert(hand>=0,'cheer mitten did not advance by .42');
 assert(cheeks.every(({i})=>hand>i),'cheek painted over raised mitten');
 const connector=p.findIndex(p=>p.kind==='stroke'&&p.strokeStyle==='#227789'&&polygon(p).length===2&&
  Math.hypot(...polygon(p)[1].map((v,i)=>v-expected[i]))<1e-7);
 assert(connector>=0&&connector<hand,'shoulder-to-mitten connector absent or covers hand');
}
f.api.destroy();
""")


def test_cheer_sparks_clear_face_and_canvas_across_turn_and_burst():
    js(r"""
let minEdge=1,minFace=1,samples=0;
for(const size of [88,220]){
 const f=fixture({mood:'cheer',size});
 // Full yaw range, burst lifetime, and actual hop timeline; retain full spark size.
 for(let deg=-41;deg<=41;deg+=.5)for(let ms=0;ms<800;ms+=16){
  const t=ms/1000,p=f.shot({yaw:deg*Math.PI/180,age:t,hop:t,time:t});
  const sparks=p.filter(p=>p.kind==='fillText'&&p.args[0]==='+');
  assert.equal(sparks.length,4,'use four upper anchors');
  const face=polygon(p.find(p=>p.kind==='fill'&&color(p,'#08151d')));
  // Enclose the visor and mouth in a conservative AABB, expanded by the full glyph em box.
  const xs=face.map(p=>p[0]),ys=face.map(p=>p[1]);
  for(const spark of sparks){
   const [_,x,y]=spark.args,font=parseFloat(spark.font.split(' ')[1]);
   assert(font*size>=8-1e-8);assert(font>=.18/3.45);
   const r=font*.6,edge=Math.min(x-r,1-x-r,y-r,1-y-r);minEdge=Math.min(minEdge,edge);
   assert(edge>=0,`spark outside ${size}px canvas at ${deg}deg / ${ms}ms`);
   const gap=Math.max(Math.min(...xs)-x-r,x-r-Math.max(...xs),Math.min(...ys)-y-r,y-r-Math.max(...ys));
   minFace=Math.min(minFace,gap);assert(gap>0,`spark crossed face at ${deg}deg / ${ms}ms`);samples++;
  }
 }
 f.api.destroy();
}
console.log(JSON.stringify({samples,minEdge,minFace}));
""")


def test_dark_contact_halo_stays_grounded_and_narrows_with_hop():
    js(r"""
const f=fixture({mood:'cheer'});
for(const theme of ['light','dark']){
 root.dataset.theme=theme;
 const a=f.shot({hop:0})[0],b=f.shot({hop:.36})[0];
 assert.deepEqual(a.fillStyle.stops,[[0,theme==='dark'?'#66b9ca40':'#0e1a1f65'],[1,theme==='dark'?'#66b9ca00':'#0e1a1f00']]);
 assert.deepEqual(a.matrix.slice(4),b.matrix.slice(4),'shadow moved with toy');
 assert(b.matrix[0]<a.matrix[0]&&b.matrix[3]<a.matrix[3]);
}
delete root.dataset.theme;darkMedia.matches=true;
assert(color(f.shot()[0],'#66b9ca40'),'system dark preference ignored');f.api.destroy();
""")


def test_small_face_strokes_and_sleepy_glyphs_have_css_pixel_floors():
    js(r"""
for(const size of [88,220])for(const theme of ['light','dark']){
 root.dataset.theme=theme;
 for(const mood of ['idle','oops','sleepy']){
  const f=fixture({size,mood});
  for(const t of [0,.5,1,1.99,3.9]){
   const p=f.shot({time:t});
   const strokes=p.filter(p=>p.kind==='stroke'&&['#8ff8ed','#41c8e6'].includes(p.strokeStyle));
   assert(strokes.length);assert(strokes.every(p=>p.lineWidth*size>=1.1-1e-8),'subpixel face stroke');
   if(mood==='sleepy'){
    const z=p.filter(p=>p.kind==='fillText'&&p.args[0]==='z');assert.equal(z.length,2);
    assert(z.every(p=>parseFloat(p.font.split(' ')[1])*size>=8-1e-8&&p.globalAlpha>=.7));
    assert(z.every(p=>p.fillStyle===(theme==='dark'?'#78d8e4':'#27768a')));
   }
  }f.api.destroy();
 }
}
""")


def test_oops_smoke_is_three_overlapping_matte_fading_puffs():
    js(r"""
const f=fixture({mood:'oops'});
function smoke(t){const p=f.shot({age:t,time:t});return p.filter(p=>p.kind==='fill'&&p.fillStyle==='#a5bbc4')}
const early=smoke(.24),late=smoke(1.1);assert.equal(early.length,3);assert.equal(late.length,3);
for(let i=0;i<3;i++){
 const a=early[i],b=late[i],radius=p=>Math.hypot(p.matrix[0],p.matrix[1]);
 assert(a.globalAlpha>0&&a.globalAlpha<1);assert(b.globalAlpha<a.globalAlpha,'puff must fade with age');
 assert(b.matrix[5]<a.matrix[5]&&radius(b)>radius(a),'puff must rise and expand');
 if(i){assert(radius(a)>radius(early[i-1]));assert(a.globalAlpha<early[i-1].globalAlpha);
  assert(Math.hypot(a.matrix[4]-early[i-1].matrix[4],a.matrix[5]-early[i-1].matrix[5])<radius(a)+radius(early[i-1]),'puffs disconnected')}
}
const p=f.shot({age:.24});
for(const puff of p.filter(p=>p.kind==='fill'&&p.fillStyle==='#a5bbc4')){
 const siblings=p.filter(p=>JSON.stringify(p.matrix)===JSON.stringify(puff.matrix));
 assert.equal(siblings.length,1,'matte puff has rim or specular drawing');
}
assert.equal(smoke(1.4).length,0);f.api.destroy();
""")


@pytest.fixture(scope="module")
def builder():
    # Import only; never rebuild the checkout's site/ from a regression test.
    return runpy.run_path(str(ROOT / "scripts/build_site.py"))


def test_builder_mounts_and_selective_inline(builder):
    phases = builder["load_lessons"]()
    index = builder["index"](phases)
    assert 'id="hbolt"' in index and 'data-bolt3d' in index
    assert '<script data-bolt3d-source>' in index
    assert 'src="mascot3d.js"' not in index
    plain = builder["shell"]("Plain", "<p>No mascot</p>", phases)
    assert 'data-bolt3d-source' not in plain
    fun = {"en": {"hook": "Hello", "mission": "Try it"}, "ko": {"hook": "안녕", "mission": "해 보기"}}
    hook = builder["fun_html"](fun, "00-01-example")[0]
    assert 'data-bolt3d' in hook and 'data-size="88"' in hook
    assert 'data-bolt3d' in builder["JS"] and 'brandbolt' in builder["HEADER"]
    single = (ROOT / "scripts/build_single.py").read_text()
    assert 'data-bolt3d-source' in single and 'mountBolts(el)' in single and 'disposeBolts(sec)' in single


@pytest.mark.parametrize("lang", ["en", "ko"])
def test_mission_celebrates_the_visible_language_hook(builder, lang):
    bind = re.search(r"function bindMissions\(\).*", builder["JS"]).group()
    script = r"""
const assert=require('assert/strict'),root={lang:LANG},check={dataset:{pid:'lesson'},checked:false};
const visible={dataset:{}},hidden={dataset:{}};
const RFS={s:{m:{}},mission(){}};
const $$=()=>[check],$=s=>s.includes('[data-lang="'+root.lang+'"]')?visible:(root.lang==='en'?visible:hidden);
let reacted;const react=(b,m)=>{reacted=b;b.dataset.mood=m};const setTimeout=()=>0;
""".replace("LANG", json.dumps(lang)) + bind + "\nbindMissions();check.checked=true;check.onchange();assert.equal(reacted,visible);"
    result = subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
