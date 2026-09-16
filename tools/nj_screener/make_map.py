"""Render the screener output as an interactive NJ map.

Produces one self-contained HTML file: pan/zoom New Jersey, every surviving
parcel drawn in place, coloured by which track it qualifies for, sized by
score, with a popup carrying the numbers that decided it.

    py make_map.py                       # uses out/nj_candidates.geojson
    py make_map.py path/to/other.geojson
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd

from common import load_config, log, resolve_path  # noqa: F401  (resolve_path re-export)

NJ_CENTER = [40.15, -74.65]

TRACK_COLORS = {
    "TRACK A + B": "#16a34a",                 # green — both paths open
    "TRACK A (plaza)": "#2563eb",             # blue  — retail by right
    "TRACK B (farm market)": "#ca8a04",       # amber — Right to Farm path
    "TRACK B — verify ag permitted": "#9333ea",  # purple — needs ordinance read
    "LIFESTYLE ONLY": "#6b7280",              # grey
}


def _style(feature):
    props = feature["properties"]
    color = TRACK_COLORS.get(props.get("verdict"), "#6b7280")
    score = props.get("score") or 0
    return {
        "fillColor": color,
        "color": color,
        "weight": 1.5,
        "fillOpacity": 0.25 + min(score, 100) / 100 * 0.5,
    }


def build_map(geojson_path: Path, cfg: dict | None = None) -> Path:
    import folium
    from folium.plugins import MarkerCluster

    cfg = cfg or load_config()
    gdf = gpd.read_file(geojson_path)
    if gdf.empty:
        log("no parcels to map")
        return geojson_path

    gdf = gdf.to_crs("EPSG:4326")
    log(f"mapping {len(gdf):,} parcels")

    m = folium.Map(location=NJ_CENTER, zoom_start=8, tiles=None)
    folium.TileLayer("CartoDB positron", name="Light").add_to(m)
    folium.TileLayer("OpenStreetMap", name="Street").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Satellite",
    ).add_to(m)

    popup_fields = [c for c in [
        "pin", "address", "municipality", "county_name", "zone_code",
        "zone_category", "gross_acres", "net_buildable_acres", "wetland_pct",
        "school_rating", "district", "est_lots", "allows_cluster",
        "highlands", "pinelands", "track_b_threshold", "verdict", "score",
    ] if c in gdf.columns]
    aliases = [f.replace("_", " ").title() for f in popup_fields]

    # One layer per track so they can be toggled independently.
    for verdict, color in TRACK_COLORS.items():
        subset = gdf[gdf.verdict == verdict]
        if subset.empty:
            continue
        folium.GeoJson(
            subset,
            name=f"{verdict} ({len(subset)})",
            style_function=_style,
            highlight_function=lambda f: {"weight": 3, "fillOpacity": 0.75},
            tooltip=folium.GeoJsonTooltip(
                fields=["municipality", "gross_acres", "score"],
                aliases=["Municipality", "Acres", "Score"], sticky=True),
            popup=folium.GeoJsonPopup(fields=popup_fields, aliases=aliases,
                                      max_width=420),
        ).add_to(m)

    # Centroid markers so small parcels stay findable when zoomed out.
    cluster = MarkerCluster(name="Parcel pins").add_to(m)
    for _, r in gdf.iterrows():
        pt = r.geometry.representative_point()
        folium.CircleMarker(
            location=[pt.y, pt.x],
            radius=3 + (r.get("score", 0) or 0) / 25,
            color=TRACK_COLORS.get(r.get("verdict"), "#6b7280"),
            fill=True, fill_opacity=0.9,
            tooltip=f"{r.get('municipality', '')} — {r.get('score', '')}/100",
        ).add_to(cluster)

    legend = """
    <div style="position:fixed;bottom:24px;left:24px;z-index:9999;
                background:rgba(255,255,255,.95);border:1px solid #d4d4d8;
                border-radius:8px;padding:12px 14px;font:13px/1.5 system-ui;
                box-shadow:0 2px 10px rgba(0,0,0,.12)">
      <div style="font-weight:700;margin-bottom:6px">NJ Land Screener</div>
      <div><span style="color:#16a34a">■</span> Track A + B — both paths open</div>
      <div><span style="color:#2563eb">■</span> Track A — plaza, retail by right</div>
      <div><span style="color:#ca8a04">■</span> Track B — farm market (Right to Farm)</div>
      <div><span style="color:#9333ea">■</span> Track B — verify ag permitted</div>
      <div><span style="color:#6b7280">■</span> Lifestyle only</div>
      <div style="margin-top:6px;color:#71717a">Opacity = composite score</div>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    folium.LayerControl(collapsed=False).add_to(m)

    out = Path(geojson_path).parent / cfg["output"]["map"]
    m.save(str(out))
    log(f"  wrote {out}")
    return out


if __name__ == "__main__":
    cfg = load_config()
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        cfg["_root"] / cfg["output"]["dir"] / cfg["output"]["geojson"]
    if not src.exists():
        sys.exit(f"[fatal] {src} not found — run screen.py first")
    build_map(src, cfg)
