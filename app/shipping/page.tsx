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
          <p><strong className="text-parchment">Free shipping</strong> is provided on all orders of £75 or more shipped within the continental United States.</p>
          <p>Orders below £75 are charged a flat shipping rate of £8.95 for standard shipping. Expedited options are available at checkout:</p>
          <ul className="list-none space-y-2 pl-4 border-l border-gold/20">
            <li><span className="text-gold">Standard (3–7 business days):</span> £8.95, free over £75</li>
            <li><span className="text-gold">Expedited (2–3 business days):</span> $19.95</li>
            <li><span className="text-gold">Overnight (next business day):</span> $39.95</li>
          </ul>
          <p>We ship via UPS, FedEx, and USPS depending on package size, destination, and service selected. A tracking number is emailed as soon as the label is created, typically the morning after your order is placed.</p>
          <p>We do not ship to P.O. Boxes for orders over $200 or for tobacco products, due to carrier restrictions.</p>
        </Section>

        <Section title="Alaska, Hawaii & US Territories">
          <p>We ship to Alaska, Hawaii, Puerto Rico, Guam, and other US territories via USPS Priority Mail. Rates are calculated at checkout based on weight and destination. Free shipping thresholds apply to orders over $100 to these destinations. Delivery times are typically 5–10 business days.</p>
        </Section>

        <Section title="International Shipping">
          <p>We currently ship to Canada, the United Kingdom, Australia, and select European countries. International shipping rates are calculated at checkout based on destination, weight, and declared value.</p>
          <p><strong className="text-parchment">Important regarding tobacco products:</strong> Customs regulations for tobacco vary by country. The customer is responsible for ensuring that their order complies with their country&apos;s import laws and for paying any applicable customs duties, import taxes, or VAT. We are not responsible for packages held or seized by customs, and we cannot mark shipments as "gift" or misrepresent contents.</p>
          <p>We do not currently ship to the European Union, due to the complexity of tobacco import regulations across member states. We apologise for this limitation and are working to resolve it.</p>
          <p>International orders typically arrive within 10–21 business days, depending on the destination country and customs processing time.</p>
        </Section>

        <Section title="Age Verification for Tobacco Products">
          <p>All orders containing tobacco products — pipes, pipe tobacco, cigars, vaping products, and related items — are subject to mandatory age verification under US federal and state law. You must be 21 years of age or older to purchase tobacco products.</p>
          <p>By placing an order for tobacco products, you confirm that you are of legal age to purchase tobacco in your jurisdiction. We use a third-party age verification service at checkout. In some cases, your carrier may require an adult signature upon delivery. If you are not available to sign, the carrier will attempt redelivery or hold the package at the nearest facility for pickup.</p>
          <p>Orders for tobacco products cannot be left at the door without a signature. Please ensure someone of legal age is available to receive the delivery.</p>
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
