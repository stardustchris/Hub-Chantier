/**
 * Composant RessourceList - Liste des ressources avec filtres
 *
 * LOG-01: Référentiel matériel
 */

import React, { useState, useEffect } from 'react'
import { Plus, Search, Filter } from 'lucide-react'
import type { Ressource, CategorieRessource } from '../../types/logistique'
import { CATEGORIES_RESSOURCES } from '../../types/logistique'
import { listRessources } from '../../api/logistique'
import RessourceCard from './RessourceCard'

interface RessourceListProps {
  onSelectRessource?: (ressource: Ressource) => void
  onCreateRessource?: () => void
  onEditRessource?: (ressource: Ressource) => void
  selectedRessourceId?: number
  isAdmin?: boolean
}

const RessourceList: React.FC<RessourceListProps> = ({
  onSelectRessource,
  onCreateRessource,
  onEditRessource,
  selectedRessourceId,
  isAdmin = false,
}) => {
  const [ressources, setRessources] = useState<Ressource[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [categorieFilter, setCategorieFilter] = useState<CategorieRessource | ''>('')
  const [showInactifs, setShowInactifs] = useState(false)

  useEffect(() => {
    loadRessources()
  }, [categorieFilter, showInactifs])

  const loadRessources = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await listRessources({
        categorie: categorieFilter || undefined,
        actif_seulement: !showInactifs,
        limit: 100,
      })
      setRessources(data.items)
    } catch (err) {
      setError('Erreur lors du chargement des ressources')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const filteredRessources = ressources.filter((r) => {
    if (!searchTerm) return true
    const search = searchTerm.toLowerCase()
    return (
      r.nom.toLowerCase().includes(search) ||
      r.code.toLowerCase().includes(search) ||
      r.description?.toLowerCase().includes(search)
    )
  })

  return (
    <div className="space-y-4">
      {/* Header avec recherche et filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Recherche */}
        <div className="relative flex-1">
          <Search
            size={18}
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
          />
          <input
            type="text"
            placeholder="Rechercher une ressource..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Filtre catégorie */}
        <div className="flex items-center gap-2">
          <Filter size={18} className="text-gray-400" />
          <select
            value={categorieFilter}
            onChange={(e) => setCategorieFilter(e.target.value as CategorieRessource | '')}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Toutes catégories</option>
            {Object.entries(CATEGORIES_RESSOURCES).map(([key, info]) => (
              <option key={key} value={key}>
                {info.label}
              </option>
            ))}
          </select>
        </div>

        {/* Toggle inactifs */}
        {isAdmin && (
          <label className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              checked={showInactifs}
              onChange={(e) => setShowInactifs(e.target.checked)}
              className="rounded text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">Afficher inactifs</span>
          </label>
        )}

        {/* Bouton créer */}
        {isAdmin && onCreateRessource && (
          <button
            onClick={onCreateRessource}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={18} />
            <span>Nouvelle ressource</span>
          </button>
        )}
      </div>

      {/* État de chargement */}
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      )}

      {/* Erreur */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Liste vide */}
      {!loading && !error && filteredRessources.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          {searchTerm || categorieFilter
            ? 'Aucune ressource ne correspond aux critères'
            : 'Aucune ressource disponible'}
        </div>
      )}

      {/* Grille de ressources */}
      {!loading && !error && filteredRessources.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRessources.map((ressource) => (
            <RessourceCard
              key={ressource.id}
              ressource={ressource}
              onSelect={onSelectRessource}
              onEdit={isAdmin ? onEditRessource : undefined}
              selected={ressource.id === selectedRessourceId}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default RessourceList
