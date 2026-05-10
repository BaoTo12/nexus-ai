'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Bot, Loader2 } from 'lucide-react'
import { login } from '@/lib/api'
import { saveAuth } from '@/lib/utils'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await login(email, password)
      saveAuth(res.access_token, res.user_id)
      router.push('/chat')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0d0d0d] px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#10a37f] to-[#1a7a5e] flex items-center justify-center mb-3 shadow-lg shadow-[#10a37f]/20">
            <Bot size={22} className="text-white" />
          </div>
          <h1 className="text-xl font-semibold text-white">Welcome back</h1>
          <p className="text-sm text-[#666] mt-1">Sign in to NexusAI</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-[#aaa] mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              className="w-full bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl px-4 py-3
                         text-sm text-white placeholder-[#555] outline-none
                         focus:border-[#10a37f]/60 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[#aaa] mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="w-full bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl px-4 py-3
                         text-sm text-white placeholder-[#555] outline-none
                         focus:border-[#10a37f]/60 transition-colors"
            />
          </div>

          {error && (
            <p className="text-xs text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-[#10a37f] hover:bg-[#0e9170] text-white text-sm font-medium
                       rounded-xl transition-colors duration-150 flex items-center justify-center gap-2
                       disabled:opacity-60 mt-2"
          >
            {loading && <Loader2 size={15} className="animate-spin" />}
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="text-center text-sm text-[#666] mt-5">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="text-[#10a37f] hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
