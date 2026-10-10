import { useState } from 'react'
import { ChevronDown, Share2, RefreshCw, FileText, Check } from 'lucide-react'

interface HeaderProps {
  onRefresh: () => void
  isRefreshing: boolean
}

export function Header({ onRefresh, isRefreshing }: HeaderProps) {
  const [copied, setCopied] = useState(false)

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <header className="px-6 py-3.5 border-b border-surface-border bg-white flex items-center justify-between select-none shrink-0">
      {/* Left: Model Selector (Reference: Cognivo Core v1 ⌵) */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-slate-900 text-sm font-bold">
          <span>AutoBargain Core v1.0</span>
          <ChevronDown className="w-4 h-4 text-slate-400" />
        </div>

        <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 font-medium hidden sm:inline-block">
          Ensemble RAG + ResNet
        </span>
      </div>

      {/* Right Actions (Reference: Share button, link, more options) */}
      <div className="flex items-center gap-2">
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-surface-hover transition-colors focus-visible:ring-2 focus-visible:ring-brand-orange"
          title="Refresh Data Peluang"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-brand-orange' : ''}`} />
        </button>

        <a
          href="/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-surface-hover transition-colors focus-visible:ring-2 focus-visible:ring-brand-orange"
          title="Dokumentasi Swagger API"
        >
          <FileText className="w-4 h-4" />
        </a>

        <button
          onClick={handleShare}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-surface-border hover:bg-surface-hover text-xs font-semibold text-slate-800 transition-colors shadow-subtle focus-visible:ring-2 focus-visible:ring-brand-orange"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-700" /> : <Share2 className="w-3.5 h-3.5" />}
          <span>{copied ? 'Tersalin!' : 'Share'}</span>
        </button>
      </div>
    </header>
  )
}
