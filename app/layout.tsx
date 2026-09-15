import type { Metadata } from 'next'
import { Playfair_Display, Lora, IM_Fell_English } from 'next/font/google'
import './globals.css'
import CartProvider from '@/context/CartContext'
import AgeGate from '@/components/ui/AgeGate'
import LayoutChrome from './LayoutChrome'

const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair',
  display: 'swap',
  weight: ['400', '500', '600', '700', '800', '900'],
  style: ['normal', 'italic'],
})

const lora = Lora({
  subsets: ['latin'],
  variable: '--font-lora',
  display: 'swap',
  weight: ['400', '500', '600', '700'],
  style: ['normal', 'italic'],
})

const imFell = IM_Fell_English({
  subsets: ['latin'],
  variable: '--font-fell',
  display: 'swap',
  weight: '400',
  style: ['normal', 'italic'],
  adjustFontFallback: false,
})

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://faridunhill.com'),
  title: {
    default: 'Faridunhill — Estate Pipes, Vintage Leather & Smoking Accessories',
    template: '%s | Faridunhill',
  },
  description:
    'Purveyors of fine estate pipes, hand-carved meerschaums, rare collectibles, vintage leather, and gentleman\'s smoking accessories. Rooted in 30 years of collecting.',
  keywords: [
    'briar pipes',
    'briar pipe',
    'meerschaum pipe',
    'estate pipes',
    'pipe accessories',
    'smoking accessories',
    'vintage leather',
    'pipe shop',
  ],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    siteName: 'Faridunhill',
    title: 'Faridunhill — Estate Pipes, Vintage Leather & Smoking Accessories',
    description:
      'Purveyors of fine estate pipes, meerschaums, rare collectibles, and gentleman\'s smoking accessories. Rooted in old-world craftsmanship.',
    images: [
      {
        url: '/images/og-default.jpg',
        width: 1200,
        height: 630,
        alt: 'Faridunhill — Fine Tobacconists',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Faridunhill — Estate Pipes & Smoking Accessories',
    description: 'Estate pipes, vintage leather, and smoking accessories. Est. 2015.',
    images: ['/images/og-default.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="en"
      className={`${playfair.variable} ${lora.variable} ${imFell.variable}`}
    >
      <body className="bg-mahogany text-parchment font-lora antialiased">
        <CartProvider>
          <AgeGate />
          <LayoutChrome>{children}</LayoutChrome>
        </CartProvider>
      </body>
    </html>
  )
}
