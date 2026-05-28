export const dynamic = 'force-dynamic'

async function getHandler() {
  const { makeRouteHandler } = await import('@keystatic/next/route-handler')
  const { default: config } = await import('../../../../keystatic.config')
  return makeRouteHandler({ config })
}

function logEnvState() {
  console.log('[Keystatic] ENV:', JSON.stringify({
    hasClientId: !!process.env.KEYSTATIC_GITHUB_CLIENT_ID,
    clientIdLen: process.env.KEYSTATIC_GITHUB_CLIENT_ID?.length ?? 0,
    clientIdPrefix: process.env.KEYSTATIC_GITHUB_CLIENT_ID?.slice(0, 6) ?? '',
    hasClientSecret: !!process.env.KEYSTATIC_GITHUB_CLIENT_SECRET,
    clientSecretLen: process.env.KEYSTATIC_GITHUB_CLIENT_SECRET?.length ?? 0,
    hasSecret: !!process.env.KEYSTATIC_SECRET,
    secretLen: process.env.KEYSTATIC_SECRET?.length ?? 0,
  }))
}

export async function GET(request: Request) {
  const url = new URL(request.url)
  const isCallback = url.pathname.includes('/oauth/callback')
  if (isCallback) {
    console.log('[Keystatic] CALLBACK URL:', request.url)
    console.log('[Keystatic] CALLBACK hasCode:', url.searchParams.has('code'), 'hasState:', url.searchParams.has('state'), 'stateLen:', url.searchParams.get('state')?.length ?? 0)
    logEnvState()
  }
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
