/** @type {import('next').NextConfig} */
const nextConfig = {
  pageExtensions: ['js', 'jsx', 'ts', 'tsx'],
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.unsplash.com' },
      { protocol: 'https', hostname: 'i.etsystatic.com' },
      { protocol: 'https', hostname: 'plus.unsplash.com' },
      { protocol: 'https', hostname: 'cdn.sanity.io' },
    ],
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          // Vercel serves this site over HTTPS only; tell browsers to refuse
          // a downgrade for two years.
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          // SAMEORIGIN rather than DENY: the Keystatic admin UI at /keystatic
          // frames its own pages.
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), payment=(), usb=()',
          },
        ],
      },
    ]
  },
  experimental: {
    outputFileTracingExcludes: {
      '*': [
        'node_modules/@swc/core-linux-x64-gnu',
        'node_modules/@swc/core-linux-x64-musl',
        'node_modules/@esbuild/**/*',
        'node_modules/webpack/**/*',
        'node_modules/rollup/**/*',
        'node_modules/terser/**/*',
        'node_modules/@mdx-js/**/*',
        'node_modules/next/dist/compiled/@next/react-dev-overlay/**/*',
        'node_modules/next/dist/compiled/webpack/**/*',
      ],
    },
  },
}

export default nextConfig
