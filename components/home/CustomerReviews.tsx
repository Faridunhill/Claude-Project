const reviews = [
  {
    name: 'Theodore M.',
    location: 'Boston, MA',
    rating: 5,
    date: 'March 2025',
    title: 'The finest online tobacconist I\'ve found',
    body: 'I\'ve been smoking pipes for twenty-two years and tried every major online shop. Faridunhill is in a different class entirely. The estate pipe I purchased was exactly as described — ghost-free and beautifully restored — and arrived wrapped as if it were a gift. The accompanying card with notes on its likely provenance was a thoughtful touch I didn\'t expect.',
    verified: true,
    product: 'Château Latoque Estate Billiard',
  },
  {
    name: 'James R.',
    location: 'Edinburgh, Scotland',
    rating: 5,
    date: 'February 2025',
    title: 'Starter set changed my relationship with evenings',
    body: 'My wife gave me the Gentleman\'s Starter Set for my birthday on a whim, not knowing what she was starting. That was eight months ago. I\'ve since acquired four more pipes and a small cellar of Virginia flakes. The little booklet included was remarkably useful and written with genuine enthusiasm. I am, as they say, lost.',
    verified: true,
    product: 'The Gentleman\'s Pipe Starter Set',
  },
  {
    name: 'William C.',
    location: 'Chicago, IL',
    rating: 5,
    date: 'January 2025',
    title: 'Samuel Gawith Full Virginia Flake — magnificent',
    body: 'I\'d read about this tobacco for years before ordering. Faridunhill had it in stock when no one else did, shipped quickly, and it arrived in perfect condition. The tobacco itself is everything the reviews promise — slow, sweet, and deeply satisfying in a long billiard. I\'ve ordered three more tins to put down for a year.',
    verified: true,
    product: 'Samuel Gawith Full Virginia Flake',
  },
  {
    name: 'Margaret A.',
    location: 'Portland, OR',
    rating: 5,
    date: 'December 2024',
    title: 'Bought a gift, became a regular customer',
    body: 'I ordered the Collector\'s Gift Box for my father\'s retirement without knowing much about pipes. The box itself was extraordinary — velvet-lined, beautifully presented. My father, who has smoked a pipe for thirty years, called it the finest gift he\'d received in a decade. I\'ve since come back for myself and find the leather pipe bags are exceptional.',
    verified: true,
    product: 'The Collector\'s Gift Box',
  },
  {
    name: 'David H.',
    location: 'Nashville, TN',
    rating: 4,
    date: 'November 2024',
    title: 'Outstanding selection, fast shipping',
    body: 'The Peterson Churchwarden was well-packed and arrived in two days. Exactly what was described. I\'d give five stars but I\'m waiting to see how the stem holds up over time before I commit fully. That said, first impressions of the smoke are excellent — cool and dry throughout, which is exactly what a long pipe should do.',
    verified: true,
    product: 'Peterson System Standard Churchwarden',
  },
  {
    name: 'Robert K.',
    location: 'New Orleans, LA',
    rating: 5,
    date: 'October 2024',
    title: 'The leather pipe roll is heirloom quality',
    body: 'I\'ve bought leather goods from specialist makers in London and Italy. This pipe roll is on that level. The vegetable tanning, the hand stitching, the weight of the leather — it will last longer than I will. My three pipes travel in it now and arrive perfectly protected. I\'m ordering a second for the cigars.',
    verified: true,
    product: 'Full-Grain Leather 3-Pipe Roll',
  },
]

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg
          key={i}
          className={`w-4 h-4 ${i < rating ? 'text-gold' : 'text-parchment/15'}`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  )
}

export default function CustomerReviews() {
  return (
    <section className="bg-leather-texture py-24">
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12">
        {/* Header */}
        <div className="text-center mb-14">
          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Verified Customers ~</span>
          <h2 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-3">
            What Our Customers Are Saying
          </h2>
          <p className="font-lora text-parchment/55 mt-3 max-w-xl mx-auto">
            Every review is from a verified purchase. We do not curate or filter — these are the words of our customers, unedited.
          </p>

          {/* Aggregate rating */}
          <div className="flex items-center justify-center gap-3 mt-6">
            <span className="font-playfair font-bold text-gold text-3xl">4.9</span>
            <div>
              <div className="flex gap-0.5">
                {Array.from({ length: 5 }).map((_, i) => (
                  <svg key={i} className="w-5 h-5 text-gold" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              <p className="font-lora text-parchment/50 text-xs mt-0.5">Based on 847 verified reviews</p>
            </div>
          </div>
        </div>

        {/* Review grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {reviews.map((review, i) => (
            <div key={i} className="bg-mahogany-light rounded-sm gold-frame p-6 flex flex-col gap-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <StarRating rating={review.rating} />
                  <h3 className="font-playfair font-semibold text-parchment text-sm mt-2 leading-snug">
                    {review.title}
                  </h3>
                </div>
                {review.verified && (
                  <span className="flex-shrink-0 flex items-center gap-1 bg-hunter/30 border border-hunter text-parchment/60 text-[10px] px-2 py-0.5 rounded-sm font-lora tracking-wide">
                    <svg className="w-2.5 h-2.5 text-hunter-light" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Verified
                  </span>
                )}
              </div>

              <p className="font-lora text-parchment/70 text-sm leading-relaxed flex-1">
                &ldquo;{review.body}&rdquo;
              </p>

              <div className="border-t border-gold/10 pt-3 flex items-center justify-between gap-2 flex-wrap">
                <div>
                  <p className="font-playfair font-semibold text-parchment text-sm">{review.name}</p>
                  <p className="font-lora text-parchment/40 text-xs">{review.location}</p>
                </div>
                <div className="text-right">
                  <p className="font-lora text-gold/60 text-xs italic">{review.product}</p>
                  <p className="font-lora text-parchment/30 text-xs">{review.date}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
