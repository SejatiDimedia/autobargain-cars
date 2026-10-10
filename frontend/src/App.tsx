import { useState } from 'react'
import { Sidebar, ActiveTab } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { DealsTable } from './components/deals/DealsTable'
import { AIConsultantView } from './components/chat/AIConsultantView'
import { AnalyticsView } from './components/analytics/AnalyticsView'
import { VectorSpaceView } from './components/visualization/VectorSpaceView'
import { LiveTerminalView } from './components/terminal/LiveTerminalView'
import { StatCards } from './components/dashboard/StatCards'
import { DealDetailModal } from './components/deals/DealDetailModal'
import { useOpportunities } from './hooks/useOpportunities'
import { useStats } from './hooks/useStats'
import { CarOpportunity } from './types/car'

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('deals')
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [selectedDeal, setSelectedDeal] = useState<CarOpportunity | null>(null)

  const { data: opportunities = [], isLoading: isOppsLoading, refetch: refetchOpps, isRefetching } = useOpportunities()
  const { data: stats, isLoading: isStatsLoading, refetch: refetchStats } = useStats()

  const handleRefresh = () => {
    refetchOpps()
    refetchStats()
  }

  return (
    <div className="h-screen w-screen bg-[#eceff3] p-2 md:p-4 overflow-hidden flex flex-col font-sans">
      {/* Outer Floating Window Canvas (Reference Style: Rounded Window with clean border & shadow) */}
      <div className="flex-1 bg-white rounded-2xl md:rounded-3xl border border-surface-border shadow-float overflow-hidden flex flex-row">
        {/* Left Collapsible Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onSelectDeal={(deal) => setSelectedDeal(deal)}
          isCollapsed={isSidebarCollapsed}
          setIsCollapsed={setIsSidebarCollapsed}
        />

        {/* Right Main Content */}
        <div className="flex-1 flex flex-col h-full overflow-hidden bg-white">
          {/* Header Bar */}
          <Header onRefresh={handleRefresh} isRefreshing={isRefetching} />

          {/* Body Content Area */}
          <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-surface-subtle/30">
            {activeTab === 'deals' && (
              <div className="space-y-5 max-w-7xl mx-auto">
                {/* Stat Cards Overview */}
                <StatCards stats={stats} isLoading={isStatsLoading} />

                {/* TanStack Deals Table */}
                <DealsTable opportunities={opportunities} isLoading={isOppsLoading} />
              </div>
            )}

            {activeTab === 'chat' && (
              <AIConsultantView />
            )}

            {activeTab === 'analytics' && (
              <div className="max-w-7xl mx-auto">
                <AnalyticsView />
              </div>
            )}

            {activeTab === 'vectors' && (
              <div className="max-w-5xl mx-auto">
                <VectorSpaceView />
              </div>
            )}

            {activeTab === 'terminal' && (
              <div className="max-w-6xl mx-auto h-full">
                <LiveTerminalView />
              </div>
            )}
          </main>

          {/* Floating Subtle Footer / Disclaimer (Reference: Cognivo can make mistakes...) */}
          <footer className="px-6 py-2 border-t border-surface-border bg-white text-center text-[11px] text-slate-400 select-none">
            AutoBargain AI Ensemble valuation is indicative. Verify actual vehicle inspection before purchase.
          </footer>
        </div>
      </div>

      {/* Standalone Detail Modal (triggered from sidebar recent deals) */}
      <DealDetailModal deal={selectedDeal} onClose={() => setSelectedDeal(null)} />
    </div>
  )
}
