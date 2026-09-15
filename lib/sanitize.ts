/**
 * Helpers for values that arrive from the public internet.
 *
 * Anything a visitor types can reach an HTML email, a log line, or a third-party
 * API. Escape it at the boundary rather than trusting the sender.
 */

const HTML_ENTITIES: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}

/** Escape a string for interpolation into HTML text or an attribute value. */
export function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (char) => HTML_ENTITIES[char])
}

/**
 * Conservative email check. Not RFC 5322 — deliberately so. It rejects the
 * shapes that cause trouble downstream: whitespace, newlines (header
 * injection), commas and semicolons (recipient smuggling), and anything
 * without a single @ and a dotted domain.
 */
export function isValidEmail(value: unknown): value is string {
  if (typeof value !== 'string') return false
  const email = value.trim()
  if (email.length === 0 || email.length > 254) return false
  if (/[\s,;<>()[\]\\]/.test(email)) return false
  return /^[^@]+@[^@]+\.[^@]{2,}$/.test(email)
}

/** Trim and cap a free-text field, rejecting anything empty or oversized. */
export function boundedText(value: unknown, maxLength: number): string | null {
  if (typeof value !== 'string') return null
  const text = value.trim()
  if (text.length === 0 || text.length > maxLength) return null
  return text
}
