import { useState, useMemo } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper,
  SortingState,
} from '@tanstack/react-table'
import { Search, ChevronDown, ChevronUp, ChevronsUpDown, ExternalLink, Eye, TrendingUp, Sparkles, Filter, ChevronLeft, ChevronRight } from 'lucide-react'
import { CarOpportunity } from '../../types/car'
import { formatMillionRupiah, formatMileage } from '../../utils/currency'
import { DealDetailModal } from './DealDetailModal'

interface DealsTableProps {
  opportunities: CarOpportunity[]
  isLoading: boolean
}

const columnHelper = createColumnHelper<CarOpportunity>()

export function DealsTable({ opportunities, isLoading }: DealsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([{ id: 'discount', desc: true }])
  const [globalFilter, setGlobalFilter] = useState('')
  const [selectedBrand, setSelectedBrand] = useState('all')
  const [minDiscount, setMinDiscount] = useState<number>(0)
  const [activeDeal, setActiveDeal] = useState<CarOpportunity | null>(null)

  // Filter list of brands
  const brands = useMemo(() => {
    const set = new Set<string>()
    opportunities.forEach((o) => {
      if (o.deal?.brand) set.add(o.deal.brand)
    })
    return ['all', ...Array.from(set).sort()]
  }, [opportunities])

  // Filtered data before passing to TanStack table
  const filteredData = useMemo(() => {
    return opportunities.filter((item) => {
      if (selectedBrand !== 'all' && item.deal?.brand !== selectedBrand) return false
      if (minDiscount > 0 && item.discount < minDiscount) return false
      return true
    })
  }, [opportunities, selectedBrand, minDiscount])

  // Columns definition using TanStack Table helper
  const columns = useMemo(
    () => [
      columnHelper.accessor((row) => `${row.deal.brand} ${row.deal.model}`, {
        id: 'vehicle',
        header: 'Unit Mobil',
        cell: (info) => {
          const deal = info.row.original.deal
          return (
            <div className="flex flex-col py-1">
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 text-sm">{deal.brand} {deal.model}</span>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-mono tabular-nums">
                  {deal.year}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-500 mt-1">
                <span>{deal.transmission}</span>
                <span className="text-slate-300">•</span>
                <span className="font-mono tabular-nums">{formatMileage(deal.mileage_km)}</span>
              </div>
            </div>
          )
        },
      }),

      columnHelper.accessor((row) => row.deal.price, {
        id: 'asking_price',
        header: 'Harga Iklan',
        cell: (info) => (
          <div className="font-semibold text-slate-900 text-sm font-mono tabular-nums">
            {formatMillionRupiah(info.getValue())}
          </div>
        ),
      }),

      columnHelper.accessor((row) => row.estimate, {
        id: 'estimate',
        header: 'Harga Wajar (TMV)',
        cell: (info) => (
          <div className="font-semibold text-blue-700 text-sm font-mono tabular-nums">
            {formatMillionRupiah(info.getValue())}
          </div>
        ),
      }),

      columnHelper.accessor((row) => row.discount, {
        id: 'discount',
        header: 'Potensi Margin',
        cell: (info) => {
          const discount = info.getValue()
          const askingPrice = info.row.original.deal.price
          const percent = askingPrice > 0 ? ((discount / askingPrice) * 100).toFixed(0) : 0

          return (
            <div className="flex items-center gap-2">
              <div className="flex flex-col">
                <span className="font-extrabold text-emerald-700 text-sm font-mono tabular-nums flex items-center gap-1">
                  <TrendingUp className="w-3.5 h-3.5" /> +{formatMillionRupiah(discount)}
                </span>
                <span className="text-[11px] text-emerald-800 font-medium font-mono tabular-nums">
                  Hemat ~{percent}%
                </span>
              </div>
            </div>
          )
        },
      }),

      columnHelper.accessor((row) => row.risk_report?.grade ?? 'Unknown', {
        id: 'grade',
        header: 'Kelayakan AI',
        cell: (info) => {
          const report = info.row.original.risk_report
          const grade = report?.grade || 'Grade A (Low Risk)'
          const score = report?.safety_score || 9.0

          const isA = grade.includes('Grade A')
          const isB = grade.includes('Grade B')

          return (
            <div className="flex items-center gap-1.5">
              <span
                className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                  isA
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                    : isB
                    ? 'bg-amber-50 text-amber-800 border-amber-200'
                    : 'bg-rose-50 text-rose-800 border-rose-200'
                }`}
              >
                {isA ? 'Grade A' : isB ? 'Grade B' : 'Grade C'}
              </span>
              <span className="text-xs text-slate-600 font-medium font-mono tabular-nums">
                {score}/10
              </span>
            </div>
          )
        },
      }),

      columnHelper.display({
        id: 'actions',
        header: 'Aksi',
        cell: (info) => {
          const opp = info.row.original
          return (
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setActiveDeal(opp)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-800 transition-colors flex items-center gap-1 focus-visible:ring-2 focus-visible:ring-brand-orange"
                title="Lihat Detail Inspeksi"
              >
                <Eye className="w-3.5 h-3.5" /> Detail
              </button>
              {opp.deal.url && (
                <a
                  href={opp.deal.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 rounded-lg text-slate-500 hover:text-brand-orange hover:bg-orange-50 transition-colors focus-visible:ring-2 focus-visible:ring-brand-orange"
                  title="Buka Iklan Asli"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
          )
        },
      }),
    ],
    []
  )

  const table = useReactTable({
    data: filteredData,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 8,
      },
    },
  })

  return (
    <div className="space-y-4">
      {/* Table Toolbar / Filters */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between bg-white p-3.5 rounded-2xl border border-surface-border shadow-subtle">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={globalFilter ?? ''}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Cari merk, tipe mobil, atau kata kunci..."
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-surface-subtle border border-surface-border text-xs text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-orange/30 focus:border-brand-orange transition-all"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs text-slate-600 font-medium">
            <Filter className="w-3.5 h-3.5" /> Filter:
          </div>

          {/* Brand Filter */}
          <select
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-surface-subtle border border-surface-border text-xs font-semibold text-slate-800 focus:outline-none focus:border-brand-orange cursor-pointer"
          >
            {brands.map((b) => (
              <option key={b} value={b}>
                {b === 'all' ? 'Semua Merk' : b}
              </option>
            ))}
          </select>

          {/* Min Profit Filter */}
          <select
            value={minDiscount}
            onChange={(e) => setMinDiscount(Number(e.target.value))}
            className="px-3 py-1.5 rounded-xl bg-surface-subtle border border-surface-border text-xs font-semibold text-slate-800 focus:outline-none focus:border-brand-orange cursor-pointer"
          >
            <option value={0}>Semua Margin</option>
            <option value={20}>Min. Margin 20 Jt</option>
            <option value={35}>Min. Margin 35 Jt</option>
            <option value={50}>Min. Margin 50 Jt</option>
            <option value={100}>Min. Margin 100 Jt</option>
          </select>

          <span className="text-xs text-slate-500 font-mono tabular-nums pl-1">
            {table.getFilteredRowModel().rows.length} Unit
          </span>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="bg-white rounded-2xl border border-surface-border shadow-subtle overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id} className="border-b border-surface-border bg-surface-subtle/80">
                  {headerGroup.headers.map((header) => {
                    const isSorted = header.column.getIsSorted()
                    return (
                      <th
                        key={header.id}
                        onClick={header.column.getToggleSortingHandler()}
                        className="px-5 py-3.5 text-xs font-bold text-slate-700 uppercase tracking-wider select-none cursor-pointer hover:bg-slate-100/80 transition-colors"
                      >
                        <div className="flex items-center gap-1.5">
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {header.column.getCanSort() && (
                            <span className="text-slate-400">
                              {isSorted === 'asc' ? (
                                <ChevronUp className="w-3.5 h-3.5 text-brand-orange" />
                              ) : isSorted === 'desc' ? (
                                <ChevronDown className="w-3.5 h-3.5 text-brand-orange" />
                              ) : (
                                <ChevronsUpDown className="w-3 h-3 opacity-40" />
                              )}
                            </span>
                          )}
                        </div>
                      </th>
                    )
                  })}
                </tr>
              ))}
            </thead>
            <tbody className="divide-y divide-surface-border">
              {isLoading ? (
                <tr>
                  <td colSpan={columns.length} className="text-center py-12 text-slate-500 text-xs">
                    <Sparkles className="w-5 h-5 animate-spin mx-auto mb-2 text-brand-orange" />
                    Memuat data peluang arbitrase...
                  </td>
                </tr>
              ) : table.getRowModel().rows.length === 0 ? (
                <tr>
                  <td colSpan={columns.length} className="text-center py-12 text-slate-500 text-xs">
                    Tidak ada unit mobil yang sesuai dengan kriteria filter.
                  </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className="hover:bg-slate-50/80 transition-colors cursor-default"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-5 py-3.5 text-xs">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="px-5 py-3 border-t border-surface-border bg-surface-subtle/50 flex items-center justify-between text-xs text-slate-600">
          <div>
            Halaman <span className="font-semibold text-slate-800 font-mono tabular-nums">{table.getState().pagination.pageIndex + 1}</span> dari{' '}
            <span className="font-semibold text-slate-800 font-mono tabular-nums">{table.getPageCount() || 1}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="p-1.5 rounded-lg border border-surface-border bg-white text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="p-1.5 rounded-lg border border-surface-border bg-white text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      <DealDetailModal deal={activeDeal} onClose={() => setActiveDeal(null)} />
    </div>
  )
}
