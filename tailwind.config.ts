import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        mahogany: {
          DEFAULT: '#2C1810',
          light: '#3D2317',
          dark: '#1A0E09',
        },
        leather: {
          DEFAULT: '#8B6B4A',
          light: '#A67C52',
          tan: '#C4956A',
          pale: '#D4AA82',
        },
        gold: {
          DEFAULT: '#C9A84C',
          light: '#D4B86A',
          dark: '#A8873A',
          pale: '#E8D5A3',
        },
        parchment: {
          DEFAULT: '#F5EDD6',
          dark: '#E8DCC0',
          deep: '#D4C4A0',
        },
        hunter: {
          DEFAULT: '#2D4A2D',
          light: '#3D6B3D',
        },
        smoke: {
          DEFAULT: '#6B6560',
          light: '#8A847E',
        },
      },
      fontFamily: {
        playfair: ['var(--font-playfair)', 'Georgia', 'serif'],
        lora: ['var(--font-lora)', 'Georgia', 'serif'],
        fell: ['var(--font-fell)', 'Georgia', 'serif'],
      },
      backgroundImage: {
        'wood-grain': "url('/images/wood-grain.png')",
        'parchment-tex': "url('/images/parchment.png')",
        'leather-tex': "url('/images/leather.png')",
      },
      boxShadow: {
        'gold': '0 0 0 1px #C9A84C, 0 4px 24px rgba(201, 168, 76, 0.15)',
        'mahogany': '0 4px 32px rgba(44, 24, 16, 0.6)',
        'inner-gold': 'inset 0 1px 0 rgba(201, 168, 76, 0.3)',
      },
    },
  },
  plugins: [],
}

export default config
