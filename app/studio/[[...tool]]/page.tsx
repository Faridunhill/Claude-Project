export const dynamic = 'force-dynamic'

export default function StudioPage() {
  const configured = !!process.env.NEXT_PUBLIC_SANITY_PROJECT_ID

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
      <div style={{ maxWidth: 540, width: '100%' }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🪵</div>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem', color: '#c9a84c' }}>
          Faridunhill CMS
        </h1>

        {configured ? (
          <>
            <p style={{ color: '#a08060', marginBottom: '2rem', lineHeight: 1.7 }}>
              Sanity is configured. Open your Sanity Studio dashboard below.
            </p>
            <a
              href={`https://manage.sanity.io/projects/${process.env.NEXT_PUBLIC_SANITY_PROJECT_ID}/studio`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-block',
                background: '#c9a84c',
                color: '#101010',
                fontWeight: 700,
                padding: '0.875rem 2rem',
                borderRadius: 4,
                textDecoration: 'none',
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                fontSize: '0.85rem',
              }}
            >
              Open Sanity Studio →
            </a>
          </>
        ) : (
          <>
            <p style={{ color: '#a08060', marginBottom: '2rem', lineHeight: 1.7 }}>
              Sanity is not yet configured. Add these environment variables in
              Vercel → Settings → Environment Variables, then redeploy.
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
                lineHeight: 2.2,
                color: '#c9a84c',
                marginBottom: '2rem',
              }}
            >
              <div>NEXT_PUBLIC_SANITY_PROJECT_ID=<span style={{ color: '#666' }}>your_project_id</span></div>
              <div>NEXT_PUBLIC_SANITY_DATASET=<span style={{ color: '#666' }}>production</span></div>
              <div>SANITY_API_TOKEN=<span style={{ color: '#666' }}>your_api_token</span></div>
            </div>
            <ol style={{ textAlign: 'left', color: '#888', fontSize: '0.9rem', lineHeight: 2.2, paddingLeft: '1.25rem', marginBottom: '2rem' }}>
              <li>Go to <strong style={{ color: '#c9a84c' }}>sanity.io</strong> → sign up free → create a project</li>
              <li>Copy your <strong style={{ color: '#c9a84c' }}>Project ID</strong> from the Manage dashboard</li>
              <li>Create an <strong style={{ color: '#c9a84c' }}>API token</strong> (Editor role) under API → Tokens</li>
              <li>Add all three vars in <strong style={{ color: '#c9a84c' }}>Vercel → Settings → Environment Variables</strong></li>
              <li>Redeploy — your dashboard will appear at this URL</li>
            </ol>
            <a
              href="https://sanity.io"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-block',
                background: '#c9a84c',
                color: '#101010',
                fontWeight: 700,
                padding: '0.875rem 2rem',
                borderRadius: 4,
                textDecoration: 'none',
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                fontSize: '0.85rem',
              }}
            >
              Create Sanity Account →
            </a>
          </>
        )}
      </div>
    </div>
  )
}
