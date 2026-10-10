import React from 'react'
import { ChevronDown, Share2, RefreshCw, Radio, FileText, Check } from 'lucide-react'
import { useAgentStatus } from '../../hooks/useAgentStatus'
import { useOpportunities } from '../../hooks/useOpportunities'

interface HeaderProps {
  onRefresh: () => void
  isRefreshing: boolean
}

export function Header({ onRefresh, isRefreshing }: HeaderProps) {
  const { data: status } = useAgentStatus()
  const { data: opportunities = [] } = useOpportunities()
  const [copied, setCopied] = React.useState(false)

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
        <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl hover:bg-surface-hover text-slate-800 text-sm font-bold transition-colors">
          <span>AutoBargain Core v1.0</span>
          <ChevronDown className="w-4 h-4 text-slate-400" />
        </button>

        <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium hidden sm:inline-block">
          Ensemble RAG + ResNet
        </span>
      </div>

      {/* Right Actions (Reference: Share button, link, more options) */}
      <div className="flex items-center gap-2">
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-surface-hover transition-colors"
          title="Refresh Data Peluang"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-brand-orange' : ''}`} />
        </button>

        <a
          href="/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-surface-hover transition-colors"
          title="Dokumentasi Swagger API"
        >
          <FileText className="w-4 h-4" />
        </a>

        <button
          onClick={handleShare}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-surface-border hover:bg-surface-hover text-xs font-semibold text-slate-700 transition-colors shadow-subtle"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Share2 className="w-3.5 h-3.5" />}
          <span>{copied ? 'Tersalin!' : 'Share'}</span>
        </button>
      </div>
    </header>
  )
}
