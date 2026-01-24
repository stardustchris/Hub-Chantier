/**
 * Types pour le module Logistique (LOG-01 à LOG-18)
 */

// ============ ENUMS ============

export type TypeRessource =
  | 'levage'
  | 'terrassement'
  | 'vehicule'
  | 'outillage'
  | 'equipement'

export type StatutReservation =
  | 'en_attente'
  | 'validee'
  | 'refusee'
  | 'annulee'

// ============ RESSOURCES ============

export interface Ressource {
  id: number
  code: string
  nom: string
  description: string | null
  type_ressource: TypeRessource
  type_ressource_label: string
  photo_url: string | null
  couleur: string
  plage_horaire_debut: string
  plage_horaire_fin: string
  validation_requise: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RessourceCreateDTO {
  code: string
  nom: string
  type_ressource: TypeRessource
  description?: string | null
  photo_url?: string | null
  couleur?: string
  plage_horaire_debut?: string
  plage_horaire_fin?: string
  validation_requise?: boolean
}

export interface RessourceUpdateDTO {
  nom?: string
  type_ressource?: TypeRessource
  description?: string | null
  photo_url?: string | null
  couleur?: string
  plage_horaire_debut?: string
  plage_horaire_fin?: string
  validation_requise?: boolean
}

export interface RessourceListResponse {
  ressources: Ressource[]
  total: number
  skip: number
  limit: number
  has_next: boolean
  has_previous: boolean
}

// ============ RESERVATIONS ============

export interface Reservation {
  id: number
  ressource_id: number
  chantier_id: number
  demandeur_id: number
  valideur_id: number | null
  date_debut: string
  date_fin: string
  heure_debut: string
  heure_fin: string
  statut: StatutReservation
  statut_label: string
  statut_couleur: string
  motif_refus: string | null
  note: string | null
  validated_at: string | null
  refused_at: string | null
  cancelled_at: string | null
  created_at: string
  updated_at: string
  // Enrichissement optionnel
  ressource_nom?: string | null
  ressource_couleur?: string | null
  chantier_nom?: string | null
  demandeur_nom?: string | null
  valideur_nom?: string | null
}

export interface ReservationCreateDTO {
  ressource_id: number
  chantier_id: number
  date_debut: string // YYYY-MM-DD
  date_fin: string
  heure_debut: string // HH:MM
  heure_fin: string
  note?: string | null
}

export interface ReservationListResponse {
  reservations: Reservation[]
  total: number
  skip: number
  limit: number
  has_next: boolean
  has_previous: boolean
}

export interface ReservationSearchParams {
  ressource_id?: number
  chantier_id?: number
  demandeur_id?: number
  statut?: StatutReservation
  date_debut?: string
  date_fin?: string
  skip?: number
  limit?: number
}

// ============ PLANNING ============

export interface PlanningRessource {
  ressource: Ressource
  reservations: Reservation[]
  semaine_debut: string
  semaine_fin: string
}

// ============ CONFLITS ============

export interface ConflitReservation {
  nouvelle_reservation: ReservationCreateDTO
  reservations_en_conflit: Reservation[]
  message: string
}

export interface ConflitCheckResponse {
  has_conflict: boolean
  conflict?: ConflitReservation
}

// ============ HELPERS ============

export const TYPE_RESSOURCE_LABELS: Record<TypeRessource, string> = {
  levage: 'Engins de levage',
  terrassement: 'Engins de terrassement',
  vehicule: 'Véhicules',
  outillage: 'Gros outillage',
  equipement: 'Équipements',
}

export const TYPE_RESSOURCE_EXEMPLES: Record<TypeRessource, string[]> = {
  levage: ['Grue mobile', 'Manitou', 'Nacelle'],
  terrassement: ['Mini-pelle', 'Pelleteuse'],
  vehicule: ['Camion benne', 'Fourgon'],
  outillage: ['Bétonnière', 'Vibrateur'],
  equipement: ['Échafaudage', 'Étais', 'Banches'],
}

export const STATUT_RESERVATION_LABELS: Record<StatutReservation, string> = {
  en_attente: 'En attente',
  validee: 'Validée',
  refusee: 'Refusée',
  annulee: 'Annulée',
}

export const STATUT_RESERVATION_COULEURS: Record<StatutReservation, string> = {
  en_attente: '#F39C12', // Jaune
  validee: '#27AE60', // Vert
  refusee: '#E74C3C', // Rouge
  annulee: '#95A5A6', // Gris
}

export const STATUT_RESERVATION_EMOJIS: Record<StatutReservation, string> = {
  en_attente: '🟡',
  validee: '🟢',
  refusee: '🔴',
  annulee: '⚪',
}
