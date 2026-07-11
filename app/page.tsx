import type { Metadata } from 'next'
import HeroSection from '@/components/home/HeroSection'
import StorySection from '@/components/home/StorySection'
import DepartmentShowcase from '@/components/home/DepartmentShowcase'
import FeaturedProducts from '@/components/home/FeaturedProducts'
import PhotoGallery from '@/components/home/PhotoGallery'
import BlogPreview from '@/components/home/BlogPreview'
import NewsletterSection from '@/components/home/NewsletterSection'

export const metadata: Metadata = {
  title: 'Faridunhill — Fine Pipes, Tobaccos & Gentleman\'s Accessories',
  description:
    'Purveyors of fine tobacco pipes, premium pipe tobacco, hand-rolled cigars, and gentleman\'s accessories. Rooted in 30 years of collector knowledge and old-world craftsmanship. Free shipping over $75.',
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
