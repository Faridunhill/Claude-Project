import { marketplaceRecord } from '@/lib/links'

/**
 * Public seller statistics from eBay and Etsy, each linked to its source.
 *
 * Every figure is checkable by the person reading it — which is the only
 * reason it belongs on the page.
 */
export default function MarketplaceRecord() {
  return (
    <div className="grid sm:grid-cols-2 gap-4">
      {marketplaceRecord.platforms.map((platform) => (
        <a
          key={platform.name}
          href={platform.href}
          target="_blank"
          rel="noopener noreferrer"
          className="block bg-mahogany-light rounded-sm p-6 gold-frame hover:border-gold/50 transition-colors group"
        >
          <p className="font-playfair font-bold text-parchment text-lg mb-4 group-hover:text-gold transition-colors">
            {platform.name}
          </p>
          <dl className="space-y-3">
            {platform.stats.map((stat) => (
              <div key={stat.label}>
                <dt className="sr-only">{stat.label}</dt>
                <dd>
                  <span className="font-playfair font-bold text-gold text-2xl">{stat.value}</span>{' '}
                  <span className="font-lora text-parchment/60 text-sm">{stat.label}</span>
                </dd>
              </div>
            ))}
          </dl>
          <p className="font-lora text-parchment/40 text-xs mt-5 group-hover:text-gold/60 transition-colors">
            Check it yourself &rarr;
          </p>
        </a>
      ))}
    </div>
  )
}
