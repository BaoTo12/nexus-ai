'use client'

import { useState, useRef, KeyboardEvent } from 'react'
import { SendHorizonal, Paperclip } from 'lucide-react'
import { cn } from '@/lib/utils'

interface InputBarProps {
  onSend: (text: string) => void
  onUploadClick: () => void
  disabled?: boolean
}

export default function InputBar({ onSend, onUploadClick, disabled = false }: InputBarProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px'
  }

  return (
    <div className="border-t border-[#1e1e1e] bg-[#0d0d0d] px-4 py-4">
      <div className="max-w-3xl mx-auto">
        <div
          className={cn(
            'flex items-end gap-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl px-4 py-3',
            'focus-within:border-[#10a37f]/60 transition-colors duration-200',
            disabled && 'opacity-60'
          )}
        >
          {/* Attach button */}
          <button
            onClick={onUploadClick}
            disabled={disabled}
            className="text-[#666] hover:text-[#aaa] transition-colors mb-0.5 shrink-0"
            title="Upload document"
          >
            <Paperclip size={18} />
          </button>

          {/* Textarea */}
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            disabled={disabled}
            placeholder="Message NexusAI… (Shift+Enter for newline)"
            rows={1}
            className="flex-1 bg-transparent text-sm text-[#e0e0e0] placeholder-[#555]
                       resize-none outline-none max-h-[200px] leading-relaxed
                       scrollbar-hide"
          />

          {/* Send button */}
          <button
            onClick={handleSend}
            disabled={disabled || !value.trim()}
            className={cn(
              'w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-all duration-150 mb-0.5',
              value.trim() && !disabled
                ? 'bg-[#10a37f] text-white hover:bg-[#0e9170] scale-100'
                : 'bg-[#2a2a2a] text-[#555] cursor-not-allowed'
            )}
          >
            <SendHorizonal size={15} />
          </button>
        </div>

        <p className="text-center text-[10px] text-[#444] mt-2">
          NexusAI can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  )
}
