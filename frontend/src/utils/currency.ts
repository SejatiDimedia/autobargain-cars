/**
 * Format angka dalam Juta Rupiah (contoh: 245.5 -> Rp 245.5 Jt atau Rp 245.500.000)
 */
export function formatMillionRupiah(valueInMillion: number, compact: boolean = true): string {
  if (valueInMillion === undefined || valueInMillion === null || isNaN(valueInMillion)) {
    return 'Rp 0'
  }

  if (compact) {
    return `Rp ${valueInMillion.toLocaleString('id-ID', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} Jt`
  }

  const fullValue = valueInMillion * 1_000_000
  return `Rp ${Math.round(fullValue).toLocaleString('id-ID')}`
}

/**
 * Format kilometer odometer (contoh: 42000 -> 42.000 km)
 */
export function formatMileage(km: number): string {
  if (!km) return '0 km'
  return `${km.toLocaleString('id-ID')} km`
}
