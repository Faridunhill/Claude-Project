import type { Metadata } from 'next'
import BuilderStudio from '@/components/encyclopedia/BuilderStudio'

export const metadata: Metadata = {
  title: 'Encyclopedia Builder',
  description: 'Turn a topic into a presenter-led learning video in your own voice and likeness.',
  robots: { index: false },
}

export default function BuilderPage() {
  return (
    <div className="min-h-screen bg-mahogany">
      <div className="bg-mahogany-dark border-b border-gold/15 py-12 text-center px-6">
        <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ The Studio ~</span>
        <h1 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-3">
          Encyclopedia Builder
        </h1>
        <p className="font-lora text-parchment/55 max-w-xl mx-auto text-base mt-4">
          Pick a topic. Claude writes the lesson, your cloned voice narrates it, and your
          avatar — cartoon or your own face — presents it on camera.
        </p>
      </div>
      <BuilderStudio />
    </div>
  )
}
