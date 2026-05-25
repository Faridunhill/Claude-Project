import { NextStudio } from 'next-sanity/studio'
import config from '@/sanity.config'

export { metadata, viewport } from 'next-sanity/studio'

const isConfigured = !!process.env.NEXT_PUBLIC_SANITY_PROJECT_ID

export default function StudioPage() {
  if (!isConfigured) {
    return (
      <div
        style={{
          position: 'fixed',
          inset: 0,
          background: '#101010',
          color: '#f5edd6',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'Georgia, serif',
          padding: '2rem',
          textAlign: 'center',
          zIndex: 9999,
        }}
      >
        <div style={{ maxWidth: 520, width: '100%' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🪵</div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem', color: '#c9a84c' }}>
            Faridunhill CMS
          </h1>
          <p style={{ color: '#a08060', marginBottom: '2rem', lineHeight: 1.7 }}>
            Sanity is not yet configured. Add the following environment
            variables in your Vercel project settings, then redeploy.
          </p>
          <div
            style={{
              background: '#1a1a1a',
              border: '1px solid #333',
              borderRadius: 6,
              padding: '1.25rem 1.5rem',
              textAlign: 'left',
              fontFamily: 'monospace',
              fontSize: '0.85rem',
              lineHeight: 2,
              color: '#c9a84c',
              marginBottom: '2rem',
            }}
          >
            <div>NEXT_PUBLIC_SANITY_PROJECT_ID=<span style={{ color: '#888' }}>your_project_id</span></div>
            <div>NEXT_PUBLIC_SANITY_DATASET=<span style={{ color: '#888' }}>production</span></div>
            <div>SANITY_API_TOKEN=<span style={{ color: '#888' }}>your_api_token</span></div>
          </div>
          <ol
            style={{
              textAlign: 'left',
              color: '#888',
              fontSize: '0.9rem',
              lineHeight: 2,
              paddingLeft: '1.25rem',
            }}
          >
            <li>Go to <strong style={{ color: '#c9a84c' }}>sanity.io</strong> → create a free account &amp; project</li>
            <li>Copy your <strong style={{ color: '#c9a84c' }}>Project ID</strong> from the Manage dashboard</li>
            <li>Create an <strong style={{ color: '#c9a84c' }}>API token</strong> (Editor role) under API → Tokens</li>
            <li>Add all three env vars in <strong style={{ color: '#c9a84c' }}>Vercel → Settings → Environment Variables</strong></li>
            <li>Redeploy — then return to <strong style={{ color: '#c9a84c' }}>/studio</strong></li>
          </ol>
        </div>
      </div>
    )
  }

  return <NextStudio config={config} />
}
