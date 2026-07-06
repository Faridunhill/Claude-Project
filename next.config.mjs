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
