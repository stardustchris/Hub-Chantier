/**
 * Service de données mock pour le module Logistique
 * Génère et persiste des données de démonstration
 * Les données sont stockées en sessionStorage pour la session courante
 */

import { RessourceFactory, ReservationFactory } from '../mocks/logistiqueFactory'
import type { Ressource, Reservation, ReservationList, RessourceList } from '../types/logistique'
import { STATUTS_RESERVATION } from '../types/logistique'

const STORAGE_KEY_RESSOURCES = 'logistique_mock_ressources'
const STORAGE_KEY_RESERVATIONS = 'logistique_mock_reservations'
const STORAGE_KEY_INITIALIZED = 'logistique_mock_initialized'

/** Noms de chantiers pour enrichir les réservations */
const CHANTIER_NAMES: Record<number, string> = {
  1: 'Résidence Les Jardins',
  2: 'Centre Commercial Riviera',
  3: 'École Jean Jaurès',
  4: 'Villa Moderne Duplex',
  5: 'Immeuble Horizon',
  6: 'Parking Souterrain Centre',
  7: 'Entrepôt Logistique Sud',
  8: 'Maison Individuelle Colline',
}

/** Noms d'utilisateurs pour enrichir les réservations */
const USER_NAMES: Record<number, string> = {
  1: 'Admin Greg',
  2: 'Pierre Martin',
  3: 'Jean Dupont',
  4: 'Marie Bernard',
  5: 'Paul Durand',
  10: 'Sophie Lambert',
  11: 'Marc Petit',
  12: 'Julie Moreau',
  13: 'Thomas Garcia',
  14: 'Camille Roux',
  15: 'Nicolas Fournier',
}

/**
 * Initialise les données mock si pas encore fait
 */
export function initializeMockData(): void {
  if (sessionStorage.getItem(STORAGE_KEY_INITIALIZED)) {
    return
  }

  RessourceFactory.resetCounter()
  ReservationFactory.resetCounter()

  // Créer les ressources (une par catégorie + quelques extras)
  const ressources: Ressource[] = [
    ...RessourceFactory.createOnePerCategory(),
    RessourceFactory.create({ categorie: 'engin_levage' }),
    RessourceFactory.create({ categorie: 'vehicule' }),
    RessourceFactory.create({ categorie: 'gros_outillage' }),
  ]

  // Créer les réservations avec des données enrichies
  const reservations: Reservation[] = []
  const today = new Date()

  for (const ressource of ressources) {
    // Planning de la semaine courante
    const weekReservations = ReservationFactory.createWeekPlanning(ressource.id, today, 1)

    // Enrichir avec les infos
    weekReservations.forEach((r) => {
      r.ressource_nom = ressource.nom
      r.ressource_code = ressource.code
      r.ressource_couleur = ressource.couleur
      r.chantier_nom = CHANTIER_NAMES[r.chantier_id] || `Chantier ${r.chantier_id}`
      r.demandeur_nom = USER_NAMES[r.demandeur_id] || `Utilisateur ${r.demandeur_id}`
      if (r.valideur_id) {
        r.valideur_nom = USER_NAMES[r.valideur_id] || `Valideur ${r.valideur_id}`
      }
    })

    reservations.push(...weekReservations)

    // Ajouter quelques réservations pour la semaine prochaine
    const nextWeek = new Date(today)
    nextWeek.setDate(today.getDate() + 7)
    const nextWeekReservations = ReservationFactory.createBatch(2, {
      ressource_id: ressource.id,
      ressource_nom: ressource.nom,
      ressource_code: ressource.code,
      ressource_couleur: ressource.couleur,
    })
    nextWeekReservations.forEach((r) => {
      r.chantier_nom = CHANTIER_NAMES[r.chantier_id] || `Chantier ${r.chantier_id}`
      r.demandeur_nom = USER_NAMES[r.demandeur_id] || `Utilisateur ${r.demandeur_id}`
      if (r.valideur_id) {
        r.valideur_nom = USER_NAMES[r.valideur_id] || `Valideur ${r.valideur_id}`
      }
    })
    reservations.push(...nextWeekReservations)
  }

  // Sauvegarder en sessionStorage
  sessionStorage.setItem(STORAGE_KEY_RESSOURCES, JSON.stringify(ressources))
  sessionStorage.setItem(STORAGE_KEY_RESERVATIONS, JSON.stringify(reservations))
  sessionStorage.setItem(STORAGE_KEY_INITIALIZED, 'true')
}

/**
 * Récupère toutes les ressources mock
 */
export function getMockRessources(): Ressource[] {
  initializeMockData()
  const data = sessionStorage.getItem(STORAGE_KEY_RESSOURCES)
  return data ? JSON.parse(data) : []
}

/**
 * Récupère toutes les réservations mock
 */
export function getMockReservations(): Reservation[] {
  initializeMockData()
  const data = sessionStorage.getItem(STORAGE_KEY_RESERVATIONS)
  return data ? JSON.parse(data) : []
}

/**
 * Récupère les réservations pour un chantier donné
 */
export function getReservationsByChantier(chantierId: number): Reservation[] {
  const reservations = getMockReservations()
  return reservations.filter((r) => r.chantier_id === chantierId)
}

/**
 * Récupère les réservations actives (validée ou en attente) pour un chantier
 */
export function getActiveReservationsByChantier(chantierId: number): Reservation[] {
  const reservations = getReservationsByChantier(chantierId)
  return reservations.filter((r) => r.statut === 'validee' || r.statut === 'en_attente')
}

/**
 * Récupère les réservations pour aujourd'hui sur un chantier
 */
export function getTodayReservationsByChantier(chantierId: number): Reservation[] {
  const today = new Date().toISOString().split('T')[0]
  const reservations = getReservationsByChantier(chantierId)
  return reservations.filter(
    (r) => r.date_reservation === today && (r.statut === 'validee' || r.statut === 'en_attente')
  )
}

/**
 * Récupère les réservations à venir sur un chantier (7 prochains jours)
 */
export function getUpcomingReservationsByChantier(chantierId: number): Reservation[] {
  const today = new Date()
  const weekFromNow = new Date(today)
  weekFromNow.setDate(today.getDate() + 7)

  const todayStr = today.toISOString().split('T')[0]
  const weekFromNowStr = weekFromNow.toISOString().split('T')[0]

  const reservations = getReservationsByChantier(chantierId)
  return reservations.filter(
    (r) =>
      r.date_reservation >= todayStr &&
      r.date_reservation <= weekFromNowStr &&
      (r.statut === 'validee' || r.statut === 'en_attente')
  )
}

/**
 * Service mock pour les listes paginées de ressources
 */
export function listMockRessources(
  categorie?: string,
  actifSeulement = true,
  limit = 100,
  offset = 0
): RessourceList {
  let ressources = getMockRessources()

  if (categorie) {
    ressources = ressources.filter((r) => r.categorie === categorie)
  }
  if (actifSeulement) {
    ressources = ressources.filter((r) => r.actif)
  }

  const total = ressources.length
  const items = ressources.slice(offset, offset + limit)

  return {
    items,
    total,
    limit,
    offset,
    has_more: offset + items.length < total,
  }
}

/**
 * Service mock pour les listes paginées de réservations par chantier
 */
export function listMockReservationsByChantier(
  chantierId: number,
  limit = 100,
  offset = 0
): ReservationList {
  const reservations = getReservationsByChantier(chantierId)
  const total = reservations.length
  const items = reservations.slice(offset, offset + limit)

  return {
    items,
    total,
    limit,
    offset,
    has_more: offset + items.length < total,
  }
}

/**
 * Réinitialise les données mock (pour les tests)
 */
export function resetMockData(): void {
  sessionStorage.removeItem(STORAGE_KEY_RESSOURCES)
  sessionStorage.removeItem(STORAGE_KEY_RESERVATIONS)
  sessionStorage.removeItem(STORAGE_KEY_INITIALIZED)
}

/**
 * Ajoute une réservation mock (pour les tests)
 */
export function addMockReservation(reservation: Reservation): void {
  const reservations = getMockReservations()
  reservations.push(reservation)
  sessionStorage.setItem(STORAGE_KEY_RESERVATIONS, JSON.stringify(reservations))
}

/**
 * Met à jour le statut d'une réservation mock
 */
export function updateMockReservationStatus(
  reservationId: number,
  statut: 'validee' | 'refusee' | 'annulee',
  valideurId?: number,
  motifRefus?: string
): Reservation | null {
  const reservations = getMockReservations()
  const index = reservations.findIndex((r) => r.id === reservationId)

  if (index === -1) return null

  const reservation = reservations[index]
  const statutInfo = STATUTS_RESERVATION[statut]

  reservation.statut = statut
  reservation.statut_label = statutInfo.label
  reservation.statut_couleur = statutInfo.color
  reservation.updated_at = new Date().toISOString()

  if (valideurId) {
    reservation.valideur_id = valideurId
    reservation.valideur_nom = USER_NAMES[valideurId] || `Valideur ${valideurId}`
    reservation.validated_at = new Date().toISOString()
  }

  if (motifRefus) {
    reservation.motif_refus = motifRefus
  }

  sessionStorage.setItem(STORAGE_KEY_RESERVATIONS, JSON.stringify(reservations))
  return reservation
}

export default {
  initializeMockData,
  getMockRessources,
  getMockReservations,
  getReservationsByChantier,
  getActiveReservationsByChantier,
  getTodayReservationsByChantier,
  getUpcomingReservationsByChantier,
  listMockRessources,
  listMockReservationsByChantier,
  resetMockData,
  addMockReservation,
  updateMockReservationStatus,
}
