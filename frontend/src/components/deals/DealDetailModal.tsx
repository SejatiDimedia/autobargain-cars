import { X, ExternalLink, ShieldAlert, ShieldCheck, AlertTriangle, TrendingUp, Calendar, Gauge, Settings2 } from 'lucide-react'
import { CarOpportunity } from '../../types/car'
import { formatMillionRupiah, formatMileage } from '../../utils/currency'

interface DealDetailModalProps {
  deal: CarOpportunity | null
  onClose: () => void
}

export function DealDetailModal({ deal, onClose }: DealDetailModalProps) {
  if (!deal) return null

  const { deal: car, estimate, discount, risk_report } = deal

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div 
        className="bg-white rounded-3xl border border-surface-border shadow-float max-w-2xl w-full max-h-[90vh] overflow-y-auto overflow-x-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-6 py-5 border-b border-surface-border flex items-center justify-between sticky top-0 bg-white/95 backdrop-blur z-10">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-orange-50 text-brand-orange border border-orange-200">
                {car.brand}
              </span>
              <span className="text-xs font-medium text-slate-600 font-mono tabular-nums">
                Tahun {car.year}
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 mt-1">
              {car.brand} {car.model}
            </h2>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors focus-visible:ring-2 focus-visible:ring-brand-orange"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 flex-1">
          {/* Price & Arbitrage Highlights */}
          <div className="grid grid-cols-3 gap-3 p-4 rounded-2xl bg-surface-subtle border border-surface-border">
            <div>
              <p className="text-xs text-slate-500 font-medium">Harga Penawaran</p>
              <p className="text-lg font-bold text-slate-900 mt-0.5 font-mono tabular-nums">
                {formatMillionRupiah(car.price)}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Estimasi Pasar (TMV)</p>
              <p className="text-lg font-bold text-blue-700 mt-0.5 font-mono tabular-nums">
                {formatMillionRupiah(estimate)}
              </p>
            </div>
            <div className="border-l border-surface-border pl-3">
              <p className="text-xs text-emerald-700 font-medium flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5" /> Potensi Margin
              </p>
              <p className="text-lg font-extrabold text-emerald-700 mt-0.5 font-mono tabular-nums">
                +{formatMillionRupiah(discount)}
              </p>
            </div>
          </div>

          {/* Key Specs */}
          <div className="grid grid-cols-3 gap-3">
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-100">
              <Calendar className="w-4 h-4 text-slate-500" />
              <div>
                <p className="text-[11px] text-slate-500">Tahun</p>
                <p className="text-xs font-semibold text-slate-900 font-mono tabular-nums">{car.year}</p>
              </div>
            </div>
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-100">
              <Gauge className="w-4 h-4 text-slate-500" />
              <div>
                <p className="text-[11px] text-slate-500">Jarak Tempuh</p>
                <p className="text-xs font-semibold text-slate-900 font-mono tabular-nums">{formatMileage(car.mileage_km)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-100">
              <Settings2 className="w-4 h-4 text-slate-500" />
              <div>
                <p className="text-[11px] text-slate-500">Transmisi</p>
                <p className="text-xs font-semibold text-slate-900">{car.transmission}</p>
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">Deskripsi Listing</h4>
            <p className="text-sm text-slate-800 bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 leading-relaxed">
              {car.car_description}
            </p>
          </div>

          {/* AI Risk & Safety Inspection Report */}
          {risk_report && (
            <div className="space-y-4 pt-2 border-t border-surface-border">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" /> Laporan Inspeksi AI Risk Analyst
                </h4>
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-full border ${
                    risk_report.grade.includes('Grade A')
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                      : risk_report.grade.includes('Grade B')
                      ? 'bg-amber-50 text-amber-800 border-amber-200'
                      : 'bg-rose-50 text-rose-800 border-rose-200'
                  }`}>
                    {risk_report.grade}
                  </span>
                  <span className="text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-md font-mono tabular-nums">
                    Skor: {risk_report.safety_score}/10
                  </span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-100 text-xs text-slate-800 leading-relaxed">
                <span className="font-semibold text-emerald-900">Evaluasi Inspektur: </span>
                {risk_report.risk_summary}
              </div>

              {/* Positive Highlights */}
              {risk_report.positive_highlights?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-emerald-800 mb-2 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5" /> Poin Positif Terverifikasi:
                  </p>
                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
                    {risk_report.positive_highlights.map((pos, idx) => (
                      <li key={idx} className="text-xs text-slate-700 flex items-center gap-2 bg-slate-50 p-2 rounded-lg border border-slate-100">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                        <span>{pos}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Red Flags */}
              {risk_report.red_flags?.length > 0 ? (
                <div>
                  <p className="text-xs font-semibold text-rose-700 mb-2 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> Catatan Risiko (Red Flags):
                  </p>
                  <ul className="space-y-1.5">
                    {risk_report.red_flags.map((flag, idx) => (
                      <li key={idx} className="text-xs text-rose-800 bg-rose-50/70 p-2.5 rounded-lg border border-rose-100 flex items-start gap-2">
                        <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                        <span>{flag}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-600 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  Tidak ditemukan red flags kritis pada unit ini.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-surface-border bg-surface-subtle flex items-center justify-between rounded-b-3xl">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 transition-colors focus-visible:ring-2 focus-visible:ring-brand-orange"
          >
            Tutup
          </button>
          {car.url ? (
            <a
              href={car.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 text-xs font-semibold rounded-xl bg-brand-orange hover:bg-brand-orange-hover text-white flex items-center gap-1.5 shadow-sm transition-colors focus-visible:ring-2 focus-visible:ring-brand-orange"
            >
              Buka Iklan Asli <ExternalLink className="w-3.5 h-3.5" />
            </a>
          ) : (
            <span className="text-xs text-slate-500">URL Iklan tidak tersedia</span>
          )}
        </div>
      </div>
    </div>
  )
}
