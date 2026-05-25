'use client'

import Link from 'next/link'

interface LogoProps {
  size?: 'sm' | 'md' | 'lg'
  variant?: 'light' | 'dark'
}

export default function Logo({ size = 'md', variant = 'light' }: LogoProps) {
  const dimensions = {
    sm: { width: 140, height: 48 },
    md: { width: 200, height: 68 },
    lg: { width: 280, height: 96 },
  }

  const { width, height } = dimensions[size]
  const gold = variant === 'light' ? '#C9A84C' : '#A8873A'
  const text = variant === 'light' ? '#F5EDD6' : '#2C1810'
  const subtext = variant === 'light' ? '#C9A84C' : '#8B6B4A'
  const dark = '#1A0E09'

  return (
    <Link href="/" aria-label="Faridunhill — Return to homepage">
      <svg
        width={width}
        height={height}
        viewBox="0 0 280 96"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-labelledby="logo-title"
      >
        <title id="logo-title">Faridunhill</title>

        {/* Outer decorative frame */}
        <rect x="1" y="1" width="278" height="94" rx="3" stroke={gold} strokeWidth="0.5" strokeOpacity="0.4" />
        <rect x="4" y="4" width="272" height="88" rx="2" stroke={gold} strokeWidth="0.3" strokeOpacity="0.2" />

        {/* Corner flourishes */}
        <text x="7" y="18" fill={gold} fontSize="9" fontFamily="serif" opacity="0.7">✦</text>
        <text x="262" y="18" fill={gold} fontSize="9" fontFamily="serif" opacity="0.7">✦</text>
        <text x="7" y="90" fill={gold} fontSize="9" fontFamily="serif" opacity="0.7">✦</text>
        <text x="262" y="90" fill={gold} fontSize="9" fontFamily="serif" opacity="0.7">✦</text>

        {/* ── TOBACCO PIPE ILLUSTRATION ── */}
        <g transform="translate(14, 8)">
          {/* Bowl outer shell */}
          <path
            d="M 0 22 L 0 64 Q 0 72 8 72 L 32 72 Q 40 72 40 64 L 40 22 Z"
            fill={gold}
            opacity="0.9"
          />
          {/* Bowl inner chamber */}
          <path
            d="M 4 24 L 4 62 Q 4 68 10 68 L 30 68 Q 36 68 36 62 L 36 24 Z"
            fill={dark}
            opacity="0.9"
          />
          {/* Top rim */}
          <rect x="-2" y="16" width="44" height="8" rx="4" fill={gold} opacity="0.95" />

          {/* Shank (horizontal tube from right side of bowl) */}
          <rect x="40" y="46" width="68" height="10" rx="5" fill={gold} opacity="0.9" />

          {/* Mouthpiece / bit (tapered end) */}
          <path d="M 108 46 L 124 51 L 108 56 Z" fill={gold} opacity="0.85" />

          {/* Smoke wisp 1 — curves left then right */}
          <path
            d="M 10 16 C 2 8 18 4 10 -2"
            stroke={gold}
            strokeWidth="1.4"
            fill="none"
            opacity="0.55"
            strokeLinecap="round"
          />
          {/* Smoke wisp 2 — curves right then left */}
          <path
            d="M 20 16 C 28 8 12 4 20 -2"
            stroke={gold}
            strokeWidth="1.4"
            fill="none"
            opacity="0.42"
            strokeLinecap="round"
          />
          {/* Smoke wisp 3 — gentle right curve */}
          <path
            d="M 30 16 C 36 10 26 6 32 0"
            stroke={gold}
            strokeWidth="1"
            fill="none"
            opacity="0.3"
            strokeLinecap="round"
          />
        </g>

        {/* Vertical divider between icon and text */}
        <line x1="152" y1="16" x2="152" y2="80" stroke={gold} strokeWidth="0.5" strokeOpacity="0.25" />

        {/* Main logotype — centered in right panel (x 152–278 → center 215) */}
        <text
          x="215"
          y="52"
          textAnchor="middle"
          fill={text}
          fontSize="21"
          fontFamily="'Playfair Display', 'Georgia', serif"
          fontWeight="700"
          letterSpacing="3"
        >
          FARIDUNHILL
        </text>

        {/* Subtitle */}
        <text
          x="215"
          y="66"
          textAnchor="middle"
          fill={subtext}
          fontSize="7"
          fontFamily="'IM Fell English', 'Georgia', serif"
          letterSpacing="4"
          fontStyle="italic"
        >
          FINE TOBACCONISTS
        </text>

        {/* Decorative rule below subtitle */}
        <line x1="162" y1="72" x2="268" y2="72" stroke={gold} strokeWidth="0.5" opacity="0.4" />
        <circle cx="215" cy="72" r="2" fill={gold} opacity="0.4" />
        <circle cx="190" cy="72" r="1" fill={gold} opacity="0.3" />
        <circle cx="240" cy="72" r="1" fill={gold} opacity="0.3" />
      </svg>
    </Link>
  )
}
