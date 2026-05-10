'use client'

import { useCallback, useRef, useState } from 'react'
import { Upload, X, FileText, Loader2, CheckCircle2 } from 'lucide-react'
import { ingestFile } from '@/lib/api'
import { cn } from '@/lib/utils'

interface UploadModalProps {
  onClose: () => void
}

type Status = 'idle' | 'uploading' | 'success' | 'error'

export default function UploadModal({ onClose }: UploadModalProps) {
  const [dragOver, setDragOver] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [message, setMessage] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback((f: File) => {
    setFile(f)
    setStatus('idle')
    setMessage('')
  }, [])

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    setStatus('uploading')
    try {
      const res = await ingestFile(file)
      setStatus('success')
      setMessage(`✅ Ingested "${res.filename}" — ${res.chunks} chunks stored.`)
    } catch (err: any) {
      setStatus('error')
      setMessage(err.message || 'Upload failed')
    }
  }

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-[#141414] border border-[#252525] rounded-2xl w-full max-w-md mx-4 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#1e1e1e]">
          <h2 className="text-sm font-semibold text-white">Upload to Knowledge Base</h2>
          <button onClick={onClose} className="text-[#666] hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className={cn(
              'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-150',
              dragOver
                ? 'border-[#10a37f] bg-[#10a37f]/5'
                : 'border-[#2a2a2a] hover:border-[#3a3a3a] bg-[#111]'
            )}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.txt,.md"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <FileText size={28} className="text-[#10a37f]" />
                <p className="text-sm text-white font-medium">{file.name}</p>
                <p className="text-xs text-[#666]">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <Upload size={28} className="text-[#666]" />
                <p className="text-sm text-[#aaa]">
                  Drag & drop a file, or <span className="text-[#10a37f]">browse</span>
                </p>
                <p className="text-xs text-[#555]">PDF, TXT, Markdown supported</p>
              </div>
            )}
          </div>

          {/* Status message */}
          {message && (
            <div
              className={cn(
                'text-xs px-3 py-2 rounded-lg',
                status === 'success'
                  ? 'bg-[#10a37f]/10 text-[#10a37f] border border-[#10a37f]/20'
                  : 'bg-red-500/10 text-red-400 border border-red-500/20'
              )}
            >
              {message}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="flex-1 py-2.5 text-sm rounded-lg border border-[#2a2a2a]
                         text-[#aaa] hover:bg-[#1e1e1e] transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={!file || status === 'uploading' || status === 'success'}
              className={cn(
                'flex-1 py-2.5 text-sm rounded-lg font-medium flex items-center justify-center gap-2 transition-colors',
                file && status !== 'uploading' && status !== 'success'
                  ? 'bg-[#10a37f] text-white hover:bg-[#0e9170]'
                  : 'bg-[#1e1e1e] text-[#555] cursor-not-allowed'
              )}
            >
              {status === 'uploading' && <Loader2 size={14} className="animate-spin" />}
              {status === 'success' && <CheckCircle2 size={14} />}
              {status === 'uploading' ? 'Uploading…' : status === 'success' ? 'Done!' : 'Upload'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
