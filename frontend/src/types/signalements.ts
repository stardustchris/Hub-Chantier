/**
 * Types pour le module Signalements (SIG-01 à SIG-20)
 */

export type Priorite = 'critique' | 'haute' | 'moyenne' | 'basse';

export type StatutSignalement = 'ouvert' | 'en_cours' | 'traite' | 'cloture';

export interface Signalement {
  id: number;
  chantier_id: number;
  titre: string;
  description: string;
  priorite: Priorite;
  priorite_label: string;
  priorite_couleur: string;
  statut: StatutSignalement;
  statut_label: string;
  statut_couleur: string;
  cree_par: number;
  cree_par_nom: string | null;
  assigne_a: number | null;
  assigne_a_nom: string | null;
  date_resolution_souhaitee: string | null;
  date_traitement: string | null;
  date_cloture: string | null;
  commentaire_traitement: string | null;
  photo_url: string | null;
  localisation: string | null;
  created_at: string;
  updated_at: string;
  est_en_retard: boolean;
  temps_restant: string | null;
  pourcentage_temps: number;
  nb_reponses: number;
  nb_escalades: number;
}

export interface Reponse {
  id: number;
  signalement_id: number;
  contenu: string;
  auteur_id: number;
  auteur_nom: string | null;
  photo_url: string | null;
  created_at: string;
  updated_at: string;
  est_resolution: boolean;
}

export interface SignalementListResponse {
  signalements: Signalement[];
  total: number;
  skip: number;
  limit: number;
}

export interface ReponseListResponse {
  reponses: Reponse[];
  total: number;
  skip: number;
  limit: number;
}

export interface SignalementStatsResponse {
  total: number;
  par_statut: Record<string, number>;
  par_priorite: Record<string, number>;
  en_retard: number;
  traites_cette_semaine: number;
  temps_moyen_resolution: number | null;
  taux_resolution: number;
}

// DTOs pour création/mise à jour
export interface SignalementCreateDTO {
  chantier_id: number;
  titre: string;
  description: string;
  priorite?: Priorite;
  assigne_a?: number | null;
  date_resolution_souhaitee?: string | null;
  photo_url?: string | null;
  localisation?: string | null;
}

export interface SignalementUpdateDTO {
  titre?: string;
  description?: string;
  priorite?: Priorite;
  assigne_a?: number | null;
  date_resolution_souhaitee?: string | null;
  photo_url?: string | null;
  localisation?: string | null;
}

export interface ReponseCreateDTO {
  contenu: string;
  photo_url?: string | null;
  est_resolution?: boolean;
}

export interface ReponseUpdateDTO {
  contenu?: string;
  photo_url?: string | null;
}

export interface SignalementSearchParams {
  query?: string;
  chantier_id?: number;
  statut?: StatutSignalement;
  priorite?: Priorite;
  date_debut?: string;
  date_fin?: string;
  en_retard_only?: boolean;
  skip?: number;
  limit?: number;
}

// Constantes
export const PRIORITE_LABELS: Record<Priorite, string> = {
  critique: 'Critique (4h)',
  haute: 'Haute (24h)',
  moyenne: 'Moyenne (48h)',
  basse: 'Basse (72h)',
};

export const PRIORITE_COLORS: Record<Priorite, string> = {
  critique: 'red',
  haute: 'orange',
  moyenne: 'yellow',
  basse: 'green',
};

export const PRIORITE_BG_COLORS: Record<Priorite, string> = {
  critique: 'bg-red-100 text-red-800',
  haute: 'bg-orange-100 text-orange-800',
  moyenne: 'bg-yellow-100 text-yellow-800',
  basse: 'bg-green-100 text-green-800',
};

export const STATUT_LABELS: Record<StatutSignalement, string> = {
  ouvert: 'Ouvert',
  en_cours: 'En cours',
  traite: 'Traité',
  cloture: 'Clôturé',
};

export const STATUT_COLORS: Record<StatutSignalement, string> = {
  ouvert: 'red',
  en_cours: 'orange',
  traite: 'blue',
  cloture: 'green',
};

export const STATUT_BG_COLORS: Record<StatutSignalement, string> = {
  ouvert: 'bg-red-100 text-red-800',
  en_cours: 'bg-orange-100 text-orange-800',
  traite: 'bg-blue-100 text-blue-800',
  cloture: 'bg-green-100 text-green-800',
};

export const PRIORITE_OPTIONS: Array<{ value: Priorite; label: string }> = [
  { value: 'critique', label: 'Critique (4h)' },
  { value: 'haute', label: 'Haute (24h)' },
  { value: 'moyenne', label: 'Moyenne (48h)' },
  { value: 'basse', label: 'Basse (72h)' },
];

export const STATUT_OPTIONS: Array<{ value: StatutSignalement; label: string }> = [
  { value: 'ouvert', label: 'Ouvert' },
  { value: 'en_cours', label: 'En cours' },
  { value: 'traite', label: 'Traité' },
  { value: 'cloture', label: 'Clôturé' },
];
