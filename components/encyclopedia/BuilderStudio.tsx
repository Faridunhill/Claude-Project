'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'

interface GeneratedEntry {
  title: string
  slug: string
  category: string
  summary: string
  narration: string
  article: string
  tags: string[]
}

type VideoState =
  | { phase: 'idle' }
  | { phase: 'rendering'; videoId: string; status: string }
  | { phase: 'done'; videoUrl: string }
  | { phase: 'error'; message: string }

const AUDIENCES = ['curious adults', 'children (8–12)', 'teenagers', 'university level']

export default function BuilderStudio() {
  // Step 1 — brief
  const [topic, setTopic] = useState('')
  const [audience, setAudience] = useState(AUDIENCES[0])
  const [lengthMinutes, setLengthMinutes] = useState(3)
  const [notes, setNotes] = useState('')

  // Step 2 — script
  const [entry, setEntry] = useState<GeneratedEntry | null>(null)
  const [scriptLoading, setScriptLoading] = useState(false)
  const [scriptError, setScriptError] = useState('')

  // Step 3 — voice preview
  const [voiceLoading, setVoiceLoading] = useState(false)
  const [voiceError, setVoiceError] = useState('')
  const [audioSrc, setAudioSrc] = useState('')

  // Step 4 — video
  const [avatarMode, setAvatarMode] = useState<'avatar' | 'photo'>('avatar')
  const [video, setVideo] = useState<VideoState>({ phase: 'idle' })
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
      if (audioSrc) URL.revokeObjectURL(audioSrc)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function generateScript() {
    setScriptLoading(true)
    setScriptError('')
    try {
      const res = await fetch('/api/encyclopedia/script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, audience, lengthMinutes, notes }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Script generation failed')
      setEntry(data)
      setAudioSrc('')
      setVideo({ phase: 'idle' })
    } catch (err) {
      setScriptError(err instanceof Error ? err.message : 'Script generation failed')
    } finally {
      setScriptLoading(false)
    }
  }

  async function previewVoice() {
    if (!entry) return
    setVoiceLoading(true)
    setVoiceError('')
    try {
      const res = await fetch('/api/encyclopedia/voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: entry.narration.slice(0, 5000) }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.error || 'Voice preview failed')
      }
      const blob = await res.blob()
      if (audioSrc) URL.revokeObjectURL(audioSrc)
      setAudioSrc(URL.createObjectURL(blob))
    } catch (err) {
      setVoiceError(err instanceof Error ? err.message : 'Voice preview failed')
    } finally {
      setVoiceLoading(false)
    }
  }

  async function renderVideo() {
    if (!entry) return
    setVideo({ phase: 'rendering', videoId: '', status: 'submitting' })
    try {
      const res = await fetch('/api/encyclopedia/video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ narration: entry.narration, mode: avatarMode }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Video render failed')

      const videoId: string = data.videoId
      setVideo({ phase: 'rendering', videoId, status: 'queued' })

      pollRef.current = setInterval(async () => {
        try {
          const s = await fetch(`/api/encyclopedia/video?videoId=${encodeURIComponent(videoId)}`)
          const status = await s.json()
          if (!s.ok) throw new Error(status.error || 'Status check failed')
          if (status.status === 'completed' && status.videoUrl) {
            if (pollRef.current) clearInterval(pollRef.current)
            setVideo({ phase: 'done', videoUrl: status.videoUrl })
          } else if (status.status === 'failed') {
            if (pollRef.current) clearInterval(pollRef.current)
            setVideo({ phase: 'error', message: status.error?.message || 'Render failed in HeyGen' })
          } else {
            setVideo({ phase: 'rendering', videoId, status: status.status })
          }
        } catch (err) {
          if (pollRef.current) clearInterval(pollRef.current)
          setVideo({ phase: 'error', message: err instanceof Error ? err.message : 'Status check failed' })
        }
      }, 8000)
    } catch (err) {
      setVideo({ phase: 'error', message: err instanceof Error ? err.message : 'Video render failed' })
    }
  }

  function exportMdx() {
    if (!entry) return
    const videoUrl = video.phase === 'done' ? video.videoUrl : ''
    const frontmatter = [
      '---',
      `title: ${JSON.stringify(entry.title)}`,
      `category: ${JSON.stringify(entry.category)}`,
      `summary: ${JSON.stringify(entry.summary)}`,
      `date: ${JSON.stringify(new Date().toISOString().slice(0, 10))}`,
      `tags: [${entry.tags.map((t) => JSON.stringify(t)).join(', ')}]`,
      `videoUrl: ${JSON.stringify(videoUrl)}`,
      `audioUrl: ""`,
      `image: ""`,
      `narration: ${JSON.stringify(entry.narration)}`,
      '---',
      '',
      entry.article,
      '',
    ].join('\n')

    const blob = new Blob([frontmatter], { type: 'text/markdown' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${entry.slug}.mdx`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  const stepDone = 'border-gold/60 text-gold'
  const stepPending = 'border-gold/20 text-parchment/40'

  return (
    <div className="max-w-screen-md mx-auto px-6 py-12 space-y-10">
      {/* Step 1 — Brief */}
      <section className="bg-mahogany-light rounded-sm gold-frame p-6 lg:p-8">
        <div className="flex items-center gap-3 mb-5">
          <span className={`w-8 h-8 rounded-full border flex items-center justify-center font-playfair text-sm ${entry ? stepDone : 'border-gold text-gold'}`}>1</span>
          <h2 className="font-playfair font-bold text-parchment text-xl">Choose a topic</h2>
        </div>

        <label className="block font-lora text-parchment/70 text-sm mb-1">Topic</label>
        <input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. Why the Roman aqueducts still stand"
          className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment placeholder:text-parchment/25 focus:outline-none focus:border-gold/50 mb-4"
        />

        <div className="grid sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block font-lora text-parchment/70 text-sm mb-1">Audience</label>
            <select
              value={audience}
              onChange={(e) => setAudience(e.target.value)}
              className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment focus:outline-none focus:border-gold/50"
            >
              {AUDIENCES.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block font-lora text-parchment/70 text-sm mb-1">
              Video length — {lengthMinutes} min
            </label>
            <input
              type="range"
              min={1}
              max={10}
              value={lengthMinutes}
              onChange={(e) => setLengthMinutes(Number(e.target.value))}
              className="w-full mt-4 accent-[#C9A84C]"
            />
          </div>
        </div>

        <label className="block font-lora text-parchment/70 text-sm mb-1">Extra guidance (optional)</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          placeholder="Angles to cover, things to avoid, tone…"
          className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment placeholder:text-parchment/25 focus:outline-none focus:border-gold/50 mb-5"
        />

        <button
          onClick={generateScript}
          disabled={!topic.trim() || scriptLoading}
          className="bg-gold hover:bg-gold-light disabled:opacity-40 disabled:cursor-not-allowed text-mahogany font-playfair font-semibold px-6 py-3 rounded-sm transition-colors"
        >
          {scriptLoading ? 'Writing script…' : entry ? 'Regenerate script' : 'Generate script'}
        </button>
        {scriptError && <p className="mt-3 font-lora text-red-400 text-sm">{scriptError}</p>}
      </section>

      {/* Step 2 — Script review */}
      <section className={`bg-mahogany-light rounded-sm gold-frame p-6 lg:p-8 ${!entry ? 'opacity-50' : ''}`}>
        <div className="flex items-center gap-3 mb-5">
          <span className={`w-8 h-8 rounded-full border flex items-center justify-center font-playfair text-sm ${entry ? 'border-gold text-gold' : stepPending}`}>2</span>
          <h2 className="font-playfair font-bold text-parchment text-xl">Review the narration</h2>
        </div>

        {entry ? (
          <>
            <p className="font-playfair text-gold text-lg mb-1">{entry.title}</p>
            <p className="font-lora text-parchment/50 text-sm mb-4">
              {entry.category} · {entry.narration.split(/\s+/).length} spoken words
            </p>
            <label className="block font-lora text-parchment/70 text-sm mb-1">
              Narration (edit freely — this is what your avatar will say)
            </label>
            <textarea
              value={entry.narration}
              onChange={(e) => setEntry({ ...entry, narration: e.target.value })}
              rows={10}
              className="w-full bg-mahogany border border-gold/20 rounded-sm px-4 py-3 font-lora text-parchment leading-relaxed focus:outline-none focus:border-gold/50"
            />
            <div className="flex flex-wrap items-center gap-4 mt-4">
              <button
                onClick={previewVoice}
                disabled={voiceLoading}
                className="btn-ghost px-5 py-2.5 rounded-sm text-sm border border-gold/30 text-gold hover:bg-gold/10 transition-colors disabled:opacity-40"
              >
                {voiceLoading ? 'Generating audio…' : '▶ Preview in my voice'}
              </button>
              {audioSrc && <audio controls src={audioSrc} className="h-9" />}
            </div>
            {voiceError && <p className="mt-3 font-lora text-red-400 text-sm">{voiceError}</p>}
          </>
        ) : (
          <p className="font-lora text-parchment/40 text-sm">Generate a script first.</p>
        )}
      </section>

      {/* Step 3 — Render video */}
      <section className={`bg-mahogany-light rounded-sm gold-frame p-6 lg:p-8 ${!entry ? 'opacity-50' : ''}`}>
        <div className="flex items-center gap-3 mb-5">
          <span className={`w-8 h-8 rounded-full border flex items-center justify-center font-playfair text-sm ${video.phase === 'done' ? stepDone : stepPending}`}>3</span>
          <h2 className="font-playfair font-bold text-parchment text-xl">Render the presenter video</h2>
        </div>

        {entry ? (
          <>
            <div className="flex flex-wrap gap-3 mb-5">
              {(
                [
                  { key: 'avatar', label: 'Cartoon / styled avatar', hint: 'HEYGEN_AVATAR_ID' },
                  { key: 'photo', label: 'My face (talking photo)', hint: 'HEYGEN_TALKING_PHOTO_ID' },
                ] as const
              ).map((opt) => (
                <button
                  key={opt.key}
                  onClick={() => setAvatarMode(opt.key)}
                  className={`px-5 py-3 rounded-sm border font-lora text-sm transition-colors ${
                    avatarMode === opt.key
                      ? 'border-gold bg-gold/10 text-gold'
                      : 'border-gold/20 text-parchment/60 hover:border-gold/40'
                  }`}
                >
                  {opt.label}
                  <span className="block text-[10px] tracking-wide opacity-60 mt-0.5">{opt.hint}</span>
                </button>
              ))}
            </div>

            <button
              onClick={renderVideo}
              disabled={video.phase === 'rendering'}
              className="bg-gold hover:bg-gold-light disabled:opacity-40 text-mahogany font-playfair font-semibold px-6 py-3 rounded-sm transition-colors"
            >
              {video.phase === 'rendering' ? `Rendering… (${video.status})` : 'Render video'}
            </button>

            {video.phase === 'rendering' && (
              <p className="mt-3 font-lora text-parchment/50 text-sm">
                HeyGen is rendering — a few minutes for a {lengthMinutes}-minute video. This page polls automatically.
              </p>
            )}
            {video.phase === 'error' && (
              <p className="mt-3 font-lora text-red-400 text-sm">{video.message}</p>
            )}
            {video.phase === 'done' && (
              <div className="mt-5">
                <video controls src={video.videoUrl} className="w-full rounded-sm border border-gold/20" />
                <p className="mt-2 font-lora text-parchment/40 text-xs">
                  HeyGen download links expire — download the MP4 and re-host it (e.g. in /public or a CDN) before publishing.
                </p>
              </div>
            )}
          </>
        ) : (
          <p className="font-lora text-parchment/40 text-sm">Generate a script first.</p>
        )}
      </section>

      {/* Step 4 — Export */}
      <section className={`bg-mahogany-light rounded-sm gold-frame p-6 lg:p-8 ${!entry ? 'opacity-50' : ''}`}>
        <div className="flex items-center gap-3 mb-5">
          <span className={`w-8 h-8 rounded-full border flex items-center justify-center font-playfair text-sm ${stepPending}`}>4</span>
          <h2 className="font-playfair font-bold text-parchment text-xl">Publish the entry</h2>
        </div>

        {entry ? (
          <>
            <p className="font-lora text-parchment/60 text-sm leading-relaxed mb-5">
              Download the entry as an MDX file, drop it into{' '}
              <code className="text-gold/80">content/encyclopedia/</code>, commit, and deploy. It appears at{' '}
              <code className="text-gold/80">/encyclopedia/{entry.slug}</code>.
              {video.phase !== 'done' && ' (You can export now and add the videoUrl to the frontmatter later.)'}
            </p>
            <button
              onClick={exportMdx}
              className="bg-gold hover:bg-gold-light text-mahogany font-playfair font-semibold px-6 py-3 rounded-sm transition-colors"
            >
              Download {entry.slug}.mdx
            </button>
          </>
        ) : (
          <p className="font-lora text-parchment/40 text-sm">Generate a script first.</p>
        )}
      </section>

      <p className="text-center font-lora text-parchment/30 text-xs">
        Need setup help? See <span className="text-gold/60">ENCYCLOPEDIA.md</span> in the repository ·{' '}
        <Link href="/encyclopedia" className="text-gold/60 hover:text-gold">Back to the Encyclopedia</Link>
      </p>
    </div>
  )
}
