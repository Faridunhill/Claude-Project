/**
 * STAGE 5 — ASSEMBLE
 *
 * Emits a self-contained storyboard that PLAYS: the panels advance on their
 * narration timings, so an episode can be watched and judged before a single
 * frame of real art exists.
 *
 * This is the rough cut. The finished render — the same panel list handed to
 * the MoviePy composer with pan/zoom, the real voice track and burned-in
 * captions — is the only thing that changes when the art and the voice land.
 * The panel list itself does not change.
 */
import { writeFileSync } from 'node:fs'
import { join } from 'node:path'

export function writeStoryboard(episode, resolved, { outDir, missing }) {
  const panels = resolved.panels
  const html = `<!doctype html>
<meta charset="utf-8">
<title>${esc(episode.title)} — storyboard</title>
<style>
  :root { color-scheme: dark; }
  body { margin:0; background:#1d120c; color:#efe3cf; font-family:Georgia,'Times New Roman',serif; }
  header { padding:28px 32px 22px; border-bottom:1px solid rgba(201,162,39,.28); }
  h1 { margin:0 0 6px; font-size:26px; font-weight:600; }
  .meta { color:rgba(239,227,207,.5); font-size:14px; }
  .claim { margin-top:14px; padding:12px 16px; border-left:3px solid #c9a227; background:rgba(201,162,39,.07); font-size:14px; }
  .claim b { color:#c9a227; font-weight:600; }
  main { max-width:1120px; margin:0 auto; padding:26px 20px 80px; }
  .stage { position:relative; background:#000; border:1px solid rgba(201,162,39,.3); }
  .stage img { display:block; width:100%; }
  .controls { display:flex; gap:14px; align-items:center; margin:16px 0 8px; flex-wrap:wrap; }
  button { background:transparent; border:1px solid rgba(201,162,39,.55); color:#c9a227;
           font-family:inherit; font-size:15px; padding:9px 20px; cursor:pointer; }
  button:hover { background:rgba(201,162,39,.12); }
  .bar { height:3px; background:rgba(201,162,39,.18); margin-top:10px; }
  .bar i { display:block; height:100%; background:#c9a227; width:0; }
  .narr { margin-top:16px; font-size:17px; line-height:1.55; min-height:3.2em; }
  .narr small { display:block; color:rgba(239,227,207,.45); font-size:13px; margin-bottom:5px;
                text-transform:uppercase; letter-spacing:.14em; }
  .grid { margin-top:44px; display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:18px; }
  .grid figure { margin:0; border:1px solid rgba(201,162,39,.18); cursor:pointer; }
  .grid figure.on { border-color:#c9a227; }
  .grid img { display:block; width:100%; }
  .grid figcaption { padding:8px 10px; font-size:12px; color:rgba(239,227,207,.55); }
  .notice { margin-top:44px; padding:16px 18px; border:1px dashed rgba(201,162,39,.4); font-size:13.5px;
            line-height:1.6; color:rgba(239,227,207,.72); }
  .notice b { color:#c9a227; }
  code { font-family:ui-monospace,Menlo,monospace; font-size:12.5px; color:rgba(239,227,207,.85); }
</style>
<header>
  <h1>${esc(episode.title)}</h1>
  <div class="meta">${panels.length} panels · ${episode.runtime}s · fact <code>${esc(episode.fact_id)}</code></div>
  <div class="claim">
    <b>Claim:</b> ${esc(String(episode.claim.reads))} → <b>${esc(String(episode.claim.era))}</b>
    · confidence: ${esc(episode.claim.confidence)}<br>
    <b>Source:</b> ${esc(episode.sources.join('; '))}
  </div>
</header>
<main>
  <div class="stage"><img id="frame" src="panels/panel-01.svg" alt=""></div>
  <div class="controls">
    <button id="play">▶ Play the episode</button>
    <button id="prev">‹ Prev</button>
    <button id="next">Next ›</button>
    <span class="meta" id="pos"></span>
  </div>
  <div class="bar"><i id="prog"></i></div>
  <div class="narr"><small id="who"></small><span id="line"></span></div>

  <div class="grid" id="grid">
    ${panels
      .map(
        (p) => `<figure data-i="${p.panel - 1}">
        <img src="panels/panel-${String(p.panel).padStart(2, '0')}.svg" alt="">
        <figcaption>${p.panel}. ${esc(p.role)} · ${p.duration}s</figcaption></figure>`
      )
      .join('\n    ')}
  </div>

  <div class="notice">
    <b>This is a rough cut made from placeholder art.</b> Every box on a panel is a real
    asset id waiting for the design commission — the engine already knows what it needs.
    ${missing.length ? `<br><br><b>${missing.length} asset ids are unfilled:</b> <code>${esc(missing.join(', '))}</code>` : ''}
    <br><br>Nothing above states a fact the cabinet did not carry, and the source line is
    generated from the cabinet, not written by hand. When the art lands, the same panel
    list renders in the finished style — <b>this file does not get rewritten.</b>
  </div>
</main>
<script>
const P = ${JSON.stringify(
    panels.map((p) => ({ n: p.panel, d: p.duration, s: p.speaker, t: p.narration }))
  )};
const frame = document.getElementById('frame'), line = document.getElementById('line'),
      who = document.getElementById('who'), pos = document.getElementById('pos'),
      prog = document.getElementById('prog'), figs = [...document.querySelectorAll('#grid figure')];
let i = 0, playing = false, timer = null, t0 = 0, raf = null;

function show(n) {
  i = (n + P.length) % P.length;
  frame.src = 'panels/panel-' + String(P[i].n).padStart(2, '0') + '.svg';
  line.textContent = P[i].t;
  who.textContent = P[i].s;
  pos.textContent = 'panel ' + P[i].n + ' of ' + P.length + ' · ' + P[i].d + 's';
  figs.forEach((f, k) => f.classList.toggle('on', k === i));
}
function tick() {
  const pct = Math.min(1, (performance.now() - t0) / (P[i].d * 1000));
  prog.style.width = (pct * 100) + '%';
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
  prog.style.width = '0'; document.getElementById('play').textContent = '▶ Play the episode';
}
document.getElementById('play').onclick = () => {
  if (playing) { stop(); return; }
  playing = true; document.getElementById('play').textContent = '❚❚ Pause';
  if (i === P.length - 1) show(0);
  step();
};
document.getElementById('next').onclick = () => { stop(); show(i + 1); };
document.getElementById('prev').onclick = () => { stop(); show(i - 1); };
figs.forEach((f) => (f.onclick = () => { stop(); show(+f.dataset.i); }));
show(0);
</script>
`
  writeFileSync(join(outDir, 'storyboard.html'), html)
}

/**
 * STAGE 7 — LEDGER. Every episode records what it claimed, from where, and
 * what was still missing when it was built. A cabinet correction later can
 * find every episode that depended on the corrected fact.
 */
export function writeLedger(episode, resolved, { outDir, missing, refused, builtAt }) {
  const ledger = {
    slug: episode.slug,
    title: episode.title,
    built_at: builtAt,
    fact_id: episode.fact_id,
    claim: episode.claim,
    caveat: episode.caveat,
    sources: episode.sources,
    runtime_seconds: episode.runtime,
    panel_count: episode.panels.length,
    assets_missing: missing,
    facts_refused_this_run: refused,
    changelog: [{ at: builtAt, what: 'first build (placeholder art)' }],
  }
  writeFileSync(join(outDir, 'episode.json'), JSON.stringify({ ...episode, panels: resolved.panels }, null, 2) + '\n')
  writeFileSync(join(outDir, 'ledger.json'), JSON.stringify(ledger, null, 2) + '\n')
  return ledger
}

function esc(s) {
  return String(s ?? '').replace(/[<>&]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' })[c])
}
