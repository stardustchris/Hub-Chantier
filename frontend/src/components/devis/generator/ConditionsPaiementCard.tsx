import { useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { devisService } from '../../../services/devis'
import type { DevisDetail } from '../../../types'
import { formatEUR } from '../../../utils/format'

interface Props {
  devis: DevisDetail
  isEditable: boolean
  onSaved: () => void
}

const ECHEANCES = [
  { value: 'reception', label: 'Paiement a reception' },
  { value: '30_jours_fin_mois', label: '30 jours fin de mois' },
  { value: '45_jours_fin_mois', label: '45 jours fin de mois' },
  { value: '60_jours', label: '60 jours' },
]

// Loi 71-584 art. 1 : retenue de garantie max 5% du marche HT
const RETENUE_OPTIONS = [
  { value: 0, label: 'Aucune' },
  { value: 5, label: '5% (Maximum legal)' },
]

export default function ConditionsPaiementCard({ devis, isEditable, onSaved }: Props) {
  const [acomptePct, setAcomptePct] = useState(Number(devis.acompte_pct || 30))
  const [retenuePct, setRetenuePct] = useState(Number(devis.retenue_garantie_pct || 0))
  const [echeance, setEcheance] = useState(devis.echeance || '30_jours_fin_mois')
  const [saving, setSaving] = useState(false)

  const totalHT = Number(devis.montant_total_ht || 0)
  const totalTTC = Number(devis.montant_total_ttc || 0)
  const acompteAmount = totalTTC * acomptePct / 100
  // Loi 71-584: retenue de garantie calculée sur HT (pas TTC)
  const retenueAmount = totalHT * retenuePct / 100

  const handleChange = async (field: string, value: number | string) => {
    if (!isEditable) return
    setSaving(true)
    try {
      await devisService.updateDevis(devis.id, { [field]: value })
      onSaved()
    } finally {
      setSaving(false)
    }
  }

  const inputClass = 'w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm disabled:bg-gray-50'

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">Conditions de paiement</h3>
      <div className="space-y-4">
        {/* Acompte */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Acompte a la commande</label>
          <div className="flex items-center gap-2">
            <div className="relative w-20">
              <input
                type="number"
                value={acomptePct}
                onChange={e => setAcomptePct(Number(e.target.value))}
                onBlur={() => handleChange('acompte_pct', acomptePct)}
                disabled={!isEditable || saving}
                className={`${inputClass} pr-7`}
                min={0}
                max={100}
              />
              <span className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 text-sm">%</span>
            </div>
            <span className="text-gray-400">=</span>
            <span className="text-sm text-gray-600">{formatEUR(acompteAmount)}</span>
          </div>
        </div>

        {/* Retenue de garantie */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Retenue de garantie</label>
          <div className="space-y-2">
            <select
              value={retenuePct}
              onChange={e => {
                const val = Number(e.target.value)
                setRetenuePct(val)
                handleChange('retenue_garantie_pct', val)
              }}
              disabled={!isEditable || saving}
              className={inputClass}
            >
              {RETENUE_OPTIONS.map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
            <input
              type="number"
              min="0"
              max="5"
              step="0.5"
              value={retenuePct}
              onChange={e => setRetenuePct(Number(e.target.value))}
              onBlur={() => handleChange('retenue_garantie_pct', retenuePct)}
              disabled={!isEditable || saving}
              className={inputClass}
              placeholder="Personnalisé (%)"
            />
            {retenuePct > 0 && (
              <p className="text-xs text-gray-500">Soit {formatEUR(retenueAmount)} retenus</p>
            )}
            {retenuePct > 5 && (
              <p className="text-xs text-orange-600 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Retenue de garantie plafonnée à 5% (loi 71-584)
              </p>
            )}
          </div>
        </div>

        {/* Echeances */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Echeances</label>
          <select
            value={echeance}
            onChange={e => {
              setEcheance(e.target.value)
              handleChange('echeance', e.target.value)
            }}
            disabled={!isEditable || saving}
            className={inputClass}
          >
            {ECHEANCES.map(e => (
              <option key={e.value} value={e.value}>{e.label}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}
