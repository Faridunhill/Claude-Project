"""Turn the filters into live search links — the front door of the screener.

This is the piece that was missing. The screener knows how to judge land; this
knows where to go and get it. It builds the exact pre-filtered search URL for
every major listing site, for every county, from `config.yml` — the same
acreage, price and county settings the screener uses — and writes them out as
one clickable page.

It does not scrape. It builds the URL a person would build by hand and hands it
over. What comes back is read by a human or pasted into intake_listings.py.

    py search_links.py                      # all counties, writes out/search_links.html
    py search_links.py --county hunterdon   # one county
    py search_links.py --commercial         # commercial-zoned searches only
    py search_links.py --print              # just print the URLs

THE LOOP THIS IS BUILT FOR — set it up once, it runs itself:

  1. Open the links below, set the filters, and on each site click
     "Save search" / "Get email alerts".
  2. New matching listings then arrive by email automatically, for free,
     with no scraping and no API.
  3. Paste them into intake_listings.py -> screen.py --listings.
  4. Call the agent on whatever survives.
"""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path


import yaml

HERE = Path(__file__).resolve().parent


# This tool deliberately does NOT import common.py. That module pulls in
# pandas and geopandas, and the whole point of this one is that it runs on any
# machine with nothing installed but PyYAML — before the GIS stack exists.
def load_config(path: str | Path | None = None) -> dict:
    with open(Path(path) if path else HERE / "config.yml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def log(msg: str) -> None:
    print(f"[links] {msg}", flush=True)

# County slugs per site. NJ has 21; the URL spellings differ by site.
COUNTIES = [
    # (display, slug-hyphen, region)
    ("Hunterdon", "hunterdon", "Central"),
    ("Mercer", "mercer", "Central"),
    ("Somerset", "somerset", "Central"),
    ("Monmouth", "monmouth", "Central"),
    ("Middlesex", "middlesex", "Central"),
    ("Ocean", "ocean", "Central"),
    ("Burlington", "burlington", "South"),
    ("Gloucester", "gloucester", "South"),
    ("Salem", "salem", "South"),
    ("Cumberland", "cumberland", "South"),
    ("Atlantic", "atlantic", "South"),
    ("Camden", "camden", "South"),
    ("Cape May", "cape-may", "South"),
    ("Warren", "warren", "North"),
    ("Sussex", "sussex", "North"),
    ("Morris", "morris", "North"),
    ("Passaic", "passaic", "North"),
    ("Bergen", "bergen", "North"),
    ("Essex", "essex", "North"),
    ("Union", "union", "North"),
    ("Hudson", "hudson", "North"),
]

# Sites whose search URLs take filters in the path or query string.
# Patterns confirmed against live result pages, September 2026.
SITES = {
    "realtor": {
        "name": "Realtor.com",
        "why": "Fed straight from the MLS — the most accurate 'still available' status of any free site. Start here.",
        "land": "https://www.realtor.com/realestateandhomes-search/{title}-County_NJ/type-land/lot-sqft-{min_sqft}",
        "commercial": "https://www.realtor.com/realestateandhomes-search/{title}-County_NJ/type-land",
    },
    "landwatch": {
        "name": "LandWatch",
        "why": "Most NJ land listings of any site (3,742 statewide). Acreage band goes in the URL.",
        "land": "https://www.landwatch.com/new-jersey-land-for-sale/{slug}-county/acres-{acre_band}",
        "commercial": "https://www.landwatch.com/new-jersey-land-for-sale/{slug}-county/commercial-property",
    },
    "landsearch": {
        "name": "LandSearch",
        "why": "Best map view. Separate paths for vacant land and commercial-zoned.",
        "land": "https://www.landsearch.com/vacant/{slug}-county-nj",
        "commercial": "https://www.landsearch.com/commercial/{slug}-county-nj",
    },
    "landdotcom": {
        "name": "Land.com",
        "why": "Deep rural and farm coverage. Type-9 path filters to farms.",
        "land": "https://www.land.com/{title}-County-NJ/all-land/",
        "commercial": "https://www.land.com/{title}-County-NJ/commercial-property/",
    },
    "crexi": {
        "name": "Crexi",
        "why": "Commercial brokers list here first. This is where plaza-zoned land shows up.",
        "land": "https://www.crexi.com/properties/NJ/Residential-Land",
        "commercial": "https://www.crexi.com/properties/NJ/Commercial-Land",
    },
    "loopnet": {
        "name": "LoopNet",
        "why": "The largest commercial database. The Route 539 Upper Freehold parcel came from here.",
        "land": "https://www.loopnet.com/search/land/new-jersey/for-sale/",
        "commercial": "https://www.loopnet.com/search/commercial-real-estate/new-jersey/for-sale/",
    },
    "zillow": {
        "name": "Zillow",
        "why": "Fewest NJ land listings of the free sites (~1,787) and status lags. Use it last, not first.",
        "land": "https://www.zillow.com/{slug}-county-nj/land/",
        "commercial": None,
    },
}


def acre_bands(lo: float, hi: float) -> list[str]:
    """LandWatch buckets acreage into fixed bands and a URL carries exactly one.

    Return EVERY band the wanted range touches, not the first — a 3-60 acre
    search that returned only "1-5" would silently hide almost every parcel
    worth looking at.
    """
    bands = [(0, 1), (1, 5), (6, 10), (11, 50), (51, 100), (101, 500)]
    hit = [f"{blo}-{bhi}" for blo, bhi in bands if lo <= bhi and hi >= blo]
    return hit or ["11-50"]


def build(county: str, slug: str, cfg: dict, commercial: bool) -> list[tuple[str, str, str]]:
    f = cfg["attribute_filters"]
    bands = acre_bands(f["min_acres"], f["max_acres"])
    base = {
        "slug": slug,
        "title": county.replace(" ", "-"),
        "min_sqft": int(f["min_acres"] * 43560),
    }
    key = "commercial" if commercial else "land"

    out = []
    for site in SITES.values():
        template = site.get(key)
        if not template:
            continue
        if "{acre_band}" in template:
            # One URL per acreage band the range touches — a single band would
            # quietly drop most of the search.
            for band in bands:
                out.append((f"{site['name']} · {band} ac",
                            template.format(**base, acre_band=band), site["why"]))
        else:
            out.append((site["name"], template.format(**base), site["why"]))
    return out


def write_page(rows: dict, cfg: dict, out_path: Path, commercial: bool) -> Path:
    f = cfg["attribute_filters"]
    req = cfg["requirements"]
    mode = "Commercial-zoned" if commercial else "Vacant land"

    parts = [f"""<title>NJ Land Search Links</title>
<style>
 :root{{--bg:#f2f4f1;--card:#fff;--ink:#17201c;--dim:#5d6b65;--rule:#d5ddd8;--accent:#0f6e6a;}}
 @media(prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#11150f;--card:#1a211c;
   --ink:#e8eee9;--dim:#9aa8a1;--rule:#2b352f;--accent:#54bdb5;}}}}
 :root[data-theme="dark"]{{--bg:#11150f;--card:#1a211c;--ink:#e8eee9;--dim:#9aa8a1;
   --rule:#2b352f;--accent:#54bdb5;}}
 body{{background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,sans-serif;margin:0;}}
 .w{{max-width:900px;margin:0 auto;padding-inline:18px;padding-block:28px 60px;}}
 h1{{font-size:30px;margin:0 0 4px;}} h2{{font-size:19px;margin:28px 0 8px;
   border-bottom:1px solid var(--rule);padding-bottom:5px;}}
 .filters{{background:var(--card);border:1px solid var(--rule);padding:12px 14px;margin:14px 0 0;
   font-size:14px;}}
 .filters b{{color:var(--accent);}}
 a{{color:var(--accent);}}
 .row{{background:var(--card);border:1px solid var(--rule);padding:10px 13px;margin-bottom:7px;}}
 .row .n{{font-weight:600;}} .row .y{{color:var(--dim);font-size:13px;margin:2px 0 5px;}}
 .row a{{font-size:13px;word-break:break-all;}}
 .step{{background:var(--card);border-left:3px solid var(--accent);padding:12px 14px;margin:6px 0;}}
 .step b{{display:block;margin-bottom:2px;}}
</style>
<div class="w">
<h1>NJ Land Search Links</h1>
<p style="color:var(--dim);margin:0">{mode} · generated from config.yml · every link opens a live search</p>

<div class="filters">
  <b>Acreage</b> {f['min_acres']}–{f['max_acres']} ac &nbsp;·&nbsp;
  <b>Schools</b> {req['min_school_rating']}+/10 &nbsp;·&nbsp;
  <b>Zoning wanted</b> {', '.join(req['zoning_categories_wanted'])} &nbsp;·&nbsp;
  <b>Region</b> {'/'.join(req['preferred_regions'])} preferred
  <br><span style="color:var(--dim);font-size:13px">Sites cannot filter zoning, wetlands,
  Highlands or schools. They give you the list; screen.py gives you the truth.</span>
</div>

<h2>Set this up once</h2>
<div class="step"><b>1 · Open a link and set the filters</b>Acreage and price on the site itself.</div>
<div class="step"><b>2 · Click "Save search" and turn on email alerts</b>Free on every site here.
  New matching listings then come to you automatically — no scraping, no API, no cost.</div>
<div class="step"><b>3 · Paste what arrives into intake_listings.py</b>It normalises anything —
  pasted text, a CSV, an email body — into the format screen.py wants.</div>
<div class="step"><b>4 · Run screen.py --listings</b>Wetlands, Highlands, Pinelands, flood,
  contamination, zoning, schools. Then call the agent on whatever survives.</div>
"""]

    for county, links in rows.items():
        parts.append(f"<h2>{html.escape(county)} County</h2>")
        for name, url, why in links:
            parts.append(
                f'<div class="row"><span class="n">{html.escape(name)}</span>'
                f'<div class="y">{html.escape(why)}</div>'
                f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(url)}</a></div>'
            )

    parts.append("</div>")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts), encoding="utf-8")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--county", help="one county by slug, e.g. hunterdon")
    ap.add_argument("--commercial", action="store_true",
                    help="commercial-zoned searches instead of vacant land")
    ap.add_argument("--region", choices=["North", "Central", "South"],
                    help="restrict to one region")
    ap.add_argument("--print", dest="show", action="store_true", help="print URLs only")
    args = ap.parse_args()

    cfg = load_config()
    req = cfg["requirements"]

    counties = COUNTIES
    if args.county:
        counties = [c for c in counties if c[1] == args.county.lower()]
        if not counties:
            sys.exit(f"[fatal] unknown county '{args.county}'")
    elif args.region:
        counties = [c for c in counties if c[2] == args.region]
    else:
        # Preferred regions first — Farid's stated order.
        pref = req["preferred_regions"]
        counties = sorted(counties, key=lambda c: (c[2] not in pref, c[2], c[0]))

    rows = {}
    for display, slug, region in counties:
        rows[f"{display} ({region})"] = build(display, slug, cfg, args.commercial)

    if args.show:
        for county, links in rows.items():
            print(f"\n== {county}")
            for name, url, _ in links:
                print(f"  {name:14s} {url}")
        return

    out = write_page(rows, cfg, HERE / cfg["output"]["dir"] / "search_links.html",
                     args.commercial)
    total = sum(len(v) for v in rows.values())
    log(f"wrote {total} search links across {len(rows)} counties -> {out}")
    log("open it, save the searches, turn on email alerts")


if __name__ == "__main__":
    main()
