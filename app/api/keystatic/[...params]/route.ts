export const dynamic = 'force-dynamic'

async function getHandler() {
  const { makeRouteHandler } = await import('@keystatic/next/route-handler')
  const { default: config } = await import('../../../../keystatic.config')
  return makeRouteHandler({ config })
}

export async function GET(request: Request) {
  try {
    const handler = await getHandler()
    return handler.GET(request)
  } catch (err) {
    console.error('[Keystatic] GET error:', err)
    return new Response(
      JSON.stringify({ error: String(err) }),
      { status: 500, headers: { 'content-type': 'application/json' } }
    )
  }
}

export async function POST(request: Request) {
  try {
    const handler = await getHandler()
    return handler.POST(request)
  } catch (err) {
    console.error('[Keystatic] POST error:', err)
    return new Response(
      JSON.stringify({ error: String(err) }),
      { status: 500, headers: { 'content-type': 'application/json' } }
    )
  }
}
