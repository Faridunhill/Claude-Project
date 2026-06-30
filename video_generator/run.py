"""
faridunhill.com Product Marketing Video Generator

Usage:
  python -m video_generator.run --product "pipe-001" --format vertical
  python -m video_generator.run --department cigars --format vertical
  python -m video_generator.run --product "Dunhill Shell Briar" --dry-run
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

from . import config
from . import composer
from . import footage
from . import llm
from . import products
from . import tts


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="video_generator",
        description="Generate a branded marketing video for faridunhill.com products.",
    )

    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--product", "-p",
        metavar="NAME_OR_ID",
        help="Product name (fuzzy match), ID (e.g. pipe-001), or slug.",
    )
    source.add_argument(
        "--department", "-d",
        metavar="DEPT",
        choices=list(config.DEPT_FILES.keys()),
        help="Department name. Generates a multi-product campaign video.",
    )

    p.add_argument(
        "--format", "-f",
        choices=["vertical", "landscape", "square"],
        default="vertical",
        help="Output format. Default: vertical (9:16 for Reels/TikTok).",
    )
    p.add_argument(
        "--max-products",
        type=int,
        default=4,
        metavar="N",
        help="Max products in a department campaign. Default: 4.",
    )
    p.add_argument(
        "--no-footage",
        action="store_true",
        help="Skip Pexels and use brand gradient background only.",
    )
    p.add_argument(
        "--output-dir",
        default=config.OUTPUT_DIR,
        metavar="PATH",
        help=f"Output directory. Default: {config.OUTPUT_DIR}",
    )
    p.add_argument(
        "--voice",
        default=config.TTS_VOICE,
        help=f"Edge TTS voice name. Default: {config.TTS_VOICE}",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated script as JSON without producing a video.",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print progress at each pipeline stage.",
    )

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    log = print if args.verbose else lambda *a, **kw: None

    # ── 1. Load product(s) ────────────────────────────────────────────────────
    if args.product:
        mode = "single"
        log(f"[1/6] Finding product: {args.product!r}")
        try:
            product = products.select_single(args.product)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        product_list = [product]
        dept = product.get("department")
        log(f"      Found: {product['name']} (${product.get('price', '?'):.2f})")
    else:
        mode = "department"
        dept = args.department
        log(f"[1/6] Loading department: {dept}")
        try:
            product_list = products.select_featured(dept, args.max_products)
        except (ValueError, FileNotFoundError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        product = None
        if not product_list:
            print(f"ERROR: No in-stock products found in department '{dept}'.", file=sys.stderr)
            sys.exit(1)
        log(f"      Selected {len(product_list)} products")

    prompt_products = [products.format_product_for_prompt(p) for p in product_list]

    # ── 2. Generate script ────────────────────────────────────────────────────
    log("[2/6] Generating marketing script with Claude...")
    try:
        script = llm.generate_script(prompt_products, args.format, mode)
    except Exception as e:
        print(f"ERROR: Script generation failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(json.dumps(script, indent=2))
        return

    log(f"      {len(script['segments'])} segments, ~{script['total_duration_seconds']}s")

    # ── 3–6: Audio + footage + compose ───────────────────────────────────────
    with tempfile.TemporaryDirectory(prefix="fh_video_") as tmpdir:

        # 3. Synthesize voiceover
        log("[3/6] Synthesizing voiceover (Edge TTS)...")
        try:
            tts_results = tts.synthesize_full_script(script, tmpdir, voice=args.voice)
        except Exception as e:
            print(f"ERROR: TTS synthesis failed: {e}", file=sys.stderr)
            sys.exit(1)
        total_audio = sum(r["duration_sec"] for r in tts_results)
        log(f"      Audio: {total_audio:.1f}s total")

        # 4. Fetch footage
        footage_clips: list[dict] = []
        if not args.no_footage:
            log("[4/6] Fetching B-roll footage from Pexels...")
            pexels_key = config.get_pexels_key()
            if pexels_key:
                footage_clips = footage.fetch_clips(
                    search_query=script["pexels_search_query"],
                    target_duration=total_audio,
                    video_format=args.format,
                    api_key=pexels_key,
                    department=dept,
                )
                log(f"      Got {len(footage_clips)} clips")
            else:
                log("      PEXELS_API_KEY not set — using brand gradient background")
        else:
            log("[4/6] Footage skipped (--no-footage)")

        # 5. Compose video
        log("[5/6] Composing video...")
        slug = product["slug"] if product else dept
        out_filename = f"{slug}_{args.format}.mp4"
        out_path = str(Path(args.output_dir) / out_filename)

        try:
            composer.compose_video(
                script=script,
                tts_results=tts_results,
                footage_clips=footage_clips,
                product=product,
                video_format=args.format,
                output_path=out_path,
            )
        except Exception as e:
            print(f"ERROR: Video composition failed: {e}", file=sys.stderr)
            sys.exit(1)

        # 6. Report
        log("[6/6] Done.")
        size_mb = Path(out_path).stat().st_size / 1_048_576
        print(f"\nVideo saved: {out_path}")
        print(f"Size:        {size_mb:.1f} MB")
        print(f"Format:      {args.format} {config.VIDEO_FORMATS[args.format]}")
        print(f"Duration:    {total_audio:.1f}s")


if __name__ == "__main__":
    main()
