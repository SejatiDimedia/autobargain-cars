import { Car, Zap, Activity } from 'lucide-react'
import { useStats } from './hooks/useStats'
import { useAgentStatus } from './hooks/useAgentStatus'

export default function App() {
  const { data: stats, isLoading: statsLoading } = useStats()
  const { data: agentStatus } = useAgentStatus()

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-[#0c1220]/70 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Car className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg leading-tight tracking-tight text-white flex items-center gap-2">
                AutoBargain AI
                <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  Arbitrage Hunter
                </span>
              </h1>
              <p className="text-xs text-slate-400">Autonomous Used Car Multi-Agent Ensemble</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
              <span className={`w-2 h-2 rounded-full ${agentStatus?.is_running ? 'bg-amber-400 animate-ping' : 'bg-emerald-400'}`} />
              <span className="text-slate-300 font-medium">
                {agentStatus?.is_running ? 'Agent Scanning...' : 'Agent Standby'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="p-8 rounded-2xl bg-[#0e1626] border border-slate-800 shadow-xl">
          <div className="flex items-center gap-3 text-cyan-400 mb-3">
            <Zap className="w-6 h-6" />
            <h2 className="text-xl font-bold text-white">Frontend Architecture Setup Berhasil!</h2>
          </div>
          <p className="text-slate-400 text-sm mb-6">
            React 18 + Vite + TanStack Query + TanStack Table + Tailwind CSS telah terpasang dan siap digunakan.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-800">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <p className="text-xs text-slate-500 uppercase font-semibold">Total Peluang Tersimpan</p>
              <p className="text-2xl font-bold text-white mt-1">
                {statsLoading ? '...' : stats?.total_opportunities ?? 0}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <p className="text-xs text-slate-500 uppercase font-semibold">Mobil di Vector Database</p>
              <p className="text-2xl font-bold text-cyan-400 mt-1">
                {statsLoading ? '...' : stats?.vector_db_car_count ?? 0}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <p className="text-xs text-slate-500 uppercase font-semibold">Status Siklus Pemindaian</p>
              <p className="text-2xl font-bold text-emerald-400 mt-1 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                {statsLoading ? '...' : `${stats?.total_cycles ?? 0} Siklus`}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
