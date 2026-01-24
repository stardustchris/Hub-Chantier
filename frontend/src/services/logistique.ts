/**
 * API client pour le module Logistique (LOG-01 à LOG-18)
 */

import api from './api'
import type {
  Ressource,
  RessourceCreateDTO,
  RessourceUpdateDTO,
  RessourceListResponse,
  Reservation,
  ReservationCreateDTO,
  ReservationListResponse,
  ReservationSearchParams,
  PlanningRessource,
  ConflitCheckResponse,
  TypeRessource,
  StatutReservation,
} from '../types/logistique'

// ============ RESSOURCES (LOG-01, LOG-02) ============

/**
 * Crée une nouvelle ressource (LOG-01) - Admin uniquement
 */
export const createRessource = async (data: RessourceCreateDTO): Promise<Ressource> => {
  const response = await api.post('/api/logistique/ressources', data)
  return response.data
}

/**
 * Récupère une ressource par son ID (LOG-02)
 */
export const getRessource = async (ressourceId: number): Promise<Ressource> => {
  const response = await api.get(`/api/logistique/ressources/${ressourceId}`)
  return response.data
}

/**
 * Liste les ressources
 */
export const listRessources = async (
  type_ressource?: TypeRessource,
  is_active: boolean = true,
  skip = 0,
  limit = 50
): Promise<RessourceListResponse> => {
  const params: Record<string, string | number | boolean> = { skip, limit, is_active }
  if (type_ressource) params.type_ressource = type_ressource

  const response = await api.get('/api/logistique/ressources', { params })
  return response.data
}

/**
 * Met à jour une ressource - Admin uniquement
 */
export const updateRessource = async (
  ressourceId: number,
  data: RessourceUpdateDTO
): Promise<Ressource> => {
  const response = await api.put(`/api/logistique/ressources/${ressourceId}`, data)
  return response.data
}

/**
 * Supprime une ressource (soft delete) - Admin uniquement
 */
export const deleteRessource = async (ressourceId: number): Promise<void> => {
  await api.delete(`/api/logistique/ressources/${ressourceId}`)
}

/**
 * Active ou désactive une ressource - Admin uniquement
 */
export const activateRessource = async (
  ressourceId: number,
  is_active: boolean
): Promise<Ressource> => {
  const response = await api.post(`/api/logistique/ressources/${ressourceId}/activate`, {
    is_active,
  })
  return response.data
}

/**
 * Récupère le planning d'une ressource pour une semaine (LOG-03)
 */
export const getRessourcePlanning = async (
  ressourceId: number,
  semaine_debut: string // YYYY-MM-DD (lundi)
): Promise<PlanningRessource> => {
  const response = await api.get(`/api/logistique/ressources/${ressourceId}/planning`, {
    params: { semaine_debut },
  })
  return response.data
}

// ============ RESERVATIONS (LOG-07 à LOG-18) ============

/**
 * Crée une nouvelle réservation (LOG-07)
 */
export const createReservation = async (data: ReservationCreateDTO): Promise<Reservation> => {
  const response = await api.post('/api/logistique/reservations', data)
  return response.data
}

/**
 * Récupère une réservation par son ID
 */
export const getReservation = async (reservationId: number): Promise<Reservation> => {
  const response = await api.get(`/api/logistique/reservations/${reservationId}`)
  return response.data
}

/**
 * Liste les réservations avec filtres
 */
export const listReservations = async (
  params: ReservationSearchParams = {}
): Promise<ReservationListResponse> => {
  const response = await api.get('/api/logistique/reservations', { params })
  return response.data
}

/**
 * Liste les réservations en attente de validation
 */
export const listPendingReservations = async (
  ressource_id?: number,
  skip = 0,
  limit = 50
): Promise<ReservationListResponse> => {
  const params: Record<string, number> = { skip, limit }
  if (ressource_id) params.ressource_id = ressource_id

  const response = await api.get('/api/logistique/reservations/pending', { params })
  return response.data
}

/**
 * Valide une réservation (LOG-11) - Chef/Conducteur uniquement
 */
export const validateReservation = async (reservationId: number): Promise<Reservation> => {
  const response = await api.post(`/api/logistique/reservations/${reservationId}/validate`)
  return response.data
}

/**
 * Refuse une réservation avec motif optionnel (LOG-11, LOG-16)
 */
export const refuseReservation = async (
  reservationId: number,
  motif?: string
): Promise<Reservation> => {
  const response = await api.post(`/api/logistique/reservations/${reservationId}/refuse`, {
    motif,
  })
  return response.data
}

/**
 * Annule une réservation (par le demandeur uniquement)
 */
export const cancelReservation = async (reservationId: number): Promise<Reservation> => {
  const response = await api.post(`/api/logistique/reservations/${reservationId}/cancel`)
  return response.data
}

/**
 * Vérifie les conflits avant création (LOG-17)
 */
export const checkReservationConflits = async (
  data: ReservationCreateDTO
): Promise<ConflitCheckResponse> => {
  const response = await api.post('/api/logistique/reservations/check-conflits', data)
  return response.data
}

// ============ HELPERS ============

/**
 * Récupère les réservations d'un chantier
 */
export const listReservationsByChantier = async (
  chantierId: number,
  statut?: StatutReservation,
  skip = 0,
  limit = 50
): Promise<ReservationListResponse> => {
  return listReservations({
    chantier_id: chantierId,
    statut,
    skip,
    limit,
  })
}

/**
 * Récupère les réservations d'une ressource
 */
export const listReservationsByRessource = async (
  ressourceId: number,
  date_debut?: string,
  date_fin?: string,
  skip = 0,
  limit = 50
): Promise<ReservationListResponse> => {
  return listReservations({
    ressource_id: ressourceId,
    date_debut,
    date_fin,
    skip,
    limit,
  })
}
