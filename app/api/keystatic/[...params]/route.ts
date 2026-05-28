export const dynamic = 'force-dynamic'

async function getHandler() {
  const { makeRouteHandler } = await import('@keystatic/next/route-handler')
  const { default: config } = await import('../../../../keystatic.config')
  return makeRouteHandler({ config })
}

export async function GET(request: Request) {
  console.log('[Keystatic] GET', request.url)
  try {
    const handler = await getHandler()
    const res = await handler.GET(request)
    if (!res.ok) {
      const body = await res.clone().text()
      console.error('[Keystatic] GET non-ok response', res.status, body)
    }
    return res
  } catch (err) {
    console.error('[Keystatic] GET error:', err)
    return new Response(
      JSON.stringify({ error: String(err) }),
      { status: 500, headers: { 'content-type': 'application/json' } }
    )
  }
}

export async function POST(request: Request) {
  console.log('[Keystatic] POST', request.url)
  try {
    const handler = await getHandler()
    const res = await handler.POST(request)
    if (!res.ok) {
      const body = await res.clone().text()
      console.error('[Keystatic] POST non-ok response', res.status, body)
    }
    return res
  } catch (err) {
    console.error('[Keystatic] POST error:', err)
    return new Response(
      JSON.stringify({ error: String(err) }),
      { status: 500, headers: { 'content-type': 'application/json' } }
    )
  }
}
