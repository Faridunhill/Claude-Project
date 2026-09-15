import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Shipping Policy',
  description: 'Faridunhill shipping policy — processing times, carriers, domestic and international rates, age verification, and order tracking.',
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-10">
      <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">{title}</h2>
      <div className="space-y-4 font-lora text-parchment/75 leading-[1.9] text-[1.02rem]">{children}</div>
    </section>
  )
}

export default function ShippingPage() {
  return (
    <div className="min-h-screen bg-mahogany">
      <div className="bg-mahogany-dark border-b border-gold/15 py-12">
        <div className="max-w-screen-lg mx-auto px-6 lg:px-12">
          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Information ~</span>
          <h1 className="font-playfair font-bold text-parchment text-4xl mt-2">Shipping Policy</h1>
          <p className="font-lora text-parchment/50 mt-2 text-sm">Last updated: May 2025</p>
        </div>
      </div>

      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-14">

        <Section title="Processing Time">
          <p>Orders are processed within 1–2 business days of receipt. Orders placed on Friday after 2 PM EST, Saturday, or Sunday are processed on the following Monday.</p>
          <p>During peak periods (holiday season, major new arrivals), processing time may extend to 2–3 business days. We will notify you by email if your order will be delayed beyond our standard window.</p>
          <p>Custom and personalised orders — including engraved items and made-to-order leather goods — carry additional production times, which are specified on the product page and confirmed at checkout.</p>
        </Section>

        <Section title="Domestic Shipping (United States)">
          <p><strong className="text-parchment">Shipping is free on every order</strong>, with no minimum, anywhere we ship. There is no shipping line at checkout because there is no shipping charge — the price you see on the product page is the price you pay.</p>
          <p>Standard delivery within the United States is typically 3–7 business days.</p>
          <p>We ship via UPS, FedEx, and USPS depending on package size, destination, and service selected. A tracking number is emailed as soon as the label is created, typically the morning after your order is placed.</p>
          <p>We can ship to P.O. Boxes where the carrier allows it. Larger or higher-value parcels may require a street address.</p>
        </Section>

        <Section title="Alaska, Hawaii & US Territories">
          <p>We ship to Alaska, Hawaii, Puerto Rico, Guam, and other US territories via USPS Priority Mail, free of charge like every other order. Delivery times are typically 5–10 business days.</p>
        </Section>

        <Section title="International Shipping">
          <p>We ship to Canada, the United Kingdom, Australia, and the European Union. International shipping is free, like every other order. You remain responsible for any customs duties, import taxes, or VAT your own country charges on arrival — those are levied by your government, not by us, and we cannot predict or prepay them.</p>
          <p>We sell no consumable tobacco — no tins, no cigars, no vaping products — so the tobacco import restrictions that complicate cross-border orders do not apply to anything in our catalogue. What we ship is pipes, leather goods, and accessories.</p>
          <p>Two practical notes. Lighters are shipped empty and by surface where regulations require it, which can add a few days. And we declare every parcel honestly: we cannot mark a shipment as a &ldquo;gift&rdquo; or understate its value, and we are not responsible for parcels held or seized by customs.</p>
          <p>International orders typically arrive within 10–21 business days, depending on the destination country and customs processing time.</p>
        </Section>

        <Section title="Age Verification">
          <p>We sell smoking accessories — pipes, leather goods, cutters, lighters and stands — and no consumable tobacco. Even so, several US states restrict the sale of smoking paraphernalia to adults, and we apply a single rule everywhere rather than guessing at your local one: <strong className="text-parchment">you must be 21 or older to buy from us.</strong></p>
          <p>You confirm your age twice: once when you enter the site, and again when you complete your order. Both are declarations you make yourself. We do not currently run an identity check against a third-party database, so the responsibility for answering honestly is yours.</p>
          <p>Most orders ship without a signature requirement. Where a parcel is high in value we may add adult signature on delivery, in which case the carrier will ask for photo ID; if nobody is available to sign, they will attempt redelivery or hold the package at the nearest facility for pickup.</p>
        </Section>

        <Section title="Order Tracking">
          <p>A tracking number is included in your shipping confirmation email. You can track your order directly on the carrier&apos;s website. If your tracking number shows no movement after 48 hours, please contact us — occasionally labels are created before handoff to the carrier.</p>
        </Section>

        <Section title="Damaged or Lost Shipments">
          <p>If your order arrives damaged, please photograph the packaging and contents immediately and contact us within 48 hours of delivery. We will file a claim with the carrier and arrange replacement or refund as appropriate.</p>
          <p>For shipments that appear lost (no tracking updates for 7+ business days), please contact us and we will investigate with the carrier. We will make you whole — either by reshipping or refunding — once the carrier investigation is complete.</p>
        </Section>

        <Section title="Contact">
          <p>For shipping questions, contact us at <a href="mailto:shipping@faridunhill.com" className="text-gold hover:underline">shipping@faridunhill.com</a> or through our <a href="/contact" className="text-gold hover:underline">contact form</a>. We respond to all enquiries within one business day.</p>
        </Section>
      </div>
    </div>
  )
}
