import { TrendingUp, Database, Zap, ArrowUpRight } from 'lucide-react'
import { StatsResponse } from '../../types/api'
import { formatMillionRupiah } from '../../utils/currency'

interface StatCardsProps {
  stats: StatsResponse | undefined
  isLoading: boolean
}

export function StatCards({ stats, isLoading }: StatCardsProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl border border-surface-border p-4 shadow-subtle animate-pulse h-24" />
    )
  }

  return (
    <div className="bg-white rounded-2xl border border-surface-border shadow-subtle overflow-hidden">
      <div className="grid grid-cols-2 lg:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-surface-border">
        {/* Metric 1: Total Profit Potential */}
        <div className="p-4 sm:p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider">
              Total Potensi Profit
            </span>
            <span className="p-1.5 rounded-lg bg-orange-50 text-brand-orange">
              <Zap className="w-3.5 h-3.5" />
            </span>
          </div>
          <div>
            <div className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight font-mono tabular-nums">
              +{formatMillionRupiah(stats?.total_potential_profit_million ?? 0)}
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Dari <span className="font-semibold text-slate-700 font-mono tabular-nums">{stats?.total_opportunities ?? 0}</span> unit terverifikasi
            </p>
          </div>
        </div>

        {/* Metric 2: Max Spread Opportunity */}
        <div className="p-4 sm:p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">
              Diskon Tertinggi
            </span>
            <span className="p-1.5 rounded-lg bg-emerald-50 text-emerald-600">
              <ArrowUpRight className="w-3.5 h-3.5" />
            </span>
          </div>
          <div>
            <div className="text-xl sm:text-2xl font-extrabold text-emerald-600 tracking-tight font-mono tabular-nums">
              +{formatMillionRupiah(stats?.max_discount_million ?? 0)}
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Selisih terbesar terhadap harga wajar
            </p>
          </div>
        </div>

        {/* Metric 3: Average Margin */}
        <div className="p-4 sm:p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider">
              Rata-Rata Margin
            </span>
            <span className="p-1.5 rounded-lg bg-blue-50 text-blue-600">
              <TrendingUp className="w-3.5 h-3.5" />
            </span>
          </div>
          <div>
            <div className="text-xl sm:text-2xl font-extrabold text-blue-600 tracking-tight font-mono tabular-nums">
              +{formatMillionRupiah(stats?.avg_discount_million ?? 0)}
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Rata-rata harga mobil: <span className="font-semibold text-slate-700 font-mono tabular-nums">Rp {Math.round(stats?.avg_car_price_million ?? 0)} Jt</span>
            </p>
          </div>
        </div>

        {/* Metric 4: ChromaDB Vectorstore Depth */}
        <div className="p-4 sm:p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider">
              Database Vektor
            </span>
            <span className="p-1.5 rounded-lg bg-purple-50 text-purple-600">
              <Database className="w-3.5 h-3.5" />
            </span>
          </div>
          <div>
            <div className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight font-mono tabular-nums flex items-center gap-2">
              <span>{stats?.vector_db_car_count ?? 0}</span>
              <span className="text-xs font-normal text-slate-400">Mobil</span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              ChromaDB Embedding Active
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
