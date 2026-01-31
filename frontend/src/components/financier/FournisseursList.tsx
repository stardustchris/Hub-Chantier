/**
 * FournisseursList - Liste des fournisseurs avec filtres (FIN-14)
 *
 * Affiche la liste des fournisseurs avec :
 * - Filtres par type et statut actif/archive
 * - Table: Raison sociale, Type, SIRET, Contact, Telephone, Statut
 * - Actions: Editer, Archiver/Reactiver, Supprimer
 */

import { useState, useEffect } from 'react'
import { Plus, Search, Filter, Pencil, Archive, RotateCcw, Trash2, Loader2 } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useToast } from '../../contexts/ToastContext'
import { logger } from '../../services/logger'
import FournisseurModal from './FournisseurModal'
import type { Fournisseur, TypeFournisseur } from '../../types'
import { TYPE_FOURNISSEUR_LABELS } from '../../types'

export default function FournisseursList() {
  const { addToast, showUndoToast } = useToast()
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [editingFournisseur, setEditingFournisseur] = useState<Fournisseur | undefined>(undefined)

  // Filtres
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<TypeFournisseur | ''>('')
  const [showArchived, setShowArchived] = useState(false)

  useEffect(() => {
    loadFournisseurs()
  }, [typeFilter, showArchived])

  const loadFournisseurs = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.listFournisseurs({
        type: typeFilter || undefined,
        actif_seulement: !showArchived,
        limit: 200,
      })
      setFournisseurs(data.items || [])
    } catch (err) {
      setError('Erreur lors du chargement des fournisseurs')
      logger.error('Erreur chargement fournisseurs', err, { context: 'FournisseursList' })
    } finally {
      setLoading(false)
    }
  }

  const handleToggleActif = async (fournisseur: Fournisseur) => {
    try {
      await financierService.updateFournisseur(fournisseur.id, {
        actif: !fournisseur.actif,
      })
      addToast({
        message: fournisseur.actif ? 'Fournisseur archive' : 'Fournisseur reactive',
        type: 'success',
      })
      loadFournisseurs()
    } catch (err) {
      logger.error('Erreur toggle actif fournisseur', err, { context: 'FournisseursList' })
      addToast({ message: 'Erreur lors de la mise a jour', type: 'error' })
    }
  }

  const handleDelete = (fournisseur: Fournisseur) => {
    const name = fournisseur.raison_sociale
    const original = [...fournisseurs]
    setFournisseurs(prev => prev.filter(f => f.id !== fournisseur.id))

    showUndoToast(
      `Fournisseur "${name}" supprime`,
      () => {
        setFournisseurs(original)
        addToast({ message: 'Suppression annulee', type: 'success', duration: 3000 })
      },
      async () => {
        try {
          await financierService.deleteFournisseur(fournisseur.id)
        } catch (err) {
          setFournisseurs(original)
          logger.error('Erreur suppression fournisseur', err, { context: 'FournisseursList' })
          addToast({ message: 'Erreur lors de la suppression', type: 'error' })
        }
      },
      5000
    )
  }

  const handleModalSuccess = () => {
    setShowModal(false)
    setEditingFournisseur(undefined)
    loadFournisseurs()
  }

  // Filtrage texte cote client
  const filtered = fournisseurs.filter((f) => {
    if (!searchTerm) return true
    const search = searchTerm.toLowerCase()
    return (
      f.raison_sociale.toLowerCase().includes(search) ||
      f.siret?.toLowerCase().includes(search) ||
      f.contact_principal?.toLowerCase().includes(search) ||
      f.email?.toLowerCase().includes(search)
    )
  })

  return (
    <div className="space-y-4">
      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher un fournisseur..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter size={18} className="text-gray-400 flex-shrink-0" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as TypeFournisseur | '')}
            className="px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tous les types</option>
            {Object.entries(TYPE_FOURNISSEUR_LABELS).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        <label className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg cursor-pointer">
          <input
            type="checkbox"
            checked={showArchived}
            onChange={(e) => setShowArchived(e.target.checked)}
            className="rounded text-blue-500 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-600 whitespace-nowrap">Archives</span>
        </label>

        <button
          onClick={() => { setEditingFournisseur(undefined); setShowModal(true) }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors whitespace-nowrap"
        >
          <Plus size={18} />
          Nouveau fournisseur
        </button>
      </div>

      {/* Erreur */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Chargement */}
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {searchTerm || typeFilter
            ? 'Aucun fournisseur ne correspond aux criteres'
            : 'Aucun fournisseur enregistre'}
        </div>
      ) : (
        <div className="bg-white border rounded-xl overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Raison sociale</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Type</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">SIRET</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Contact</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Telephone</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Statut</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((fournisseur) => (
                <tr key={fournisseur.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {fournisseur.raison_sociale}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {TYPE_FOURNISSEUR_LABELS[fournisseur.type]}
                  </td>
                  <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                    {fournisseur.siret || '-'}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {fournisseur.contact_principal || '-'}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {fournisseur.telephone ? (
                      <a href={`tel:${fournisseur.telephone}`} className="text-blue-600 hover:underline">
                        {fournisseur.telephone}
                      </a>
                    ) : '-'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                      fournisseur.actif
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-500'
                    }`}>
                      {fournisseur.actif ? 'Actif' : 'Archive'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-center gap-1">
                      <button
                        onClick={() => { setEditingFournisseur(fournisseur); setShowModal(true) }}
                        className="p-1.5 text-gray-400 hover:text-blue-600 rounded"
                        title="Modifier"
                      >
                        <Pencil size={14} />
                      </button>
                      <button
                        onClick={() => handleToggleActif(fournisseur)}
                        className="p-1.5 text-gray-400 hover:text-orange-600 rounded"
                        title={fournisseur.actif ? 'Archiver' : 'Reactiver'}
                      >
                        {fournisseur.actif ? <Archive size={14} /> : <RotateCcw size={14} />}
                      </button>
                      <button
                        onClick={() => handleDelete(fournisseur)}
                        className="p-1.5 text-gray-400 hover:text-red-600 rounded"
                        title="Supprimer"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <FournisseurModal
          fournisseur={editingFournisseur}
          onClose={() => { setShowModal(false); setEditingFournisseur(undefined) }}
          onSuccess={handleModalSuccess}
        />
      )}
    </div>
  )
}
