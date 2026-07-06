export const dynamic = 'force-dynamic'

async function getHandler() {
  const { makeRouteHandler } = await import('@keystatic/next/route-handler')
  const { default: config } = await import('../../../../keystatic.config')
  return makeRouteHandler({ config })
}

export async function GET(request: Request) {
  const handler = await getHandler()
  return handler.GET(request)
}

export async function POST(request: Request) {
  const handler = await getHandler()
  return handler.POST(request)
}
