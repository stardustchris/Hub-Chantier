/**
 * Composant RessourceCard - Affiche une ressource dans une carte
 *
 * LOG-02: Fiche ressource - Nom, code, photo, couleur, plage horaire par défaut
 */

import React from 'react'
import { Settings, Clock, CheckCircle, XCircle } from 'lucide-react'
import type { Ressource } from '../../types/logistique'
import { CATEGORIES_RESSOURCES } from '../../types/logistique'
import { formatPlageHoraire } from '../../api/logistique'

interface RessourceCardProps {
  ressource: Ressource
  onSelect?: (ressource: Ressource) => void
  onEdit?: (ressource: Ressource) => void
  selected?: boolean
}

const RessourceCard: React.FC<RessourceCardProps> = ({
  ressource,
  onSelect,
  onEdit,
  selected = false,
}) => {
  const categorieInfo = CATEGORIES_RESSOURCES[ressource.categorie]

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border-2 transition-all cursor-pointer hover:shadow-md ${
        selected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'
      } ${!ressource.actif ? 'opacity-60' : ''}`}
      onClick={() => onSelect?.(ressource)}
    >
      {/* Header avec couleur */}
      <div
        className="h-2 rounded-t-lg"
        style={{ backgroundColor: ressource.couleur }}
      />

      <div className="p-4">
        {/* Photo et infos principales */}
        <div className="flex items-start gap-3">
          {ressource.photo_url ? (
            <img
              src={ressource.photo_url}
              alt={ressource.nom}
              className="w-16 h-16 rounded-lg object-cover"
            />
          ) : (
            <div
              className="w-16 h-16 rounded-lg flex items-center justify-center text-white text-xl font-bold"
              style={{ backgroundColor: ressource.couleur }}
            >
              {ressource.code.substring(0, 2)}
            </div>
          )}

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-gray-500">
                [{ressource.code}]
              </span>
              {!ressource.actif && (
                <span className="text-xs px-1.5 py-0.5 bg-gray-200 text-gray-600 rounded">
                  Inactif
                </span>
              )}
            </div>
            <h3 className="font-semibold text-gray-900 truncate">
              {ressource.nom}
            </h3>
            <span
              className="inline-block text-xs px-2 py-0.5 rounded-full text-white mt-1"
              style={{ backgroundColor: categorieInfo.color }}
            >
              {categorieInfo.label}
            </span>
          </div>

          {onEdit && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onEdit(ressource)
              }}
              className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
            >
              <Settings size={18} />
            </button>
          )}
        </div>

        {/* Description */}
        {ressource.description && (
          <p className="text-sm text-gray-600 mt-2 line-clamp-2">
            {ressource.description}
          </p>
        )}

        {/* Infos supplémentaires */}
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Clock size={14} />
            <span>
              {formatPlageHoraire(
                ressource.heure_debut_defaut,
                ressource.heure_fin_defaut
              )}
            </span>
          </div>

          <div className="flex items-center gap-1 text-sm">
            {ressource.validation_requise ? (
              <>
                <CheckCircle size={14} className="text-orange-500" />
                <span className="text-orange-600">Validation N+1</span>
              </>
            ) : (
              <>
                <XCircle size={14} className="text-green-500" />
                <span className="text-green-600">Sans validation</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default RessourceCard
