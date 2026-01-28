import type { User, Chantier, Affectation, Pointage, PostMedia, PhotoFormulaire } from '../types'
import type { Ressource, Reservation, PlanningRessource } from '../types/logistique'
import type { Document, Dossier, DossierTree } from '../types/documents'

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
    phases: [],
    created_at: new Date().toISOString(),
    ...overrides,
  }
}

// ===== RESSOURCES =====
export function createMockRessource(overrides: Partial<Ressource> = {}): Ressource {
  return {
    id: 1,
    nom: 'Grue Mobile',
    code: 'GRU001',
    categorie: 'engin_levage',
    categorie_label: 'Engin de levage',
    couleur: '#E74C3C',
    heure_debut_defaut: '08:00',
    heure_fin_defaut: '17:00',
    validation_requise: true,
    actif: true,
    created_at: new Date().toISOString(),
    ...overrides,
  }
}

// ===== RESERVATIONS =====
export function createMockReservation(overrides: Partial<Reservation> = {}): Reservation {
  return {
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
    statut: 'validee',
    statut_label: 'Validée',
    statut_couleur: '#4CAF50',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  }
}

// ===== PLANNING RESSOURCE =====
export function createMockPlanningRessource(
  overrides: Partial<PlanningRessource> = {}
): PlanningRessource {
  return {
    ressource_id: 1,
    ressource_nom: 'Grue Mobile',
    ressource_code: 'GRU001',
    ressource_couleur: '#E74C3C',
    date_debut: new Date().toISOString().split('T')[0],
    date_fin: new Date().toISOString().split('T')[0],
    reservations: [],
    jours: [],
    ...overrides,
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
    statut: 'en_attente',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    // Enrichissement
    utilisateur_nom: 'Jean Dupont',
    chantier_nom: 'Chantier Test',
    chantier_couleur: '#10B981',
    statut_label: 'En attente',
    statut_couleur: '#FFC107',
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
    type_document: 'plan',
    taille: 1024,
    taille_formatee: '1 KB',
    mime_type: 'application/pdf',
    uploaded_by: 1,
    uploaded_by_nom: 'Jean Dupont',
    uploaded_at: new Date().toISOString(),
    description: null,
    version: 1,
    icone: 'file-text',
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
    type_dossier: 'dossier_chantier',
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
