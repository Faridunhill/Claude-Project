import { NextRequest, NextResponse } from 'next/server'
import { isValidEmail, boundedText } from '@/lib/sanitize'
import { rateLimit, clientKey } from '@/lib/rate-limit'

const RATE_LIMIT = 5
const RATE_WINDOW_MS = 10 * 60 * 1000

export async function POST(request: NextRequest) {
  try {
    const limit = rateLimit(clientKey(request, 'newsletter'), RATE_LIMIT, RATE_WINDOW_MS)
    if (!limit.ok) {
      return NextResponse.json(
        { error: 'Too many sign-ups. Please try again shortly.' },
        { status: 429, headers: { 'Retry-After': String(limit.retryAfter) } }
      )
    }

    const body = await request.json().catch(() => null)
    if (!body || typeof body !== 'object') {
      return NextResponse.json({ error: 'A valid email address is required.' }, { status: 400 })
    }

    const { email: rawEmail, phone: rawPhone } = body as Record<string, unknown>

    if (!isValidEmail(rawEmail)) {
      return NextResponse.json({ error: 'A valid email address is required.' }, { status: 400 })
    }
    const email = rawEmail.trim()
    const phone = rawPhone === undefined || rawPhone === null || rawPhone === ''
      ? ''
      : boundedText(rawPhone, 30)

    if (phone === null) {
      return NextResponse.json({ error: 'That phone number is not valid.' }, { status: 400 })
    }

    const apiKey = process.env.MAILCHIMP_API_KEY
    const audienceId = process.env.MAILCHIMP_AUDIENCE_ID
    const serverPrefix = process.env.MAILCHIMP_SERVER_PREFIX || 'us1'

    if (!apiKey || !audienceId) {
      console.error('Mailchimp env vars not set')
      return NextResponse.json({ error: 'Newsletter service unavailable.' }, { status: 503 })
    }

    const memberData: Record<string, unknown> = {
      email_address: email,
      status: 'subscribed',
      merge_fields: {
        PHONE: phone,
      },
      tags: ['website-signup', 'gentlemans-circle'],
    }

    const response = await fetch(
      `https://${serverPrefix}.api.mailchimp.com/3.0/lists/${audienceId}/members`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `apikey ${apiKey}`,
        },
        body: JSON.stringify(memberData),
      }
    )

    const data = await response.json()

    if (response.ok) {
      return NextResponse.json({ success: true })
    }

    /* Mailchimp returns 400 with title "Member Exists" if already subscribed — treat as success */
    if (data.title === 'Member Exists') {
      return NextResponse.json({ success: true })
    }

    console.error('Mailchimp error:', data)
    return NextResponse.json(
      { error: 'Unable to subscribe. Please try again.' },
      { status: 500 }
    )
  } catch (error) {
    console.error('Newsletter route error:', error)
    return NextResponse.json(
      { error: 'An unexpected error occurred.' },
      { status: 500 }
    )
  }
}
