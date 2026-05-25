'use client'

import { useEffect } from 'react'

export default function StudioLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Bypass the age gate for Studio admin access
    try { sessionStorage.setItem('fh-age-verified', '1') } catch {}
  }, [])

  return <>{children}</>
}
