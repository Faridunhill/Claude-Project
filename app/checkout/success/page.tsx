import Link from 'next/link'

export default function CheckoutSuccessPage() {
  return (
    <div className="min-h-screen bg-mahogany flex items-center justify-center px-6">
      <div className="text-center max-w-lg">
        <div className="text-gold text-6xl mb-6">✦</div>
        <h1 className="font-playfair font-bold text-parchment text-4xl mb-4">Order Confirmed</h1>
        <div className="h-px bg-gradient-to-r from-transparent via-gold/40 to-transparent my-6" />
        <p className="font-lora text-parchment/70 leading-relaxed mb-4">
          Thank you for your order. A confirmation email is on its way to you. We will process
          and ship your order within 1–2 business days.
        </p>
        <p className="font-lora text-parchment/50 text-sm mb-8">
          If you ordered tobacco products, remember that an adult signature will be required upon delivery.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/shop" className="btn-gold px-8 py-3.5 rounded-sm text-sm tracking-widest uppercase">
            Continue Shopping
          </Link>
          <Link href="/blog" className="btn-ghost px-8 py-3.5 rounded-sm text-sm tracking-widest uppercase">
            Read the Journal
          </Link>
        </div>
        <p className="font-fell italic text-gold/40 text-base mt-12">
          &ldquo;Light slowly. Smoke slowly. Savour everything.&rdquo;
        </p>
      </div>
    </div>
  )
}
