import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NexusAI — Multi-Agent Chatbot',
  description: 'An intelligent multi-agent assistant powered by LangGraph, RAG, and local LLMs.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0d0d0d] text-[#ececec] h-screen overflow-hidden`}>
        {children}
      </body>
    </html>
  )
}
