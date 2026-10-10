import React from 'react'
import { BarChart3, TrendingUp, ShieldCheck, Database, Trash2, Sparkles, CheckCircle2 } from 'lucide-react'
import { useStats } from '../../hooks/useStats'
import { useClearOpportunities } from '../../hooks/useOpportunities'
import { StatCards } from '../dashboard/StatCards'
import { formatMillionRupiah } from '../../utils/currency'

export function AnalyticsView() {
  const { data: stats, isLoading } = useStats()
  const { mutate: clearMemory, isPending: isClearing } = useClearOpportunities()

  const brandDist = stats?.brand_distribution || {}
  const gradeDist = stats?.grade_distribution || {}

  const sortedBrands = Object.entries(brandDist).sort((a, b) => b[1] - a[1])
  const maxBrandCount = sortedBrands.length > 0 ? sortedBrands[0][1] : 1

  return (
    <div className="space-y-6">
      {/* 4 Stat Overview Cards */}
      <StatCards stats={stats} isLoading={isLoading} />

      {/* Distribution Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Brand Distribution Card */}
        <div className="p-5 rounded-2xl bg-white border border-surface-border shadow-subtle space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-brand-orange" />
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Sebaran Merk Mobil Arbitrase
              </h3>
            </div>
            <span className="text-xs text-slate-400">
              {Object.keys(brandDist).length} Merk
            </span>
          </div>

          <div className="space-y-2.5">
            {sortedBrands.length === 0 ? (
              <p className="text-xs text-slate-400 py-6 text-center">Belum ada data merk.</p>
            ) : (
              sortedBrands.slice(0, 6).map(([brand, count]) => {
                const percent = Math.round((count / (stats?.total_opportunities || 1)) * 100)
                const barWidth = Math.round((count / maxBrandCount) * 100)

                return (
                  <div key={brand} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-semibold text-slate-800">{brand}</span>
                      <span className="text-slate-500 font-medium">
                        {count} unit ({percent}%)
                      </span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-brand-orange to-amber-500 rounded-full transition-all duration-500"
                        style={{ width: `${barWidth}%` }}
                      />
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>

        {/* AI Risk Grade Distribution Card */}
        <div className="p-5 rounded-2xl bg-white border border-surface-border shadow-subtle space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Hasil Kelayakan AI Risk Inspector
                </h3>
              </div>
              <span className="text-xs text-slate-400">Tingkat Keamanan</span>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-100 text-center">
                <p className="text-xs font-bold text-emerald-800">Grade A</p>
                <p className="text-xl font-extrabold text-emerald-600 mt-1">
                  {gradeDist['Grade A'] ?? 0}
                </p>
                <p className="text-[10px] text-emerald-700/80 mt-0.5">Low Risk</p>
              </div>

              <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-100 text-center">
                <p className="text-xs font-bold text-amber-800">Grade B</p>
                <p className="text-xl font-extrabold text-amber-600 mt-1">
                  {gradeDist['Grade B'] ?? 0}
                </p>
                <p className="text-[10px] text-amber-700/80 mt-0.5">Medium Risk</p>
              </div>

              <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-100 text-center">
                <p className="text-xs font-bold text-rose-800">Grade C</p>
                <p className="text-xl font-extrabold text-rose-600 mt-1">
                  {gradeDist['Grade C'] ?? 0}
                </p>
                <p className="text-[10px] text-rose-700/80 mt-0.5">High Risk</p>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 mt-4 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
              AI Risk Inspector mengevaluasi 15+ parameter keamanan termasuk kecocokan harga wajar, riwayat servis resmi, status pajak STNK/BPKB, serta anomali jarak tempuh.
            </p>
          </div>

          {/* Action to clear memory */}
          <div className="pt-3 border-t border-surface-border flex items-center justify-between">
            <span className="text-xs text-slate-500">Reset cache memori arbitrase:</span>
            <button
              onClick={() => {
                if (window.confirm('Yakin ingin mengosongkan seluruh memori arbitrase tersimpan?')) {
                  clearMemory()
                }
              }}
              disabled={isClearing}
              className="px-3 py-1.5 rounded-xl border border-rose-200 text-rose-600 hover:bg-rose-50 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{isClearing ? 'Menghapus...' : 'Kosongkan Memori'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
