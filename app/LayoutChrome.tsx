'use client'

import { usePathname } from 'next/navigation'
import Navigation from '@/components/layout/Navigation'
import Footer from '@/components/layout/Footer'
import type { ReactNode } from 'react'

export default function LayoutChrome({ children }: { children: ReactNode }) {
  const pathname = usePathname()
  if (pathname?.startsWith('/keystatic')) return <>{children}</>
  return (
    <>
      <Navigation />
      <main>{children}</main>
      <Footer />
    </>
  )
}
