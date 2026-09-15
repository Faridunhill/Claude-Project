# Encyclopedia Builder — Setup Guide

Turn any topic into a short learning video presented by **you** — your face (or a cartoon/styled avatar of you) and your cloned voice — plus a written encyclopedia entry for the site.

## How it works

```
Topic ──▶ Claude writes the lesson ──▶ ElevenLabs speaks it in your voice ──▶ HeyGen renders
          (narration + article)         (preview in the Builder)              your avatar presenting
                                                                                      │
                                                              /encyclopedia/<slug> ◀──┘
                                                              (MDX entry + video)
```

- **Library:** `/encyclopedia` — entries grouped by category
- **Entry page:** `/encyclopedia/<slug>` — video player + article
- **Studio:** `/encyclopedia/builder` — the four-step creation flow
- **Content:** one `.mdx` file per entry in `content/encyclopedia/`

## 1. Anthropic (script writing)

1. Create an API key at [platform.claude.com](https://platform.claude.com) → API Keys.
2. Set `ANTHROPIC_API_KEY` in `.env.local`.

The Builder calls Claude Opus 4.8 and returns a structured entry: title, category, a spoken
narration script (written for reading aloud on camera), and a longer written article.

## 2. ElevenLabs (your voice)

1. Sign up at [elevenlabs.io](https://elevenlabs.io) (voice cloning needs the Starter plan or above).
2. **Voices → Add voice → Instant Voice Clone.** Upload 1–3 minutes of clean recorded speech —
   a quiet room, no music, your natural presenting tone. Read varied sentences, not a monotone list.
3. You must confirm the voice is your own — cloning a voice you don't own violates their terms.
4. Copy the **Voice ID** from the voice's settings, and an **API key** from your profile.
5. Set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID`.

The Builder's "Preview in my voice" button uses this to let you hear the narration before
committing to a video render.

## 3. HeyGen (your avatar on camera)

1. Sign up at [heygen.com](https://heygen.com) (API access needs a Creator plan or an API plan;
   check current pricing — video rendering is credit-based).
2. Create your presenter. Two options, matching the two modes in the Builder:
   - **My face — "talking photo":** upload a clear, front-facing photo of yourself
     (HeyGen calls this a Photo/Instant Avatar). Copy its **Talking Photo ID** →
     `HEYGEN_TALKING_PHOTO_ID`. For higher quality, record the ~2-minute webcam footage flow
     to create a full video avatar instead, and use its ID as `HEYGEN_AVATAR_ID`.
   - **Cartoon / styled avatar:** in HeyGen, generate a stylized avatar (their AI avatar
     generator can produce an illustrated/cartoon look from your photo), or pick a studio
     avatar you like. Copy its **Avatar ID** → `HEYGEN_AVATAR_ID`.
3. Give HeyGen your voice: either create a **voice clone inside HeyGen**, or **link your
   ElevenLabs account** (HeyGen supports ElevenLabs integration) so your existing clone is
   available. Copy the resulting **Voice ID** → `HEYGEN_VOICE_ID`.
4. Create an **API key** (Settings → API) → `HEYGEN_API_KEY`.

> API shapes current as of mid-2026: the app calls `POST /v2/video/generate` and polls
> `GET /v1/video_status.get`. If HeyGen changes these, update
> `app/api/encyclopedia/video/route.ts`.

## 4. Publishing an entry

1. In the Builder, download the generated `.mdx` file.
2. **Re-host the video.** HeyGen's `video_url` links expire after a short time. Download the
   MP4 and either commit it under `public/videos/` (fine for a handful of small videos) or
   upload it to a CDN / bucket, then put that permanent URL in the entry's `videoUrl`
   frontmatter.
3. Drop the `.mdx` into `content/encyclopedia/`, optionally set a cover `image`, commit, push,
   deploy. The entry appears on `/encyclopedia` automatically.

### Entry frontmatter reference

```yaml
title: "Why Roman Concrete Outlasts Our Own"
category: "History"        # History | Science & Nature | Arts & Culture |
                           # Craft & Technique | People & Places | Language & Ideas
summary: "One-line teaser shown on cards."
date: "2026-07-23"
tags: ["engineering", "ancient rome"]
videoUrl: "/videos/roman-concrete.mp4"   # permanent URL — leave "" until rendered
audioUrl: ""                             # optional narration-only audio
image: "https://…"                       # card/poster image
narration: "The exact script the avatar speaks…"
```

## Costs, roughly

| Service | What you pay for |
|---|---|
| Anthropic | Per script — cents per entry on Opus 4.8 |
| ElevenLabs | Monthly plan with character quota; a 3-min narration ≈ 3,000 characters |
| HeyGen | Credits per rendered video minute — the dominant cost; check current plans |

## Notes

- The Builder page (`/encyclopedia/builder`) is `robots: noindex`, but it is **not**
  authenticated — anyone who finds the URL could spend your API credits. Before going live,
  either protect it (e.g. Vercel password protection / middleware with a shared secret) or
  keep the API keys out of the production environment and run the Builder locally.
- Only clone your **own** face and voice. Both ElevenLabs and HeyGen require consent
  verification, and impersonating others violates their terms and, in many places, the law.
