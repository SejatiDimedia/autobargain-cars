import { useState, useMemo } from 'react'
import { Database, Sparkles, Info } from 'lucide-react'
import { useTsnePlot } from '../../hooks/useStats'
import { TsnePoint } from '../../types/api'

export function VectorSpaceView() {
  const { data: plotData, isLoading } = useTsnePlot(250)
  const [selectedBrand, setSelectedBrand] = useState<string>('all')
  const [hoveredPoint, setHoveredPoint] = useState<TsnePoint | null>(null)

  const points = plotData?.points || []

  // Compute 2D min/max bounds for SVG projection
  const bounds = useMemo(() => {
    if (points.length === 0) return { minX: 0, maxX: 1, minY: 0, maxY: 1 }
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
    points.forEach((p) => {
      if (p.x < minX) minX = p.x
      if (p.x > maxX) maxX = p.x
      if (p.y < minY) minY = p.y
      if (p.y > maxY) maxY = p.y
    })
    return { minX, maxX, minY, maxY }
  }, [points])

  const filteredPoints = useMemo(() => {
    if (selectedBrand === 'all') return points
    return points.filter((p) => p.brand === selectedBrand)
  }, [points, selectedBrand])

  return (
    <div className="space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row gap-3 items-start md:items-center justify-between p-4 bg-white rounded-2xl border border-surface-border shadow-subtle">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-purple-50 text-purple-700 border border-purple-100">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              ChromaDB 3D Embedding Vector Space
            </h3>
            <p className="text-xs text-slate-600 mt-0.5">
              Proyeksi t-SNE dari kemiripan semantik mobil bekas pada Vector Database.
            </p>
          </div>
        </div>

        {/* Brand Legend Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            onClick={() => setSelectedBrand('all')}
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all focus-visible:ring-2 focus-visible:ring-brand-orange ${
              selectedBrand === 'all'
                ? 'bg-slate-900 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Semua ({points.length})
          </button>
          {plotData?.brands?.slice(0, 7).map((brand, i) => {
            const color = plotData.brand_colors[i] || '#888'
            const isSelected = selectedBrand === brand
            return (
              <button
                key={brand}
                onClick={() => setSelectedBrand(brand)}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all border focus-visible:ring-2 focus-visible:ring-brand-orange ${
                  isSelected
                    ? 'border-slate-800 bg-white text-slate-900 shadow-sm'
                    : 'border-transparent bg-slate-50 text-slate-700 hover:bg-slate-100'
                }`}
              >
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span>{brand}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="relative bg-white rounded-2xl border border-surface-border shadow-subtle p-6 flex flex-col items-center justify-center min-h-[460px] overflow-hidden">
        {isLoading ? (
          <div className="flex flex-col items-center gap-2 text-slate-500 text-xs">
            <Sparkles className="w-6 h-6 animate-spin text-brand-orange" />
            <span>Menghitung proyeksi t-SNE dari ChromaDB embeddings...</span>
          </div>
        ) : points.length === 0 ? (
          <div className="text-slate-500 text-xs">Database belum memiliki titik data embedding.</div>
        ) : (
          <div className="w-full h-full flex flex-col items-center">
            {/* SVG Interactive Scatter Visualization */}
            <svg viewBox="0 0 700 400" className="w-full max-w-2xl h-[380px]">
              {/* Subtle Grid Lines */}
              <line x1="50" y1="200" x2="650" y2="200" stroke="#f1f5f9" strokeWidth="1" strokeDasharray="4" />
              <line x1="350" y1="30" x2="350" y2="370" stroke="#f1f5f9" strokeWidth="1" strokeDasharray="4" />

              {filteredPoints.map((pt, idx) => {
                const normX = ((pt.x - bounds.minX) / (bounds.maxX - bounds.minX || 1)) * 560 + 70
                const normY = ((pt.y - bounds.minY) / (bounds.maxY - bounds.minY || 1)) * 300 + 50
                const isHovered = hoveredPoint === pt

                return (
                  <circle
                    key={idx}
                    cx={normX}
                    cy={normY}
                    r={isHovered ? 8 : 5}
                    fill={pt.color}
                    fillOpacity={isHovered ? 1 : 0.8}
                    stroke={isHovered ? '#0f172a' : '#ffffff'}
                    strokeWidth={isHovered ? 2 : 1}
                    className="cursor-pointer transition-all duration-150"
                    onMouseEnter={() => setHoveredPoint(pt)}
                    onMouseLeave={() => setHoveredPoint(null)}
                  />
                )
              })}
            </svg>

            {/* Hovered Point Card Banner */}
            <div className="w-full max-w-xl mt-3 p-3 rounded-xl bg-surface-subtle border border-surface-border flex items-start gap-2.5 text-left text-xs min-h-[56px]">
              <Info className="w-4 h-4 text-brand-orange shrink-0 mt-0.5" />
              {hoveredPoint ? (
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900">{hoveredPoint.brand}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-200/80 text-slate-700 font-mono tabular-nums">
                      Embedding Vector #{points.indexOf(hoveredPoint) + 1}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-700 mt-0.5 line-clamp-2 leading-relaxed">
                    {hoveredPoint.description}
                  </p>
                </div>
              ) : (
                <p className="text-[11px] text-slate-500 italic">
                  Arahkan kursor ke titik vektor untuk melihat detail dokumen mobil yang terindeks di ChromaDB.
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
