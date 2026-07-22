import { MetadataRoute } from 'next'
import { getAllProducts, departmentMeta } from '@/lib/products'
import { getAllPostSlugs } from '@/lib/mdx'
import { getAllArchiveItems } from '@/lib/archive'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://faridunhill.com'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const products = await getAllProducts()
  const blogSlugs = await getAllPostSlugs()

  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    { url: `${BASE_URL}/shop`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${BASE_URL}/blog`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.8 },
    { url: `${BASE_URL}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.6 },
    { url: `${BASE_URL}/contact`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.5 },
    { url: `${BASE_URL}/shipping`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.4 },
    { url: `${BASE_URL}/returns`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.4 },
    { url: `${BASE_URL}/privacy`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.3 },
  ]

  const departmentPages: MetadataRoute.Sitemap = Object.keys(departmentMeta).map((dept) => ({
    url: `${BASE_URL}/shop/${dept}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }))

  const productPages: MetadataRoute.Sitemap = products.map((p) => ({
    url: `${BASE_URL}/shop/${p.department}/${p.slug}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  const blogPages: MetadataRoute.Sitemap = blogSlugs.map((slug) => ({
    url: `${BASE_URL}/blog/${slug}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: 0.6,
  }))

  // Encyclopedia: sold-archive pages are permanent SEO assets
  const archiveItems = getAllArchiveItems()
  const archivePages: MetadataRoute.Sitemap = [
    ...(archiveItems.length
      ? [{
          url: `${BASE_URL}/archive`,
          lastModified: new Date(),
          changeFrequency: 'weekly' as const,
          priority: 0.7,
        }]
      : []),
    ...archiveItems.map((item) => ({
      url: `${BASE_URL}/archive/${item.slug}`,
      lastModified: new Date(),
      changeFrequency: 'yearly' as const,
      priority: 0.6,
    })),
  ]

  return [...staticPages, ...departmentPages, ...productPages, ...blogPages, ...archivePages]
}
