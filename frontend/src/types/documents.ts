/**
 * Types pour le module Documents (GED)
 */

export type NiveauAcces = 'compagnon' | 'chef_chantier' | 'conducteur' | 'admin';

export type TypeDocument = 'pdf' | 'image' | 'excel' | 'word' | 'video' | 'autre';

export type TypeDossier =
  | '01_plans'
  | '02_administratif'
  | '03_securite'
  | '04_qualite'
  | '05_photos'
  | '06_comptes_rendus'
  | '07_livraisons'
  | 'custom';

export type TypeAutorisation = 'lecture' | 'ecriture' | 'admin';

export interface Dossier {
  id: number;
  chantier_id: number;
  nom: string;
  type_dossier: TypeDossier;
  niveau_acces: NiveauAcces;
  parent_id: number | null;
  ordre: number;
  chemin_complet: string;
  nombre_documents: number;
  nombre_sous_dossiers: number;
  created_at: string;
}

export interface DossierTree extends Dossier {
  children: DossierTree[];
}

export interface Document {
  id: number;
  chantier_id: number;
  dossier_id: number;
  nom: string;
  nom_original: string;
  type_document: TypeDocument;
  taille: number;
  taille_formatee: string;
  mime_type: string;
  uploaded_by: number;
  uploaded_by_nom: string | null;
  uploaded_at: string;
  description: string | null;
  version: number;
  icone: string;
  extension: string;
  niveau_acces: NiveauAcces | null;
}

export interface Autorisation {
  id: number;
  user_id: number;
  user_nom: string | null;
  type_autorisation: TypeAutorisation;
  dossier_id: number | null;
  document_id: number | null;
  cible_nom: string | null;
  accorde_par: number;
  accorde_par_nom: string | null;
  created_at: string;
  expire_at: string | null;
  est_valide: boolean;
}

export interface Arborescence {
  chantier_id: number;
  dossiers: DossierTree[];
  total_documents: number;
  total_taille: number;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  skip: number;
  limit: number;
}

export interface AutorisationListResponse {
  autorisations: Autorisation[];
  total: number;
}

// DTOs pour création/mise à jour
export interface DossierCreateDTO {
  chantier_id: number;
  nom: string;
  type_dossier?: TypeDossier;
  niveau_acces?: NiveauAcces;
  parent_id?: number | null;
}

export interface DossierUpdateDTO {
  nom?: string;
  niveau_acces?: NiveauAcces;
  parent_id?: number | null;
}

export interface DocumentUpdateDTO {
  nom?: string;
  description?: string;
  dossier_id?: number;
  niveau_acces?: NiveauAcces | null;
}

export interface AutorisationCreateDTO {
  user_id: number;
  type_autorisation: TypeAutorisation;
  dossier_id?: number;
  document_id?: number;
  expire_at?: string;
}

// Constantes
export const NIVEAU_ACCES_LABELS: Record<NiveauAcces, string> = {
  compagnon: 'Tous les utilisateurs',
  chef_chantier: 'Chefs + Conducteurs de travaux + Admin',
  conducteur: 'Conducteurs de travaux + Admin',
  admin: 'Administrateurs uniquement',
};

export const TYPE_DOCUMENT_LABELS: Record<TypeDocument, string> = {
  pdf: 'PDF',
  image: 'Image',
  excel: 'Excel',
  word: 'Word',
  video: 'Vidéo',
  autre: 'Autre',
};

export const TYPE_DOCUMENT_ICONS: Record<TypeDocument, string> = {
  pdf: 'file-pdf',
  image: 'file-image',
  excel: 'file-excel',
  word: 'file-word',
  video: 'file-video',
  autre: 'file',
};

export const TYPE_DOSSIER_LABELS: Record<TypeDossier, string> = {
  '01_plans': 'Plans',
  '02_administratif': 'Documents administratifs',
  '03_securite': 'Sécurité',
  '04_qualite': 'Qualité',
  '05_photos': 'Photos',
  '06_comptes_rendus': 'Comptes-rendus',
  '07_livraisons': 'Livraisons',
  custom: 'Personnalisé',
};

// Taille max en bytes (10 Go)
export const MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024;

// Nombre max de fichiers simultanés
export const MAX_FILES_UPLOAD = 10;

// Extensions acceptées
export const ACCEPTED_EXTENSIONS = [
  '.pdf',
  '.png',
  '.jpg',
  '.jpeg',
  '.gif',
  '.webp',
  '.xls',
  '.xlsx',
  '.csv',
  '.doc',
  '.docx',
  '.mp4',
  '.avi',
  '.mov',
];
