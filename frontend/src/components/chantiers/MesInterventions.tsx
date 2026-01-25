/**
 * MesInterventions - Affiche les interventions planifiees de l'utilisateur courant sur un chantier
 *
 * Permet a l'utilisateur de voir quand il est/etait planifie sur ce chantier,
 * meme s'il intervient a plusieurs moments.
 */

import { useState, useEffect } from 'react'
import { Calendar, Clock, Loader2, AlertCircle } from 'lucide-react'
import { planningService } from '../../services/planning'
import { useAuth } from '../../contexts/AuthContext'
import { formatDateFull } from '../../utils/dates'
import type { Affectation } from '../../types'

interface MesInterventionsProps {
  chantierId: number | string
}

export default function MesInterventions({ chantierId }: MesInterventionsProps) {
  const { user } = useAuth()
  const [affectations, setAffectations] = useState<Affectation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user?.id) return

    const loadInterventions = async () => {
      setLoading(true)
      setError(null)

      try {
        // Charger les affectations pour les 12 derniers mois et les 12 prochains mois
        const today = new Date()
        const pastDate = new Date(today)
        pastDate.setMonth(pastDate.getMonth() - 12)
        const futureDate = new Date(today)
        futureDate.setMonth(futureDate.getMonth() + 12)

        const dateDebut = pastDate.toISOString().split('T')[0]
        const dateFin = futureDate.toISOString().split('T')[0]

        // Utiliser getAffectations avec les filtres utilisateur_id et chantier_id
        const allAffectations = await planningService.getAffectations({
          date_debut: dateDebut,
          date_fin: dateFin,
          utilisateur_ids: [String(user.id)],
          chantier_ids: [String(chantierId)],
        })

        // Trier par date (plus recentes en premier pour le futur, puis passees)
        const sorted = allAffectations.sort((a, b) => {
          const dateA = new Date(a.date)
          const dateB = new Date(b.date)
          return dateA.getTime() - dateB.getTime()
        })

        setAffectations(sorted)
      } catch (err) {
        console.error('Erreur chargement interventions:', err)
        setError('Impossible de charger vos interventions')
      } finally {
        setLoading(false)
      }
    }

    loadInterventions()
  }, [user?.id, chantierId])

  // Ne pas afficher si pas d'utilisateur connecte
  if (!user) return null

  // Separer interventions passees et futures
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const futureInterventions = affectations.filter((a) => new Date(a.date) >= today)
  const pastInterventions = affectations.filter((a) => new Date(a.date) < today).reverse()

  const formatTime = (time?: string) => {
    if (!time) return ''
    return time.substring(0, 5) // HH:mm
  }

  const formatInterventionTime = (affectation: Affectation) => {
    if (affectation.heure_debut && affectation.heure_fin) {
      return `${formatTime(affectation.heure_debut)} - ${formatTime(affectation.heure_fin)}`
    }
    if (affectation.heure_debut) {
      return `A partir de ${formatTime(affectation.heure_debut)}`
    }
    return 'Journee complete'
  }

  const isToday = (dateStr: string) => {
    const date = new Date(dateStr)
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    )
  }

  const InterventionItem = ({ affectation, isPast }: { affectation: Affectation; isPast: boolean }) => (
    <div
      className={`flex items-center gap-3 py-2 px-3 rounded-lg ${
        isToday(affectation.date)
          ? 'bg-primary-50 border border-primary-200'
          : isPast
            ? 'bg-gray-50 text-gray-500'
            : 'bg-white border border-gray-100'
      }`}
    >
      <Calendar className={`w-4 h-4 flex-shrink-0 ${isPast ? 'text-gray-400' : 'text-primary-500'}`} />
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${isToday(affectation.date) ? 'text-primary-700' : ''}`}>
          {isToday(affectation.date) ? "Aujourd'hui" : formatDateFull(affectation.date)}
        </p>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Clock className="w-3 h-3" />
          <span>{formatInterventionTime(affectation)}</span>
        </div>
        {affectation.note && (
          <p className="text-xs text-gray-400 mt-1 truncate">{affectation.note}</p>
        )}
      </div>
    </div>
  )

  return (
    <div className="card">
      <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Calendar className="w-5 h-5 text-primary-500" />
        Mes interventions sur ce chantier
      </h2>

      {loading ? (
        <div className="flex items-center justify-center py-4 text-gray-500">
          <Loader2 className="w-5 h-5 animate-spin mr-2" />
          Chargement...
        </div>
      ) : error ? (
        <div className="flex items-center gap-2 text-red-600 text-sm py-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      ) : affectations.length === 0 ? (
        <p className="text-gray-500 text-sm py-2">
          Vous n'avez pas d'interventions planifiees sur ce chantier.
        </p>
      ) : (
        <div className="space-y-4">
          {/* Interventions futures */}
          {futureInterventions.length > 0 && (
            <div>
              <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                A venir ({futureInterventions.length})
              </h3>
              <div className="space-y-2">
                {futureInterventions.slice(0, 5).map((a) => (
                  <InterventionItem key={a.id} affectation={a} isPast={false} />
                ))}
                {futureInterventions.length > 5 && (
                  <p className="text-xs text-gray-500 text-center py-1">
                    + {futureInterventions.length - 5} autres interventions a venir
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Interventions passees */}
          {pastInterventions.length > 0 && (
            <div>
              <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                Passees ({pastInterventions.length})
              </h3>
              <div className="space-y-2">
                {pastInterventions.slice(0, 3).map((a) => (
                  <InterventionItem key={a.id} affectation={a} isPast={true} />
                ))}
                {pastInterventions.length > 3 && (
                  <p className="text-xs text-gray-400 text-center py-1">
                    + {pastInterventions.length - 3} autres interventions passees
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
