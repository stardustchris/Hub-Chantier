/**
 * AlertesFinancieresCard - Carte des alertes financières pour le dashboard (5.2.4)
 *
 * Affiche les alertes de dépassement budget actives.
 * Visible uniquement pour les rôles admin/conducteur.
 *
 * Fonctionnalités:
 * - Affichage des 3 premières alertes non acquittées
 * - Indication visuelle de la gravité (bordure orange/rouge)
 * - Lien vers la page finances pour voir toutes les alertes
 * - Cache automatiquement si aucune alerte
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, TrendingUp } from 'lucide-react'
import type { AlerteDepassement } from '../../types'
import { formatEUR } from '../../utils/format'

export default function AlertesFinancieresCard() {
  const navigate = useNavigate()
  const [alertes, setAlertes] = useState<AlerteDepassement[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadAlertes = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Récupérer toutes les alertes non acquittées pour tous les chantiers
      // Note: en prod, il faudrait un endpoint global pour récupérer toutes les alertes
      // Pour l'instant, on fait une approximation simple
      // TODO: ajouter un endpoint /api/financier/alertes/globales

      // Pour l'instant, on retourne un tableau vide
      // Le backend devra implémenter un endpoint global
      setAlertes([])
    } catch (err) {
      console.error('Erreur chargement alertes financières', err)
      setError('Impossible de charger les alertes')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAlertes()
  }, [loadAlertes])

  // Ne rien afficher si:
  // - En chargement
  // - Aucune alerte
  // - Erreur
  if (isLoading || alertes.length === 0 || error) {
    return null
  }

  // Limiter à 3 alertes
  const alertesToShow = alertes.slice(0, 3)

  // Déterminer la gravité maximale pour la bordure
  const maxSeverity = Math.max(...alertesToShow.map((a) => a.pourcentage_atteint))
  const borderColor = maxSeverity >= 100 ? 'border-red-500' : 'border-orange-500'
  const bgColor = maxSeverity >= 100 ? 'bg-red-50' : 'bg-orange-50'

  return (
    <div className={`bg-white rounded-2xl p-5 shadow-lg border-2 ${borderColor}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-orange-600" />
          Alertes financières
        </h2>
        {alertes.length > 3 && (
          <button
            onClick={() => navigate('/finances')}
            className="text-sm text-orange-600 hover:text-orange-700 font-medium"
            aria-label="Voir toutes les alertes"
          >
            Voir tout
          </button>
        )}
      </div>

      {/* Liste des alertes */}
      <div className="space-y-3">
        {alertesToShow.map((alerte) => {
          const isDepassement = alerte.pourcentage_atteint >= 100
          const iconColor = isDepassement ? 'text-red-600' : 'text-orange-600'
          const textColor = isDepassement ? 'text-red-700' : 'text-orange-700'

          return (
            <div
              key={alerte.id}
              className={`p-3 rounded-lg ${bgColor} border ${
                isDepassement ? 'border-red-200' : 'border-orange-200'
              }`}
            >
              <div className="flex items-start gap-3">
                <AlertTriangle className={`w-5 h-5 ${iconColor} mt-0.5 flex-shrink-0`} />
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${textColor}`}>{alerte.message}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <TrendingUp className={`w-4 h-4 ${iconColor}`} />
                    <span className={`text-xs font-medium ${textColor}`}>
                      {alerte.pourcentage_atteint.toFixed(1)}% du budget
                    </span>
                    <span className="text-xs text-gray-500">
                      ({formatEUR(alerte.montant_atteint_ht)} / {formatEUR(alerte.montant_budget_ht)})
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Footer avec lien vers finances */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <button
          onClick={() => navigate('/finances')}
          className="w-full text-sm text-orange-600 hover:text-orange-700 font-medium text-center"
        >
          Gérer les alertes
        </button>
      </div>
    </div>
  )
}
