export interface CarDeal {
  brand: string
  model: string
  year: number
  mileage_km: number
  transmission: string
  car_description: string
  price: number // dalam Juta Rupiah
  url: string
}

export interface DealRiskReport {
  safety_score: number
  grade: string // Grade A (Low Risk), Grade B, Grade C
  red_flags: string[]
  positive_highlights: string[]
  risk_summary: string
}

export interface CarOpportunity {
  deal: CarDeal
  estimate: number // dalam Juta Rupiah
  discount: number // dalam Juta Rupiah
  risk_report?: DealRiskReport | null
}
