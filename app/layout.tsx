import type { Metadata } from 'next'
import { Playfair_Display, Lora, IM_Fell_English } from 'next/font/google'
import './globals.css'
import Navigation from '@/components/layout/Navigation'
import Footer from '@/components/layout/Footer'
import CartProvider from '@/context/CartContext'

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
})

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://faridunhill.com'),
  title: {
    default: 'Faridunhill — Fine Pipes, Tobaccos & Gentleman\'s Accessories',
    template: '%s | Faridunhill',
  },
  description:
    'Purveyors of fine tobacco pipes, premium pipe tobacco, hand-rolled cigars, vaping products, and gentleman\'s accessories. Rooted in 30 years of collector knowledge and old-world craftsmanship.',
  keywords: [
    'tobacco pipes',
    'pipe tobacco',
    'cigars',
    'briar pipe',
    'meerschaum pipe',
    'estate pipes',
    'pipe accessories',
    'smoking accessories',
    'premium tobacco',
    'pipe shop',
  ],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    siteName: 'Faridunhill',
    title: 'Faridunhill — Fine Pipes, Tobaccos & Gentleman\'s Accessories',
    description:
      'Purveyors of fine tobacco pipes, premium pipe tobacco, hand-rolled cigars, and gentleman\'s accessories. Rooted in old-world craftsmanship.',
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
    title: 'Faridunhill — Fine Pipes & Tobaccos',
    description: 'Purveyors of fine pipes, tobaccos, and gentleman\'s accessories.',
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
          <Navigation />
          <main>{children}</main>
          <Footer />
        </CartProvider>
      </body>
    </html>
  )
}
