import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'MLStream | Real-Time MLOps & Drift Observability',
  description: 'Enterprise MLOps & AI Observability Engine',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  )
}
