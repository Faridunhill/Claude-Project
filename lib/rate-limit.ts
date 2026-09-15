/**
 * Fixed-window rate limiter, in process memory.
 *
 * LIMITATION, read before relying on this: serverless functions scale out, and
 * each instance keeps its own counters. An attacker spread across enough
 * concurrent instances gets a correspondingly higher effective limit, and
 * counters reset whenever an instance is recycled.
 *
 * This stops casual form spam and accidental double-submits. It is not a
 * defence against a determined attacker. For that, move the counter to shared
 * storage (Vercel KV, Upstash) or put Vercel's firewall in front of the route.
 */

interface Window {
  count: number
  resetAt: number
}

const windows = new Map<string, Window>()
const MAX_TRACKED_KEYS = 10_000

function sweep(now: number) {
  // forEach rather than for..of: this project's tsconfig has no `target`, so
  // Map iteration is not downlevel-compiled. Deleting during forEach is safe.
  windows.forEach((window, key) => {
    if (window.resetAt <= now) windows.delete(key)
  })
}

export interface RateLimitResult {
  ok: boolean
  /** Seconds until the caller may retry. Zero when `ok`. */
  retryAfter: number
}

export function rateLimit(key: string, limit: number, windowMs: number): RateLimitResult {
  const now = Date.now()
  const existing = windows.get(key)

  if (!existing || existing.resetAt <= now) {
    // Bound memory before inserting: a flood of unique keys must not grow
    // without limit. Sweeping expired entries first usually frees enough.
    if (windows.size >= MAX_TRACKED_KEYS) {
      sweep(now)
      if (windows.size >= MAX_TRACKED_KEYS) windows.clear()
    }
    windows.set(key, { count: 1, resetAt: now + windowMs })
    return { ok: true, retryAfter: 0 }
  }

  if (existing.count >= limit) {
    return { ok: false, retryAfter: Math.ceil((existing.resetAt - now) / 1000) }
  }

  existing.count += 1
  return { ok: true, retryAfter: 0 }
}

/**
 * Best-effort client identity. `x-forwarded-for` is attacker-controlled in
 * general, but on Vercel the platform overwrites it, so the leftmost entry is
 * the real client. Falls back to a shared bucket rather than failing open per
 * request.
 */
export function clientKey(request: Request, scope: string): string {
  const forwarded = request.headers.get('x-forwarded-for')
  const ip = forwarded?.split(',')[0]?.trim() || request.headers.get('x-real-ip') || 'unknown'
  return `${scope}:${ip}`
}
