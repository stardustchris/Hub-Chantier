/**
 * AchatsPage - Gestion des achats et bons de commande
 * CDC Module 17 - FIN-05
 *
 * Connecté à l'API GET /api/financier/achats.
 */

import { useState, useEffect, useCallback } from 'react'
import Layout from '../components/Layout'
import AchatModal from '../components/financier/AchatModal'
import { financierService } from '../services/financier'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import type { Achat, Chantier, Fournisseur, LotBudgetaire, StatutAchat } from '../types'
import {
  ShoppingCart,
  Plus,
  Search,
  CheckCircle,
  Clock,
  XCircle,
  Package,
  Building2,
  Calendar,
  Euro,
  FileText,
  Loader2,
  AlertTriangle,
} from 'lucide-react'

const STATUT_CONFIG: Record<string, { label: string; color: string; icon: typeof Clock }> = {
  en_attente: { label: 'En attente', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
  validee: { label: 'Validée', color: 'bg-blue-100 text-blue-800', icon: CheckCircle },
  livree: { label: 'Livrée', color: 'bg-green-100 text-green-800', icon: Package },
  annulee: { label: 'Annulée', color: 'bg-red-100 text-red-800', icon: XCircle },
  facturee: { label: 'Facturée', color: 'bg-indigo-100 text-indigo-800', icon: FileText },
  refusee: { label: 'Refusée', color: 'bg-red-100 text-red-800', icon: XCircle },
}

function formatMontant(montant: number) {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(montant)
}

export default function AchatsPage() {
  const [achats, setAchats] = useState<Achat[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [statutFilter, setStatutFilter] = useState<string>('tous')

  // Modal state
  const [showModal, setShowModal] = useState(false)
  const [selectedChantierId, setSelectedChantierId] = useState<number | null>(null)
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([])
  const [lots, setLots] = useState<LotBudgetaire[]>([])
  const [showChantierPicker, setShowChantierPicker] = useState(false)

  const loadAchats = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params: { statut?: string } = {}
      if (statutFilter !== 'tous') params.statut = statutFilter
      const data = await financierService.listAchats(params)
      setAchats(data.items)
    } catch (err) {
      logger.error('Erreur chargement achats', err, { context: 'AchatsPage' })
      setError('Erreur lors du chargement des achats')
    } finally {
      setLoading(false)
    }
  }, [statutFilter])

  const loadChantiers = useCallback(async () => {
    try {
      const data = await chantiersService.list({ size: 100 })
      setChantiers(data.items.filter((c) => c.statut !== 'ferme'))
    } catch (err) {
      logger.error('Erreur chargement chantiers', err, { context: 'AchatsPage' })
    }
  }, [])

  useEffect(() => {
    loadAchats()
    loadChantiers()
  }, [loadAchats, loadChantiers])

  // Charger fournisseurs + lots quand un chantier est sélectionné
  const handleOpenModal = useCallback(async (chantierId: number) => {
    try {
      const [fournData, budgetData] = await Promise.all([
        financierService.listFournisseurs(),
        financierService.getBudgetByChantier(chantierId).catch(() => null),
      ])
      setFournisseurs(fournData.items || fournData)
      setLots(budgetData?.lots || [])
      setSelectedChantierId(chantierId)
      setShowChantierPicker(false)
      setShowModal(true)
    } catch (err) {
      logger.error('Erreur chargement données modal', err, { context: 'AchatsPage' })
    }
  }, [])

  const handleNewClick = useCallback(() => {
    if (chantiers.length === 1) {
      handleOpenModal(Number(chantiers[0].id))
    } else {
      setShowChantierPicker(true)
    }
  }, [chantiers, handleOpenModal])

  const filteredAchats = achats.filter((a) => {
    const q = searchQuery.toLowerCase()
    const matchSearch =
      !q ||
      (a.libelle || '').toLowerCase().includes(q) ||
      (a.chantier_nom || '').toLowerCase().includes(q) ||
      (a.fournisseur_nom || '').toLowerCase().includes(q) ||
      (a.numero_facture || '').toLowerCase().includes(q)
    return matchSearch
  })

  // Statistiques
  const totalHT = achats.reduce((sum, a) => sum + (a.total_ht || 0), 0)
  const totalTTC = achats.reduce((sum, a) => sum + (a.total_ttc || 0), 0)
  const enAttente = achats.filter((a) => a.statut === 'en_attente').length
  const validees = achats.filter((a) => a.statut === 'validee').length

  return (
    <Layout title="Achats & Bons de commande">
      <div className="space-y-6">
        {/* Statistiques globales */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total HT</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{formatMontant(totalHT)}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Euro className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total TTC</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{formatMontant(totalTTC)}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">En attente</p>
                <p className="text-2xl font-bold text-yellow-600 mt-1">{enAttente}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Validées</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">{validees}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Barre d'actions */}
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex flex-col md:flex-row gap-3 flex-1 w-full">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher un achat..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input pl-10 w-full"
                />
              </div>
              <select
                value={statutFilter}
                onChange={(e) => setStatutFilter(e.target.value)}
                className="input w-full md:w-48"
              >
                <option value="tous">Tous les statuts</option>
                <option value="en_attente">En attente</option>
                <option value="validee">Validée</option>
                <option value="livree">Livrée</option>
                <option value="facturee">Facturée</option>
                <option value="annulee">Annulée</option>
              </select>
            </div>
            <button
              onClick={handleNewClick}
              className="btn btn-primary flex items-center gap-2 w-full md:w-auto"
            >
              <Plus className="w-4 h-4" />
              Nouveau bon de commande
            </button>
          </div>
        </div>

        {/* Picker chantier (popup simple) */}
        {showChantierPicker && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="fixed inset-0 bg-black/50" onClick={() => setShowChantierPicker(false)} />
            <div className="relative bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
              <h3 className="text-lg font-semibold mb-4">Sélectionner un chantier</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {chantiers.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => handleOpenModal(Number(c.id))}
                    className="w-full text-left px-4 py-3 rounded-lg hover:bg-primary-50 hover:text-primary-700 transition-colors border border-gray-200"
                  >
                    <div className="font-medium">{c.nom}</div>
                    <div className="text-sm text-gray-500">{c.code}</div>
                  </button>
                ))}
              </div>
              <button
                onClick={() => setShowChantierPicker(false)}
                className="mt-4 w-full px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Annuler
              </button>
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
          </div>
        )}

        {/* Erreur */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Liste des achats */}
        {!loading && !error && (
          <div className="space-y-4">
            {filteredAchats.map((achat) => {
              const config = STATUT_CONFIG[achat.statut] || STATUT_CONFIG.en_attente
              const StatutIcon = config.icon

              return (
                <div
                  key={achat.id}
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{achat.libelle}</h3>
                        <div className="flex items-center gap-4 mt-1 flex-wrap">
                          <div className="flex items-center gap-1.5 text-sm text-gray-500">
                            <Building2 className="w-4 h-4" />
                            <span>{achat.chantier_nom || `Chantier #${achat.chantier_id}`}</span>
                          </div>
                          <div className="text-sm text-gray-500">
                            Fournisseur:{' '}
                            <span className="font-medium">
                              {achat.fournisseur_nom || `#${achat.fournisseur_id}`}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 shrink-0 ${config.color}`}
                    >
                      <StatutIcon className="w-3.5 h-3.5" />
                      {config.label}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Date commande</p>
                      <div className="flex items-center gap-1.5 mt-1">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        <p className="text-sm font-medium text-gray-900">
                          {new Date(achat.date_commande + 'T00:00:00').toLocaleDateString('fr-FR')}
                        </p>
                      </div>
                    </div>
                    {achat.date_livraison_prevue && (
                      <div>
                        <p className="text-xs text-gray-500">Livraison prévue</p>
                        <div className="flex items-center gap-1.5 mt-1">
                          <Package className="w-4 h-4 text-gray-400" />
                          <p className="text-sm font-medium text-gray-900">
                            {new Date(achat.date_livraison_prevue + 'T00:00:00').toLocaleDateString(
                              'fr-FR'
                            )}
                          </p>
                        </div>
                      </div>
                    )}
                    <div>
                      <p className="text-xs text-gray-500">Montant HT</p>
                      <p className="text-sm font-semibold text-gray-900 mt-1">
                        {formatMontant(achat.total_ht)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Montant TTC</p>
                      <p className="text-sm font-semibold text-blue-600 mt-1">
                        {formatMontant(achat.total_ttc)}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}

            {filteredAchats.length === 0 && (
              <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
                <ShoppingCart className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Aucun achat trouvé</p>
              </div>
            )}
          </div>
        )}

        {/* Modal création achat */}
        {showModal && selectedChantierId && (
          <AchatModal
            chantierId={selectedChantierId}
            fournisseurs={fournisseurs}
            lots={lots}
            onClose={() => {
              setShowModal(false)
              setSelectedChantierId(null)
            }}
            onSuccess={() => {
              setShowModal(false)
              setSelectedChantierId(null)
              loadAchats()
            }}
          />
        )}
      </div>
    </Layout>
  )
}
