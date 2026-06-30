import json
from typing import Literal

import anthropic

from . import config

_SYSTEM_PROMPT = f"""You are a copywriter for {config.STORE_URL}, a premium smoke shop with a Victorian-era aesthetic.
Your task is to write a punchy 30-60 second social media marketing video script.

Tone: Confident, literary, and aspirational — like a well-read gentleman writing copy.
Never use generic phrases like "amazing", "incredible", or "don't miss out".
Pricing should feel like a statement of quality, not a bargain pitch.
Always end with the call to action: "Shop now at {config.STORE_URL}"

Respond ONLY with valid JSON matching this exact schema — no markdown, no commentary:
{{
  "total_duration_seconds": <integer 30-60>,
  "pexels_search_query": "<3-5 word specific search term for B-roll footage>",
  "segments": [
    {{
      "index": 0,
      "type": "hook",
      "spoken_text": "<voiceover text for this segment>",
      "display_text": "<short on-screen text, max 8 words>",
      "duration_seconds": <float>,
      "style": "title"
    }}
  ]
}}

Segment types (in order):
- "hook": exactly 1 segment, 3-5s, style "title"
- "highlight": 2-4 segments, 4-8s each, style "subtitle" or "price"
- "cta": exactly 1 segment, 5-7s, style "cta"

Style values: "title", "subtitle", "price", "cta"
The last segment MUST be type "cta" with spoken_text ending in "Shop now at {config.STORE_URL}"
Use style "price" for the segment that mentions the product price.
"""


ScriptSegment = dict
VideoScript = dict


def generate_script(
    products: list[dict],
    video_format: str,
    mode: Literal["single", "department"],
    *,
    max_retries: int = 2,
) -> VideoScript:
    client = anthropic.Anthropic(api_key=config.get_anthropic_key())
    user_message = _build_user_message(products, video_format, mode)

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        message = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = message.content[0].text.strip()

        # Strip accidental markdown fences
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:].lstrip()

        try:
            script = json.loads(raw)
            _validate_script(script)
            return script
        except (json.JSONDecodeError, AssertionError, KeyError) as e:
            last_error = e
            if attempt < max_retries:
                continue

    raise ValueError(
        f"Claude returned an invalid script after {max_retries + 1} attempts: {last_error}"
    )


def _build_user_message(products: list[dict], video_format: str, mode: str) -> str:
    if mode == "single":
        product = products[0]
        return (
            f"Create a 30-45 second video script for this single product:\n\n"
            f"{json.dumps(product, indent=2)}\n\n"
            f"Video format: {video_format}\n"
            f"Hook: name the product and brand immediately.\n"
            f"Include 2-3 highlight segments: price, a standout spec or origin, and one line of brand story.\n"
            f"Keep display_text concise — it will appear as a large on-screen overlay."
        )
    else:
        return (
            f"Create a 45-60 second department campaign script featuring these {len(products)} products:\n\n"
            f"{json.dumps(products, indent=2)}\n\n"
            f"Video format: {video_format}\n"
            f"Hook: name the department category (e.g. 'Premium Tobacco Pipes').\n"
            f"Each product gets one highlight segment — focus on its most distinctive quality or price.\n"
            f"CTA segment should reference the department."
        )


def _validate_script(script: dict) -> None:
    assert "segments" in script, "Missing 'segments'"
    assert isinstance(script["segments"], list), "'segments' must be a list"
    assert len(script["segments"]) >= 2, "Need at least 2 segments"
    assert "pexels_search_query" in script, "Missing 'pexels_search_query'"
    last = script["segments"][-1]
    assert last.get("type") == "cta", "Last segment must be type 'cta'"
    for seg in script["segments"]:
        for field in ("index", "type", "spoken_text", "display_text", "duration_seconds", "style"):
            assert field in seg, f"Segment missing field: {field}"
