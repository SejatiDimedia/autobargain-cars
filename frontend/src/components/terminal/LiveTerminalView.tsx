import { useState, useRef, useEffect, useMemo } from 'react'
import { Terminal, Trash2, Play, Sparkles, Filter, Search } from 'lucide-react'
import { useAgentLogs } from '../../hooks/useAgentLogs'
import { useAgentStatus, useRunAgent } from '../../hooks/useAgentStatus'
import { LogEntry } from '../../types/api'

interface AgentTheme {
  id: string
  displayName: string
  badgeBg: string
  badgeText: string
  badgeBorder: string
  textColor: string
  dotColor: string
}

function getAgentTheme(agent?: string, message?: string): AgentTheme {
  const combined = `${agent || ''} ${message || ''}`.toLowerCase()

  // 1. Scanner Agent (Cyan)
  if (combined.includes('scanner')) {
    return {
      id: 'scanner',
      displayName: 'Scanner Agent',
      badgeBg: 'bg-cyan-950/80',
      badgeText: 'text-cyan-300',
      badgeBorder: 'border-cyan-700/60 shadow-[0_0_8px_rgba(6,182,212,0.18)]',
      textColor: 'text-cyan-200',
      dotColor: 'bg-cyan-400',
    }
  }

  // 2. Planning Agent / Autonomous Planning (Emerald Green)
  if (combined.includes('planning') || combined.includes('planner') || combined.includes('autonomous')) {
    return {
      id: 'planner',
      displayName: 'Planning Agent',
      badgeBg: 'bg-emerald-950/80',
      badgeText: 'text-emerald-300',
      badgeBorder: 'border-emerald-700/60 shadow-[0_0_8px_rgba(16,185,129,0.18)]',
      textColor: 'text-emerald-200',
      dotColor: 'bg-emerald-400',
    }
  }

  // 3. Ensemble Valuation Agent (Amber / Gold)
  if (combined.includes('ensemble')) {
    return {
      id: 'ensemble',
      displayName: 'Ensemble Agent',
      badgeBg: 'bg-amber-950/80',
      badgeText: 'text-amber-300',
      badgeBorder: 'border-amber-700/60 shadow-[0_0_8px_rgba(245,158,11,0.18)]',
      textColor: 'text-amber-200',
      dotColor: 'bg-amber-400',
    }
  }

  // 4. Neural Network Agent / PyTorch (Fuchsia / Magenta)
  if (combined.includes('neural') || combined.includes('pytorch')) {
    return {
      id: 'neural',
      displayName: 'Neural Network Agent',
      badgeBg: 'bg-fuchsia-950/80',
      badgeText: 'text-fuchsia-300',
      badgeBorder: 'border-fuchsia-700/60 shadow-[0_0_8px_rgba(217,70,239,0.18)]',
      textColor: 'text-fuchsia-200',
      dotColor: 'bg-fuchsia-400',
    }
  }

  // 5. Specialist Valuation Agent (Orange)
  if (combined.includes('specialist')) {
    return {
      id: 'specialist',
      displayName: 'Specialist Agent',
      badgeBg: 'bg-orange-950/80',
      badgeText: 'text-orange-300',
      badgeBorder: 'border-orange-700/60 shadow-[0_0_8px_rgba(249,115,22,0.18)]',
      textColor: 'text-orange-200',
      dotColor: 'bg-orange-400',
    }
  }

  // 6. Risk Analyst Agent (Rose / Coral Red)
  if (combined.includes('risk')) {
    return {
      id: 'risk',
      displayName: 'Risk Analyst Agent',
      badgeBg: 'bg-rose-950/80',
      badgeText: 'text-rose-300',
      badgeBorder: 'border-rose-700/60 shadow-[0_0_8px_rgba(244,63,94,0.18)]',
      textColor: 'text-rose-200',
      dotColor: 'bg-rose-400',
    }
  }

  // 7. Frontier / Conversational ReAct Agent (Sky Blue)
  if (combined.includes('frontier') || combined.includes('react') || combined.includes('conversational')) {
    return {
      id: 'frontier',
      displayName: 'Frontier / ReAct Agent',
      badgeBg: 'bg-sky-950/80',
      badgeText: 'text-sky-300',
      badgeBorder: 'border-sky-700/60 shadow-[0_0_8px_rgba(14,165,233,0.18)]',
      textColor: 'text-sky-200',
      dotColor: 'bg-sky-400',
    }
  }

  // 8. Messaging / Preprocessor Agent (Indigo)
  if (combined.includes('messaging') || combined.includes('telegram') || combined.includes('preprocessor')) {
    return {
      id: 'messaging',
      displayName: 'Messaging / Prep Agent',
      badgeBg: 'bg-indigo-950/80',
      badgeText: 'text-indigo-300',
      badgeBorder: 'border-indigo-700/60 shadow-[0_0_8px_rgba(99,102,241,0.18)]',
      textColor: 'text-indigo-200',
      dotColor: 'bg-indigo-400',
    }
  }

  // 9. AutoBargain System / Framework default (Slate)
  return {
    id: 'system',
    displayName: agent || 'AutoBargain System',
    badgeBg: 'bg-slate-800/80',
    badgeText: 'text-slate-300',
    badgeBorder: 'border-slate-700',
    textColor: 'text-slate-200',
    dotColor: 'bg-slate-400',
  }
}

function cleanMessageText(text: string): string {
  // Bersihkan ANSI escape sequence jika ada sisa
  let clean = text.replace(/\x1b\[[0-9;]*[a-zA-Z]/g, '').trim()
  // Bersihkan tag kurung siku agen di awal pesan jika terduplikasi
  clean = clean.replace(/^\[[a-zA-Z0-9\s_.-]+\]\s*/, '').trim()
  return clean || text
}

const AGENT_FILTERS = [
  { id: 'all', label: 'Semua Agen', dot: 'bg-slate-400' },
  { id: 'scanner', label: 'Scanner', dot: 'bg-cyan-400' },
  { id: 'planner', label: 'Planner', dot: 'bg-emerald-400' },
  { id: 'ensemble', label: 'Ensemble', dot: 'bg-amber-400' },
  { id: 'neural', label: 'Neural Net', dot: 'bg-fuchsia-400' },
  { id: 'risk', label: 'Risk Analyst', dot: 'bg-rose-400' },
  { id: 'frontier', label: 'Frontier / ReAct', dot: 'bg-sky-400' },
  { id: 'system', label: 'System', dot: 'bg-slate-400' },
]

export function LiveTerminalView() {
  const { logs, isConnected, clearLogs } = useAgentLogs()
  const { data: status } = useAgentStatus()
  const { mutate: runScan, isPending: isStartingScan } = useRunAgent()
  const [autoScroll, setAutoScroll] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const logContainerRef = useRef<HTMLDivElement>(null)

  // Hitung sebaran log per agen untuk badge jumlah
  const agentCounts = useMemo(() => {
    const counts: Record<string, number> = { all: logs.length }
    logs.forEach((log) => {
      const theme = getAgentTheme(log.agent, log.message)
      counts[theme.id] = (counts[theme.id] || 0) + 1
    })
    return counts
  }, [logs])

  // Filter logs berdasarkan agen yang dipilih dan kata kunci pencarian
  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      const theme = getAgentTheme(log.agent, log.message)
      if (selectedAgent !== 'all' && theme.id !== selectedAgent) {
        return false
      }
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase()
        const matchMsg = log.message.toLowerCase().includes(query)
        const matchAgent = (log.agent || '').toLowerCase().includes(query)
        if (!matchMsg && !matchAgent) return false
      }
      return true
    })
  }, [logs, selectedAgent, searchQuery])

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [filteredLogs, autoScroll])

  return (
    <div className="flex flex-col h-full space-y-3">
      {/* Terminal Header & Main Action Bar */}
      <div className="flex items-center justify-between p-3.5 bg-white rounded-2xl border border-surface-border shadow-subtle">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-slate-900 text-white">
            <Terminal className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Console Eksekusi Agen (Live Multi-Agent Stream)
              </h3>
              <span
                className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold border ${
                  isConnected
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                    : 'bg-rose-50 text-rose-800 border-rose-200'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
                {isConnected ? 'SSE Live Connected' : 'Disconnected'}
              </span>
            </div>
            <p className="text-[11px] text-slate-600 mt-0.5">
              Setiap agen memiliki warna eksekusi unik untuk membedakan proses pemindaian, valuasi, AI neural, dan analisis risiko secara real-time.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1.5 text-xs text-slate-600 select-none cursor-pointer pr-2">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded text-brand-orange focus:ring-brand-orange"
            />
            <span>Auto-scroll</span>
          </label>

          <button
            onClick={clearLogs}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors focus-visible:ring-2 focus-visible:ring-brand-orange"
            title="Bersihkan log"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          <button
            onClick={() => runScan()}
            disabled={status?.is_running || isStartingScan}
            className="px-3.5 py-1.5 rounded-xl bg-brand-orange hover:bg-brand-orange-hover text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all focus-visible:ring-2 focus-visible:ring-brand-orange"
          >
            {status?.is_running ? (
              <>
                <Sparkles className="w-3.5 h-3.5 animate-spin" /> Sedang Memindai...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" /> Jalankan Scan Sekarang
              </>
            )}
          </button>
        </div>
      </div>

      {/* Agent Legend & Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-3.5 py-2.5 bg-[#0a0e17] rounded-xl border border-slate-800 shadow-inner text-xs">
        <div className="flex items-center gap-1.5 overflow-x-auto py-0.5 scrollbar-thin">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider shrink-0 flex items-center gap-1 mr-1">
            <Filter className="w-3 h-3 text-slate-400" /> Legend / Filter:
          </span>
          {AGENT_FILTERS.map((f) => {
            const count = agentCounts[f.id] || 0
            const isActive = selectedAgent === f.id
            return (
              <button
                key={f.id}
                onClick={() => setSelectedAgent(f.id)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all border ${
                  isActive
                    ? 'bg-slate-800 text-white border-slate-600 shadow-sm'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800/80 hover:bg-slate-800/60 hover:text-slate-300'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${f.dot}`} />
                <span>{f.label}</span>
                {count > 0 && (
                  <span
                    className={`ml-0.5 px-1.5 py-0.2 rounded-full text-[9px] font-bold ${
                      isActive ? 'bg-slate-700 text-white' : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {count}
                  </span>
                )}
              </button>
            )
          })}
        </div>

        {/* Quick Search */}
        <div className="relative shrink-0">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Cari log atau teks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-200 text-[11px] rounded-lg pl-7 pr-2.5 py-1 w-44 focus:outline-none focus:border-brand-orange placeholder:text-slate-600 transition-colors"
          />
        </div>
      </div>

      {/* Terminal Screen Container */}
      <div
        ref={logContainerRef}
        className="flex-1 bg-[#090d14] rounded-2xl border border-slate-800/90 p-4 font-mono text-xs overflow-y-auto max-h-[62vh] min-h-[420px] shadow-2xl text-slate-300 space-y-1.5 selection:bg-brand-orange/30 selection:text-white"
      >
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-slate-500 font-sans text-xs">
            <Terminal className="w-8 h-8 opacity-40 mb-2" />
            <p className="text-slate-400 font-medium">Belum ada output log.</p>
            <p className="text-[11px] text-slate-500 mt-1">
              Klik "Jalankan Scan Sekarang" untuk memicu pipeline multi-agent dan melihat eksekusi warna tiap agen.
            </p>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-500 font-sans text-xs">
            <Filter className="w-6 h-6 opacity-40 mb-2" />
            <p className="text-slate-400 font-medium">Tidak ada log yang cocok dengan filter saat ini.</p>
            <button
              onClick={() => {
                setSelectedAgent('all')
                setSearchQuery('')
              }}
              className="mt-2 text-brand-orange hover:underline text-xs"
            >
              Reset filter
            </button>
          </div>
        ) : (
          filteredLogs.map((log: LogEntry, idx: number) => {
            const isWarn = log.level === 'WARNING'
            const isError = log.level === 'ERROR'
            const theme = getAgentTheme(log.agent, log.message)
            const cleanText = cleanMessageText(log.message)

            return (
              <div
                key={idx}
                className="flex items-start gap-2.5 leading-relaxed hover:bg-white/[0.04] py-1 px-2 rounded-lg transition-colors font-mono group"
              >
                {/* Timestamp */}
                <span className="text-slate-500 select-none shrink-0 text-[11px] tabular-nums pt-0.5">
                  [{log.timestamp}]
                </span>

                {/* Agent Badge (Warna Unik Tiap Agen) */}
                <span
                  className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-bold tracking-wide border select-none shrink-0 transition-transform ${theme.badgeBg} ${theme.badgeText} ${theme.badgeBorder}`}
                  title={theme.displayName}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${theme.dotColor}`} />
                  {theme.displayName}
                </span>

                {/* Level Badge jika Warning / Error */}
                {log.level !== 'INFO' && (
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold select-none shrink-0 ${
                      isError
                        ? 'bg-rose-950 text-rose-300 border border-rose-800'
                        : isWarn
                        ? 'bg-amber-950 text-amber-300 border border-amber-800'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {log.level}
                  </span>
                )}

                {/* Pesan Eksekusi dengan Warna Agen */}
                <span
                  className={`break-words flex-1 text-xs leading-relaxed ${
                    isError
                      ? 'text-rose-300 font-semibold'
                      : isWarn
                      ? 'text-amber-200'
                      : theme.textColor
                  }`}
                >
                  {cleanText}
                </span>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
