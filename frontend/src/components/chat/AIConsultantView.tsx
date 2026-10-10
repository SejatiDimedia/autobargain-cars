import { useState, useRef, useEffect } from 'react'
import {
  Sparkles,
  Send,
  Cpu,
  Globe,
  Paperclip,
  Mic,
  ShieldCheck,
  TrendingUp,
  Search,
  Bot,
  User,
  RefreshCw,
  Trash2,
  Copy,
  Check,
  RotateCcw,
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { sendChatMessage, getChatHistory, clearChatHistory } from '../../api/client'

function normalizeMarkdown(content: string): string {
  if (!content) return ''
  let text = content

  // 1. Fix joined table rows on a single line with || -> |\n
  text = text.replace(/\|\|\s*(?=\|)/g, '|\n')
  text = text.replace(/\|\|\s*(?=[^\n|])/g, '|\n| ')

  // 2. Ensure table has a blank line before its header row if preceded by plain text (not ending with |)
  text = text.replace(/([^\n|])\n(\|(?:\s*[^|\n]+\s*\|)+)/g, '$1\n\n$2')

  // 3. Remove any blank lines between table rows that break GFM tables
  text = text.replace(/(\|(?:\s*[^|\n]+\s*\|)+)\n\s*\n(\|(?:\s*[^|\n]+\s*\|)+)/g, '$1\n$2')
  text = text.replace(/(\|(?:\s*[^|\n]+\s*\|)+)\n\s*\n(\|(?:\s*[^|\n]+\s*\|)+)/g, '$1\n$2')

  return text
}

interface Message {
  id?: number
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export function AIConsultantView() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isHistoryLoading, setIsHistoryLoading] = useState(true)
  const [useDeeperValuation, setUseDeeperValuation] = useState(true)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Load chat history from backend database on mount
  useEffect(() => {
    let isMounted = true
    async function loadHistory() {
      try {
        setIsHistoryLoading(true)
        const res = await getChatHistory('default', 50)
        if (isMounted && res.messages) {
          setMessages(res.messages)
        }
      } catch (err) {
        console.warn('Gagal memuat riwayat chat dari server:', err)
      } finally {
        if (isMounted) setIsHistoryLoading(false)
      }
    }
    loadHistory()
    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSend = async (customPrompt?: string) => {
    const textToSend = customPrompt || input.trim()
    if (!textToSend || isLoading) return

    const now = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
    const userMsg: Message = { role: 'user', content: textToSend, timestamp: now }

    setMessages((prev) => [...prev, userMsg])
    if (!customPrompt) setInput('')
    setIsLoading(true)

    try {
      const res = await sendChatMessage(textToSend, 'default')
      const assistantMsg: Message = {
        role: 'assistant',
        content: res.response,
        timestamp: res.timestamp || new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err: any) {
      const errorMsg: Message = {
        role: 'assistant',
        content: `Mohon maaf, terjadi kendala saat memproses: ${err.message || 'Gagal terhubung ke API'}`,
        timestamp: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearChat = async () => {
    if (!window.confirm('Bersihkan riwayat percakapan konsultasi?')) return
    try {
      await clearChatHistory('default')
      setMessages([])
    } catch (err) {
      console.error('Gagal membersihkan riwayat chat:', err)
    }
  }

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  const quickPrompts = [
    {
      icon: TrendingUp,
      title: 'Taksir Harga Pasar',
      desc: 'Valuasi akurat berbasis 110+ data mobil live dan RAG ChromaDB.',
      prompt: 'Taksir harga pasar wajar untuk Honda Civic 1.5 Turbo tahun 2019 transmisi matic dengan odo 40rb km kondisi mulus.',
    },
    {
      icon: ShieldCheck,
      title: 'Audit Risiko Kendaraan',
      desc: 'Cek potensi red flags, odo reset, dan indikasi bekas tabrak/banjir.',
      prompt: 'Bagaimana cara menganalisis risiko dan red flags mobil bekas Pajero Sport 2020?',
    },
    {
      icon: Search,
      title: 'Rekomendasi Arbitrase',
      desc: 'Temukan unit mobil dengan selisih keuntungan terbesar saat ini.',
      prompt: 'Apa saja 3 mobil bekas dengan potensi diskon arbitrase paling tinggi saat ini?',
    },
  ]

  if (isHistoryLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-slate-500 text-xs">
        <RefreshCw className="w-5 h-5 animate-spin text-brand-orange mb-2" />
        <span>Memuat riwayat konsultasi dari database...</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto py-2">
      {/* If no messages yet, show hero reference screen */}
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center flex-1 text-center py-6 animate-in fade-in duration-200">
          {/* Centered Branded Logo */}
          <div className="w-20 h-20 rounded-2xl overflow-hidden shadow-subtle mb-4 border border-surface-border bg-white flex items-center justify-center p-1.5">
            <img src="/logo.png" alt="AutoBargain Cars" className="w-full h-full object-contain" />
          </div>

          {/* Main Title - No banned eyebrow kicker, strong commanding typography */}
          <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight mb-2">
            Konsultasi Arbitrase Mobil Bekas
          </h2>
          <p className="text-xs text-slate-500 max-w-md mx-auto mb-8 leading-relaxed">
            Taksir estimasi harga pasar wajar, audit riwayat kelayakan unit, dan temukan celah keuntungan arbitrase secara real-time.
          </p>

          {/* Floating Prompt Box (Reference Style) */}
          <div className="w-full max-w-2xl bg-white rounded-3xl border border-surface-border shadow-float p-3 text-left transition-all focus-within:ring-2 focus-within:ring-brand-orange/30 focus-within:border-brand-orange">
            {/* Top Toolbar inside input */}
            <div className="flex items-center gap-2 mb-2 px-2 pt-1">
              <button
                type="button"
                onClick={() => setUseDeeperValuation(!useDeeperValuation)}
                className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold border transition-all ${
                  useDeeperValuation
                    ? 'bg-orange-50 text-brand-orange border-orange-200'
                    : 'bg-slate-50 text-slate-500 border-slate-200'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-brand-orange" />
                <span>Deeper Valuation</span>
              </button>
            </div>

            {/* Input Textarea */}
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              placeholder="Tanyakan valuasi mobil, audit risiko unit, atau tips negosiasi..."
              rows={3}
              className="w-full px-2 py-1.5 text-sm text-slate-900 placeholder-slate-400 bg-transparent resize-none focus:outline-none"
            />

            {/* Bottom Controls Bar inside Prompt Box */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-100 px-2 pb-1">
              <div className="flex items-center gap-1.5 text-slate-400">
                <span title="Neural Network ResNet active" className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-700 cursor-pointer transition-colors">
                  <Cpu className="w-4 h-4" />
                </span>
                <span title="ChromaDB RAG connected" className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-700 cursor-pointer transition-colors">
                  <Globe className="w-4 h-4" />
                </span>
                <span title="Upload spesifikasi unit" className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-700 cursor-pointer transition-colors">
                  <Paperclip className="w-4 h-4" />
                </span>
                <span title="Voice input" className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-700 cursor-pointer transition-colors">
                  <Mic className="w-4 h-4" />
                </span>
              </div>

              <button
                type="button"
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="w-8 h-8 rounded-full bg-brand-orange hover:bg-brand-orange-hover text-white flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed shadow-orange-sm transition-transform active:scale-95 focus-visible:ring-2 focus-visible:ring-brand-orange"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Starter Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full max-w-2xl mt-8">
            {quickPrompts.map((card, idx) => {
              const Icon = card.icon
              return (
                <div
                  key={idx}
                  onClick={() => handleSend(card.prompt)}
                  className="p-4 rounded-2xl bg-white border border-surface-border hover:border-orange-200 hover:shadow-subtle cursor-pointer transition-all text-left group"
                >
                  <Icon className="w-5 h-5 text-slate-700 group-hover:text-brand-orange transition-colors mb-2.5" />
                  <h4 className="text-xs font-bold text-slate-900 group-hover:text-brand-orange transition-colors">
                    {card.title}
                  </h4>
                  <p className="text-[11px] text-slate-600 mt-1 leading-snug">
                    {card.desc}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      ) : (
        /* Conversation Mode */
        <div className="flex flex-col flex-1 h-[78vh]">
          {/* Top Session Control Header */}
          <div className="flex items-center justify-between px-3 py-2 bg-white rounded-2xl border border-surface-border shadow-subtle mb-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-bold text-slate-800">AI Consultant Memory Sesi Aktif</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono tabular-nums">
                {messages.length} Pesan Tersimpan
              </span>
            </div>

            <button
              onClick={handleClearChat}
              title="Bersihkan riwayat dan mulai sesi baru"
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-xs text-rose-600 hover:bg-rose-50 border border-transparent hover:border-rose-100 transition-all font-medium"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Bersihkan Chat</span>
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto space-y-4 px-2 py-2">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 group ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-orange to-amber-500 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`relative max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed transition-all ${
                    msg.role === 'user'
                      ? 'bg-slate-900 text-white rounded-br-none shadow-sm'
                      : 'bg-white text-slate-800 border border-surface-border rounded-bl-none shadow-subtle'
                  }`}
                >
                  {/* Rich Markdown Rendering for Eye-Catching AI Responses */}
                  {msg.role === 'assistant' ? (
                    <div className="prose prose-sm max-w-none text-slate-800 space-y-2">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h1: ({ ...props }) => (
                            <h3 className="text-sm font-extrabold text-slate-900 mt-2 mb-1.5 border-b pb-1 border-slate-100" {...props} />
                          ),
                          h2: ({ ...props }) => (
                            <h4 className="text-xs font-bold text-slate-900 mt-2 mb-1 text-brand-orange" {...props} />
                          ),
                          h3: ({ ...props }) => (
                            <h5 className="text-xs font-bold text-slate-900 mt-2 mb-1 flex items-center gap-1.5" {...props} />
                          ),
                          p: ({ ...props }) => (
                            <p className="mb-2 last:mb-0 leading-relaxed text-xs text-slate-700" {...props} />
                          ),
                          ul: ({ ...props }) => (
                            <ul className="space-y-1 mb-2.5 ml-3.5 list-disc text-xs text-slate-700" {...props} />
                          ),
                          ol: ({ ...props }) => (
                            <ol className="space-y-1 mb-2.5 ml-3.5 list-decimal text-xs text-slate-700 font-mono" {...props} />
                          ),
                          li: ({ ...props }) => (
                            <li className="leading-relaxed" {...props} />
                          ),
                          strong: ({ ...props }) => (
                            <strong className="font-bold text-slate-900" {...props} />
                          ),
                          blockquote: ({ ...props }) => (
                            <blockquote className="border-l-2 border-brand-orange bg-orange-50/70 text-slate-800 px-3 py-2 rounded-r-xl my-2 text-xs font-medium" {...props} />
                          ),
                          code: ({ ...props }) => (
                            <code className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-900 font-mono text-[11px] font-semibold" {...props} />
                          ),
                          table: ({ ...props }) => (
                            <div className="my-3 overflow-x-auto rounded-xl border border-surface-border bg-white shadow-subtle max-w-full">
                              <table className="w-full min-w-[520px] text-left text-xs border-collapse" {...props} />
                            </div>
                          ),
                          thead: ({ ...props }) => (
                            <thead className="bg-slate-50/90 border-b border-surface-border text-slate-800 font-bold text-[11px] uppercase tracking-wider" {...props} />
                          ),
                          th: ({ ...props }) => (
                            <th className="px-3.5 py-2.5 font-bold text-slate-900 border-r border-slate-100 last:border-r-0 whitespace-nowrap bg-slate-50" {...props} />
                          ),
                          tbody: ({ ...props }) => (
                            <tbody className="divide-y divide-slate-100 bg-white" {...props} />
                          ),
                          tr: ({ ...props }) => (
                            <tr className="hover:bg-orange-50/25 transition-colors" {...props} />
                          ),
                          td: ({ ...props }) => (
                            <td className="px-3.5 py-2.5 text-slate-700 border-r border-slate-100 last:border-r-0 leading-relaxed font-sans" {...props} />
                          ),
                        }}
                      >
                        {normalizeMarkdown(msg.content)}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <div className="whitespace-pre-wrap font-sans text-xs leading-relaxed text-white">
                      {msg.content}
                    </div>
                  )}

                  {/* Message Footer: Timestamp and Copy Button */}
                  <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-100/60 text-[10px]">
                    <span
                      className={`font-mono tabular-nums ${
                        msg.role === 'user' ? 'text-slate-400' : 'text-slate-500'
                      }`}
                    >
                      {msg.timestamp}
                    </span>

                    <button
                      onClick={() => handleCopy(msg.content, i)}
                      title="Salin isi pesan"
                      className={`p-1 rounded transition-colors opacity-0 group-hover:opacity-100 ${
                        msg.role === 'user'
                          ? 'hover:bg-slate-800 text-slate-400 hover:text-white'
                          : 'hover:bg-slate-100 text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      {copiedIndex === i ? (
                        <Check className="w-3 h-3 text-emerald-500" />
                      ) : (
                        <Copy className="w-3 h-3" />
                      )}
                    </button>
                  </div>
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-xl bg-slate-200 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-3 items-center">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-orange to-amber-500 text-white flex items-center justify-center shrink-0 shadow-xs">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white border border-surface-border rounded-2xl px-4 py-3 text-xs text-slate-700 flex items-center gap-2.5 shadow-subtle">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-brand-orange" />
                  <span className="font-medium">AI Consultant sedang menganalisis database & merumuskan rekomendasi...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Floating Input in Conversation Mode */}
          <div className="pt-2">
            <div className="bg-white rounded-2xl border border-surface-border shadow-subtle p-2 flex items-center gap-2 focus-within:ring-2 focus-within:ring-brand-orange/30 focus-within:border-brand-orange transition-all">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSend()
                }}
                placeholder="Tulis pertanyaan valuasi lanjutan atau analisis mobil lain..."
                className="flex-1 px-3 py-2 text-xs text-slate-900 placeholder-slate-400 bg-transparent focus:outline-none"
              />
              <button
                type="button"
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="w-9 h-9 rounded-xl bg-brand-orange hover:bg-brand-orange-hover text-white flex items-center justify-center disabled:opacity-40 transition-all shadow-orange-sm active:scale-95 focus-visible:ring-2 focus-visible:ring-brand-orange shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
