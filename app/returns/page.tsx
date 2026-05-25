import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Return Policy',
  description: 'Faridunhill 30-day return policy. Clear process steps, condition requirements, and tobacco product exceptions explained.',
}

export default function ReturnsPage() {
  return (
    <div className="min-h-screen bg-mahogany">
      <div className="bg-mahogany-dark border-b border-gold/15 py-12">
        <div className="max-w-screen-lg mx-auto px-6 lg:px-12">
          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Information ~</span>
          <h1 className="font-playfair font-bold text-parchment text-4xl mt-2">Return Policy</h1>
          <p className="font-lora text-parchment/50 mt-2 text-sm">Last updated: May 2025</p>
        </div>
      </div>

      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-14 space-y-10">

        {/* Summary box */}
        <div className="bg-mahogany-light rounded-sm p-7 gold-frame">
          <h2 className="font-playfair font-bold text-parchment text-xl mb-3">The Short Version</h2>
          <p className="font-lora text-parchment/75 leading-relaxed">
            We accept returns on most items within 30 days of delivery, provided they are unused and in original condition.
            Tobacco products, opened tins, and pipes that have been smoked cannot be returned, for obvious reasons.
            If anything arrives damaged or not as described, we will make it right immediately, no questions asked.
          </p>
        </div>

        {/* Eligible items */}
        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">What Can Be Returned</h2>
          <div className="font-lora text-parchment/75 leading-[1.9] space-y-4">
            <p>The following items are eligible for return within 30 days of delivery:</p>
            <ul className="space-y-2 pl-4 border-l border-gold/20">
              <li><span className="text-gold">Pipes (new):</span> Unsmoked, in original condition with all original packaging.</li>
              <li><span className="text-gold">Accessories:</span> Unused pipe tools, cleaners, stands, cutters, humidors, and similar items in original condition.</li>
              <li><span className="text-gold">Leather goods:</span> Unused, with no signs of wear or use, in original packaging.</li>
              <li><span className="text-gold">Gift sets:</span> Unopened, with all original contents present.</li>
              <li><span className="text-gold">Lighters:</span> Unfilled and unused, in original condition.</li>
            </ul>
            <p>Items must be returned in the same condition in which they were received. We cannot accept returns on items that show signs of use, damage caused after delivery, or incomplete returns (missing parts, manuals, or packaging).</p>
          </div>
        </section>

        {/* Non-returnable */}
        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">What Cannot Be Returned</h2>
          <div className="font-lora text-parchment/75 leading-[1.9] space-y-4">
            <p>For health, safety, and regulatory reasons, the following items are non-returnable under all circumstances:</p>
            <ul className="space-y-2 pl-4 border-l border-gold/20">
              <li><span className="text-gold">All pipe tobacco:</span> Including opened and unopened tins. Tobacco products cannot be returned or exchanged once the transaction is complete.</li>
              <li><span className="text-gold">All cigars:</span> Once cigars leave our humidity-controlled storage, we cannot guarantee their condition upon return. No exceptions.</li>
              <li><span className="text-gold">All vaping products and e-liquids:</span> For health and safety reasons, these are non-returnable once shipped.</li>
              <li><span className="text-gold">Pipes that have been smoked:</span> Estate pipes and new pipes that show evidence of having been smoked cannot be returned. If you are uncertain whether a pipe is right for you, please contact us before purchasing — we are happy to advise.</li>
              <li><span className="text-gold">Personalised or custom items:</span> Including engraved items and made-to-order leather goods, unless they arrive defective or not as described.</li>
              <li><span className="text-gold">Sale & Clearance items:</span> All clearance sales are final.</li>
            </ul>
          </div>
        </section>

        {/* Process */}
        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">How to Initiate a Return</h2>
          <div className="font-lora text-parchment/75 leading-[1.9] space-y-4">
            <p>To initiate a return, please follow these steps:</p>
            <div className="space-y-5">
              {[
                { step: '01', title: 'Contact us first', body: 'Email us at returns@faridunhill.com or use our contact form, providing your order number, the item(s) you wish to return, and the reason for the return. Do not ship anything back until you have received a Return Merchandise Authorisation (RMA) number from us.' },
                { step: '02', title: 'Receive your RMA', body: 'We will respond within one business day with your RMA number and the return shipping address. Include the RMA number on your return package — packages without an RMA number may be delayed or refused.' },
                { step: '03', title: 'Package the item carefully', body: 'Use the original packaging where possible. Pipes should be wrapped to prevent movement and damage in transit. We are not responsible for items damaged during return shipping due to inadequate packaging.' },
                { step: '04', title: 'Ship it back', body: 'You are responsible for return shipping costs unless the return is due to our error (wrong item shipped, item not as described, or defective product). We recommend using a trackable shipping method; we are not responsible for return packages that are lost in transit.' },
                { step: '05', title: 'Receive your refund', body: 'Once we receive and inspect the return, we will process your refund within 3–5 business days. Refunds are issued to the original payment method. You will receive a confirmation email when the refund is processed.' },
              ].map((item) => (
                <div key={item.step} className="flex gap-5 bg-mahogany-light rounded-sm p-4 border border-gold/10">
                  <span className="font-playfair font-bold text-gold text-xl flex-shrink-0 w-8">{item.step}</span>
                  <div>
                    <p className="font-playfair font-semibold text-parchment mb-1">{item.title}</p>
                    <p className="text-parchment/65 text-sm">{item.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Damaged/wrong items */}
        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">Damaged or Incorrect Items</h2>
          <div className="font-lora text-parchment/75 leading-[1.9] space-y-4">
            <p>If your order arrives damaged or we sent you the wrong item, we will correct it immediately at no cost to you. Please photograph the item and packaging, then contact us within 48 hours of delivery. We will arrange free return shipping and either reship the correct item or issue a full refund, whichever you prefer.</p>
            <p>For estate pipes specifically: every estate pipe is described in detail and photographed carefully before listing. If the pipe arrives in substantially different condition than described, contact us within 5 days and we will make it right.</p>
          </div>
        </section>

        {/* Contact */}
        <div className="bg-mahogany-light rounded-sm p-7 gold-frame text-center">
          <p className="font-playfair font-semibold text-parchment text-lg mb-2">Questions?</p>
          <p className="font-lora text-parchment/65 text-sm mb-4">
            We are always happy to help. Our head tobacconist personally reviews every return enquiry.
          </p>
          <Link href="/contact" className="btn-gold inline-flex px-8 py-3 rounded-sm text-sm tracking-widest uppercase">
            Contact Us
          </Link>
        </div>
      </div>
    </div>
  )
}
