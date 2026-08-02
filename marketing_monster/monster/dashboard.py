"""THE DASHBOARD — the agent with a face.

A local page, served from Farid's own machine, so running the business does
not require a command line. Pure stdlib: http.server and one HTML string. No
framework, no npm, no build step, nothing to keep up to date.

It binds to 127.0.0.1 only. The Well never leaves the machine (M4), and a
dashboard that could be reached from outside would be a hole in that wall.

ON THE WALL AND THIS PAGE. It shows every business Farid owns, side by side.
That is not a breach: the wall (B3) stops the AGENTS from seeing each other's
data — one root, one process, no shared index. Farid owns all three and may
look at all three. The page reads each kitchen separately and never mixes
their numbers into one figure, because a combined total would be exactly the
kind of cross-business fact the cookbook may not carry.

What it shows, in the order that matters:
  1. WHAT NEEDS YOU — the reserved-power questions, answerable with a click.
     Everything else on the page is information; this is the only part that
     is a job.
  2. The scoreboard, blind spots first (§2.3 — no lying by omission).
  3. The listing desk: type a title, see what pipes like it actually fetched.
  4. Stock, and what the machine has learned but not yet believed.
"""
from __future__ import annotations

import json
import pathlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .judge import Judge
from .ledger import LedgerError
from .listing import ListingDesk
from .playbook import Playbook
from .report import ledger_health, weekly_report
from .scale import Scale

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Faridunhill — Marketing</title><style>
:root{--gold:#c9a24b;--ink:#0d0d0f;--panel:#17171b;--line:#2a2a30;
      --txt:#e8e4d8;--mut:#8a857a;--good:#7ea86b;--warn:#c98a3a;--bad:#b4553f}
*{box-sizing:border-box}
body{margin:0;background:var(--ink);color:var(--txt);font-family:Georgia,serif;
     font-size:16px;line-height:1.5}
header{border-bottom:1px solid var(--gold);padding:18px 24px;display:flex;
       justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:10px}
h1{margin:0;color:var(--gold);font-size:20px;letter-spacing:2px;font-weight:normal}
.sub{color:var(--mut);font-size:13px}
main{max-width:1000px;margin:0 auto;padding:24px}
section{background:var(--panel);border:1px solid var(--line);border-radius:8px;
        padding:20px 22px;margin-bottom:20px}
h2{margin:0 0 14px;font-size:13px;letter-spacing:2px;text-transform:uppercase;
   color:var(--mut);font-family:Helvetica,Arial,sans-serif}
.ask{border-left:3px solid var(--gold);padding:14px 16px;margin-bottom:14px;
     background:rgba(201,162,75,.06);border-radius:0 6px 6px 0}
.ask .what{font-size:17px;margin-bottom:4px}
.ask .why{color:var(--mut);font-size:13px;margin-bottom:12px}
button{font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:1px;
       padding:9px 20px;border:none;border-radius:5px;cursor:pointer;margin-right:8px}
.yes{background:var(--gold);color:#111;font-weight:bold}
.no{background:transparent;color:var(--mut);border:1px solid var(--line)}
.later{background:transparent;color:var(--mut);border:1px solid var(--line)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px}
.tile .n{font-size:30px;color:var(--gold);line-height:1.1}
.tile .l{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:1px;
         font-family:Helvetica,Arial,sans-serif;margin-top:4px}
input[type=text]{width:100%;background:#0e0e11;border:1px solid var(--line);
       border-radius:6px;color:var(--txt);padding:12px 14px;font-family:inherit;
       font-size:16px;margin-bottom:10px}
.answer{background:#0e0e11;border-radius:6px;padding:14px 16px;margin-top:12px;
        white-space:pre-wrap;font-size:15px}
.price{font-size:26px;color:var(--gold)}
table{width:100%;border-collapse:collapse;font-size:14px}
td,th{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line)}
th{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:1px;
   font-family:Helvetica,Arial,sans-serif}
.ok{color:var(--good)}.warn{color:var(--warn)}.bad{color:var(--bad)}
pre{white-space:pre-wrap;font-size:13px;color:var(--mut);margin:0;
    font-family:ui-monospace,Menlo,Consolas,monospace}
.quiet{color:var(--mut);font-size:14px}
.lesson{padding:8px 0;border-bottom:1px solid var(--line);font-size:14px}
.tag{font-family:Helvetica,Arial,sans-serif;font-size:10px;letter-spacing:1px;
     padding:2px 7px;border-radius:3px;margin-right:8px}
.proposed{background:#3a3a20;color:var(--gold)}
.confirmed{background:#24361f;color:var(--good)}
footer{color:var(--mut);font-size:12px;text-align:center;padding:20px}
nav{display:flex;gap:2px;padding:0 24px;border-bottom:1px solid var(--line);
    flex-wrap:wrap}
nav button{background:transparent;color:var(--mut);border:none;border-bottom:2px solid transparent;
    border-radius:0;padding:12px 18px;margin:0;font-size:14px;letter-spacing:1px}
nav button.on{color:var(--gold);border-bottom-color:var(--gold)}
nav button.cold{opacity:.45}
.notstarted{padding:30px 4px;text-align:center;color:var(--mut)}
.notstarted b{color:var(--txt);display:block;margin-bottom:8px;font-size:17px}
</style></head><body>
<header>
  <h1>THE MARKETING MONSTER</h1>
  <div class="sub" id="stamp">loading…</div>
</header>
<nav id="tabs"></nav>
<main>
  <div id="cold" style="display:none"></div>
  <div id="body">
  <section id="asks-box">
    <h2>What needs you</h2>
    <div id="asks"></div>
  </section>

  <section>
    <h2>This week</h2>
    <div class="grid" id="tiles"></div>
  </section>

  <section>
    <h2>Listing a pipe — what should I ask?</h2>
    <input type="text" id="title" placeholder="Type the pipe title, e.g. Dunhill Shell Briar Bulldog Group 4">
    <button class="yes" onclick="ask()">What is it worth?</button>
    <div id="advice"></div>
  </section>

  <section>
    <h2>Still live</h2>
    <div id="stock"></div>
  </section>

  <section>
    <h2>What it has learned</h2>
    <div id="lessons"></div>
  </section>

  <section>
    <h2>The machine's own report</h2>
    <pre id="report"></pre>
    <div style="margin-top:14px">
      <button class="no" onclick="runNow()">Run it now</button>
      <span class="quiet" id="runmsg"></span>
    </div>
  </section>
  </div>
</main>
<footer>Runs on this computer only. Nothing here is on the internet.</footer>
<script>
let S = {}, CLONE = null, CLONES = [];
async function boot(){
  CLONES = await (await fetch('/api/clones')).json();
  CLONE = CLONE || (CLONES.find(c => c.ready) || CLONES[0]).name;
  drawTabs();
  load();
}
function drawTabs(){
  document.getElementById('tabs').innerHTML = CLONES.map(c =>
    `<button class="${c.name===CLONE?'on':''} ${c.ready?'':'cold'}"
       onclick="pick('${c.name}')">${esc(c.label)}${c.asks?' ('+c.asks+')':''}</button>`
  ).join('');
}
function pick(name){ CLONE = name; drawTabs(); load(); }
async function load(){
  S = await (await fetch('/api/state?clone=' + encodeURIComponent(CLONE))).json();
  document.getElementById('stamp').textContent = S.label + ' · ' + S.now;
  document.getElementById('body').style.display = S.ready ? '' : 'none';
  document.getElementById('cold').style.display = S.ready ? 'none' : '';
  if(!S.ready){
    document.getElementById('cold').innerHTML =
      `<div class="notstarted"><b>${esc(S.label)} has not been started yet.</b>
       ${esc(S.why)}</div>`;
    return;
  }
  drawAsks(); drawTiles(); drawStock(); drawLessons();
  document.getElementById('report').textContent = S.report;
}
function drawAsks(){
  const box = document.getElementById('asks');
  if(!S.asks.length){
    box.innerHTML = '<div class="quiet">Nothing needs you today.</div>';
    return;
  }
  box.innerHTML = S.asks.map(a => `
    <div class="ask">
      <div class="what">${esc(a.proposal)}</div>
      <div class="why">${esc(a.id)} · ${esc(a.kind)} · ${esc(a.reason)}</div>
      <button class="yes"   onclick="answer('${a.id}','yes')">Yes</button>
      <button class="no"    onclick="answer('${a.id}','no')">No</button>
      <button class="later" onclick="answer('${a.id}','later')">Later</button>
    </div>`).join('');
}
function drawTiles(){
  const t = S.tiles;
  document.getElementById('tiles').innerHTML = `
    <div class="tile"><div class="n">${t.sales}</div><div class="l">sales this week</div></div>
    <div class="tile"><div class="n">${t.value}</div><div class="l">recorded</div></div>
    <div class="tile"><div class="n">${t.live}</div><div class="l">still live</div></div>
    <div class="tile"><div class="n">${t.unattributable}</div><div class="l">cause unknown</div></div>
    <div class="tile"><div class="n ${t.health_class}">${t.health}</div><div class="l">organs writing</div></div>`;
}
function drawStock(){
  if(!S.stock.length){
    document.getElementById('stock').innerHTML =
      '<div class="quiet">Nothing listed through the agent yet. Every pipe you list here starts a clock, so it can tell you later how long things take to sell.</div>';
    return;
  }
  document.getElementById('stock').innerHTML =
    '<table><tr><th>days live</th><th>asked</th><th>pipe</th></tr>' +
    S.stock.map(s => `<tr><td>${s.days}</td><td>${s.asked}</td><td>${esc(s.sku)}</td></tr>`).join('') +
    '</table>';
}
function drawLessons(){
  if(!S.lessons.length){
    document.getElementById('lessons').innerHTML =
      '<div class="quiet">Nothing yet. A lesson has to show up twice, in two different weeks, before the agent believes it.</div>';
    return;
  }
  document.getElementById('lessons').innerHTML = S.lessons.map(l => `
    <div class="lesson"><span class="tag ${l.status.toLowerCase()}">${l.status}</span>
      ${esc(l.claim)}<div class="quiet">${esc(l.evidence)}</div></div>`).join('');
}
async function answer(id, verdict){
  const r = await post('/api/answer', {id, verdict, clone: CLONE});
  if(r.error){ alert(r.error); return; }
  load();
}
async function ask(){
  const title = document.getElementById('title').value.trim();
  if(!title) return;
  const r = await post('/api/price', {title, clone: CLONE});
  const box = document.getElementById('advice');
  if(r.advice){
    box.innerHTML = `<div class="answer">
      <div class="price">${r.low} &mdash; ${r.high}</div>
      <div class="quiet">middle ${r.median} · best ever ${r.best}</div>
      <div style="margin-top:10px">${esc(r.why)}</div>
      <div class="quiet" style="margin-top:8px">evidence: ${esc(r.confidence)}</div>
    </div>`;
  } else {
    box.innerHTML = `<div class="answer">${esc(r.why)}</div>`;
  }
}
async function runNow(){
  document.getElementById('runmsg').textContent = 'working…';
  const r = await post('/api/run', {clone: CLONE});
  document.getElementById('runmsg').textContent = r.summary || r.error || 'done';
  load();
}
async function post(url, body){
  const res = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'},
                               body: JSON.stringify(body)});
  return res.json();
}
function esc(s){ return String(s == null ? '' : s)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
boot();
setInterval(load, 60000);
</script></body></html>
"""


# Farid's businesses. The label is what he calls them; the name is the folder.
KITCHENS = [
    ("pipes", "Faridunhill · pipes"),
    ("groundtruth", "GroundTruth · real estate"),
    ("ashcombe", "Ashcombe · stationery"),
]


def list_kitchens(base: pathlib.Path) -> list[dict]:
    """Every business, whether it has been started or not. A kitchen that does
    not exist yet says so rather than being hidden — the plan is three, and a
    dashboard showing one would quietly redefine the plan as one."""
    out = []
    for name, label in KITCHENS:
        root = base / "clones" / name
        ready = (root / "well").is_dir()
        asks = 0
        if ready:
            try:
                asks = len(Judge(root).open_items())
            except Exception:
                asks = 0
        out.append({"name": name, "label": label, "ready": ready, "asks": asks})
    return out


def _money(value: float | None) -> str:
    return f"{value:,.0f}" if value else "—"


def build_state(base: pathlib.Path, clone: str) -> dict:
    from datetime import datetime, timezone
    from .report import _age_days

    root = base / "clones" / clone
    label = dict(KITCHENS).get(clone, clone)
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M UTC")
    if not (root / "well").is_dir():
        return {"clone": clone, "label": label, "ready": False, "now": stamp,
                "why": ("One design, cloned three times — but v1.0 and MIND both "
                        "ruled: prove the loop on pipes until one lesson is "
                        "CONFIRMED, then copy. Cloning an unproven machine three "
                        "times just gives you three unproven machines.")}
    scale, book, judge = Scale(root), Playbook(root), Judge(root)
    desk = ListingDesk(root)

    recent = [r for r in scale.rows() if r.get("ts") and _age_days(r["ts"]) <= 7]
    sales = [r for r in recent if r["event"] == "sale"]
    unattr, total = scale.unattributable_share()
    health = ledger_health(root)
    silent = [h for h in health if h["silent"]]

    return {
        "clone": clone,
        "label": label,
        "ready": True,
        "now": stamp,
        "asks": [{"id": r["decision_id"], "proposal": r["proposal"],
                  "kind": r["needs_farid"], "reason": r["reason"]}
                 for r in judge.open_items()],
        "tiles": {
            "sales": len(sales),
            "value": _money(sum(r["value"] or 0 for r in sales)),
            "live": len(desk.still_unsold()),
            "unattributable": f"{(unattr / total * 100):.0f}%" if total else "—",
            "health": f"{len(health) - len(silent)}/{len(health)}",
            "health_class": "bad" if silent else "ok",
        },
        "stock": [{"days": s["days_live"], "asked": _money(s["asked"]),
                   "sku": s["sku"]} for s in desk.still_unsold()[:20]],
        "lessons": [{"status": x.status, "claim": x.claim,
                     "evidence": f"{x.n} · {x.effect} · review {x.review}"}
                    for x in book.lines()[:20]],
        "report": weekly_report(root),
    }


def make_handler(base: pathlib.Path, clone: str):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):        # keep the console quiet
            pass

        def _send(self, code: int, body: bytes, kind: str):
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, payload: dict, code: int = 200):
            self._send(code, json.dumps(payload).encode(), "application/json")

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                return self._send(200, PAGE.encode(), "text/html; charset=utf-8")
            if self.path == "/api/clones":
                return self._json(list_kitchens(base))
            if self.path.startswith("/api/state"):
                from urllib.parse import parse_qs, urlparse
                asked = parse_qs(urlparse(self.path).query).get("clone", [clone])[0]
                if asked not in dict(KITCHENS):
                    return self._json({"error": "unknown kitchen"}, 400)
                try:
                    return self._json(build_state(base, asked))
                except Exception as exc:
                    return self._json({"error": str(exc)}, 500)
            self._send(404, b"not here", "text/plain")

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                return self._json({"error": "bad request"}, 400)
            asked = body.get("clone") or clone
            if asked not in dict(KITCHENS):
                return self._json({"error": "unknown kitchen"}, 400)
            root = base / "clones" / asked
            try:
                if self.path == "/api/answer":
                    verdict = {"yes": "DO", "no": "REJECT",
                               "later": "DEFER"}[body["verdict"]]
                    Judge(root).answer(body["id"], verdict,
                                       f"Farid answered {body['verdict']} on the dashboard")
                    return self._json({"ok": True})
                if self.path == "/api/price":
                    comps = ListingDesk(root).comparables(body.get("title", ""))
                    return self._json({
                        "advice": comps["advice"],
                        "low": _money(comps.get("low")),
                        "high": _money(comps.get("high")),
                        "median": _money(comps.get("median")),
                        "best": _money(comps.get("best")),
                        "confidence": comps.get("confidence", ""),
                        "why": comps["why"]})
                if self.path == "/api/run":
                    from .auto import Autopilot
                    result = Autopilot(base, asked).run()
                    return self._json({"summary": (
                        f"{result['files_ingested']} files, "
                        f"{result['sales_recorded']} sales, "
                        f"{result['twins_made']} listings, "
                        f"{result['waiting_for_farid']} question(s)")})
            except LedgerError as exc:
                return self._json({"error": str(exc)}, 400)
            except Exception as exc:
                return self._json({"error": str(exc)}, 500)
            self._json({"error": "unknown"}, 404)

    return Handler


def serve(base: pathlib.Path, clone: str = "pipes", port: int = 8765,
          open_browser: bool = True):
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(base, clone))
    url = f"http://127.0.0.1:{port}/"
    print(f"Dashboard: {url}")
    print("  Runs on this computer only — nothing is on the internet.")
    print("  Leave this window open. Close it (or press Ctrl+C) to stop.")
    if open_browser:
        import threading
        import webbrowser
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()
