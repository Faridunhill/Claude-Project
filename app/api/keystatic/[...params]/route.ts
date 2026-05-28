export const dynamic = 'force-dynamic'

async function getHandler() {
  const { makeRouteHandler } = await import('@keystatic/next/route-handler')
  const { default: config } = await import('../../../../keystatic.config')
  return makeRouteHandler({ config })
}

function cleanRequest(request: Request): Request {
  const url = new URL(request.url)
  // Strip Next.js internal routing params that can confuse Keystatic
  url.searchParams.delete('nxtPparams')
  url.searchParams.delete('nxtPslug')
  if (url.toString() === request.url) return request
  return new Request(url.toString(), request)
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
  const isLogin = url.pathname.endsWith('/github/login')
  const isDebug = url.pathname.endsWith('/debug')

  // Temporary debug endpoint — remove after auth is working
  if (isDebug) {
    const envInfo = {
      hasClientId: !!process.env.KEYSTATIC_GITHUB_CLIENT_ID,
      clientIdLen: process.env.KEYSTATIC_GITHUB_CLIENT_ID?.length ?? 0,
      clientIdPrefix: process.env.KEYSTATIC_GITHUB_CLIENT_ID?.slice(0, 6) ?? '',
      hasClientSecret: !!process.env.KEYSTATIC_GITHUB_CLIENT_SECRET,
      clientSecretLen: process.env.KEYSTATIC_GITHUB_CLIENT_SECRET?.length ?? 0,
      hasSecret: !!process.env.KEYSTATIC_SECRET,
      secretLen: process.env.KEYSTATIC_SECRET?.length ?? 0,
      nodeVersion: process.version,
    }
    // Simulate a login request to capture what GitHub URL Keystatic generates
    let loginDebug: Record<string, unknown> = {}
    try {
      const handler = await getHandler()
      const loginReq = new Request(`${url.origin}/api/keystatic/github/login`, { method: 'GET', headers: request.headers })
      const loginRes = await handler.GET(loginReq)
      const location = loginRes.headers.get('location') ?? ''
      try {
        const ghUrl = new URL(location)
        loginDebug = {
          redirectStatus: loginRes.status,
          githubClientId: ghUrl.searchParams.get('client_id'),
          redirectUri: ghUrl.searchParams.get('redirect_uri'),
          hasState: ghUrl.searchParams.has('state'),
          stateLen: ghUrl.searchParams.get('state')?.length ?? 0,
          scope: ghUrl.searchParams.get('scope'),
        }
      } catch { loginDebug = { redirectStatus: loginRes.status, location } }
    } catch (e) { loginDebug = { error: String(e) } }
    return new Response(JSON.stringify({ envInfo, loginDebug }, null, 2), { headers: { 'content-type': 'application/json' } })
  }
  if (isCallback) {
    console.log('[Keystatic] CALLBACK URL:', request.url)
    console.log('[Keystatic] CALLBACK hasCode:', url.searchParams.has('code'), 'hasState:', url.searchParams.has('state'), 'stateLen:', url.searchParams.get('state')?.length ?? 0)
    logEnvState()
  }
  if (isLogin) logEnvState()
  try {
    const handler = await getHandler()
    const res = await handler.GET(cleanRequest(request))
    if (isLogin && (res.status === 302 || res.status === 307)) {
      const location = res.headers.get('location') ?? ''
      try {
        const ghUrl = new URL(location)
        console.log('[Keystatic] LOGIN→GitHub hasState:', ghUrl.searchParams.has('state'), 'stateLen:', ghUrl.searchParams.get('state')?.length ?? 0, 'clientId:', ghUrl.searchParams.get('client_id'))
      } catch { console.log('[Keystatic] LOGIN location:', location) }
    }
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
    const res = await handler.POST(cleanRequest(request))
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
