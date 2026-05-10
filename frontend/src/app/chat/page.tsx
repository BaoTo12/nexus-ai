'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { v4 as uuidv4 } from 'uuid'

import Sidebar from '@/components/Sidebar'
import ChatWindow from '@/components/ChatWindow'
import InputBar from '@/components/InputBar'
import UploadModal from '@/components/UploadModal'
import { Message } from '@/components/MessageBubble'

import { sendMessage, fetchSessions, fetchHistory } from '@/lib/api'
import { isAuthenticated } from '@/lib/utils'

interface Session {
  id: string
  title: string
  created_at: string
}

export default function ChatPage() {
  const router = useRouter()

  const [sessions, setSessions] = useState<Session[]>([])
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showUpload, setShowUpload] = useState(false)

  // Guard: redirect if not logged in
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
    }
  }, [router])

  // Load sessions on mount
  const loadSessions = useCallback(async () => {
    try {
      const data = await fetchSessions()
      setSessions(data)
      if (!activeSessionId && data.length > 0) {
        setActiveSessionId(data[0].id)
      }
    } catch {
      // Not authenticated — will be redirected above
    }
  }, [activeSessionId])

  useEffect(() => {
    loadSessions()
  }, [])

  // Load history when session changes
  useEffect(() => {
    if (!activeSessionId) return
    setMessages([])
    fetchHistory(activeSessionId)
      .then((history) => {
        setMessages(
          history.map((m) => ({
            id: m.id,
            role: m.role as 'user' | 'assistant',
            content: m.content,
          }))
        )
      })
      .catch(() => setMessages([]))
  }, [activeSessionId])

  const handleSend = useCallback(
    async (text: string) => {
      if (isLoading) return

      // Optimistically add user message
      const userMsg: Message = {
        id: uuidv4(),
        role: 'user',
        content: text,
      }

      // Placeholder assistant message (streaming)
      const assistantMsgId = uuidv4()
      const assistantMsg: Message = {
        id: assistantMsgId,
        role: 'assistant',
        content: '',
        streaming: true,
        step: 'supervisor',
      }

      setMessages((prev) => [...prev, userMsg, assistantMsg])
      setIsLoading(true)

      try {
        await sendMessage(text, activeSessionId, {
          onSessionId: (id) => {
            setActiveSessionId(id)
            loadSessions() // refresh sidebar
          },
          onStep: (node) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMsgId ? { ...m, step: node } : m
              )
            )
          },
          onToken: (token) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMsgId
                  ? { ...m, content: m.content + token, step: undefined }
                  : m
              )
            )
          },
          onDone: (full) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMsgId
                  ? { ...m, content: full || m.content, streaming: false, step: undefined }
                  : m
              )
            )
          },
          onError: (err) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMsgId
                  ? {
                      ...m,
                      content: `⚠️ ${err}`,
                      streaming: false,
                      step: undefined,
                    }
                  : m
              )
            )
          },
        })
      } finally {
        setIsLoading(false)
      }
    },
    [activeSessionId, isLoading, loadSessions]
  )

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={(id) => setActiveSessionId(id)}
        onSessionsChange={loadSessions}
        onUploadClick={() => setShowUpload(true)}
      />

      <main className="flex flex-col flex-1 overflow-hidden">
        <ChatWindow messages={messages} isLoading={isLoading} />
        <InputBar
          onSend={handleSend}
          onUploadClick={() => setShowUpload(true)}
          disabled={isLoading}
        />
      </main>

      {showUpload && <UploadModal onClose={() => setShowUpload(false)} />}
    </div>
  )
}
