import asyncio
from pathlib import Path
from typing import TypedDict

import edge_tts

from . import config


class WordTiming(TypedDict):
    word: str
    start_sec: float
    end_sec: float


class TTSResult(TypedDict):
    audio_path: str
    duration_sec: float
    word_timings: list[WordTiming]


def synthesize_segment(
    text: str,
    output_path: str,
    voice: str = config.TTS_VOICE,
    rate: str = config.TTS_RATE,
) -> TTSResult:
    return asyncio.run(_async_synthesize(text, output_path, voice, rate))


async def _async_synthesize(
    text: str, output_path: str, voice: str, rate: str
) -> TTSResult:
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    word_timings: list[WordTiming] = []
    audio_bytes = bytearray()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            # Edge TTS uses 100-nanosecond units
            offset_sec = chunk["offset"] / 10_000_000
            duration_sec = chunk["duration"] / 10_000_000
            word_timings.append({
                "word": chunk["text"],
                "start_sec": offset_sec,
                "end_sec": offset_sec + duration_sec,
            })

    Path(output_path).write_bytes(bytes(audio_bytes))

    total_duration = word_timings[-1]["end_sec"] if word_timings else 0.0

    # Fallback: if no word timings, estimate from text length (avg 3 chars/sec)
    if not word_timings:
        total_duration = max(len(text) / 15, 2.0)

    return {
        "audio_path": output_path,
        "duration_sec": total_duration,
        "word_timings": word_timings,
    }


def synthesize_full_script(
    script: dict,
    temp_dir: str,
    voice: str = config.TTS_VOICE,
) -> list[TTSResult]:
    results = []
    for seg in script["segments"]:
        out_path = str(Path(temp_dir) / f"seg_{seg['index']:02d}.mp3")
        result = synthesize_segment(seg["spoken_text"], out_path, voice=voice)
        results.append(result)
    return results
