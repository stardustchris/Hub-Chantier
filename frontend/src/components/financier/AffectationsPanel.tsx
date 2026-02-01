/**
 * AffectationsPanel - Gestion des affectations taches <-> lots budgetaires (FIN-03)
 *
 * Affiche :
 * - Table des affectations existantes avec colonnes Tache, Lot, % Affectation, Actions
 * - Formulaire de creation (select tache, select lot, % input)
 * - Bouton supprimer avec confirmation
 * - SuiviAvancementPanel integre en dessous
 */

import { useState, useEffect, useCallback } from 'react'
import { Plus, Loader2, Trash2, AlertCircle } from 'lucide-react'
import { financierService } from '../../services/financier'
import { tachesService } from '../../services/taches'
import { useAuth } from '../../contexts/AuthContext'
import { logger } from '../../services/logger'
import SuiviAvancementPanel from './SuiviAvancementPanel'
import type { AffectationTacheLot, Tache, LotBudgetaire } from '../../types'

interface AffectationsPanelProps {
  chantierId: number
  budgetId: number
}

const formatPct = (value: string): string => {
  const num = parseFloat(value)
  if (isNaN(num)) return value
  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(num) + ' %'
}

export default function AffectationsPanel({ chantierId, budgetId }: AffectationsPanelProps) {
  const { user } = useAuth()
  const [affectations, setAffectations] = useState<AffectationTacheLot[]>([])
  const [taches, setTaches] = useState<Tache[]>([])
  const [lots, setLots] = useState<LotBudgetaire[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  // Form state
  const [selectedTacheId, setSelectedTacheId] = useState<string>('')
  const [selectedLotId, setSelectedLotId] = useState<string>('')
  const [pourcentage, setPourcentage] = useState<string>('100')
  const [showForm, setShowForm] = useState(false)

  const canManage = user?.role === 'admin' || user?.role === 'conducteur'

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const [affectationsData, tachesData, lotsData] = await Promise.all([
        financierService.getAffectationsByChantier(chantierId),
        tachesService.listByChantier(chantierId, { size: 200, include_sous_taches: false }),
        financierService.listLots(budgetId),
      ])
      setAffectations(affectationsData)
      setTaches(tachesData.items)
      setLots(lotsData)
    } catch (err) {
      setError('Erreur lors du chargement des affectations')
      logger.error('Erreur chargement affectations', err, { context: 'AffectationsPanel' })
    } finally {
      setLoading(false)
    }
  }, [chantierId, budgetId])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleCreate = async () => {
    const tacheId = parseInt(selectedTacheId)
    const lotId = parseInt(selectedLotId)
    const pct = parseFloat(pourcentage)

    if (isNaN(tacheId) || isNaN(lotId)) return
    if (isNaN(pct) || pct <= 0 || pct > 100) return

    try {
      setSaving(true)
      await financierService.createAffectation({
        chantier_id: chantierId,
        tache_id: tacheId,
        lot_budgetaire_id: lotId,
        pourcentage_affectation: pct,
      })
      setSelectedTacheId('')
      setSelectedLotId('')
      setPourcentage('100')
      setShowForm(false)
      await loadData()
    } catch (err) {
      logger.error('Erreur creation affectation', err, { context: 'AffectationsPanel' })
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Supprimer cette affectation ?')) return
    try {
      await financierService.deleteAffectation(id)
      setAffectations(prev => prev.filter(a => a.id !== id))
    } catch (err) {
      logger.error('Erreur suppression affectation', err, { context: 'AffectationsPanel' })
    }
  }

  // Resolve names for display
  const getTacheTitre = (tacheId: number): string => {
    const tache = taches.find(t => t.id === tacheId)
    return tache ? tache.titre : `Tache #${tacheId}`
  }

  const getLotLabel = (lotId: number): string => {
    const lot = lots.find(l => l.id === lotId)
    return lot ? `${lot.code_lot} - ${lot.libelle}` : `Lot #${lotId}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
        <div>
          <p>{error}</p>
          <button onClick={loadData} className="text-sm underline mt-1">Reessayer</button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Affectations table */}
      <div className="bg-white border rounded-xl">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold text-gray-900">Affectations taches / lots</h3>
          {canManage && (
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm transition-colors"
            >
              <Plus size={14} />
              Nouvelle affectation
            </button>
          )}
        </div>

        {/* Creation form */}
        {showForm && canManage && (
          <div className="p-4 bg-gray-50 border-b space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tache *</label>
                <select
                  value={selectedTacheId}
                  onChange={(e) => setSelectedTacheId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="">Selectionner une tache</option>
                  {taches.map((t) => (
                    <option key={t.id} value={t.id}>
                      #{t.id} - {t.titre}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Lot budgetaire *</label>
                <select
                  value={selectedLotId}
                  onChange={(e) => setSelectedLotId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="">Selectionner un lot</option>
                  {lots.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.code_lot} - {l.libelle}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">% Affectation</label>
                <input
                  type="number"
                  value={pourcentage}
                  onChange={(e) => setPourcentage(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  min={0}
                  max={100}
                  step="0.01"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setShowForm(false); setSelectedTacheId(''); setSelectedLotId(''); setPourcentage('100') }}
                className="px-3 py-1.5 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100 text-sm transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={handleCreate}
                disabled={saving || !selectedTacheId || !selectedLotId}
                className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm transition-colors"
              >
                {saving ? 'Creation...' : 'Creer'}
              </button>
            </div>
          </div>
        )}

        {affectations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Aucune affectation pour ce chantier
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Tache</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Lot budgetaire</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">% Affectation</th>
                  {canManage && (
                    <th className="text-center px-4 py-3 font-medium text-gray-500">Actions</th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {affectations.map((aff) => (
                  <tr key={aff.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-700">{getTacheTitre(aff.tache_id)}</td>
                    <td className="px-4 py-3 text-gray-700">{getLotLabel(aff.lot_budgetaire_id)}</td>
                    <td className="px-4 py-3 text-right font-medium text-gray-700">
                      {formatPct(aff.pourcentage_affectation)}
                    </td>
                    {canManage && (
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={() => handleDelete(aff.id)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                          title="Supprimer"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Suivi avancement integre */}
      <SuiviAvancementPanel chantierId={chantierId} />
    </div>
  )
}
