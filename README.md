# Faridunhill Store

Production-ready e-commerce website for **faridunhill.com** — a premium online smoke shop specialising in tobacco pipes, pipe tobacco, cigars, leather accessories, vaping products, and gentleman's accessories.

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS with custom Victorian design system
- **Payments:** Stripe Checkout (redirect to hosted checkout)
- **Email Collection:** Mailchimp API v3
- **Blog Engine:** MDX files in `/content/blog/`
- **Products:** JSON files in `/data/products/` (upgradeable to DB)
- **Deployment:** Vercel

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/faridunhill/claude-project.git
cd claude-project

# 2. Install dependencies
npm install

# 3. Set up environment variables
cp .env.example .env.local
# Fill in your Stripe and Mailchimp keys (see below)

# 4. Run the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment Variables

Copy `.env.example` to `.env.local` and fill in the values:

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (starts with `pk_test_` or `pk_live_`) |
| `STRIPE_SECRET_KEY` | Stripe secret key (starts with `sk_test_` or `sk_live_`) |
| `MAILCHIMP_API_KEY` | Mailchimp API key (ends with `-us1` or similar) |
| `MAILCHIMP_AUDIENCE_ID` | Mailchimp Audience/List ID |
| `MAILCHIMP_SERVER_PREFIX` | Mailchimp server prefix (e.g., `us1`) |
| `NEXT_PUBLIC_SITE_URL` | Your production URL (e.g., `https://faridunhill.com`) |

### Getting Your Keys

**Stripe (test mode):**
1. Go to [dashboard.stripe.com/test/apikeys](https://dashboard.stripe.com/test/apikeys)
2. Copy the publishable key and secret key

**Mailchimp:**
1. Go to Account → Extras → API Keys in Mailchimp
2. Create a new key
3. Find your Audience ID under Audience → Settings → Audience name and defaults

## Deployment to Vercel

1. Push this repository to GitHub
2. Go to [vercel.com](https://vercel.com) and import the repository
3. Add all environment variables in Project Settings → Environment Variables
4. Deploy — Vercel detects Next.js automatically

**Custom domain:**
1. In Vercel: Settings → Domains → Add `faridunhill.com`
2. At your DNS provider: add the CNAME record Vercel provides
3. SSL is automatic

## Project Structure

```
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout (fonts, navigation, footer)
│   ├── page.tsx            # Homepage
│   ├── shop/               # Department and product pages
│   ├── blog/               # Journal index and post pages
│   ├── about/              # About Us page
│   ├── contact/            # Contact form
│   ├── shipping/           # Shipping policy
│   ├── returns/            # Return policy
│   ├── privacy/            # Privacy policy
│   └── api/                # API routes (Stripe, Mailchimp)
├── components/
│   ├── layout/             # Navigation, Footer, CartDrawer
│   ├── home/               # Homepage sections
│   └── ui/                 # Shared UI components
├── content/blog/           # MDX blog posts
├── context/CartContext.tsx # Cart state management
├── data/products/          # JSON product data
└── lib/                    # Utilities (products, MDX, etc.)
```

## Adding Products

Edit the JSON files in `/data/products/`. Each file corresponds to a department. Product schema:

```json
{
  "id": "unique-id",
  "name": "Product Name",
  "brand": "Brand Name",
  "slug": "url-friendly-slug",
  "department": "tobacco-pipes",
  "category": "Briar Pipes",
  "price": 125.00,
  "originalPrice": null,
  "sku": "FH-PIPE-XXX",
  "images": ["https://your-image-url.com/image.jpg"],
  "featured": true,
  "inStock": true,
  "rating": 4.8,
  "reviewCount": 42,
  "description": "Editorial description of the product...",
  "tags": ["briar", "billiard", "premium"]
}
```

## Encyclopedia Builder

The site includes an **Encyclopedia** (`/encyclopedia`) of short presenter-led learning videos,
and a **Builder** (`/encyclopedia/builder`) that creates them: Claude writes the lesson script,
ElevenLabs narrates it in your cloned voice, and HeyGen renders your avatar — cartoon-styled or
built from a photo of your face — presenting it on camera. Entries live as MDX files in
`content/encyclopedia/`.

Full setup (voice cloning, avatar creation, API keys): see **[ENCYCLOPEDIA.md](./ENCYCLOPEDIA.md)**.

## Adding Blog Posts

Create a new `.mdx` file in `/content/blog/` with this frontmatter:

```mdx
---
title: "Post Title"
author: "Author Name"
date: "2025-05-25"
category: "Pipe Culture"
excerpt: "Brief excerpt for cards and SEO..."
image: "https://your-image-url.com/image.jpg"
tags: ["tag1", "tag2"]
---

Your post content here...
```

Categories: `Pipe Culture`, `Tobacco Reviews`, `Cigar Corner`, `Collector's Guide`, `How-To & Technique`, `News & New Arrivals`

## Going Live Checklist

- [ ] Replace all Unsplash placeholder images with commissioned photography
- [ ] Add real Stripe live keys in Vercel environment variables
- [ ] Verify Mailchimp API key and Audience ID are correct
- [ ] Set `NEXT_PUBLIC_SITE_URL` to `https://faridunhill.com`
- [ ] Configure Stripe webhook for order confirmation emails
- [ ] Add age verification service (e.g., AgeID, Veratad)
- [ ] Add Disqus shortname for blog comments
- [ ] Wire contact form to email service (Resend, SendGrid, etc.)
- [ ] Add Google Analytics or preferred analytics provider
- [ ] Test Stripe checkout in live mode with a real card
- [ ] Verify all department/product pages render correctly
- [ ] Run Lighthouse audit and address any scores below 90

## License

Private. All rights reserved — Faridunhill.
