import {
  Search,
  MessageSquare,
  BarChart3,
  Database,
  Terminal,
  Plus,
  PanelLeftClose,
  Cpu,
  RefreshCw,
} from 'lucide-react'
import { useAgentStatus, useRunAgent } from '../../hooks/useAgentStatus'
import { useOpportunities } from '../../hooks/useOpportunities'
import { CarOpportunity } from '../../types/car'

export type ActiveTab = 'deals' | 'chat' | 'analytics' | 'vectors' | 'terminal'

interface SidebarProps {
  activeTab: ActiveTab
  setActiveTab: (tab: ActiveTab) => void
  onSelectDeal?: (deal: CarOpportunity) => void
  isCollapsed: boolean
  setIsCollapsed: (collapsed: boolean) => void
}

export function Sidebar({
  activeTab,
  setActiveTab,
  onSelectDeal,
  isCollapsed,
  setIsCollapsed,
}: SidebarProps) {
  const { data: status } = useAgentStatus()
  const { data: opportunities = [] } = useOpportunities()
  const { mutate: runScan, isPending: isStartingScan } = useRunAgent()

  const navItems = [
    { id: 'deals' as ActiveTab, label: 'Peluang Arbitrase', icon: Search, badge: `${opportunities.length}` },
    { id: 'chat' as ActiveTab, label: 'AI Car Consultant', icon: MessageSquare },
    { id: 'analytics' as ActiveTab, label: 'Analitik Pasar', icon: BarChart3 },
    { id: 'vectors' as ActiveTab, label: '3D Vector Space', icon: Database },
    { id: 'terminal' as ActiveTab, label: 'Live Console SSE', icon: Terminal },
  ]

  // Top 5 arbitrage deals for recent deals section in sidebar
  const topDeals = opportunities.slice(0, 5)

  return (
    <aside
      className={`h-full bg-surface-sidebar border-r border-surface-border flex flex-col justify-between transition-all duration-200 select-none ${
        isCollapsed ? 'w-20 px-3' : 'w-64 px-4'
      } py-5`}
    >
      {/* Top Part */}
      <div className="space-y-4">
        {/* Brand Header */}
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2.5 overflow-hidden">
            {/* Branded Logo Icon Mark */}
            <div className="w-8 h-8 rounded-xl overflow-hidden shrink-0 shadow-xs bg-slate-900 flex items-center justify-center">
              <img src="/icon.png" alt="AutoBargain Logo" className="w-full h-full object-cover" />
            </div>
            {!isCollapsed && (
              <span className="font-extrabold text-slate-900 tracking-tight text-base font-sans">
                AutoBargain
              </span>
            )}
          </div>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors focus-visible:ring-2 focus-visible:ring-brand-orange"
            title={isCollapsed ? 'Buka Sidebar' : 'Tutup Sidebar'}
          >
            <PanelLeftClose className={`w-4 h-4 transition-transform ${isCollapsed ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Primary Action Button (Reference: + New Chat solid orange) */}
        <button
          onClick={() => runScan()}
          disabled={status?.is_running || isStartingScan}
          className={`w-full py-2.5 px-3 rounded-xl bg-brand-orange hover:bg-brand-orange-hover text-white font-semibold text-xs flex items-center shadow-orange-sm transition-all disabled:opacity-60 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-brand-orange ${
            isCollapsed ? 'justify-center' : 'justify-between'
          }`}
          title="Memicu siklus pemindaian pasar baru"
        >
          <div className="flex items-center gap-2">
            {status?.is_running ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            {!isCollapsed && (
              <span>{status?.is_running ? 'Memindai Pasar...' : 'Scan Pasar Baru'}</span>
            )}
          </div>
          {!isCollapsed && (
            <kbd className="text-[10px] bg-white/25 px-1.5 py-0.5 rounded text-white font-mono font-medium">
              ⌘S
            </kbd>
          )}
        </button>

        {/* Main Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all focus-visible:ring-2 focus-visible:ring-brand-orange ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-surface-hover'
                } ${isCollapsed ? 'justify-center' : ''}`}
                title={item.label}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-brand-orange' : 'text-slate-500'}`} />
                {!isCollapsed && <span className="flex-1 text-left">{item.label}</span>}
                {!isCollapsed && item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold font-mono tabular-nums ${
                      isActive ? 'bg-slate-800 text-orange-400' : 'bg-slate-200/80 text-slate-700'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            )
          })}
        </nav>

        {/* Recent Deals Section (Reference: TODAY / YESTERDAY history items) */}
        {!isCollapsed && (
          <div className="pt-3 border-t border-surface-border space-y-2">
            <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">
              Peluang Terhangat
            </p>
            <div className="space-y-0.5 max-h-48 overflow-y-auto">
              {topDeals.length === 0 ? (
                <p className="px-3 text-[11px] text-slate-400 italic">Belum ada unit ditemukan</p>
              ) : (
                topDeals.map((opp, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSelectDeal?.(opp)}
                    className="w-full text-left px-3 py-1.5 rounded-lg text-[11px] text-slate-600 hover:text-slate-900 hover:bg-surface-hover transition-colors truncate block group"
                  >
                    <div className="truncate font-medium flex items-center justify-between">
                      <span className="truncate group-hover:text-brand-orange transition-colors">
                        {opp.deal.brand} {opp.deal.model}
                      </span>
                      <span className="text-[10px] font-bold text-emerald-700 ml-1 shrink-0 font-mono tabular-nums">
                        +{Math.round(opp.discount)}jt
                      </span>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Part: System Status (NO DUMMY USER LOGIN!) */}
      <div className="pt-3 border-t border-surface-border space-y-2">
        {!isCollapsed ? (
          <div className="p-3 rounded-2xl bg-white border border-surface-border shadow-subtle space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-700 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-brand-orange" /> Engine Multi-Agent
              </span>
              <span
                className={`w-2 h-2 rounded-full ${
                  status?.is_running ? 'bg-amber-400 animate-ping' : 'bg-emerald-500'
                }`}
                title={status?.is_running ? 'Running' : 'Standby'}
              />
            </div>
            <div className="text-[11px] text-slate-600 flex items-center justify-between pt-1 border-t border-slate-100">
              <span>Status:</span>
              <span className="font-semibold text-slate-800">
                {status?.is_running ? 'Scanning Pasar...' : 'Ready / Standby'}
              </span>
            </div>
            <div className="text-[11px] text-slate-600 flex items-center justify-between">
              <span>Total Siklus:</span>
              <span className="font-semibold text-slate-800 font-mono tabular-nums">{status?.total_cycles ?? 0} Kali</span>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <span
              className={`w-3 h-3 rounded-full ${
                status?.is_running ? 'bg-amber-400 animate-ping' : 'bg-emerald-500'
              }`}
              title="Engine Active"
            />
          </div>
        )}
      </div>
    </aside>
  )
}
