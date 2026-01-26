/**
 * Section Logistique pour la page détail chantier
 * Affiche les réservations de matériel pour ce chantier
 */

import { Link } from 'react-router-dom'
import { Truck, Calendar, Clock, ChevronRight, AlertCircle, CheckCircle } from 'lucide-react'
import { useChantierLogistique } from '../../hooks'
import type { Reservation } from '../../types/logistique'
import { STATUTS_RESERVATION } from '../../types/logistique'

interface ChantierLogistiqueSectionProps {
  chantierId: string
}

function ReservationItem({ reservation }: { reservation: Reservation }) {
  const statutInfo = STATUTS_RESERVATION[reservation.statut]
  const isEnAttente = reservation.statut === 'en_attente'

  return (
    <div
      className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
      style={{ borderLeft: `3px solid ${reservation.ressource_couleur || '#3498DB'}` }}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900 truncate">
            {reservation.ressource_nom || `Ressource ${reservation.ressource_id}`}
          </span>
          {reservation.ressource_code && (
            <span className="text-xs font-mono bg-gray-200 px-1.5 py-0.5 rounded">
              {reservation.ressource_code}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" />
            {new Date(reservation.date_reservation).toLocaleDateString('fr-FR', {
              weekday: 'short',
              day: 'numeric',
              month: 'short',
            })}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {reservation.heure_debut.substring(0, 5)} - {reservation.heure_fin.substring(0, 5)}
          </span>
        </div>
      </div>
      <div className="shrink-0">
        <span
          className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full"
          style={{ backgroundColor: statutInfo.bgColor, color: statutInfo.color }}
        >
          {isEnAttente ? (
            <AlertCircle className="w-3 h-3" />
          ) : (
            <CheckCircle className="w-3 h-3" />
          )}
          {statutInfo.label}
        </span>
      </div>
    </div>
  )
}

export default function ChantierLogistiqueSection({ chantierId }: ChantierLogistiqueSectionProps) {
  const { upcomingReservations, stats, isLoading } = useChantierLogistique(chantierId)

  if (isLoading) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-16 bg-gray-100 rounded"></div>
            <div className="h-16 bg-gray-100 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
          <Truck className="w-5 h-5 text-blue-600" />
          Logistique
        </h2>
        <Link
          to="/logistique"
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          Voir tout
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-2 bg-blue-50 rounded-lg">
          <p className="text-2xl font-bold text-blue-600">{stats.todayCount}</p>
          <p className="text-xs text-gray-500">Aujourd'hui</p>
        </div>
        <div className="text-center p-2 bg-green-50 rounded-lg">
          <p className="text-2xl font-bold text-green-600">{stats.upcomingCount}</p>
          <p className="text-xs text-gray-500">Cette semaine</p>
        </div>
        <div className="text-center p-2 bg-yellow-50 rounded-lg">
          <p className="text-2xl font-bold text-yellow-600">{stats.pendingCount}</p>
          <p className="text-xs text-gray-500">En attente</p>
        </div>
      </div>

      {/* Liste des réservations à venir */}
      {upcomingReservations.length > 0 ? (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700 mb-2">Reservations a venir</p>
          {upcomingReservations.slice(0, 4).map((reservation) => (
            <ReservationItem key={reservation.id} reservation={reservation} />
          ))}
          {upcomingReservations.length > 4 && (
            <Link
              to="/logistique"
              className="block text-center text-sm text-blue-600 hover:text-blue-700 py-2"
            >
              +{upcomingReservations.length - 4} autres reservations
            </Link>
          )}
        </div>
      ) : (
        <div className="text-center py-6 text-gray-500">
          <Truck className="w-10 h-10 mx-auto mb-2 text-gray-300" />
          <p className="text-sm">Aucune reservation prevue</p>
          <Link
            to="/logistique"
            className="text-sm text-blue-600 hover:text-blue-700 mt-2 inline-block"
          >
            Faire une demande
          </Link>
        </div>
      )}
    </div>
  )
}
