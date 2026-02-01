import type { DevisDetail, TypeDebourse } from '../../types'
import { TYPE_DEBOURSE_LABELS } from '../../types'
import { TrendingUp, TrendingDown } from 'lucide-react'

const formatEUR = (value: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

interface MargesPanelProps {
  devis: DevisDetail
}

interface LotMargeInfo {
  numero: string
  libelle: string
  debourse: number
  vente: number
  marge_pct: number
}

interface TypeMargeInfo {
  type: TypeDebourse
  label: string
  total: number
}

export default function MargesPanel({ devis }: MargesPanelProps) {
  // Calcul marges par lot
  const margesLots: LotMargeInfo[] = devis.lots.map((lot) => ({
    numero: lot.numero,
    libelle: lot.libelle,
    debourse: lot.total_debourse_ht,
    vente: lot.total_vente_ht,
    marge_pct: lot.marge_lot_pct,
  }))

  // Calcul debourses par type
  const deboursesByType: Record<string, number> = {}
  devis.lots.forEach((lot) => {
    lot.lignes.forEach((ligne) => {
      ligne.debourses.forEach((d) => {
        deboursesByType[d.type_debourse] = (deboursesByType[d.type_debourse] || 0) + d.montant
      })
    })
  })

  const typesMarges: TypeMargeInfo[] = (Object.entries(deboursesByType) as [TypeDebourse, number][])
    .map(([type, total]) => ({
      type,
      label: TYPE_DEBOURSE_LABELS[type],
      total,
    }))
    .sort((a, b) => b.total - a.total)

  const margeGlobalePct = devis.marge_globale_pct
  const isPositive = margeGlobalePct >= 0

  return (
    <div className="space-y-6">
      {/* Marge globale */}
      <div className={`rounded-xl p-5 ${isPositive ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Marge globale</p>
            <p className={`text-3xl font-bold mt-1 ${isPositive ? 'text-green-700' : 'text-red-700'}`}>
              {margeGlobalePct.toFixed(1)}%
            </p>
          </div>
          <div className={`w-14 h-14 rounded-full flex items-center justify-center ${isPositive ? 'bg-green-100' : 'bg-red-100'}`}>
            {isPositive ? (
              <TrendingUp className="w-7 h-7 text-green-600" />
            ) : (
              <TrendingDown className="w-7 h-7 text-red-600" />
            )}
          </div>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Debourse sec</span>
            <p className="font-semibold text-orange-700">{formatEUR(devis.total_debourse_sec)}</p>
          </div>
          <div>
            <span className="text-gray-500">Vente HT</span>
            <p className="font-semibold">{formatEUR(devis.montant_total_ht)}</p>
          </div>
          <div>
            <span className="text-gray-500">TTC</span>
            <p className="font-semibold">{formatEUR(devis.montant_total_ttc)}</p>
          </div>
        </div>
      </div>

      {/* Marges par lot */}
      {margesLots.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Marges par lot</h4>
          <div className="space-y-2">
            {margesLots.map((lot) => (
              <div key={lot.numero} className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg">
                <div className="flex-1 min-w-0">
                  <span className="text-xs font-mono text-gray-400">{lot.numero}</span>
                  <p className="text-sm font-medium text-gray-900 truncate">{lot.libelle}</p>
                </div>
                <div className="text-right text-sm">
                  <span className="text-gray-500">{formatEUR(lot.debourse)}</span>
                  <span className="mx-1 text-gray-300">/</span>
                  <span className="font-medium">{formatEUR(lot.vente)}</span>
                </div>
                <div className="w-16 text-right">
                  <span className={`text-sm font-bold ${lot.marge_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {lot.marge_pct.toFixed(1)}%
                  </span>
                </div>
                {/* Barre visuelle */}
                <div className="w-24">
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${lot.marge_pct >= 15 ? 'bg-green-500' : lot.marge_pct >= 0 ? 'bg-yellow-500' : 'bg-red-500'}`}
                      style={{ width: `${Math.min(Math.max(lot.marge_pct, 0), 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Repartition debourses par type */}
      {typesMarges.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Repartition debourses par type</h4>
          <div className="space-y-2">
            {typesMarges.map((t) => {
              const pct = devis.total_debourse_sec > 0
                ? (t.total / devis.total_debourse_sec) * 100
                : 0
              return (
                <div key={t.type} className="flex items-center gap-3">
                  <span className="w-32 text-sm text-gray-600">{t.label}</span>
                  <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full bg-blue-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="w-20 text-right text-sm font-medium">{formatEUR(t.total)}</span>
                  <span className="w-12 text-right text-xs text-gray-500">{pct.toFixed(0)}%</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
