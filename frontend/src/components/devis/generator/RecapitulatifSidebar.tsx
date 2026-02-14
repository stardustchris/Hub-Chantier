import { AlertTriangle } from 'lucide-react'
import type { DevisDetail } from '../../../types'
import { formatEUR } from '../../../utils/format'

interface Props {
  devis: DevisDetail
}

export default function RecapitulatifSidebar({ devis }: Props) {
  const totalHT = Number(devis.montant_total_ht || 0)
  const totalTTC = Number(devis.montant_total_ttc || 0)
  const retenuePct = Number(devis.retenue_garantie_pct || 0)
  const retenueAmount = Number(devis.montant_retenue_garantie || 0) || (totalTTC * retenuePct / 100)
  const acomptePct = Number(devis.acompte_pct || 0)
  const acompteAmount = totalTTC * acomptePct / 100
  const netAPayer = Number(devis.montant_net_a_payer || 0) || (totalTTC - retenueAmount - acompteAmount)

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">Recapitulatif</h3>

      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Total HT</span>
          <span className="font-medium">{formatEUR(totalHT)}</span>
        </div>

        <div className="border-t border-gray-100 pt-3 flex justify-between text-sm">
          <span className="text-gray-600">Total HT net</span>
          <span className="font-medium">{formatEUR(totalHT)}</span>
        </div>

        {/* DEV-TVA: Ventilation TVA multi-taux */}
        {devis.ventilation_tva && devis.ventilation_tva.length > 0 && (
          devis.ventilation_tva.map((v, i) => (
            <div key={i} className="flex justify-between text-sm">
              <span className="text-gray-600">
                TVA {v.taux}% <span className="text-xs text-gray-600">(base {formatEUR(v.base_ht)})</span>
              </span>
              <span className="font-medium">{formatEUR(v.montant_tva)}</span>
            </div>
          ))
        )}

        <div className="border-t border-gray-100 pt-3 flex justify-between">
          <span className="font-medium text-gray-900">Total TTC</span>
          <span className="font-bold text-lg">{formatEUR(totalTTC)}</span>
        </div>

        {retenuePct > 0 && (
          <div className="flex justify-between text-sm text-gray-500">
            <span>Retenue de garantie ({retenuePct}%)</span>
            <span>- {formatEUR(retenueAmount)}</span>
          </div>
        )}

        {acomptePct > 0 && (
          <div className="flex justify-between text-sm text-gray-500">
            <span>Acompte ({acomptePct}%)</span>
            <span>- {formatEUR(acompteAmount)}</span>
          </div>
        )}

        {/* Net a payer card */}
        <div className="bg-indigo-600 text-white rounded-lg p-4 -mx-2">
          <div className="flex justify-between items-center">
            <span className="font-medium">Net a payer</span>
            <span className="text-2xl font-bold">{formatEUR(netAPayer)}</span>
          </div>
          {(retenuePct > 0 || acomptePct > 0) && (
            <p className="text-indigo-200 text-xs mt-1">Apres deduction acompte et retenue</p>
          )}
        </div>
      </div>

      {/* DEV-TVA: Mention legale TVA reduite */}
      {devis.mention_tva_reduite && (
        <div className="mt-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
          <div className="flex gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-amber-800 leading-relaxed">{devis.mention_tva_reduite}</p>
          </div>
        </div>
      )}
    </div>
  )
}
