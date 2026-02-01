/**
 * AchatsPage - Gestion des achats et bons de commande
 * CDC Module 17 - FIN-05
 */

import { useState } from 'react'
import Layout from '../components/Layout'
import {
  ShoppingCart,
  Plus,
  Search,
  Filter,
  FileText,
  CheckCircle,
  Clock,
  XCircle,
  Package,
  Building2,
  Calendar,
  Euro,
} from 'lucide-react'

interface BonCommande {
  id: string
  numero: string
  chantier_nom: string
  fournisseur: string
  date_emission: string
  date_livraison_prevue?: string
  montant_ht: number
  montant_ttc: number
  statut: 'en_attente' | 'validee' | 'livree' | 'annulee'
  articles_count: number
}

export default function AchatsPage() {
  const [bonCommandes] = useState<BonCommande[]>([
    {
      id: '1',
      numero: 'BC-2026-001',
      chantier_nom: 'Villa Moderne Duplex',
      fournisseur: 'Béton Express',
      date_emission: '2026-01-20',
      date_livraison_prevue: '2026-01-27',
      montant_ht: 12500,
      montant_ttc: 15000,
      statut: 'validee',
      articles_count: 3,
    },
    {
      id: '2',
      numero: 'BC-2026-002',
      chantier_nom: 'Résidence Les Jardins',
      fournisseur: 'Acier Pro',
      date_emission: '2026-01-22',
      date_livraison_prevue: '2026-02-05',
      montant_ht: 28000,
      montant_ttc: 33600,
      statut: 'en_attente',
      articles_count: 5,
    },
    {
      id: '3',
      numero: 'BC-2026-003',
      chantier_nom: 'École Jean Jaurès',
      fournisseur: 'Matériaux du Bâtiment',
      date_emission: '2026-01-15',
      date_livraison_prevue: '2026-01-22',
      montant_ht: 8500,
      montant_ttc: 10200,
      statut: 'livree',
      articles_count: 8,
    },
  ])

  const [searchQuery, setSearchQuery] = useState('')
  const [statutFilter, setStatutFilter] = useState<string>('tous')

  const getStatutConfig = (statut: BonCommande['statut']) => {
    switch (statut) {
      case 'en_attente':
        return {
          label: 'En attente',
          color: 'bg-yellow-100 text-yellow-800',
          icon: Clock,
        }
      case 'validee':
        return {
          label: 'Validée',
          color: 'bg-blue-100 text-blue-800',
          icon: CheckCircle,
        }
      case 'livree':
        return {
          label: 'Livrée',
          color: 'bg-green-100 text-green-800',
          icon: Package,
        }
      case 'annulee':
        return {
          label: 'Annulée',
          color: 'bg-red-100 text-red-800',
          icon: XCircle,
        }
      default:
        return {
          label: statut,
          color: 'bg-gray-100 text-gray-800',
          icon: FileText,
        }
    }
  }

  const formatMontant = (montant: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
    }).format(montant)
  }

  const filteredBonCommandes = bonCommandes.filter((bc) => {
    const matchSearch =
      bc.numero.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bc.chantier_nom.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bc.fournisseur.toLowerCase().includes(searchQuery.toLowerCase())

    const matchStatut = statutFilter === 'tous' || bc.statut === statutFilter

    return matchSearch && matchStatut
  })

  // Statistiques
  const totalHT = bonCommandes.reduce((sum, bc) => sum + bc.montant_ht, 0)
  const totalTTC = bonCommandes.reduce((sum, bc) => sum + bc.montant_ttc, 0)
  const enAttente = bonCommandes.filter((bc) => bc.statut === 'en_attente').length
  const validees = bonCommandes.filter((bc) => bc.statut === 'validee').length

  return (
    <Layout title="Achats & Bons de commande">
      <div className="space-y-6">
        {/* Statistiques globales */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total HT</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatMontant(totalHT)}
                </p>
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
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatMontant(totalTTC)}
                </p>
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
                  placeholder="Rechercher un bon de commande..."
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
                <option value="annulee">Annulée</option>
              </select>
            </div>
            <button className="btn btn-primary flex items-center gap-2 w-full md:w-auto">
              <Plus className="w-4 h-4" />
              Nouveau bon de commande
            </button>
          </div>
        </div>

        {/* Liste des bons de commande */}
        <div className="space-y-4">
          {filteredBonCommandes.map((bc) => {
            const statutConfig = getStatutConfig(bc.statut)
            const StatutIcon = statutConfig.icon

            return (
              <div
                key={bc.id}
                className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{bc.numero}</h3>
                      <div className="flex items-center gap-4 mt-1">
                        <div className="flex items-center gap-1.5 text-sm text-gray-500">
                          <Building2 className="w-4 h-4" />
                          <span>{bc.chantier_nom}</span>
                        </div>
                        <div className="text-sm text-gray-500">
                          Fournisseur: <span className="font-medium">{bc.fournisseur}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 ${statutConfig.color}`}>
                    <StatutIcon className="w-3.5 h-3.5" />
                    {statutConfig.label}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-500">Date émission</p>
                    <div className="flex items-center gap-1.5 mt-1">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <p className="text-sm font-medium text-gray-900">
                        {new Date(bc.date_emission).toLocaleDateString('fr-FR')}
                      </p>
                    </div>
                  </div>
                  {bc.date_livraison_prevue && (
                    <div>
                      <p className="text-xs text-gray-500">Livraison prévue</p>
                      <div className="flex items-center gap-1.5 mt-1">
                        <Package className="w-4 h-4 text-gray-400" />
                        <p className="text-sm font-medium text-gray-900">
                          {new Date(bc.date_livraison_prevue).toLocaleDateString('fr-FR')}
                        </p>
                      </div>
                    </div>
                  )}
                  <div>
                    <p className="text-xs text-gray-500">Montant HT</p>
                    <p className="text-sm font-semibold text-gray-900 mt-1">
                      {formatMontant(bc.montant_ht)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Montant TTC</p>
                    <p className="text-sm font-semibold text-blue-600 mt-1">
                      {formatMontant(bc.montant_ttc)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div className="text-sm text-gray-500">
                    {bc.articles_count} article{bc.articles_count > 1 ? 's' : ''}
                  </div>
                  <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                    Voir les détails →
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        {filteredBonCommandes.length === 0 && (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <ShoppingCart className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">Aucun bon de commande trouvé</p>
          </div>
        )}
      </div>
    </Layout>
  )
}
