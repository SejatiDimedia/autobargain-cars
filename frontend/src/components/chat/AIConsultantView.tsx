import React, { useState, useRef, useEffect } from 'react'
import { Sparkles, Send, Cpu, Globe, Paperclip, Mic, ShieldCheck, TrendingUp, Search, MessageSquare, Bot, User, RefreshCw } from 'lucide-react'
import { sendChatMessage } from '../../api/client'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export function AIConsultantView() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [useDeeperValuation, setUseDeeperValuation] = useState(true)
  const chatEndRef = useRef<HTMLDivElement>(null)

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
      const res = await sendChatMessage(textToSend)
      const assistantMsg: Message = {
        role: 'assistant',
        content: res.response,
        timestamp: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err: any) {
      const errorMsg: Message = {
        role: 'assistant',
        content: `Mohon maaf, terjadi kendala saat memproses: ${err.message || 'Gagal terhubung ke API'}`,
        timestamp: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
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

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto py-2">
      {/* If no messages yet, show hero reference screen */}
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center flex-1 text-center py-6 animate-in fade-in duration-200">
          {/* Top Pill (Reference: Upgrade free plan to full access) */}
          <div className="mb-6 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-subtle border border-surface-border text-[11px] font-medium text-slate-600 shadow-subtle">
            <span className="text-brand-orange">⚡</span>
            <span>AutoBargain Multi-Agent Ensemble • 100% Free-Tier Ready</span>
          </div>

          {/* Centered Orange Geometric Icon */}
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-orange to-amber-500 flex items-center justify-center shadow-orange-sm mb-4">
            <svg viewBox="0 0 24 24" className="w-8 h-8 text-white stroke-current fill-none stroke-2">
              <rect x="3" y="3" width="7" height="7" rx="1.5" />
              <rect x="14" y="3" width="7" height="7" rx="1.5" />
              <rect x="14" y="14" width="7" height="7" rx="1.5" />
              <rect x="3" y="14" width="7" height="7" rx="1.5" />
            </svg>
          </div>

          {/* Main Title */}
          <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight mb-8">
            Konsultasi Arbitrase Mobil Bekas
          </h2>

          {/* Floating Prompt Box (Reference Style) */}
          <div className="w-full max-w-2xl bg-white rounded-3xl border border-surface-border shadow-float p-3 text-left transition-all focus-within:ring-2 focus-within:ring-brand-orange/20 focus-within:border-brand-orange">
            {/* Top Toolbar inside input */}
            <div className="flex items-center gap-2 mb-2 px-2 pt-1">
              <button
                type="button"
                onClick={() => setUseDeeperValuation(!useDeeperValuation)}
                className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold border transition-all ${
                  useDeeperValuation
                    ? 'bg-orange-50 text-brand-orange border-orange-200'
                    : 'bg-slate-50 text-slate-400 border-slate-200'
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
              className="w-full px-2 py-1.5 text-sm text-slate-800 placeholder-slate-400 bg-transparent resize-none focus:outline-none"
            />

            {/* Bottom Controls Bar inside Prompt Box */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-100 px-2 pb-1">
              <div className="flex items-center gap-2.5 text-slate-400">
                <span title="Neural Network ResNet active" className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-600 cursor-pointer transition-colors">
                  <Cpu className="w-4 h-4" />
                </span>
                <span title="ChromaDB RAG connected" className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-600 cursor-pointer transition-colors">
                  <Globe className="w-4 h-4" />
                </span>
                <span title="Upload spesifikasi / foto" className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-600 cursor-pointer transition-colors">
                  <Paperclip className="w-4 h-4" />
                </span>
                <span title="Voice input" className="p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-600 cursor-pointer transition-colors">
                  <Mic className="w-4 h-4" />
                </span>
              </div>

              <button
                type="button"
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="w-8 h-8 rounded-full bg-brand-orange hover:bg-brand-orange-hover text-white flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed shadow-orange-sm transition-transform active:scale-95"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Starter Cards (Reference: Summarize Text, Creative Writing, Answer Questions) */}
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
                  <p className="text-[11px] text-slate-500 mt-1 leading-snug">
                    {card.desc}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      ) : (
        /* Conversation Mode */
        <div className="flex flex-col flex-1 h-[75vh]">
          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto space-y-4 px-2 py-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-xl bg-orange-100 text-brand-orange flex items-center justify-center shrink-0 mt-0.5 border border-orange-200">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-slate-900 text-white rounded-br-none shadow-sm'
                      : 'bg-white text-slate-800 border border-surface-border rounded-bl-none shadow-subtle'
                  }`}
                >
                  <div className="whitespace-pre-wrap font-sans">{msg.content}</div>
                  <div
                    className={`text-[10px] mt-1.5 text-right ${
                      msg.role === 'user' ? 'text-slate-400' : 'text-slate-400'
                    }`}
                  >
                    {msg.timestamp}
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
                <div className="w-8 h-8 rounded-xl bg-orange-100 text-brand-orange flex items-center justify-center shrink-0 border border-orange-200">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white border border-surface-border rounded-2xl px-4 py-3 text-xs text-slate-500 flex items-center gap-2 shadow-subtle">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-brand-orange" />
                  <span>AI Agent sedang menganalisis pasar & database...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Floating Input in Conversation Mode */}
          <div className="pt-2">
            <div className="bg-white rounded-2xl border border-surface-border shadow-subtle p-2 flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSend()
                }}
                placeholder="Tulis pesan lanjutan atau pertanyaan lain..."
                className="flex-1 px-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 bg-transparent focus:outline-none"
              />
              <button
                type="button"
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="w-8 h-8 rounded-xl bg-brand-orange hover:bg-brand-orange-hover text-white flex items-center justify-center disabled:opacity-40 transition-colors shadow-sm"
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
