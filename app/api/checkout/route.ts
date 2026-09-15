import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { getAllProducts } from '@/lib/products'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-06-20',
})

const CURRENCY = 'usd'
const MAX_LINES = 50
const MAX_QUANTITY_PER_LINE = 10

/**
 * What the browser is allowed to tell us: which product, and how many.
 * Price, name, and image are read from the catalogue server-side — a cart
 * payload that carries its own price lets anyone name their own total.
 */
interface CartLine {
  id: string
  quantity: number
}

function parseCart(raw: unknown): CartLine[] | null {
  if (!Array.isArray(raw) || raw.length === 0 || raw.length > MAX_LINES) return null

  const byId = new Map<string, number>()

  for (const entry of raw) {
    if (typeof entry !== 'object' || entry === null) return null
    const { id, quantity } = entry as { id?: unknown; quantity?: unknown }

    if (typeof id !== 'string' || id.length === 0 || id.length > 200) return null
    if (
      typeof quantity !== 'number' ||
      !Number.isInteger(quantity) ||
      quantity < 1 ||
      quantity > MAX_QUANTITY_PER_LINE
    ) {
      return null
    }

    const total = (byId.get(id) ?? 0) + quantity
    if (total > MAX_QUANTITY_PER_LINE) return null
    byId.set(id, total)
  }

  return Array.from(byId, ([id, quantity]) => ({ id, quantity }))
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => null)
    const lines = parseCart((body as { items?: unknown } | null)?.items)

    if (!lines) {
      return NextResponse.json({ error: 'Invalid cart.' }, { status: 400 })
    }

    const catalogue = await getAllProducts()
    const bySlug = new Map(catalogue.map((p) => [p.slug, p]))

    const lineItems: Stripe.Checkout.SessionCreateParams.LineItem[] = []

    for (const line of lines) {
      const product = bySlug.get(line.id)

      if (!product) {
        return NextResponse.json(
          { error: 'An item in your cart is no longer available.' },
          { status: 400 }
        )
      }
      if (!product.inStock) {
        return NextResponse.json(
          { error: `${product.name} is out of stock.` },
          { status: 400 }
        )
      }
      if (!Number.isFinite(product.price) || product.price <= 0) {
        console.error('Product has no usable price:', product.slug)
        return NextResponse.json(
          { error: 'An item in your cart is not available for purchase.' },
          { status: 400 }
        )
      }

      // Stripe needs a publicly reachable absolute URL, or no image at all.
      const image = product.images.find((url) => url.startsWith('https://'))

      lineItems.push({
        price_data: {
          currency: CURRENCY,
          product_data: {
            name: product.name,
            ...(image ? { images: [image] } : {}),
            metadata: {
              shop: 'faridunhill',
              slug: product.slug,
              sku: product.sku,
            },
          },
          unit_amount: Math.round(product.price * 100),
        },
        quantity: line.quantity,
      })
    }

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: lineItems,
      mode: 'payment',
      success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/?cart=open`,
      shipping_address_collection: {
        allowed_countries: ['US', 'CA', 'GB', 'AU'],
      },
      phone_number_collection: {
        enabled: true,
      },
      custom_text: {
        shipping_address: {
          message:
            'You must be 21 or older to purchase tobacco products. Orders containing tobacco require an adult signature on delivery.',
        },
        submit: {
          message: 'By completing your purchase, you confirm you are 21 years of age or older.',
        },
      },
      metadata: {
        source: 'faridunhill_store',
      },
    })

    return NextResponse.json({ url: session.url })
  } catch (error) {
    console.error('Stripe checkout error:', error)
    return NextResponse.json({ error: 'Failed to create checkout session' }, { status: 500 })
  }
}
