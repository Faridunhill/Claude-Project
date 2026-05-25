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
        <text x="6" y="16" fill={gold} fontSize="10" fontFamily="serif" opacity="0.7">✦</text>
        <text x="262" y="16" fill={gold} fontSize="10" fontFamily="serif" opacity="0.7">✦</text>
        <text x="6" y="90" fill={gold} fontSize="10" fontFamily="serif" opacity="0.7">✦</text>
        <text x="262" y="90" fill={gold} fontSize="10" fontFamily="serif" opacity="0.7">✦</text>

        {/* Crossed pipes illustration */}
        <g transform="translate(16, 20)">
          {/* Pipe 1 — angled left */}
          <g transform="rotate(-20, 28, 28)">
            {/* Bowl */}
            <rect x="8" y="18" width="14" height="18" rx="2" fill={gold} opacity="0.9" />
            <rect x="9" y="19" width="12" height="14" rx="1" fill="#2C1810" opacity="0.6" />
            {/* Shank */}
            <rect x="22" y="24" width="24" height="5" rx="2.5" fill={gold} opacity="0.85" />
            {/* Mouthpiece */}
            <ellipse cx="47" cy="26.5" rx="3" ry="2" fill={gold} opacity="0.7" />
            {/* Bowl top rim */}
            <rect x="6" y="16" width="18" height="4" rx="2" fill={gold} opacity="0.7" />
            {/* Smoke wisp */}
            <path d="M15 16 Q13 10 15 6 Q17 2 15 0" stroke={gold} strokeWidth="1" fill="none" opacity="0.4" strokeLinecap="round" />
          </g>

          {/* Pipe 2 — angled right */}
          <g transform="rotate(20, 28, 28)">
            <rect x="8" y="18" width="14" height="18" rx="2" fill={gold} opacity="0.7" />
            <rect x="9" y="19" width="12" height="14" rx="1" fill="#2C1810" opacity="0.6" />
            <rect x="22" y="24" width="24" height="5" rx="2.5" fill={gold} opacity="0.65" />
            <ellipse cx="47" cy="26.5" rx="3" ry="2" fill={gold} opacity="0.5" />
            <rect x="6" y="16" width="18" height="4" rx="2" fill={gold} opacity="0.55" />
          </g>
        </g>

        {/* Ribbon / banner */}
        <path
          d="M72 42 L76 38 L272 38 L268 42 L272 46 L76 46 L72 42 Z"
          fill={gold}
          opacity="0.15"
          stroke={gold}
          strokeWidth="0.5"
          strokeOpacity="0.5"
        />

        {/* Main logotype */}
        <text
          x="175"
          y="52"
          textAnchor="middle"
          fill={text}
          fontSize="22"
          fontFamily="'Playfair Display', 'Georgia', serif"
          fontWeight="700"
          letterSpacing="3"
        >
          FARIDUNHILL
        </text>

        {/* Subtitle line */}
        <text
          x="175"
          y="66"
          textAnchor="middle"
          fill={subtext}
          fontSize="7.5"
          fontFamily="'IM Fell English', 'Georgia', serif"
          letterSpacing="4"
          fontStyle="italic"
        >
          FINE TOBACCONISTS · EST. 2015
        </text>

        {/* Decorative rule below subtitle */}
        <line x1="100" y1="72" x2="250" y2="72" stroke={gold} strokeWidth="0.5" opacity="0.4" />
        <circle cx="175" cy="72" r="2" fill={gold} opacity="0.4" />
        <circle cx="145" cy="72" r="1" fill={gold} opacity="0.3" />
        <circle cx="205" cy="72" r="1" fill={gold} opacity="0.3" />
      </svg>
    </Link>
  )
}
