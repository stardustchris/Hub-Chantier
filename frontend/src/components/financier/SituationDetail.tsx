/**
 * SituationDetail - Detail d'une situation de travaux (FIN-07)
 *
 * Affiche :
 * - En-tete: numero, periode, statut, montants
 * - Table des lignes: code_lot, libelle, avancement %, montants
 * - Edition inline avancement % en mode brouillon
 * - Actions workflow
 */

import { useState, useEffect, useCallback } from 'react'
import { Loader2, Save, Send, Check, UserCheck } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useAuth } from '../../contexts/AuthContext'
import { logger } from '../../services/logger'
import type { SituationTravaux, LigneSituationCreate } from '../../types'
import { STATUT_SITUATION_CONFIG } from '../../types'
import { formatEUR } from '../../utils/format'

interface SituationDetailProps {
  situationId: number
  budgetId: number
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatPct = (value: number): string =>
  value.toLocaleString('fr-FR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %'

export default function SituationDetail({ situationId }: SituationDetailProps) {
  const { user } = useAuth()
  const [situation, setSituation] = useState<SituationTravaux | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [editedAvancements, setEditedAvancements] = useState<Record<number, number>>({})

  const canManage = user?.role === 'admin' || user?.role === 'conducteur'
  const isEditable = canManage && situation?.statut === 'brouillon'

  const loadSituation = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.getSituation(situationId)
      setSituation(data)
      // Initialize edited avancements
      const avancements: Record<number, number> = {}
      data.lignes.forEach(l => {
        avancements[l.lot_budgetaire_id] = l.pourcentage_avancement
      })
      setEditedAvancements(avancements)
    } catch (err) {
      setError('Erreur lors du chargement de la situation')
      logger.error('Erreur chargement situation', err, { context: 'SituationDetail' })
    } finally {
      setLoading(false)
    }
  }, [situationId])

  useEffect(() => {
    loadSituation()
  }, [loadSituation])

  const handleAvancementChange = (lotId: number, value: string) => {
    const num = parseFloat(value)
    if (!isNaN(num) && num >= 0 && num <= 100) {
      setEditedAvancements(prev => ({ ...prev, [lotId]: num }))
    }
  }

  const handleSave = async () => {
    if (!situation) return
    try {
      setSaving(true)
      const lignes: LigneSituationCreate[] = Object.entries(editedAvancements).map(([lotId, pct]) => ({
        lot_budgetaire_id: parseInt(lotId),
        pourcentage_avancement: pct,
      }))
      const updated = await financierService.updateSituation(situation.id, { lignes })
      setSituation(updated)
    } catch (err) {
      console.error('Erreur mise a jour situation:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleSoumettre = async () => {
    if (!situation) return
    try {
      const updated = await financierService.soumettreSituation(situation.id)
      setSituation(updated)
    } catch (err) {
      console.error('Erreur soumission situation:', err)
    }
  }

  const handleValider = async () => {
    if (!situation) return
    try {
      const updated = await financierService.validerSituation(situation.id)
      setSituation(updated)
    } catch (err) {
      console.error('Erreur validation situation:', err)
    }
  }

  const handleValiderClient = async () => {
    if (!situation) return
    try {
      const updated = await financierService.validerClientSituation(situation.id)
      setSituation(updated)
    } catch (err) {
      console.error('Erreur validation client situation:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error || !situation) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error || 'Situation introuvable'}
      </div>
    )
  }

  const statutConfig = STATUT_SITUATION_CONFIG[situation.statut]

  // Compute totals
  const totalMarcheHt = situation.lignes.reduce((sum, l) => sum + l.montant_marche_ht, 0)
  const totalPeriodeHt = situation.lignes.reduce((sum, l) => sum + l.montant_periode_ht, 0)
  const totalCumuleHt = situation.lignes.reduce((sum, l) => sum + l.montant_cumule_ht, 0)

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-white border rounded-xl p-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-gray-900">Situation {situation.numero}</h3>
              <span
                className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                style={{
                  backgroundColor: statutConfig.couleur + '20',
                  color: statutConfig.couleur,
                }}
              >
                {statutConfig.label}
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Periode : {formatDate(situation.periode_debut)} - {formatDate(situation.periode_fin)}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {isEditable && (
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm transition-colors"
              >
                <Save size={14} />
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            )}
            {canManage && situation.statut === 'brouillon' && (
              <button
                onClick={handleSoumettre}
                className="flex items-center gap-1 px-3 py-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm transition-colors"
              >
                <Send size={14} />
                Soumettre
              </button>
            )}
            {canManage && situation.statut === 'en_validation' && (
              <button
                onClick={handleValider}
                className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm transition-colors"
              >
                <Check size={14} />
                Valider
              </button>
            )}
            {canManage && situation.statut === 'emise' && (
              <button
                onClick={handleValiderClient}
                className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm transition-colors"
              >
                <UserCheck size={14} />
                Valider client
              </button>
            )}
          </div>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Montant periode HT</p>
            <p className="text-lg font-bold text-gray-900">{formatEUR(situation.montant_periode_ht)}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Montant cumule HT</p>
            <p className="text-lg font-bold text-gray-900">{formatEUR(situation.montant_cumule_ht)}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Montant TTC</p>
            <p className="text-lg font-bold text-gray-900">{formatEUR(situation.montant_ttc)}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Net a payer</p>
            <p className="text-lg font-bold text-blue-700">{formatEUR(situation.montant_net)}</p>
          </div>
        </div>
      </div>

      {/* Lignes table */}
      <div className="bg-white border rounded-xl">
        <div className="p-4 border-b">
          <h4 className="font-semibold text-gray-900">Detail par lot</h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Lot</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Libelle</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Avancement</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Marche HT</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Periode HT</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Cumule HT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {situation.lignes.map((ligne) => (
                <tr key={ligne.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-gray-700">{ligne.code_lot || '-'}</td>
                  <td className="px-4 py-3 text-gray-700">{ligne.libelle_lot || '-'}</td>
                  <td className="px-4 py-3 text-center">
                    {isEditable ? (
                      <input
                        type="number"
                        value={editedAvancements[ligne.lot_budgetaire_id] ?? ligne.pourcentage_avancement}
                        onChange={(e) => handleAvancementChange(ligne.lot_budgetaire_id, e.target.value)}
                        className="w-20 px-2 py-1 text-center border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        min={0}
                        max={100}
                        step={0.1}
                      />
                    ) : (
                      <span className="font-medium">{formatPct(ligne.pourcentage_avancement)}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right whitespace-nowrap">{formatEUR(ligne.montant_marche_ht)}</td>
                  <td className="px-4 py-3 text-right whitespace-nowrap">{formatEUR(ligne.montant_periode_ht)}</td>
                  <td className="px-4 py-3 text-right whitespace-nowrap font-medium">{formatEUR(ligne.montant_cumule_ht)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gray-50 font-semibold">
              <tr>
                <td className="px-4 py-3" colSpan={3}>Total</td>
                <td className="px-4 py-3 text-right whitespace-nowrap">{formatEUR(totalMarcheHt)}</td>
                <td className="px-4 py-3 text-right whitespace-nowrap">{formatEUR(totalPeriodeHt)}</td>
                <td className="px-4 py-3 text-right whitespace-nowrap">{formatEUR(totalCumuleHt)}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Additional info */}
      {situation.notes && (
        <div className="bg-white border rounded-xl p-4">
          <h4 className="font-semibold text-gray-900 mb-2">Notes</h4>
          <p className="text-sm text-gray-600">{situation.notes}</p>
        </div>
      )}

      <div className="bg-white border rounded-xl p-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
          <div>
            <span className="text-gray-500">Retenue de garantie</span>
            <p className="font-medium">{situation.retenue_garantie_pct.toLocaleString('fr-FR')} % ({formatEUR(situation.montant_retenue_garantie)})</p>
          </div>
          <div>
            <span className="text-gray-500">TVA</span>
            <p className="font-medium">{situation.taux_tva.toLocaleString('fr-FR')} % ({formatEUR(situation.montant_tva)})</p>
          </div>
        </div>
      </div>
    </div>
  )
}
