import { NextRequest, NextResponse } from 'next/server'

const RESEND_API_KEY = process.env.RESEND_API_KEY
const TO_EMAIL = 'vintagepipevault@gmail.com'

export async function POST(request: NextRequest) {
  try {
    const { name, email, subject, message } = await request.json()

    if (!name || !email || !subject || !message) {
      return NextResponse.json({ error: 'All fields are required.' }, { status: 400 })
    }

    if (!RESEND_API_KEY) {
      console.error('RESEND_API_KEY not set')
      return NextResponse.json({ error: 'Email service unavailable.' }, { status: 503 })
    }

    const subjectLabels: Record<string, string> = {
      product: 'Product Question',
      order: 'Order Enquiry',
      estate: 'Estate Pipe Enquiry',
      advice: 'Pipe Smoking Advice',
      return: 'Return or Exchange',
      other: 'General Enquiry',
    }

    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from: 'Faridunhill Contact Form <contact@faridunhill.com>',
        to: [TO_EMAIL],
        reply_to: email,
        subject: `[Faridunhill] ${subjectLabels[subject] ?? subject} — from ${name}`,
        html: `
          <div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 32px; background: #f5edd6; color: #2c1810;">
            <div style="border-bottom: 2px solid #c9a84c; padding-bottom: 16px; margin-bottom: 24px;">
              <h2 style="font-size: 22px; margin: 0; color: #2c1810;">New Contact Form Submission</h2>
              <p style="margin: 4px 0 0; color: #8b6b4a; font-style: italic;">Faridunhill — faridunhill.com</p>
            </div>

            <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
              <tr>
                <td style="padding: 8px 0; color: #8b6b4a; width: 120px; vertical-align: top;">Name</td>
                <td style="padding: 8px 0; font-weight: bold;">${name}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #8b6b4a; vertical-align: top;">Email</td>
                <td style="padding: 8px 0;"><a href="mailto:${email}" style="color: #c9a84c;">${email}</a></td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #8b6b4a; vertical-align: top;">Subject</td>
                <td style="padding: 8px 0;">${subjectLabels[subject] ?? subject}</td>
              </tr>
            </table>

            <div style="background: #fff8ec; border-left: 3px solid #c9a84c; padding: 16px 20px; border-radius: 2px;">
              <p style="margin: 0; line-height: 1.8; white-space: pre-wrap;">${message.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>
            </div>

            <p style="margin-top: 24px; font-size: 12px; color: #8b6b4a; border-top: 1px solid #d4c4a0; padding-top: 16px;">
              Reply directly to this email to respond to ${name}.
            </p>
          </div>
        `,
      }),
    })

    if (!res.ok) {
      const error = await res.json()
      console.error('Resend error:', error)
      return NextResponse.json({ error: 'Failed to send message.' }, { status: 500 })
    }

    return NextResponse.json({ success: true })
  } catch (err) {
    console.error('Contact route error:', err)
    return NextResponse.json({ error: 'An unexpected error occurred.' }, { status: 500 })
  }
}
