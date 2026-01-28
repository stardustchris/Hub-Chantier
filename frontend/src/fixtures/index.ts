import type { User, Chantier, Affectation, Pointage, PostMedia, PhotoFormulaire } from '../types'
import type { Ressource, Reservation, PlanningRessource } from '../types/logistique'
import type { Document, Dossier, DossierTree } from '../types/documents'
import type { Signalement } from '../types/signalements'

// ===== USERS =====
export function createMockUser(overrides: Partial<User> = {}): User {
  return {
    id: '1',
    email: 'test@example.com',
    nom: 'Dupont',
    prenom: 'Jean',
    role: 'conducteur',
    type_utilisateur: 'employe',
    couleur: '#3B82F6',
    is_active: true,
    created_at: new Date().toISOString(),
    ...overrides,
  }
}

// ===== CHANTIERS =====
export function createMockChantier(overrides: Partial<Chantier> = {}): Chantier {
  return {
    id: '1',
    code: 'CH001',
    nom: 'Chantier Test',
    adresse: '1 rue de Test',
    statut: 'en_cours',
    couleur: '#10B981',
    conducteurs: [],
    chefs: [],
    phases: [],
    created_at: new Date().toISOString(),
    ...overrides,
  }
}

// ===== RESSOURCES =====
export function createMockRessource(overrides: Partial<Ressource> = {}): Ressource {
  const defaults = {
    id: 1,
    nom: 'Grue Mobile',
    code: 'GRU001',
    categorie: 'engin_levage' as const,
    categorie_label: 'Engin de levage',
    couleur: '#E74C3C',
    heure_debut_defaut: '08:00',
    heure_fin_defaut: '17:00',
    validation_requise: true,
    actif: true,
    created_at: new Date().toISOString(),
  }
  return {
    ...defaults,
    ...overrides,
    // Ensure required fields are not undefined
    categorie_label: overrides.categorie_label ?? defaults.categorie_label,
  }
}

// ===== RESERVATIONS =====
export function createMockReservation(overrides: Partial<Reservation> = {}): Reservation {
  const defaults = {
    id: 1,
    ressource_id: 1,
    ressource_nom: 'Grue Mobile',
    ressource_code: 'GRU001',
    ressource_couleur: '#E74C3C',
    chantier_id: 1,
    chantier_nom: 'Chantier Test',
    demandeur_id: 1,
    demandeur_nom: 'Jean Dupont',
    date_reservation: new Date().toISOString().split('T')[0],
    heure_debut: '08:00',
    heure_fin: '17:00',
    statut: 'validee' as const,
    statut_label: 'Validée',
    statut_couleur: '#4CAF50',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  return {
    ...defaults,
    ...overrides,
    // Ensure required fields are not undefined
    statut_label: overrides.statut_label ?? defaults.statut_label,
  }
}

// ===== PLANNING RESSOURCE =====
export function createMockPlanningRessource(
  overrides: Partial<PlanningRessource> = {}
): PlanningRessource {
  const defaults = {
    ressource_id: 1,
    ressource_nom: 'Grue Mobile',
    ressource_code: 'GRU001',
    ressource_couleur: '#E74C3C',
    date_debut: new Date().toISOString().split('T')[0],
    date_fin: new Date().toISOString().split('T')[0],
    reservations: [],
    jours: [],
  }
  return {
    ...defaults,
    ...overrides,
    // Ensure required fields are not undefined
    ressource_nom: overrides.ressource_nom ?? defaults.ressource_nom,
    ressource_code: overrides.ressource_code ?? defaults.ressource_code,
    ressource_couleur: overrides.ressource_couleur ?? defaults.ressource_couleur,
  }
}

// ===== POINTAGES =====
export function createMockPointage(overrides: Partial<Pointage> = {}): Pointage {
  return {
    id: 1,
    utilisateur_id: 1,
    chantier_id: 1,
    date_pointage: new Date().toISOString().split('T')[0],
    heures_normales: '08:00',
    heures_supplementaires: '00:00',
    total_heures: '08:00',
    total_heures_decimal: 8.0,
    statut: 'brouillon',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    // Enrichissement (optional)
    utilisateur_nom: 'Jean Dupont',
    chantier_nom: 'Chantier Test',
    chantier_couleur: '#10B981',
    ...overrides,
  }
}

// ===== AFFECTATIONS =====
export function createMockAffectation(overrides: Partial<Affectation> = {}): Affectation {
  return {
    id: '1',
    utilisateur_id: '1',
    chantier_id: '1',
    date: new Date().toISOString().split('T')[0],
    type_affectation: 'unique',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    created_by: '1',
    // Enrichissement
    utilisateur_nom: 'Jean Dupont',
    utilisateur_couleur: '#3B82F6',
    chantier_nom: 'Chantier Test',
    ...overrides,
  }
}

// ===== DOCUMENTS =====
export function createMockDocument(overrides: Partial<Document> = {}): Document {
  return {
    id: 1,
    chantier_id: 1,
    dossier_id: 1,
    nom: 'Test Document.pdf',
    nom_original: 'Test Document.pdf',
    type_document: 'pdf',
    taille: 1024,
    taille_formatee: '1 KB',
    mime_type: 'application/pdf',
    uploaded_by: 1,
    uploaded_by_nom: 'Jean Dupont',
    uploaded_at: new Date().toISOString(),
    description: null,
    version: 1,
    icone: 'file-pdf',
    extension: 'pdf',
    niveau_acces: null,
    ...overrides,
  }
}

// ===== DOSSIERS =====
export function createMockDossier(overrides: Partial<Dossier> = {}): Dossier {
  return {
    id: 1,
    chantier_id: 1,
    nom: 'Dossier Test',
    type_dossier: 'custom',
    niveau_acces: 'compagnon',
    parent_id: null,
    ordre: 1,
    chemin_complet: '/Dossier Test',
    nombre_documents: 0,
    nombre_sous_dossiers: 0,
    created_at: new Date().toISOString(),
    ...overrides,
  }
}

// ===== DOSSIER TREE =====
export function createMockDossierTree(overrides: Partial<DossierTree> = {}): DossierTree {
  return {
    ...createMockDossier(overrides),
    children: [],
    ...overrides,
  }
}

// ===== POST MEDIA =====
export function createMockPostMedia(overrides: Partial<PostMedia> = {}): PostMedia {
  return {
    id: '1',
    type: 'image',
    url: 'https://example.com/image.jpg',
    ...overrides,
  }
}

// ===== PHOTO FORMULAIRE =====
export function createMockPhotoFormulaire(overrides: Partial<PhotoFormulaire> = {}): PhotoFormulaire {
  return {
    id: 1,
    champ_nom: 'photo_test',
    url: 'https://example.com/photo.jpg',
    nom_fichier: 'photo.jpg',
    ...overrides,
  }
}

// ===== SIGNALEMENTS =====
export function createMockSignalement(overrides: Partial<Signalement> = {}): Signalement {
  return {
    id: 1,
    chantier_id: 1,
    titre: 'Signalement Test',
    description: 'Description du signalement',
    priorite: 'moyenne',
    priorite_label: 'Moyenne',
    priorite_couleur: '#FFA500',
    statut: 'ouvert',
    statut_label: 'Ouvert',
    statut_couleur: '#3B82F6',
    cree_par: 1,
    cree_par_nom: 'Jean Dupont',
    assigne_a: null,
    assigne_a_nom: null,
    date_resolution_souhaitee: null,
    date_traitement: null,
    date_cloture: null,
    commentaire_traitement: null,
    photo_url: null,
    localisation: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    est_en_retard: false,
    temps_restant: null,
    pourcentage_temps: 0,
    nb_reponses: 0,
    nb_escalades: 0,
    ...overrides,
  }
}
