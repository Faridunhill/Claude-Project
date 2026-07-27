'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { BASE_CURRENCY, CURRENCIES } from '@/lib/currency'

interface CurrencyState {
  currency: string
  setCurrency: (code: string) => void
  /** True once the stored preference has been read on the client.
   *  Prices render in the base currency until then, so the server HTML
   *  and the first client paint agree (no hydration mismatch). */
  ready: boolean
}

const CurrencyContext = createContext<CurrencyState | undefined>(undefined)

const STORAGE_KEY = 'fh_currency'

export function CurrencyProvider({ children }: { children: React.ReactNode }) {
  const [currency, setCurrencyState] = useState<string>(BASE_CURRENCY)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved && CURRENCIES.some((c) => c.code === saved)) {
        setCurrencyState(saved)
      }
    } catch {
      /* private mode / storage disabled — stay on the base currency */
    }
    setReady(true)
  }, [])

  const setCurrency = (code: string) => {
    setCurrencyState(code)
    try {
      localStorage.setItem(STORAGE_KEY, code)
    } catch {
      /* preference just won't persist */
    }
  }

  return (
    <CurrencyContext.Provider value={{ currency, setCurrency, ready }}>
      {children}
    </CurrencyContext.Provider>
  )
}

export function useCurrency(): CurrencyState {
  const ctx = useContext(CurrencyContext)
  if (!ctx) throw new Error('useCurrency must be used within CurrencyProvider')
  return ctx
}
