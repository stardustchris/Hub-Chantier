// Types pour Hub Chantier

// ===== UTILISATEURS =====
export type UserRole = 'administrateur' | 'conducteur' | 'chef_chantier' | 'compagnon'
export type UserType = 'employe' | 'sous_traitant'
export type Metier = 'macon' | 'coffreur' | 'ferrailleur' | 'grutier' | 'charpentier' | 'couvreur' | 'electricien' | 'plombier' | 'autre'

export interface User {
  id: string
  email: string
  nom: string
  prenom: string
  role: UserRole
  type_utilisateur: UserType
  telephone?: string
  metier?: Metier
  code_utilisateur?: string
  couleur?: string
  photo_profil?: string
  contact_urgence_nom?: string
  contact_urgence_telephone?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface UserCreate {
  email: string
  password: string
  nom: string
  prenom: string
  role?: UserRole
  type_utilisateur?: UserType
  telephone?: string
  metier?: Metier
  code_utilisateur?: string
  couleur?: string
}

export interface UserUpdate {
  nom?: string
  prenom?: string
  role?: UserRole
  type_utilisateur?: UserType
  telephone?: string
  metier?: Metier
  code_utilisateur?: string
  couleur?: string
  contact_urgence_nom?: string
  contact_urgence_telephone?: string
}

// ===== CHANTIERS =====
export type ChantierStatut = 'ouvert' | 'en_cours' | 'receptionne' | 'ferme'

export interface Chantier {
  id: string
  code: string
  nom: string
  adresse: string
  statut: ChantierStatut
  couleur?: string
  latitude?: number
  longitude?: number
  contact_nom?: string
  contact_telephone?: string
  heures_estimees?: number
  date_debut_prevue?: string
  date_fin_prevue?: string
  description?: string
  conducteurs: User[]
  chefs: User[]
  created_at: string
  updated_at?: string
}

export interface ChantierCreate {
  nom: string
  adresse: string
  couleur?: string
  latitude?: number
  longitude?: number
  contact_nom?: string
  contact_telephone?: string
  heures_estimees?: number
  date_debut_prevue?: string
  date_fin_prevue?: string
  description?: string
}

export interface ChantierUpdate {
  nom?: string
  adresse?: string
  couleur?: string
  latitude?: number
  longitude?: number
  contact_nom?: string
  contact_telephone?: string
  heures_estimees?: number
  date_debut_prevue?: string
  date_fin_prevue?: string
  description?: string
}

// ===== DASHBOARD / FEED =====
export type PostType = 'message' | 'photo' | 'urgent'
export type TargetType = 'tous' | 'chantiers' | 'utilisateurs'

export interface PostMedia {
  id: string
  url: string
  type: 'image' | 'video'
  thumbnail_url?: string
}

export interface PostComment {
  id: string
  contenu: string
  auteur: User
  created_at: string
}

export interface PostLike {
  user_id: string
  user: User
}

export interface Post {
  id: string
  contenu: string
  type: PostType
  auteur: User
  target_type: TargetType
  target_chantiers?: Chantier[]
  target_utilisateurs?: User[]
  medias: PostMedia[]
  commentaires: PostComment[]
  likes: PostLike[]
  likes_count: number
  commentaires_count: number
  is_pinned: boolean
  pinned_until?: string
  is_urgent: boolean
  created_at: string
  updated_at?: string
}

export interface PostCreate {
  contenu: string
  type?: PostType
  target_type?: TargetType
  target_chantier_ids?: string[]
  target_utilisateur_ids?: string[]
  is_urgent?: boolean
}

export interface CommentCreate {
  contenu: string
}

// ===== PAGINATION =====
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// ===== COULEURS UTILISATEURS =====
export const USER_COLORS = [
  { name: 'Rouge', code: '#E74C3C' },
  { name: 'Orange', code: '#E67E22' },
  { name: 'Jaune', code: '#F1C40F' },
  { name: 'Vert clair', code: '#2ECC71' },
  { name: 'Vert fonce', code: '#27AE60' },
  { name: 'Marron', code: '#795548' },
  { name: 'Corail', code: '#FF7043' },
  { name: 'Magenta', code: '#EC407A' },
  { name: 'Bleu fonce', code: '#2C3E50' },
  { name: 'Bleu clair', code: '#3498DB' },
  { name: 'Cyan', code: '#1ABC9C' },
  { name: 'Violet', code: '#9B59B6' },
  { name: 'Rose', code: '#E91E63' },
  { name: 'Gris', code: '#607D8B' },
  { name: 'Indigo', code: '#3F51B5' },
  { name: 'Lime', code: '#CDDC39' },
] as const

// ===== METIERS =====
export const METIERS: Record<Metier, { label: string; color: string }> = {
  macon: { label: 'Macon', color: '#795548' },
  coffreur: { label: 'Coffreur', color: '#F1C40F' },
  ferrailleur: { label: 'Ferrailleur', color: '#607D8B' },
  grutier: { label: 'Grutier', color: '#1ABC9C' },
  charpentier: { label: 'Charpentier', color: '#2ECC71' },
  couvreur: { label: 'Couvreur', color: '#E67E22' },
  electricien: { label: 'Electricien', color: '#EC407A' },
  plombier: { label: 'Plombier', color: '#3498DB' },
  autre: { label: 'Autre', color: '#607D8B' },
}

// ===== ROLES =====
export const ROLES: Record<UserRole, { label: string; color: string }> = {
  administrateur: { label: 'Administrateur', color: '#9B59B6' },
  conducteur: { label: 'Conducteur', color: '#3498DB' },
  chef_chantier: { label: 'Chef de chantier', color: '#27AE60' },
  compagnon: { label: 'Compagnon', color: '#607D8B' },
}

// ===== STATUTS CHANTIER =====
export const CHANTIER_STATUTS: Record<ChantierStatut, { label: string; color: string; icon: string }> = {
  ouvert: { label: 'Ouvert', color: '#3498DB', icon: 'circle' },
  en_cours: { label: 'En cours', color: '#27AE60', icon: 'play' },
  receptionne: { label: 'Receptionne', color: '#F1C40F', icon: 'check' },
  ferme: { label: 'Ferme', color: '#E74C3C', icon: 'lock' },
}
