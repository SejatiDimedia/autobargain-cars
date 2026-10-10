import React from 'react'
import { TrendingUp, Database, ShieldCheck, Zap, Activity, DollarSign } from 'lucide-react'
import { StatsResponse } from '../../types/api'
import { formatMillionRupiah } from '../../utils/currency'

interface StatCardsProps {
  stats: StatsResponse | undefined
  isLoading: boolean
}

export function StatCards({ stats, isLoading }: StatCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="p-4 rounded-2xl bg-white border border-surface-border shadow-subtle animate-pulse h-24" />
        ))}
      </div>
    )
  }

  const cards = [
    {
      title: 'Peluang Terdeteksi',
      value: `${stats?.total_opportunities ?? 0} Unit`,
      sub: 'Tersaring via Structured Output',
      icon: Zap,
      color: 'text-brand-orange',
      bg: 'bg-orange-50',
    },
    {
      title: 'Diskon Tertinggi',
      value: `+${formatMillionRupiah(stats?.max_discount_million ?? 0)}`,
      sub: 'Selisih harga terhadap pasar',
      icon: TrendingUp,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
    },
    {
      title: 'Rata-Rata Margin',
      value: `+${formatMillionRupiah(stats?.avg_discount_million ?? 0)}`,
      sub: `Potensi Total: Rp ${Math.round(stats?.total_potential_profit_million ?? 0)} Jt`,
      icon: DollarSign,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      title: 'Database Vektor',
      value: `${stats?.vector_db_car_count ?? 0} Mobil`,
      sub: 'ChromaDB Indexed Memory',
      icon: Database,
      color: 'text-purple-600',
      bg: 'bg-purple-50',
    },
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {cards.map((card, idx) => {
        const Icon = card.icon
        return (
          <div
            key={idx}
            className="p-4 rounded-2xl bg-white border border-surface-border shadow-subtle flex flex-col justify-between"
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                {card.title}
              </span>
              <div className={`p-2 rounded-xl ${card.bg}`}>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
            </div>
            <div className="mt-2">
              <div className="text-xl font-extrabold text-slate-900 tracking-tight">
                {card.value}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                {card.sub}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
