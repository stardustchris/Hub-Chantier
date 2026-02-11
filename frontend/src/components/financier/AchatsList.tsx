/**
 * AchatsList - Liste des achats d'un chantier avec filtres (FIN-05)
 *
 * Affiche les achats avec :
 * - Colonnes: Date, Fournisseur, Libelle, Montant HT, TVA, TTC, Statut
 * - Badge colore par statut
 * - Filtres par statut et fournisseur
 * - Actions workflow par ligne
 */

import { useState, useEffect } from 'react'
import { Plus, Filter, Loader2 } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useAuth } from '../../contexts/AuthContext'
import { logger } from '../../services/logger'
import AchatModal from './AchatModal'
import AchatWorkflowActions from './AchatWorkflowActions'
import type { Achat, Fournisseur, LotBudgetaire, StatutAchat } from '../../types'
import { STATUT_ACHAT_CONFIG, TYPE_ACHAT_LABELS } from '../../types'
import { formatEUR } from '../../utils/format'

interface AchatsListProps {
  chantierId: number
  budgetId?: number
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export default function AchatsList({ chantierId, budgetId }: AchatsListProps) {
  const { user } = useAuth()
  const [achats, setAchats] = useState<Achat[]>([])
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([])
  const [lots, setLots] = useState<LotBudgetaire[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [editingAchat, setEditingAchat] = useState<Achat | undefined>(undefined)

  // Filtres
  const [statutFilter, setStatutFilter] = useState<StatutAchat | ''>('')
  const [fournisseurFilter, setFournisseurFilter] = useState<number | ''>('')

  const canCreate = user?.role === 'admin' || user?.role === 'conducteur' || user?.role === 'chef_chantier'
  const canManage = user?.role === 'admin' || user?.role === 'conducteur'

  useEffect(() => {
    loadData()
  }, [chantierId, statutFilter])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [achatsData, fournisseursData] = await Promise.all([
        financierService.listAchats({
          chantier_id: chantierId,
          statut: statutFilter || undefined,
          limit: 100,
        }),
        financierService.listFournisseurs({ actif_seulement: true, limit: 200 }),
      ])

      setAchats(achatsData.items || [])
      setFournisseurs(fournisseursData.items || [])

      // Charger les lots si on a un budgetId
      if (budgetId) {
        const lotsData = await financierService.listLots(budgetId)
        setLots(lotsData)
      }
    } catch (err) {
      setError('Erreur lors du chargement des achats')
      logger.error('Erreur chargement achats', err, { context: 'AchatsList' })
    } finally {
      setLoading(false)
    }
  }

  const handleAchatUpdate = (updatedAchat: Achat) => {
    setAchats(prev => prev.map(a => a.id === updatedAchat.id ? updatedAchat : a))
  }

  const handleModalSuccess = () => {
    setShowModal(false)
    setEditingAchat(undefined)
    loadData()
  }

  // Filtrage par fournisseur (cote client)
  const filteredAchats = fournisseurFilter
    ? achats.filter(a => a.fournisseur_id === fournisseurFilter)
    : achats

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
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 border-b">
        <h3 className="font-semibold text-gray-900">Achats</h3>
        <div className="flex flex-wrap items-center gap-2">
          {/* Filtre statut */}
          <div className="flex items-center gap-1">
            <Filter size={14} className="text-gray-400" />
            <select
              value={statutFilter}
              onChange={(e) => setStatutFilter(e.target.value as StatutAchat | '')}
              className="text-sm px-2 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Tous les statuts</option>
              {Object.entries(STATUT_ACHAT_CONFIG).map(([key, config]) => (
                <option key={key} value={key}>{config.label}</option>
              ))}
            </select>
          </div>

          {/* Filtre fournisseur */}
          {fournisseurs.length > 0 && (
            <select
              value={fournisseurFilter}
              onChange={(e) => setFournisseurFilter(e.target.value ? parseInt(e.target.value) : '')}
              className="text-sm px-2 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Tous les fournisseurs</option>
              {fournisseurs.map((f) => (
                <option key={f.id} value={f.id}>{f.raison_sociale}</option>
              ))}
            </select>
          )}

          {canCreate && (
            <button
              onClick={() => { setEditingAchat(undefined); setShowModal(true) }}
              className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm transition-colors"
            >
              <Plus size={14} />
              Nouvel achat
            </button>
          )}
        </div>
      </div>

      {filteredAchats.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {statutFilter || fournisseurFilter
            ? 'Aucun achat ne correspond aux filtres'
            : 'Aucun achat pour ce chantier'}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Date</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Fournisseur</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Libelle</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Type</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">HT</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">TTC</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Statut</th>
                {canManage && (
                  <th className="text-center px-4 py-3 font-medium text-gray-500">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredAchats.map((achat) => {
                const statutConfig = STATUT_ACHAT_CONFIG[achat.statut]
                return (
                  <tr key={achat.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                      {formatDate(achat.date_commande)}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {achat.fournisseur_nom || '-'}
                    </td>
                    <td className="px-4 py-3 text-gray-700 max-w-[120px] sm:max-w-[160px] lg:max-w-[200px] truncate">
                      {achat.libelle}
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {TYPE_ACHAT_LABELS[achat.type_achat]}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      {formatEUR(achat.total_ht)}
                    </td>
                    <td className="px-4 py-3 text-right font-medium whitespace-nowrap">
                      {formatEUR(achat.total_ttc)}
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
                    {canManage && (
                      <td className="px-4 py-3 text-center">
                        <AchatWorkflowActions
                          achat={achat}
                          onUpdate={handleAchatUpdate}
                        />
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <AchatModal
          chantierId={chantierId}
          achat={editingAchat}
          fournisseurs={fournisseurs}
          lots={lots}
          onClose={() => { setShowModal(false); setEditingAchat(undefined) }}
          onSuccess={handleModalSuccess}
        />
      )}
    </div>
  )
}
