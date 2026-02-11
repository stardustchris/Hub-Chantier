import type { DevisDetail, TypeDebourse, VentilationTVA } from '../../types'
import { TYPE_DEBOURSE_LABELS } from '../../types'
import { TrendingUp, TrendingDown, Shield, AlertTriangle } from 'lucide-react'
import { formatEUR } from '../../utils/format'

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
    libelle: lot.titre,
    debourse: Number(lot.debourse_sec),
    vente: Number(lot.total_ht),
    marge_pct: Number(lot.marge_lot_pct ?? 0),
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

  const margeGlobalePct = Number(devis.taux_marge_global)
  const isPositive = margeGlobalePct >= 0

  // Calcul recap financier (DEV-22 + DEV-TVA)
  const totalHT = Number(devis.montant_total_ht)
  const totalTTC = Number(devis.montant_total_ttc)

  // DEV-TVA: Ventilation multi-taux (fallback sur taux defaut si absent)
  const ventilationTVA: VentilationTVA[] = devis.ventilation_tva?.length
    ? devis.ventilation_tva
    : [{ taux: Number(devis.taux_tva_defaut), base_ht: totalHT, montant_tva: totalHT * (Number(devis.taux_tva_defaut) / 100) }]
  const montantTVA = ventilationTVA.reduce((sum, v) => sum + Number(v.montant_tva), 0)
  const retenueGarantiePct = Number(devis.retenue_garantie_pct ?? 0)
  const montantRetenue = devis.montant_retenue_garantie != null
    ? Number(devis.montant_retenue_garantie)
    : totalTTC * (retenueGarantiePct / 100)
  const netAPayer = devis.montant_net_a_payer != null
    ? Number(devis.montant_net_a_payer)
    : totalTTC - montantRetenue

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
        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Vente HT</span>
            <p className="font-semibold">{formatEUR(Number(devis.montant_total_ht))}</p>
          </div>
          <div>
            <span className="text-gray-500">TTC</span>
            <p className="font-semibold">{formatEUR(Number(devis.montant_total_ttc))}</p>
          </div>
        </div>
      </div>

      {/* Recapitulatif financier (DEV-22) */}
      <div className="rounded-xl border border-gray-200 overflow-hidden">
        <div className="bg-gray-50 px-5 py-3 border-b border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700">Recapitulatif financier</h4>
        </div>
        <div className="divide-y divide-gray-100">
          <div className="flex items-center justify-between px-5 py-3">
            <span className="text-sm text-gray-600">Total HT</span>
            <span className="text-sm font-medium text-gray-900">{formatEUR(totalHT)}</span>
          </div>
          {/* DEV-TVA: Ventilation TVA multi-taux */}
          {ventilationTVA.map((v) => (
            <div key={v.taux} className="flex items-center justify-between px-5 py-3">
              <span className="text-sm text-gray-600">
                TVA {Number(v.taux)}%
                {ventilationTVA.length > 1 && (
                  <span className="text-xs text-gray-400 ml-1">(base {formatEUR(Number(v.base_ht))})</span>
                )}
              </span>
              <span className="text-sm font-medium text-gray-900">{formatEUR(Number(v.montant_tva))}</span>
            </div>
          ))}
          <div className="flex items-center justify-between px-5 py-3 bg-gray-50">
            <span className="text-sm font-semibold text-gray-700">Total TTC</span>
            <span className="text-sm font-bold text-gray-900">{formatEUR(totalTTC)}</span>
          </div>
          {retenueGarantiePct > 0 && (
            <div className="flex items-center justify-between px-5 py-3">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-amber-500" />
                <span className="text-sm text-amber-700">
                  Retenue de garantie ({retenueGarantiePct}%)
                </span>
              </div>
              <span className="text-sm font-medium text-amber-700">- {formatEUR(montantRetenue)}</span>
            </div>
          )}
          <div className="flex items-center justify-between px-5 py-4 bg-blue-50">
            <span className="text-base font-bold text-blue-800">Net a payer</span>
            <span className="text-lg font-bold text-blue-800">{formatEUR(netAPayer)}</span>
          </div>
        </div>
        {/* DEV-TVA: Mention legale TVA reduite (reforme 01/2025) */}
        {devis.mention_tva_reduite && (
          <div className="px-5 py-3 bg-amber-50 border-t border-amber-200">
            <div className="flex gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-amber-700 leading-relaxed">
                {devis.mention_tva_reduite}
              </p>
            </div>
          </div>
        )}
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
              const totalDebourse = typesMarges.reduce((sum, tm) => sum + tm.total, 0)
              const pct = totalDebourse > 0
                ? (t.total / totalDebourse) * 100
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
