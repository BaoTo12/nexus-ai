'use client'

import { useState, useCallback } from 'react'
import {
  Plus, MessageSquare, Upload, LogOut, ChevronRight, Bot
} from 'lucide-react'
import { cn, formatDate, clearAuth } from '@/lib/utils'
import { createSession } from '@/lib/api'
import { useRouter } from 'next/navigation'

interface Session {
  id: string
  title: string
  created_at: string
}

interface SidebarProps {
  sessions: Session[]
  activeSessionId: string | null
  onSelectSession: (id: string) => void
  onSessionsChange: () => void
  onUploadClick: () => void
}

export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onSessionsChange,
  onUploadClick,
}: SidebarProps) {
  const router = useRouter()
  const [creating, setCreating] = useState(false)

  const handleNewChat = useCallback(async () => {
    setCreating(true)
    try {
      const sess = await createSession()
      onSessionsChange()
      onSelectSession(sess.id)
    } catch {
      // ignore
    } finally {
      setCreating(false)
    }
  }, [onSelectSession, onSessionsChange])

  const handleLogout = () => {
    clearAuth()
    router.push('/login')
  }

  return (
    <aside className="flex flex-col h-full bg-[#111111] border-r border-[#1e1e1e] w-[260px] shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 py-5 border-b border-[#1e1e1e]">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#10a37f] to-[#1a7a5e] flex items-center justify-center">
          <Bot size={16} className="text-white" />
        </div>
        <span className="font-semibold text-[15px] text-white tracking-tight">NexusAI</span>
      </div>

      {/* New Chat button */}
      <div className="px-3 pt-3">
        <button
          onClick={handleNewChat}
          disabled={creating}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium
                     bg-[#10a37f] hover:bg-[#0e9170] text-white transition-colors duration-150
                     disabled:opacity-50"
        >
          <Plus size={16} />
          New Chat
        </button>
      </div>

      {/* Session list */}
      <nav className="flex-1 overflow-y-auto scrollbar-thin px-2 py-3 space-y-0.5">
        {sessions.length === 0 && (
          <p className="text-xs text-[#666] px-3 py-2">No conversations yet</p>
        )}
        {sessions.map((sess) => (
          <button
            key={sess.id}
            onClick={() => onSelectSession(sess.id)}
            className={cn(
              'w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-left group transition-colors duration-100',
              activeSessionId === sess.id
                ? 'bg-[#1e1e1e] text-white'
                : 'text-[#aaa] hover:bg-[#181818] hover:text-white'
            )}
          >
            <MessageSquare size={14} className="shrink-0 opacity-60" />
            <span className="flex-1 text-sm truncate">{sess.title}</span>
            <span className="text-[10px] text-[#555] shrink-0 hidden group-hover:block">
              {formatDate(sess.created_at)}
            </span>
          </button>
        ))}
      </nav>

      {/* Bottom actions */}
      <div className="border-t border-[#1e1e1e] p-3 space-y-1">
        <button
          onClick={onUploadClick}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm
                     text-[#aaa] hover:bg-[#181818] hover:text-white transition-colors"
        >
          <Upload size={15} />
          Upload Document
        </button>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm
                     text-[#aaa] hover:bg-[#1e1e1e] hover:text-red-400 transition-colors"
        >
          <LogOut size={15} />
          Sign Out
        </button>
      </div>
    </aside>
  )
}
