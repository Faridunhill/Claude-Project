import Image from 'next/image'

/* Replace these Unsplash URLs with commissioned lifestyle photography.
   Each image should depict atmospheric pipe/tobacco scenes in warm, Victorian-adjacent settings.
   Target aspect ratios: landscape for wide shots, portrait for intimate scenes. */
const storyImages = [
  {
    src: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=900&q=85',
    alt: 'Two gentlemen in a warmly lit private library examine a tobacco tin by candlelight',
    caption:
      'It was nearly nine o\'clock when Harrington produced the tin from his coat — a Samuel Gawith blend he\'d kept back from a journey to Kendal the previous autumn. The library was quiet save for the tick of the grandfather clock and the occasional settling of the fire. He pressed the flake into the bowl with a deliberateness that suggested the evening had been planned with some care.',
    aspect: 'landscape',
  },
  {
    src: 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=700&q=85',
    alt: 'A meerschaum pipe resting on an open leather-bound volume, amber light falling across the bowl',
    caption:
      'The meerschaum had been his grandfather\'s — purchased in Vienna in the winter of 1923. It had coloured to a deep amber over the years, wearing its history in the gradations of its patina. He did not smoke it often. It was a pipe for important evenings, for decisions that deserved the weight of something older than himself.',
    aspect: 'portrait',
  },
  {
    src: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=900&q=85',
    alt: 'A selection of pipe tobacco tins arranged on a mahogany shelf',
    caption:
      'The tins arrived from London on a Tuesday, wrapped in brown paper and tied with twine in the old manner. He laid them out on the desk one by one — Dunhill, Samuel Gawith, Cornell & Diehl — each one a small promise. Outside, November pressed its grey face against the window. Inside, the lamp burned steadily, and the evening arranged itself around the agreeable question of which tin to open first.',
    aspect: 'landscape',
  },
  {
    src: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=700&q=85',
    alt: 'Hands cupping a lit briar pipe in late afternoon light',
    caption:
      'There is a particular quality to the first draw of a well-packed pipe — a resistance, then a give, and then the smoke comes, warm and slow, carrying with it the suggestion that the next hour need not be hurried. He sat back in the leather chair and watched the light change on the ceiling. The tobacco was Virginia, dark and sweet. The afternoon, at last, had found its proper pace.',
    aspect: 'portrait',
  },
  {
    src: 'https://images.unsplash.com/photo-1512909006721-3d6018887383?w=900&q=85',
    alt: 'A Victorian-style writing desk with a briar pipe, whiskey glass, and open correspondence',
    caption:
      'The letter from his brother arrived the same morning as the Peterson System he\'d ordered. He set them side by side on the desk — the pipe unsmoked, the letter unread — and regarded them both with equal anticipation. Some pleasures are better for being deferred. He lit the pipe first, as was only proper, and then broke the seal on the envelope, and read slowly, in the way that good letters deserve.',
    aspect: 'landscape',
  },
]

export default function PhotoGallery() {
  return (
    <section className="bg-mahogany py-24">
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12">
        {/* Header */}
        <div className="text-center mb-14">
          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Scenes from the Smoking Room ~</span>
          <h2 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-3">
            A Story in Smoke
          </h2>
          <div className="mt-4 max-w-xl mx-auto">
            <div className="h-px bg-gradient-to-r from-transparent via-gold/40 to-transparent" />
          </div>
        </div>

        {/* Gallery grid — alternating layout */}
        <div className="space-y-8">
          {storyImages.map((img, index) => (
            <div
              key={index}
              className={`flex flex-col ${
                index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'
              } gap-6 items-center`}
            >
              {/* Image */}
              <div className={`w-full ${img.aspect === 'portrait' ? 'lg:w-2/5' : 'lg:w-3/5'} flex-shrink-0`}>
                <div className="relative rounded-sm overflow-hidden gold-frame">
                  <div className={img.aspect === 'portrait' ? 'aspect-[3/4]' : 'aspect-[16/9]'}>
                    <Image
                      src={img.src}
                      alt={img.alt}
                      fill
                      className="object-cover"
                      sizes="(max-width: 1024px) 100vw, 60vw"
                    />
                    {/* Warm vignette */}
                    <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-mahogany/30 pointer-events-none" />
                  </div>
                  {/* Corner ornaments */}
                  <span className="absolute top-3 left-3 text-gold/40 text-xs">✦</span>
                  <span className="absolute bottom-3 right-3 text-gold/40 text-xs">✦</span>
                </div>
              </div>

              {/* Caption */}
              <div className={`w-full ${img.aspect === 'portrait' ? 'lg:w-3/5' : 'lg:w-2/5'}`}>
                <div className="border-l-2 border-gold/40 pl-6 py-2">
                  <span className="font-fell italic text-gold text-xs tracking-widest">
                    Scene {String(index + 1).padStart(2, '0')}
                  </span>
                  <p className="font-lora text-parchment/75 text-base leading-[1.95] mt-3">
                    {img.caption}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
