/**
 * Store currency.
 *
 * BASE = USD. Every `price` in the catalogue is a US dollar figure —
 * they were imported from the dollar eBay/Etsy listings. A previous
 * change relabelled them as GBP without converting, which silently
 * marked the whole shop up by roughly a third; that is why the base
 * is pinned here in one place rather than typed as a symbol into a
 * dozen JSX files.
 *
 * Customers may VIEW prices in another currency. The conversion is
 * indicative only — checkout always charges in the base currency, and
 * the UI says so. Displaying one currency and silently charging
 * another is the exact bug this module exists to prevent.
 */

export const BASE_CURRENCY = 'USD' as const

export interface CurrencyDef {
  code: string
  symbol: string
  label: string
  /** Units of this currency per 1 USD. */
  rate: number
}

/**
 * Indicative rates, hand-maintained. Update with `RATES_UPDATED` when
 * you change them. Deliberately static: the site is statically
 * generated, so a build-time fetch would freeze a rate into the HTML
 * with no way to tell how stale it is.
 */
export const RATES_UPDATED = '2026-07-27'

export const CURRENCIES: CurrencyDef[] = [
  { code: 'USD', symbol: '$', label: 'US Dollar', rate: 1 },
  { code: 'GBP', symbol: '£', label: 'British Pound', rate: 0.74 },
  { code: 'EUR', symbol: '€', label: 'Euro', rate: 0.86 },
  { code: 'CAD', symbol: 'C$', label: 'Canadian Dollar', rate: 1.37 },
  { code: 'AUD', symbol: 'A$', label: 'Australian Dollar', rate: 1.51 },
]

export function getCurrency(code: string): CurrencyDef {
  return CURRENCIES.find((c) => c.code === code?.toUpperCase()) ?? CURRENCIES[0]
}

/** Convert a base-currency (USD) amount into `code`. */
export function convert(amountUsd: number, code: string): number {
  return amountUsd * getCurrency(code).rate
}

/**
 * Format a BASE-currency amount for display in `code`.
 * Pass a non-USD code only where the UI also makes the charge
 * currency clear.
 */
export function formatPrice(amountUsd: number, code: string = BASE_CURRENCY): string {
  const c = getCurrency(code)
  return `${c.symbol}${convert(amountUsd, code).toFixed(2)}`
}

/**
 * Format an amount that is ALREADY in `code` — no conversion.
 * Used for historical realized prices in the sold archive: a price a
 * pipe actually fetched is a fact recorded in the currency it settled
 * in, and must never be re-expressed through today's rate.
 */
export function formatFixed(amount: number, code: string): string {
  return `${getCurrency(code).symbol}${amount.toFixed(2)}`
}
