/**
 * SituationsList - Liste des situations de travaux (FIN-07)
 *
 * Affiche les situations d'un chantier avec :
 * - Colonnes: numero, periode, montant_periode_ht, montant_cumule_ht, statut, actions
 * - Workflow buttons: Soumettre, Valider, Valider Client
 * - Click sur ligne pour voir le detail
 */

import { useState, useEffect, useCallback } from 'react'
import { Loader2, Eye, Trash2, Send, Check, UserCheck } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useAuth } from '../../contexts/AuthContext'
import { logger } from '../../services/logger'
import SituationDetail from './SituationDetail'
import type { SituationTravaux } from '../../types'
import { STATUT_SITUATION_CONFIG } from '../../types'

interface SituationsListProps {
  chantierId: number
  budgetId: number
}

const formatEUR = (value: number): string =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export default function SituationsList({ chantierId, budgetId }: SituationsListProps) {
  const { user } = useAuth()
  const [situations, setSituations] = useState<SituationTravaux[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSituationId, setSelectedSituationId] = useState<number | null>(null)

  const canManage = user?.role === 'admin' || user?.role === 'conducteur'

  const loadSituations = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.listSituations(chantierId)
      setSituations(data)
    } catch (err) {
      setError('Erreur lors du chargement des situations')
      logger.error('Erreur chargement situations', err, { context: 'SituationsList' })
    } finally {
      setLoading(false)
    }
  }, [chantierId])

  useEffect(() => {
    loadSituations()
  }, [loadSituations])

  const handleSoumettre = async (id: number) => {
    try {
      const updated = await financierService.soumettreSituation(id)
      setSituations(prev => prev.map(s => s.id === updated.id ? updated : s))
    } catch (err) {
      console.error('Erreur soumission situation:', err)
    }
  }

  const handleValider = async (id: number) => {
    try {
      const updated = await financierService.validerSituation(id)
      setSituations(prev => prev.map(s => s.id === updated.id ? updated : s))
    } catch (err) {
      console.error('Erreur validation situation:', err)
    }
  }

  const handleValiderClient = async (id: number) => {
    try {
      const updated = await financierService.validerClientSituation(id)
      setSituations(prev => prev.map(s => s.id === updated.id ? updated : s))
    } catch (err) {
      console.error('Erreur validation client situation:', err)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Supprimer cette situation ?')) return
    try {
      await financierService.deleteSituation(id)
      setSituations(prev => prev.filter(s => s.id !== id))
    } catch (err) {
      console.error('Erreur suppression situation:', err)
    }
  }

  // If viewing detail, show SituationDetail
  if (selectedSituationId !== null) {
    return (
      <div>
        <button
          onClick={() => { setSelectedSituationId(null); loadSituations() }}
          className="mb-4 text-sm text-blue-600 hover:text-blue-800 transition-colors"
        >
          Retour a la liste
        </button>
        <SituationDetail
          situationId={selectedSituationId}
          budgetId={budgetId}
        />
      </div>
    )
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
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    )
  }

  return (
    <div className="bg-white border rounded-xl">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold text-gray-900">Situations de travaux</h3>
      </div>

      {situations.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Aucune situation de travaux pour ce chantier
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Numero</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Periode</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Montant periode HT</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Montant cumule HT</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Net TTC</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Statut</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {situations.map((situation) => {
                const statutConfig = STATUT_SITUATION_CONFIG[situation.statut]
                return (
                  <tr key={situation.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-gray-700">{situation.numero}</td>
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                      {formatDate(situation.periode_debut)} - {formatDate(situation.periode_fin)}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      {formatEUR(situation.montant_periode_ht)}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      {formatEUR(situation.montant_cumule_ht)}
                    </td>
                    <td className="px-4 py-3 text-right font-medium whitespace-nowrap">
                      {formatEUR(situation.montant_net)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: statutConfig.couleur + '20',
                          color: statutConfig.couleur,
                        }}
                      >
                        {statutConfig.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => setSelectedSituationId(situation.id)}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                          title="Voir detail"
                        >
                          <Eye size={16} />
                        </button>
                        {canManage && situation.statut === 'brouillon' && (
                          <>
                            <button
                              onClick={() => handleSoumettre(situation.id)}
                              className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                              title="Soumettre"
                            >
                              <Send size={16} />
                            </button>
                            <button
                              onClick={() => handleDelete(situation.id)}
                              className="p-1 text-red-600 hover:bg-red-50 rounded"
                              title="Supprimer"
                            >
                              <Trash2 size={16} />
                            </button>
                          </>
                        )}
                        {canManage && situation.statut === 'en_validation' && (
                          <button
                            onClick={() => handleValider(situation.id)}
                            className="p-1 text-green-600 hover:bg-green-50 rounded"
                            title="Valider"
                          >
                            <Check size={16} />
                          </button>
                        )}
                        {canManage && situation.statut === 'emise' && (
                          <button
                            onClick={() => handleValiderClient(situation.id)}
                            className="p-1 text-green-600 hover:bg-green-50 rounded"
                            title="Valider client"
                          >
                            <UserCheck size={16} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
