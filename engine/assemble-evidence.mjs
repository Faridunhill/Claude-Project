/**
 * STAGE 5 — ASSEMBLE, EVIDENCE FORMAT
 *
 * The rough cut with no art in it at all: a real photograph, a slow push, a
 * text card, the caption, the brand frame. What you watch here is what the
 * finished video is — the only thing the renderer adds later is the voice
 * track and an mp4 container.
 *
 * Layers are the same five as always, so nothing downstream changed:
 *   5 frame + caption · 4 the card · 3 THE PHOTOGRAPH · 2 (empty — no
 *   characters) · 1 the ground.
 */
import { writeFileSync } from 'node:fs'
import { join } from 'node:path'

const esc = (s) =>
  String(s ?? '').replace(/[<>&"]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;' })[c])

export function writeEvidenceStoryboard(episode, { outDir }) {
  const p = episode.panels
  const photo = episode.photo

  const html = `<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(episode.title)}</title>
<style>
  :root { color-scheme: dark; --gold:#c9a227; --parch:#f0e5d2; --ground:#160e0a; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--ground); color:var(--parch);
         font-family:Georgia,"Iowan Old Style",serif; }
  header { padding:24px 26px 20px; border-bottom:1px solid rgba(201,162,39,.25); }
  h1 { margin:0 0 5px; font-size:clamp(19px,3.4vw,26px); font-weight:600; }
  .meta { color:rgba(240,229,210,.5); font-size:13.5px; }
  main { max-width:1000px; margin:0 auto; padding:22px 18px 70px; }

  /* the frame — 16:9 stage */
  .stage { position:relative; aspect-ratio:16/9; overflow:hidden; background:#000;
           border:1px solid rgba(201,162,39,.35); }
  .stage .photo { position:absolute; inset:0; width:100%; height:100%; object-fit:cover;
                  transform-origin:center; transition:transform .1s linear; }
  .stage .vignette { position:absolute; inset:0;
    background:radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,.55) 100%); }
  .stage .rule { position:absolute; inset:14px; border:1px solid rgba(201,162,39,.5); pointer-events:none; }
  .wordmark { position:absolute; top:26px; left:0; right:0; text-align:center;
    font-size:12px; letter-spacing:.42em; color:var(--gold); text-shadow:0 1px 6px #000; }

  .card { position:absolute; left:6%; top:50%; transform:translateY(-50%); max-width:56%;
          padding:16px 20px; background:rgba(12,7,5,.78); border-left:3px solid var(--gold);
          backdrop-filter:blur(2px); }
  .card .lab { display:block; font-size:11px; letter-spacing:.15em; text-transform:uppercase;
               color:var(--gold); margin-bottom:6px; }
  .card .val { font-size:clamp(16px,2.6vw,25px); line-height:1.3; }
  .card.wrong { border-left-color:#c05a44; } .card.wrong .lab { color:#e08a72; }
  .card.right { border-left-color:#6f9a63; } .card.right .lab { color:#9dc48f; }
  .card.warn  { border-left-color:#c08a2a; }
  .card.citation .val { font-size:clamp(12px,1.7vw,15px); line-height:1.45; color:rgba(240,229,210,.85); }

  .cap { position:absolute; left:0; right:0; bottom:0; padding:16px 8% 20px;
         background:linear-gradient(transparent, rgba(0,0,0,.8) 40%); text-align:center;
         font-size:clamp(14px,2.1vw,20px); }
  .credit { position:absolute; right:22px; bottom:16px; font-size:10.5px;
            color:rgba(240,229,210,.5); }

  .controls { display:flex; gap:12px; align-items:center; margin:15px 0 6px; flex-wrap:wrap; }
  button { background:transparent; border:1px solid rgba(201,162,39,.55); color:var(--gold);
           font-family:inherit; font-size:15px; padding:9px 20px; cursor:pointer; }
  button:hover, button:focus-visible { background:rgba(201,162,39,.13); outline:none; }
  .bar { height:3px; background:rgba(201,162,39,.16); } .bar i { display:block; height:100%; background:var(--gold); width:0; }
  .strip { margin-top:26px; display:flex; gap:8px; flex-wrap:wrap; }
  .strip button { font-size:12px; padding:6px 11px; opacity:.65; }
  .strip button.on { opacity:1; background:rgba(201,162,39,.16); }
  .note { margin-top:34px; padding:15px 17px; border:1px dashed rgba(201,162,39,.4);
          font-size:13.5px; line-height:1.6; color:rgba(240,229,210,.75); }
  .note b { color:var(--gold); }
  @media (prefers-reduced-motion: reduce) { .stage .photo { transition:none !important; } }
</style>
<header>
  <h1>${esc(episode.title)}</h1>
  <div class="meta">${p.length} panels · ${episode.runtime}s · no characters, no drawings · fact ${esc(episode.fact_id)}</div>
</header>
<main>
  <div class="stage">
    ${
      photo
        ? `<img class="photo" id="photo" src="${esc(photo.file)}" alt="">`
        : `<div class="photo" id="photo" style="display:grid;place-items:center;color:rgba(240,229,210,.4)">no photograph of this brand in the catalogue yet</div>`
    }
    <div class="vignette"></div>
    <div class="rule"></div>
    <div class="wordmark">FARIDUNHILL</div>
    <div class="card" id="card"><span class="lab" id="lab"></span><span class="val" id="val"></span></div>
    <div class="cap" id="cap"></div>
    <div class="credit">${esc(photo ? photo.citation : 'photograph pending')}</div>
  </div>

  <div class="controls">
    <button id="play">▶ Play</button>
    <button id="prev">‹</button>
    <button id="next">›</button>
    <span class="meta" id="pos"></span>
  </div>
  <div class="bar"><i id="prog"></i></div>
  <div class="strip" id="strip"></div>

  <div class="note">
    <b>This is the whole format.</b> A real pipe from the archive, a slow push, the words, your voice.
    No character, no drawings, nothing to commission — so nothing here is waiting on anybody.
    <br><br>The photograph illustrates the <b>brand</b>, never the claim: we show a real ${esc(episode.brand)}
    while explaining how ${esc(episode.brand)}s are dated, and we never suggest this particular pipe carries
    the mark under discussion. Every word spoken comes from the cabinet, and the source is on screen.
    <br><br><b>Add the voice and this is the finished video.</b>
  </div>
</main>
<script>
const P = ${JSON.stringify(p.map((x) => ({ n: x.panel, d: x.duration, t: x.narration, c: x.card, r: x.role })))};
const photo = document.getElementById('photo'), card = document.getElementById('card'),
      lab = document.getElementById('lab'), val = document.getElementById('val'),
      cap = document.getElementById('cap'), pos = document.getElementById('pos'),
      prog = document.getElementById('prog'), strip = document.getElementById('strip');
let i = 0, playing = false, timer = null, t0 = 0, raf = null;

P.forEach((x, k) => {
  const b = document.createElement('button');
  b.textContent = (k + 1) + '. ' + x.r;
  b.onclick = () => { stop(); show(k); };
  strip.appendChild(b);
});

function show(n) {
  i = (n + P.length) % P.length;
  const x = P[i];
  card.className = 'card ' + (x.c.kind || 'plain');
  lab.textContent = x.c.label || '';
  lab.style.display = x.c.label ? 'block' : 'none';
  val.textContent = x.c.text || '';
  cap.textContent = x.t;
  pos.textContent = 'panel ' + x.n + ' of ' + P.length + ' · ' + x.d + 's';
  [...strip.children].forEach((b, k) => b.classList.toggle('on', k === i));
  const zoomIn = i % 2 === 0;
  photo.style.transition = 'none';
  photo.style.transform = 'scale(' + (zoomIn ? 1 : 1.08) + ')';
  requestAnimationFrame(() => {
    photo.style.transition = 'transform ' + x.d + 's linear';
    photo.style.transform = 'scale(' + (zoomIn ? 1.08 : 1) + ')';
  });
}
function tick() {
  prog.style.width = Math.min(1, (performance.now() - t0) / (P[i].d * 1000)) * 100 + '%';
  if (playing) raf = requestAnimationFrame(tick);
}
function step() {
  if (!playing) return;
  t0 = performance.now(); tick();
  timer = setTimeout(() => {
    if (i === P.length - 1) { stop(); return; }
    show(i + 1); step();
  }, P[i].d * 1000);
}
function stop() {
  playing = false; clearTimeout(timer); cancelAnimationFrame(raf);
  prog.style.width = '0'; document.getElementById('play').textContent = '▶ Play';
}
document.getElementById('play').onclick = () => {
  if (playing) return stop();
  playing = true; document.getElementById('play').textContent = '❚❚ Pause';
  if (i === P.length - 1) show(0);
  step();
};
document.getElementById('next').onclick = () => { stop(); show(i + 1); };
document.getElementById('prev').onclick = () => { stop(); show(i - 1); };
show(0);
</script>
`
  writeFileSync(join(outDir, 'storyboard.html'), html)
}
