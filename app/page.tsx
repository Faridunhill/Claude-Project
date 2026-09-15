import type { Metadata } from 'next'
import HeroSection from '@/components/home/HeroSection'
import StorySection from '@/components/home/StorySection'
import DepartmentShowcase from '@/components/home/DepartmentShowcase'
import FeaturedProducts from '@/components/home/FeaturedProducts'
import PhotoGallery from '@/components/home/PhotoGallery'
import BlogPreview from '@/components/home/BlogPreview'
import NewsletterSection from '@/components/home/NewsletterSection'

export const metadata: Metadata = {
  title: 'Faridunhill — Estate Pipes, Vintage Leather & Smoking Accessories',
  description:
    'Estate pipes, hand-carved meerschaum, vintage leather cases, and smoking accessories. Around a hundred estate pipes listed at any time. Rooted in 30 years of collecting. Free shipping on every order.',
}

export default function HomePage() {
  return (
    <>
      {/* Section 1: Full-screen hero */}
      <HeroSection />

      {/* Section 2: Brand story, editorial copy */}
      <StorySection />

      {/* Section 3: Department showcase grid */}
      <DepartmentShowcase />

      {/* Section 4: Featured products horizontal scroll */}
      <FeaturedProducts />

      {/* Section 5: Lifestyle photo story */}
      <PhotoGallery />

      {/* Section 6: Journal / blog preview */}
      <BlogPreview />

      {/* Customer reviews section removed: testimonials were fabricated
          (fake names, fake "verified" flags, products not in catalog).
          Restore only with real, verifiable customer reviews. */}

      {/* Section 8: Newsletter & phone collection */}
      <NewsletterSection />
    </>
  )
}
