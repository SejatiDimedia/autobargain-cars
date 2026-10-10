import React, { useState, useRef, useEffect } from 'react'
import { Terminal, Trash2, ArrowDown, Play, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react'
import { useAgentLogs } from '../../hooks/useAgentLogs'
import { useAgentStatus, useRunAgent } from '../../hooks/useAgentStatus'

export function LiveTerminalView() {
  const { logs, isConnected, clearLogs } = useAgentLogs()
  const { data: status } = useAgentStatus()
  const { mutate: runScan, isPending: isStartingScan } = useRunAgent()
  const [autoScroll, setAutoScroll] = useState(true)
  const logContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  return (
    <div className="flex flex-col h-full space-y-3">
      {/* Terminal Header & Action Bar */}
      <div className="flex items-center justify-between p-3.5 bg-white rounded-2xl border border-surface-border shadow-subtle">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-slate-900 text-white">
            <Terminal className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Console Eksekusi Agen (Live SSE)
              </h3>
              <span
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                  isConnected
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    : 'bg-rose-50 text-rose-700 border-rose-200'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
                {isConnected ? 'SSE Live Connected' : 'Disconnected'}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Streaming real-time log reasoning: Scanner, Ensemble, RAG ChromaDB, & Risk Inspector.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1.5 text-xs text-slate-500 select-none cursor-pointer pr-2">
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
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
            title="Bersihkan log"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          <button
            onClick={() => runScan()}
            disabled={status?.is_running || isStartingScan}
            className="px-3.5 py-1.5 rounded-xl bg-brand-orange hover:bg-brand-orange-hover text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
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

      {/* Terminal Screen Container */}
      <div
        ref={logContainerRef}
        className="flex-1 bg-[#0f141f] rounded-2xl border border-slate-800 p-4 font-mono text-xs overflow-y-auto max-h-[65vh] min-h-[400px] shadow-inner text-slate-300 space-y-1.5"
      >
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-slate-500 font-sans text-xs">
            <Terminal className="w-8 h-8 opacity-40 mb-2" />
            <p>Belum ada output log.</p>
            <p className="text-[11px] text-slate-600 mt-1">Klik "Jalankan Scan Sekarang" untuk memicu pipeline multi-agent.</p>
          </div>
        ) : (
          logs.map((log, idx) => {
            const isInfo = log.level === 'INFO'
            const isWarn = log.level === 'WARNING'
            const isError = log.level === 'ERROR'

            let colorClass = 'text-slate-300'
            if (isWarn) colorClass = 'text-amber-300'
            if (isError) colorClass = 'text-rose-400'
            if (log.message.includes('✅') || log.message.includes('selesai')) colorClass = 'text-emerald-400 font-semibold'
            if (log.message.includes('🚀') || log.message.includes('AutoBargain')) colorClass = 'text-cyan-300 font-semibold'

            return (
              <div key={idx} className="flex items-start gap-2 leading-relaxed hover:bg-white/[0.02] py-0.5 px-1 rounded">
                <span className="text-slate-500 select-none shrink-0 font-sans text-[11px]">
                  [{log.timestamp}]
                </span>
                <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold select-none shrink-0 ${
                  isError ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                  isWarn ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                  'bg-slate-800/80 text-slate-400'
                }`}>
                  {log.level}
                </span>
                <span className={`break-all ${colorClass}`}>
                  {log.message}
                </span>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
