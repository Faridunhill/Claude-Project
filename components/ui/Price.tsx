'use client'

import { useCurrency } from '@/context/CurrencyContext'
import { formatFixed, formatPrice } from '@/lib/currency'

/**
 * Renders a BASE-currency (USD) catalogue amount in whatever currency
 * the customer has selected.
 */
export default function Price({
  amount,
  className,
}: {
  amount: number
  className?: string
}) {
  const { currency } = useCurrency()
  return <span className={className}>{formatPrice(amount, currency)}</span>
}

/**
 * Renders a historical realized price EXACTLY as it settled — never
 * converted. A sold price is a fact about a completed transaction; a
 * collector reading the archive as a comparable must see the real
 * figure, not today's rate applied to it.
 */
export function FixedPrice({
  amount,
  currency,
  className,
  showCode = true,
}: {
  amount: number
  currency: string
  className?: string
  showCode?: boolean
}) {
  return (
    <span className={className}>
      {formatFixed(amount, currency)}
      {showCode && (
        <span className="text-parchment/40 text-sm font-lora font-normal ml-1.5">
          {currency}
        </span>
      )}
    </span>
  )
}
