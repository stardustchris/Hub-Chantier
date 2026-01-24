/**
 * Service API pour le module Logistique
 *
 * LOG-01 à LOG-18: Gestion du matériel et réservations
 */

import api from '../services/api'
import type {
  Ressource,
  RessourceCreate,
  RessourceUpdate,
  RessourceList,
  RessourceFilters,
  Reservation,
  ReservationCreate,
  ReservationUpdate,
  ReservationList,
  PlanningRessource,
} from '../types/logistique'

const BASE_URL = '/logistique'

// =============================================================================
// RESSOURCES (LOG-01, LOG-02)
// =============================================================================

/**
 * Crée une nouvelle ressource (Admin uniquement)
 * LOG-01: Référentiel matériel
 */
export const createRessource = async (data: RessourceCreate): Promise<Ressource> => {
  const response = await api.post(`${BASE_URL}/ressources`, data)
  return response.data
}

/**
 * Liste les ressources avec filtres
 */
export const listRessources = async (filters: RessourceFilters = {}): Promise<RessourceList> => {
  const params = new URLSearchParams()
  if (filters.categorie) params.append('categorie', filters.categorie)
  if (filters.actif_seulement !== undefined) params.append('actif_seulement', String(filters.actif_seulement))
  if (filters.limit) params.append('limit', String(filters.limit))
  if (filters.offset) params.append('offset', String(filters.offset))

  const response = await api.get(`${BASE_URL}/ressources?${params.toString()}`)
  return response.data
}

/**
 * Récupère une ressource par son ID
 */
export const getRessource = async (ressourceId: number): Promise<Ressource> => {
  const response = await api.get(`${BASE_URL}/ressources/${ressourceId}`)
  return response.data
}

/**
 * Met à jour une ressource (Admin uniquement)
 */
export const updateRessource = async (ressourceId: number, data: RessourceUpdate): Promise<Ressource> => {
  const response = await api.put(`${BASE_URL}/ressources/${ressourceId}`, data)
  return response.data
}

/**
 * Supprime une ressource (Admin uniquement)
 */
export const deleteRessource = async (ressourceId: number): Promise<void> => {
  await api.delete(`${BASE_URL}/ressources/${ressourceId}`)
}

/**
 * Récupère le planning d'une ressource
 * LOG-03: Planning par ressource - Vue calendrier hebdomadaire 7 jours
 * LOG-04: Navigation semaine
 */
export const getPlanningRessource = async (
  ressourceId: number,
  dateDebut: string,
  dateFin?: string
): Promise<PlanningRessource> => {
  const params = new URLSearchParams()
  params.append('date_debut', dateDebut)
  if (dateFin) params.append('date_fin', dateFin)

  const response = await api.get(`${BASE_URL}/ressources/${ressourceId}/planning?${params.toString()}`)
  return response.data
}

/**
 * Récupère l'historique des réservations d'une ressource
 * LOG-18: Historique par ressource
 */
export const getHistoriqueRessource = async (
  ressourceId: number,
  limit = 100,
  offset = 0
): Promise<ReservationList> => {
  const response = await api.get(
    `${BASE_URL}/ressources/${ressourceId}/historique?limit=${limit}&offset=${offset}`
  )
  return response.data
}

// =============================================================================
// RÉSERVATIONS (LOG-07 à LOG-18)
// =============================================================================

/**
 * Crée une nouvelle réservation
 * LOG-07: Demande de réservation
 * LOG-08: Sélection chantier obligatoire
 * LOG-09: Sélection créneau
 */
export const createReservation = async (data: ReservationCreate): Promise<Reservation> => {
  const response = await api.post(`${BASE_URL}/reservations`, data)
  return response.data
}

/**
 * Récupère une réservation par son ID
 */
export const getReservation = async (reservationId: number): Promise<Reservation> => {
  const response = await api.get(`${BASE_URL}/reservations/${reservationId}`)
  return response.data
}

/**
 * Met à jour une réservation (si en attente)
 */
export const updateReservation = async (
  reservationId: number,
  data: ReservationUpdate
): Promise<Reservation> => {
  const response = await api.put(`${BASE_URL}/reservations/${reservationId}`, data)
  return response.data
}

/**
 * Liste les réservations en attente de validation
 * LOG-11: Workflow validation
 */
export const listReservationsEnAttente = async (
  limit = 100,
  offset = 0
): Promise<ReservationList> => {
  const response = await api.get(
    `${BASE_URL}/reservations/en-attente?limit=${limit}&offset=${offset}`
  )
  return response.data
}

/**
 * Valide une réservation
 * LOG-11: Workflow validation - Chef valide → Confirmée
 */
export const validerReservation = async (reservationId: number): Promise<Reservation> => {
  const response = await api.post(`${BASE_URL}/reservations/${reservationId}/valider`)
  return response.data
}

/**
 * Refuse une réservation
 * LOG-16: Motif de refus
 */
export const refuserReservation = async (
  reservationId: number,
  motif?: string
): Promise<Reservation> => {
  const response = await api.post(`${BASE_URL}/reservations/${reservationId}/refuser`, { motif })
  return response.data
}

/**
 * Annule une réservation
 */
export const annulerReservation = async (reservationId: number): Promise<Reservation> => {
  const response = await api.post(`${BASE_URL}/reservations/${reservationId}/annuler`)
  return response.data
}

// =============================================================================
// UTILITAIRES
// =============================================================================

/**
 * Formate une plage horaire pour l'affichage
 */
export const formatPlageHoraire = (heureDebut: string, heureFin: string): string => {
  const formatHeure = (h: string) => h.substring(0, 5)
  return `${formatHeure(heureDebut)} - ${formatHeure(heureFin)}`
}

/**
 * Calcule le lundi de la semaine d'une date
 */
export const getLundiSemaine = (date: Date): Date => {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  return new Date(d.setDate(diff))
}

/**
 * Génère les jours d'une semaine
 */
export const getJoursSemaine = (lundiDate: Date): Date[] => {
  const jours: Date[] = []
  for (let i = 0; i < 7; i++) {
    const jour = new Date(lundiDate)
    jour.setDate(lundiDate.getDate() + i)
    jours.push(jour)
  }
  return jours
}

/**
 * Formate une date au format ISO (YYYY-MM-DD)
 */
export const formatDateISO = (date: Date): string => {
  return date.toISOString().split('T')[0]
}

/**
 * Vérifie si deux plages horaires se chevauchent
 * LOG-17: Conflit de réservation
 */
export const plagesHorairesSeChevauchent = (
  debut1: string,
  fin1: string,
  debut2: string,
  fin2: string
): boolean => {
  return debut1 < fin2 && fin1 > debut2
}

// Export par défaut du service
export default {
  // Ressources
  createRessource,
  listRessources,
  getRessource,
  updateRessource,
  deleteRessource,
  getPlanningRessource,
  getHistoriqueRessource,
  // Réservations
  createReservation,
  getReservation,
  updateReservation,
  listReservationsEnAttente,
  validerReservation,
  refuserReservation,
  annulerReservation,
  // Utilitaires
  formatPlageHoraire,
  getLundiSemaine,
  getJoursSemaine,
  formatDateISO,
  plagesHorairesSeChevauchent,
}
