import type { Metadata } from 'next'
import CinematicHero from '@/components/home/CinematicHero'
import PhilosophyReveal from '@/components/home/PhilosophyReveal'
import NumberedShowcase from '@/components/home/NumberedShowcase'
import DepartmentShowcase from '@/components/home/DepartmentShowcase'
import RitualSection from '@/components/home/RitualSection'
import BeliefColumns from '@/components/home/BeliefColumns'
import CustomerReviews from '@/components/home/CustomerReviews'
import NewsletterSection from '@/components/home/NewsletterSection'

export const metadata: Metadata = {
  title: 'Faridunhill — The Art of the Pipe',
  description:
    "Purveyors of fine estate pipes, hand-carved meerschaums, rare collectibles, leather goods, and gentleman's smoking accessories. Rooted in 30 years of collector knowledge and old-world craftsmanship.",
}

export default function HomePage() {
  return (
    <>
      {/* Section 1: Cinematic full-screen hero */}
      <CinematicHero />

      {/* Section 2: Scroll-revealed philosophy quote */}
      <PhilosophyReveal />

      {/* Section 3: Numbered flagship showcase (real catalog) */}
      <NumberedShowcase />

      {/* Section 4: Department showcase grid */}
      <DepartmentShowcase />

      {/* Section 5: The Ritual */}
      <RitualSection />

      {/* Section 6: Belief / Curation / Source story columns */}
      <BeliefColumns />

      {/* Section 7: Customer reviews */}
      <CustomerReviews />

      {/* Section 8: Newsletter — The Inner Circle */}
      <NewsletterSection />
    </>
  )
}
