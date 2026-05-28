import { createHmac, randomBytes } from 'crypto'

export const dynamic = 'force-dynamic'

async function getHandler() {
  const { makeRouteHandler } = await import('@keystatic/next/route-handler')
  const { default: config } = await import('../../../../keystatic.config')
  return makeRouteHandler({ config })
}

function cleanRequest(request: Request): Request {
  const url = new URL(request.url)
  url.searchParams.delete('nxtPparams')
  url.searchParams.delete('nxtPslug')
  if (url.toString() === request.url) return request
  return new Request(url.toString(), request)
}

// Patch the GitHub login redirect: add missing scope + signed state that
// @keystatic/next@5.0.0 fails to generate due to a known bug.
function patchLoginRedirect(res: Response): Response {
  const location = res.headers.get('location') ?? ''
  let ghUrl: URL
  try { ghUrl = new URL(location) } catch { return res }
  if (ghUrl.hostname !== 'github.com') return res

  let changed = false

  if (!ghUrl.searchParams.has('scope')) {
    ghUrl.searchParams.set('scope', 'repo')
    changed = true
  }

  if (!ghUrl.searchParams.has('state')) {
    const secret = process.env.KEYSTATIC_SECRET ?? ''
    const nonce = randomBytes(16).toString('hex')
    const sig = createHmac('sha256', secret).update(nonce).digest('hex')
    ghUrl.searchParams.set('state', `${nonce}.${sig}`)
    changed = true
  }

  if (!changed) return res
  const headers = new Headers(res.headers)
  headers.set('location', ghUrl.toString())
  return new Response(null, { status: res.status, headers })
}

export async function GET(request: Request) {
  const url = new URL(request.url)
  const isLogin = url.pathname.endsWith('/github/login')
  const isDebug = url.pathname.endsWith('/debug')

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
    let loginDebug: Record<string, unknown> = {}
    try {
      const handler = await getHandler()
      const loginReq = new Request(`${url.origin}/api/keystatic/github/login`, { method: 'GET', headers: request.headers })
      const raw = await handler.GET(loginReq)
      const patched = patchLoginRedirect(raw)
      const location = patched.headers.get('location') ?? ''
      try {
        const ghUrl = new URL(location)
        loginDebug = {
          redirectStatus: patched.status,
          githubClientId: ghUrl.searchParams.get('client_id'),
          redirectUri: ghUrl.searchParams.get('redirect_uri'),
          hasState: ghUrl.searchParams.has('state'),
          stateLen: ghUrl.searchParams.get('state')?.length ?? 0,
          scope: ghUrl.searchParams.get('scope'),
        }
      } catch { loginDebug = { redirectStatus: patched.status, location } }
    } catch (e) { loginDebug = { error: String(e) } }
    return new Response(JSON.stringify({ envInfo, loginDebug }, null, 2), { headers: { 'content-type': 'application/json' } })
  }

  try {
    const handler = await getHandler()
    const res = await handler.GET(cleanRequest(request))
    const patched = isLogin ? patchLoginRedirect(res) : res
    if (!patched.ok && patched.status !== 302 && patched.status !== 307) {
      const body = await patched.clone().text()
      console.error('[Keystatic] GET non-ok response', patched.status, body)
    }
    return patched
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
