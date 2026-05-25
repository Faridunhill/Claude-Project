import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description: 'Faridunhill privacy policy — how we collect, use, and protect your personal information.',
}

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-mahogany">
      <div className="bg-mahogany-dark border-b border-gold/15 py-12">
        <div className="max-w-screen-lg mx-auto px-6 lg:px-12">
          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Legal ~</span>
          <h1 className="font-playfair font-bold text-parchment text-4xl mt-2">Privacy Policy</h1>
          <p className="font-lora text-parchment/50 mt-2 text-sm">Last updated: May 2025</p>
        </div>
      </div>

      <div className="max-w-screen-lg mx-auto px-6 lg:px-12 py-14 space-y-10 font-lora text-parchment/75 leading-[1.9]">
        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">Overview</h2>
          <p>Faridunhill (&ldquo;we,&rdquo; &ldquo;us,&rdquo; &ldquo;our&rdquo;) is committed to protecting your personal information. This policy explains what information we collect, how we use it, and your rights with respect to it.</p>
        </section>

        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">Information We Collect</h2>
          <p>We collect the following categories of information:</p>
          <ul className="space-y-2 mt-3 pl-4 border-l border-gold/20">
            <li><strong className="text-parchment">Order information:</strong> Name, email, shipping address, and phone number (when provided), collected at checkout through Stripe&apos;s secure payment platform.</li>
            <li><strong className="text-parchment">Newsletter subscriptions:</strong> Email address and optional phone number, collected when you join the Gentleman&apos;s Circle.</li>
            <li><strong className="text-parchment">Usage data:</strong> Standard web analytics including pages visited, time on site, and general location data (country/region level). We use this data in aggregate to improve our website.</li>
          </ul>
        </section>

        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">How We Use Your Information</h2>
          <p>We use your information solely to: fulfil your orders; communicate with you about your orders; send newsletter and marketing communications you have opted into; comply with legal obligations (including age verification requirements); and improve our website and services.</p>
          <p className="mt-4"><strong className="text-parchment">We do not sell your personal information.</strong> We do not share your information with third parties except as necessary to fulfil your orders (shipping carriers) or as required by law.</p>
        </section>

        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">Your Rights</h2>
          <p>You have the right to access, correct, or delete your personal information. You may also opt out of marketing communications at any time by clicking the unsubscribe link in any email or by contacting us directly. To exercise any of these rights, contact us at <a href="mailto:privacy@faridunhill.com" className="text-gold hover:underline">privacy@faridunhill.com</a>.</p>
        </section>

        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">Payments</h2>
          <p>All payment processing is handled by Stripe. We do not store or have access to your credit card information. Stripe&apos;s privacy policy governs the handling of your payment data and can be found at stripe.com/privacy.</p>
        </section>

        <section>
          <h2 className="font-playfair font-bold text-parchment text-2xl mb-4 pb-3 border-b border-gold/15">Contact</h2>
          <p>For privacy questions or requests, contact us at <a href="mailto:privacy@faridunhill.com" className="text-gold hover:underline">privacy@faridunhill.com</a>.</p>
        </section>
      </div>
    </div>
  )
}
