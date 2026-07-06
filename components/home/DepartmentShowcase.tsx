import Image from 'next/image'
import Link from 'next/link'

const departments = [
  {
    name: 'Estate Pipes',
    slug: 'estate-pipes',
    desc: 'Restored estate pipes from the great workshops of Europe — each with history in the grain.',
    image: 'https://i.etsystatic.com/34479460/r/il/d22f04/7660094618/il_fullxfull.7660094618_qvl4.jpg',
    accent: 'from-mahogany to-mahogany-dark',
  },
  {
    name: 'Meerschaum',
    slug: 'meerschaum',
    desc: 'Hand-carved Turkish meerschaum — figurals and classics that color with every smoke.',
    image: 'https://i.etsystatic.com/34479460/r/il/9ed80b/7771380885/il_fullxfull.7771380885_is59.jpg',
    accent: 'from-hunter to-mahogany-dark',
  },
  {
    name: 'Rare & Collectible',
    slug: 'rare-collectible',
    desc: 'Complete sets, rarities, and museum-grade pieces for the serious collector.',
    image: 'https://i.etsystatic.com/34479460/r/il/df7987/7663292576/il_fullxfull.7663292576_kbvp.jpg',
    accent: 'from-mahogany to-mahogany-dark',
  },
  {
    name: 'Leather Bags & Cases',
    slug: 'leather-bags',
    desc: 'Handcrafted leather — pipe bags, tobacco pouches, and travel companions.',
    image: 'https://i.etsystatic.com/34479460/r/il/010080/4097242757/il_fullxfull.4097242757_k0j5.jpg',
    accent: 'from-leather-tan/40 to-mahogany-dark',
  },
  {
    name: 'Cigar & Smoking Accessories',
    slug: 'cigar-smoking-accessories',
    desc: 'Cutters, humidors, ashtrays, tampers, and stands — every fine thing in between.',
    image: 'https://i.etsystatic.com/34479460/r/il/a3dec9/7743422566/il_fullxfull.7743422566_29ep.jpg',
    accent: 'from-mahogany to-mahogany-dark',
  },
  {
    name: 'Lighters & Matches',
    slug: 'lighters',
    desc: 'Vintage petrol and jet lighters — strike the proper flame, every time.',
    image: 'https://i.etsystatic.com/34479460/r/il/c54c6c/7778612773/il_fullxfull.7778612773_o35w.jpg',
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
