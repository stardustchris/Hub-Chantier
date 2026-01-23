/**
 * API client pour le module Signalements (SIG-01 à SIG-20)
 */

import api from '../services/api';
import type {
  Signalement,
  Reponse,
  SignalementListResponse,
  ReponseListResponse,
  SignalementStatsResponse,
  SignalementCreateDTO,
  SignalementUpdateDTO,
  ReponseCreateDTO,
  ReponseUpdateDTO,
  SignalementSearchParams,
  Priorite,
  StatutSignalement,
} from '../types/signalements';

// ============ SIGNALEMENTS ============

/**
 * Crée un nouveau signalement (SIG-01)
 */
export const createSignalement = async (data: SignalementCreateDTO): Promise<Signalement> => {
  const response = await api.post('/signalements', data);
  return response.data;
};

/**
 * Récupère un signalement par son ID (SIG-02)
 */
export const getSignalement = async (signalementId: number): Promise<Signalement> => {
  const response = await api.get(`/signalements/${signalementId}`);
  return response.data;
};

/**
 * Liste les signalements d'un chantier (SIG-03)
 */
export const listSignalementsByChantier = async (
  chantierId: number,
  skip = 0,
  limit = 100,
  statut?: StatutSignalement,
  priorite?: Priorite
): Promise<SignalementListResponse> => {
  const params: Record<string, string | number> = { skip, limit };
  if (statut) params.statut = statut;
  if (priorite) params.priorite = priorite;

  const response = await api.get(`/signalements/chantier/${chantierId}`, { params });
  return response.data;
};

/**
 * Recherche des signalements avec filtres (SIG-10, SIG-19, SIG-20)
 */
export const searchSignalements = async (
  params: SignalementSearchParams
): Promise<SignalementListResponse> => {
  const queryParams: Record<string, string | number | boolean> = {
    skip: params.skip || 0,
    limit: params.limit || 100,
  };

  if (params.query) queryParams.query = params.query;
  if (params.chantier_id) queryParams.chantier_id = params.chantier_id;
  if (params.statut) queryParams.statut = params.statut;
  if (params.priorite) queryParams.priorite = params.priorite;
  if (params.date_debut) queryParams.date_debut = params.date_debut;
  if (params.date_fin) queryParams.date_fin = params.date_fin;
  if (params.en_retard_only) queryParams.en_retard_only = params.en_retard_only;

  const response = await api.get('/signalements', { params: queryParams });
  return response.data;
};

/**
 * Met à jour un signalement (SIG-04)
 */
export const updateSignalement = async (
  signalementId: number,
  data: SignalementUpdateDTO
): Promise<Signalement> => {
  const response = await api.put(`/signalements/${signalementId}`, data);
  return response.data;
};

/**
 * Supprime un signalement (SIG-05)
 */
export const deleteSignalement = async (signalementId: number): Promise<void> => {
  await api.delete(`/signalements/${signalementId}`);
};

/**
 * Assigne un signalement à un utilisateur
 */
export const assignerSignalement = async (
  signalementId: number,
  assigneA: number
): Promise<Signalement> => {
  const response = await api.post(`/signalements/${signalementId}/assigner`, null, {
    params: { assigne_a: assigneA },
  });
  return response.data;
};

/**
 * Marque un signalement comme traité (SIG-08)
 */
export const marquerTraite = async (
  signalementId: number,
  commentaire: string
): Promise<Signalement> => {
  const response = await api.post(`/signalements/${signalementId}/traiter`, {
    commentaire,
  });
  return response.data;
};

/**
 * Clôture un signalement (SIG-09)
 */
export const cloturerSignalement = async (signalementId: number): Promise<Signalement> => {
  const response = await api.post(`/signalements/${signalementId}/cloturer`);
  return response.data;
};

/**
 * Réouvre un signalement clôturé
 */
export const reouvrirSignalement = async (signalementId: number): Promise<Signalement> => {
  const response = await api.post(`/signalements/${signalementId}/reouvrir`);
  return response.data;
};

// ============ STATISTIQUES ============

/**
 * Récupère les statistiques des signalements (SIG-18)
 */
export const getStatistiques = async (
  chantierId?: number,
  dateDebut?: string,
  dateFin?: string
): Promise<SignalementStatsResponse> => {
  const params: Record<string, string | number> = {};
  if (chantierId) params.chantier_id = chantierId;
  if (dateDebut) params.date_debut = dateDebut;
  if (dateFin) params.date_fin = dateFin;

  const response = await api.get('/signalements/stats/global', { params });
  return response.data;
};

/**
 * Récupère les signalements en retard (SIG-16)
 */
export const getSignalementsEnRetard = async (
  chantierId?: number,
  skip = 0,
  limit = 100
): Promise<SignalementListResponse> => {
  const params: Record<string, string | number> = { skip, limit };
  if (chantierId) params.chantier_id = chantierId;

  const response = await api.get('/signalements/alertes/en-retard', { params });
  return response.data;
};

// ============ REPONSES ============

/**
 * Ajoute une réponse à un signalement (SIG-07)
 */
export const createReponse = async (
  signalementId: number,
  data: ReponseCreateDTO
): Promise<Reponse> => {
  const response = await api.post(`/signalements/${signalementId}/reponses`, data);
  return response.data;
};

/**
 * Liste les réponses d'un signalement
 */
export const listReponses = async (
  signalementId: number,
  skip = 0,
  limit = 100
): Promise<ReponseListResponse> => {
  const response = await api.get(`/signalements/${signalementId}/reponses`, {
    params: { skip, limit },
  });
  return response.data;
};

/**
 * Met à jour une réponse
 */
export const updateReponse = async (
  reponseId: number,
  data: ReponseUpdateDTO
): Promise<Reponse> => {
  const response = await api.put(`/signalements/reponses/${reponseId}`, data);
  return response.data;
};

/**
 * Supprime une réponse
 */
export const deleteReponse = async (reponseId: number): Promise<void> => {
  await api.delete(`/signalements/reponses/${reponseId}`);
};

// ============ HELPERS ============

/**
 * Retourne l'icône selon la priorité
 */
export const getPrioriteIcon = (priorite: Priorite): string => {
  const icons: Record<Priorite, string> = {
    critique: '🔴',
    haute: '🟠',
    moyenne: '🟡',
    basse: '🟢',
  };
  return icons[priorite] || '⚪';
};

/**
 * Retourne l'icône selon le statut
 */
export const getStatutIcon = (statut: StatutSignalement): string => {
  const icons: Record<StatutSignalement, string> = {
    ouvert: '⚠️',
    en_cours: '🔄',
    traite: '✅',
    cloture: '✔️',
  };
  return icons[statut] || '❓';
};

/**
 * Formate le temps restant
 */
export const formatTempsRestant = (tempsRestant: string | null): string => {
  if (!tempsRestant) return '-';
  return tempsRestant;
};

/**
 * Détermine si un signalement est en alerte
 */
export const isSignalementEnAlerte = (signalement: Signalement): boolean => {
  return signalement.est_en_retard || signalement.pourcentage_temps >= 50;
};
