/**
 * Types pour le module Logistique
 *
 * LOG-01 à LOG-18: Gestion du matériel et réservations
 */

// ===== CATÉGORIES DE RESSOURCES (LOG-01) =====
export type CategorieRessource =
  | 'engin_levage'
  | 'engin_terrassement'
  | 'vehicule'
  | 'gros_outillage'
  | 'equipement'

export const CATEGORIES_RESSOURCES: Record<CategorieRessource, {
  label: string
  exemples: string[]
  validationRequise: boolean
  color: string
}> = {
  engin_levage: {
    label: 'Engin de levage',
    exemples: ['Grue mobile', 'Manitou', 'Nacelle', 'Chariot élévateur'],
    validationRequise: true,
    color: '#E74C3C',
  },
  engin_terrassement: {
    label: 'Engin de terrassement',
    exemples: ['Mini-pelle', 'Pelleteuse', 'Compacteur', 'Dumper'],
    validationRequise: true,
    color: '#E67E22',
  },
  vehicule: {
    label: 'Véhicule',
    exemples: ['Camion benne', 'Fourgon', 'Véhicule utilitaire'],
    validationRequise: false,
    color: '#3498DB',
  },
  gros_outillage: {
    label: 'Gros outillage',
    exemples: ['Bétonnière', 'Vibrateur', 'Pompe à béton'],
    validationRequise: false,
    color: '#9B59B6',
  },
  equipement: {
    label: 'Équipement',
    exemples: ['Échafaudage', 'Étais', 'Banches', 'Coffrages'],
    validationRequise: true,
    color: '#27AE60',
  },
}

// ===== STATUTS DE RÉSERVATION (LOG-11, LOG-12) =====
export type StatutReservation =
  | 'en_attente'
  | 'validee'
  | 'refusee'
  | 'annulee'

export const STATUTS_RESERVATION: Record<StatutReservation, {
  label: string
  emoji: string
  color: string
  bgColor: string
}> = {
  en_attente: {
    label: 'En attente',
    emoji: '🟡',
    color: '#FFC107',
    bgColor: '#FFF8E1',
  },
  validee: {
    label: 'Validée',
    emoji: '🟢',
    color: '#4CAF50',
    bgColor: '#E8F5E9',
  },
  refusee: {
    label: 'Refusée',
    emoji: '🔴',
    color: '#F44336',
    bgColor: '#FFEBEE',
  },
  annulee: {
    label: 'Annulée',
    emoji: '⚫',
    color: '#9E9E9E',
    bgColor: '#F5F5F5',
  },
}

// ===== RESSOURCES (LOG-01, LOG-02) =====
export interface Ressource {
  id: number
  nom: string
  code: string
  categorie: CategorieRessource
  categorie_label: string
  photo_url?: string
  couleur: string
  heure_debut_defaut: string
  heure_fin_defaut: string
  validation_requise: boolean
  actif: boolean
  description?: string
  created_at?: string
  updated_at?: string
  created_by?: number
}

export interface RessourceCreate {
  nom: string
  code: string
  categorie: CategorieRessource
  photo_url?: string
  couleur?: string
  heure_debut_defaut?: string
  heure_fin_defaut?: string
  validation_requise?: boolean
  description?: string
}

export interface RessourceUpdate {
  nom?: string
  code?: string
  categorie?: CategorieRessource
  photo_url?: string
  couleur?: string
  heure_debut_defaut?: string
  heure_fin_defaut?: string
  validation_requise?: boolean
  actif?: boolean
  description?: string
}

export interface RessourceList {
  items: Ressource[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

// ===== RÉSERVATIONS (LOG-07 à LOG-18) =====
export interface Reservation {
  id: number
  ressource_id: number
  ressource_nom?: string
  ressource_code?: string
  ressource_couleur?: string
  chantier_id: number
  chantier_nom?: string
  demandeur_id: number
  demandeur_nom?: string
  date_reservation: string
  heure_debut: string
  heure_fin: string
  statut: StatutReservation
  statut_label: string
  statut_couleur: string
  motif_refus?: string
  commentaire?: string
  valideur_id?: number
  valideur_nom?: string
  validated_at?: string
  created_at?: string
  updated_at?: string
}

export interface ReservationCreate {
  ressource_id: number
  chantier_id: number
  date_reservation: string
  heure_debut: string
  heure_fin: string
  commentaire?: string
}

export interface ReservationUpdate {
  date_reservation?: string
  heure_debut?: string
  heure_fin?: string
  commentaire?: string
}

export interface ReservationList {
  items: Reservation[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

// ===== PLANNING (LOG-03, LOG-04) =====
export interface PlanningRessource {
  ressource_id: number
  ressource_nom: string
  ressource_code: string
  ressource_couleur: string
  date_debut: string
  date_fin: string
  reservations: Reservation[]
  jours: string[]
}

// ===== FILTRES =====
export interface ReservationFilters {
  ressource_id?: number
  chantier_id?: number
  demandeur_id?: number
  date_debut?: string
  date_fin?: string
  statuts?: StatutReservation[]
  limit?: number
  offset?: number
}

export interface RessourceFilters {
  categorie?: CategorieRessource
  actif_seulement?: boolean
  limit?: number
  offset?: number
}
