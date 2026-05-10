'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Bot, User } from 'lucide-react'
import { cn, STEP_LABELS } from '@/lib/utils'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
  step?: string
}

interface MessageBubbleProps {
  message: Message
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex gap-4 px-4 py-5 group', isUser ? 'flex-row-reverse' : 'flex-row')}>
      {/* Avatar */}
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5',
          isUser
            ? 'bg-[#1e1e1e] text-[#aaa]'
            : 'bg-gradient-to-br from-[#10a37f] to-[#1a7a5e] text-white'
        )}
      >
        {isUser ? <User size={14} /> : <Bot size={14} />}
      </div>

      {/* Content */}
      <div className={cn('flex flex-col gap-1.5 max-w-[75%]', isUser && 'items-end')}>
        {/* Agent step indicator */}
        {!isUser && message.step && (
          <span className="text-xs text-[#10a37f] fade-in-up flex items-center gap-1">
            {STEP_LABELS[message.step] ?? `🔄 ${message.step}…`}
          </span>
        )}

        {/* Bubble */}
        <div
          className={cn(
            'rounded-2xl px-4 py-3 text-sm leading-relaxed',
            isUser
              ? 'bg-[#10a37f] text-white rounded-tr-sm'
              : 'bg-[#1a1a1a] text-[#e0e0e0] rounded-tl-sm border border-[#252525]',
            message.streaming && !isUser && 'cursor-blink'
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content || ' '}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
