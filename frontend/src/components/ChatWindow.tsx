'use client'

import { useRef, useEffect } from 'react'
import MessageBubble, { Message } from './MessageBubble'
import { Bot } from 'lucide-react'

interface ChatWindowProps {
  messages: Message[]
  isLoading: boolean
}

export default function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-6 px-4 text-center">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#10a37f] to-[#1a7a5e] flex items-center justify-center shadow-lg shadow-[#10a37f]/20">
          <Bot size={28} className="text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-semibold text-white mb-2">How can I help you?</h2>
          <p className="text-[#666] text-sm max-w-md">
            I can answer questions from documents, check the weather, query data, or just chat.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-2 w-full max-w-md mt-2">
          {[
            "What's the weather in Tokyo?",
            'Show me total revenue by product',
            'What does my uploaded document say?',
            'Send an email to team@example.com',
          ].map((prompt) => (
            <button
              key={prompt}
              className="text-left px-3 py-3 rounded-xl bg-[#1a1a1a] border border-[#252525]
                         text-[#aaa] text-xs hover:bg-[#222] hover:text-white
                         hover:border-[#10a37f]/40 transition-all duration-150"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin">
      <div className="max-w-3xl mx-auto pb-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
          <div className="flex gap-4 px-4 py-5">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#10a37f] to-[#1a7a5e] flex items-center justify-center shrink-0">
              <Bot size={14} className="text-white" />
            </div>
            <div className="flex items-center gap-1.5 mt-2">
              <span className="w-2 h-2 rounded-full bg-[#10a37f] animate-bounce [animation-delay:0ms]" />
              <span className="w-2 h-2 rounded-full bg-[#10a37f] animate-bounce [animation-delay:150ms]" />
              <span className="w-2 h-2 rounded-full bg-[#10a37f] animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
