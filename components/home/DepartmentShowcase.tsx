import Image from 'next/image'
import Link from 'next/link'

const departments = [
  {
    name: 'Tobacco Pipes',
    slug: 'tobacco-pipes',
    desc: 'Estate finds, classic briars, and carved meerschaums — each one a lifetime companion.',
    /* Replace with a proper product photo */
    image: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80',
    accent: 'from-mahogany to-mahogany-dark',
  },
  {
    name: 'Pipe Tobacco',
    slug: 'pipe-tobacco',
    desc: 'Virginia, Burley, Latakia, and aromatic blends, chosen by smokers for smokers.',
    image: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600&q=80',
    accent: 'from-hunter to-mahogany-dark',
  },
  {
    name: 'Premium Cigars',
    slug: 'cigars',
    desc: 'Hand-rolled excellence, from the highlands of Nicaragua to the Vuelta Abajo.',
    image: 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=600&q=80',
    accent: 'from-mahogany to-mahogany-dark',
  },
  {
    name: 'Leather Cases',
    slug: 'leather-bags',
    desc: 'Handcrafted in full-grain leather — pipe rolls, cigar cases, and travel companions.',
    image: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80',
    accent: 'from-leather-tan/40 to-mahogany-dark',
  },
  {
    name: 'Accessories',
    slug: 'pipe-accessories',
    desc: 'Tampers, pipe tools, stands, humidors, and every fine thing in between.',
    image: 'https://images.unsplash.com/photo-1585155770447-2f66e2a397b5?w=600&q=80',
    accent: 'from-mahogany to-mahogany-dark',
  },
  {
    name: 'Gift Sets',
    slug: 'gift-sets',
    desc: 'Curated collections for the beginner and the collector — beautifully presented.',
    image: 'https://images.unsplash.com/photo-1512909006721-3d6018887383?w=600&q=80',
    accent: 'from-gold/20 to-mahogany-dark',
  },
]

export default function DepartmentShowcase() {
  return (
    <section className="bg-wood-texture py-24">
      <div className="max-w-screen-xl mx-auto px-6 lg:px-12">
        {/* Header */}
        <div className="text-center mb-14">
          <span className="font-fell italic text-gold/70 text-sm tracking-widest">~ Explore ~</span>
          <h2 className="font-playfair font-bold text-parchment text-4xl lg:text-5xl mt-3">
            The Departments
          </h2>
          <p className="font-lora text-parchment/55 mt-3 max-w-xl mx-auto text-base">
            Each department is a world unto itself, stocked with care and curated with knowledge
            accumulated over thirty years of dedicated collecting.
          </p>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {departments.map((dept) => (
            <Link
              key={dept.slug}
              href={`/shop/${dept.slug}`}
              className="group relative aspect-[4/3] overflow-hidden rounded-sm gold-frame product-card block"
            >
              {/* Background image — swap Unsplash URLs for real product photography */}
              <Image
                src={dept.image}
                alt={dept.name}
                fill
                className="object-cover transition-transform duration-700 group-hover:scale-105"
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
              />

              {/* Gradient overlay */}
              <div className={`absolute inset-0 bg-gradient-to-t ${dept.accent} opacity-80 group-hover:opacity-70 transition-opacity duration-300`} />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />

              {/* Corner ornament */}
              <div className="absolute top-3 right-3 text-gold/40 text-xs">✦</div>

              {/* Content */}
              <div className="absolute bottom-0 left-0 right-0 p-5">
                <h3 className="font-playfair font-bold text-parchment text-xl leading-tight group-hover:text-gold transition-colors duration-200">
                  {dept.name}
                </h3>
                <p className="font-lora text-parchment/65 text-sm mt-1.5 line-clamp-2 group-hover:text-parchment/80 transition-colors">
                  {dept.desc}
                </p>
                <div className="flex items-center gap-1.5 mt-3 text-gold text-xs font-playfair tracking-wider uppercase opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  Browse Collection
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* View all button */}
        <div className="text-center mt-10">
          <Link href="/shop" className="btn-ghost inline-flex items-center gap-2 px-8 py-3 rounded-sm text-sm tracking-widest uppercase">
            View All Departments
          </Link>
        </div>
      </div>
    </section>
  )
}
