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

// ===== PLANNING / AFFECTATIONS =====
export type TypeAffectation = 'unique' | 'recurrente'
export type JourSemaine = 0 | 1 | 2 | 3 | 4 | 5 | 6

export interface Affectation {
  id: string
  utilisateur_id: string
  chantier_id: string
  date: string
  heure_debut?: string
  heure_fin?: string
  note?: string
  type_affectation: TypeAffectation
  jours_recurrence?: JourSemaine[]
  created_at: string
  updated_at: string
  created_by: string
  // Enrichissement (depuis l'API)
  utilisateur_nom?: string
  utilisateur_couleur?: string
  utilisateur_metier?: string
  chantier_nom?: string
  chantier_couleur?: string
}

export interface AffectationCreate {
  utilisateur_id: string
  chantier_id: string
  date: string
  heure_debut?: string
  heure_fin?: string
  note?: string
  type_affectation?: TypeAffectation
  jours_recurrence?: JourSemaine[]
  date_fin_recurrence?: string
}

export interface AffectationUpdate {
  date?: string
  utilisateur_id?: string
  chantier_id?: string
  heure_debut?: string
  heure_fin?: string
  note?: string
}

export interface PlanningFilters {
  date_debut: string
  date_fin: string
  utilisateur_ids?: string[]
  chantier_ids?: string[]
  metiers?: string[]
}

export interface DuplicateAffectationsRequest {
  utilisateur_id: string
  source_date_debut: string
  source_date_fin: string
  target_date_debut: string
}

// Jours de la semaine
export const JOURS_SEMAINE: Record<JourSemaine, { label: string; short: string }> = {
  0: { label: 'Lundi', short: 'Lun' },
  1: { label: 'Mardi', short: 'Mar' },
  2: { label: 'Mercredi', short: 'Mer' },
  3: { label: 'Jeudi', short: 'Jeu' },
  4: { label: 'Vendredi', short: 'Ven' },
  5: { label: 'Samedi', short: 'Sam' },
  6: { label: 'Dimanche', short: 'Dim' },
}

// ===== TACHES (TAC-01 à TAC-20) =====
export type StatutTache = 'a_faire' | 'termine'
export type UniteMesure = 'm2' | 'm3' | 'ml' | 'kg' | 'litre' | 'unite' | 'forfait'
export type CouleurProgression = 'gris' | 'vert' | 'jaune' | 'rouge'
export type StatutValidation = 'en_attente' | 'validee' | 'rejetee'

export interface Tache {
  id: number
  chantier_id: number
  titre: string
  description?: string
  parent_id?: number
  ordre: number
  statut: StatutTache
  statut_display: string
  statut_icon: string
  date_echeance?: string
  unite_mesure?: UniteMesure
  unite_mesure_display?: string
  quantite_estimee?: number
  quantite_realisee: number
  heures_estimees?: number
  heures_realisees: number
  progression_heures: number
  progression_quantite: number
  couleur_progression: CouleurProgression
  couleur_hex: string
  est_terminee: boolean
  est_en_retard: boolean
  a_sous_taches: boolean
  nombre_sous_taches: number
  nombre_sous_taches_terminees: number
  template_id?: number
  created_at: string
  updated_at: string
  sous_taches: Tache[]
}

export interface TacheCreate {
  chantier_id: number
  titre: string
  description?: string
  parent_id?: number
  date_echeance?: string
  unite_mesure?: UniteMesure
  quantite_estimee?: number
  heures_estimees?: number
}

export interface TacheUpdate {
  titre?: string
  description?: string
  date_echeance?: string
  unite_mesure?: UniteMesure
  quantite_estimee?: number
  heures_estimees?: number
  statut?: StatutTache
  ordre?: number
}

export interface TacheStats {
  chantier_id: number
  total_taches: number
  taches_terminees: number
  taches_en_cours: number
  taches_en_retard: number
  heures_estimees_total: number
  heures_realisees_total: number
  progression_globale: number
}

// Templates de taches (TAC-04)
export interface SousTacheModele {
  titre: string
  description?: string
  ordre: number
  unite_mesure?: UniteMesure
  heures_estimees_defaut?: number
}

export interface TemplateModele {
  id: number
  nom: string
  description?: string
  categorie?: string
  unite_mesure?: UniteMesure
  unite_mesure_display?: string
  heures_estimees_defaut?: number
  nombre_sous_taches: number
  is_active: boolean
  created_at: string
  updated_at: string
  sous_taches: SousTacheModele[]
}

export interface TemplateCreate {
  nom: string
  description?: string
  categorie?: string
  unite_mesure?: UniteMesure
  heures_estimees_defaut?: number
  sous_taches?: SousTacheModele[]
}

// Feuilles de taches (TAC-18)
export interface FeuilleTache {
  id: number
  tache_id: number
  utilisateur_id: number
  chantier_id: number
  date_travail: string
  heures_travaillees: number
  quantite_realisee: number
  commentaire?: string
  statut_validation: StatutValidation
  statut_display: string
  est_validee: boolean
  est_en_attente: boolean
  est_rejetee: boolean
  validateur_id?: number
  date_validation?: string
  motif_rejet?: string
  created_at: string
  updated_at: string
}

export interface FeuilleTacheCreate {
  tache_id: number
  utilisateur_id: number
  chantier_id: number
  date_travail: string
  heures_travaillees: number
  quantite_realisee?: number
  commentaire?: string
}

// Constantes des unites de mesure (TAC-09)
export const UNITES_MESURE: Record<UniteMesure, { label: string; symbol: string }> = {
  m2: { label: 'Metres carres', symbol: 'm²' },
  m3: { label: 'Metres cubes', symbol: 'm³' },
  ml: { label: 'Metres lineaires', symbol: 'ml' },
  kg: { label: 'Kilogrammes', symbol: 'kg' },
  litre: { label: 'Litres', symbol: 'L' },
  unite: { label: 'Unites', symbol: 'u' },
  forfait: { label: 'Forfait', symbol: 'fft' },
}

// Couleurs de progression (TAC-20)
export const COULEURS_PROGRESSION: Record<CouleurProgression, { label: string; color: string; bgColor: string }> = {
  gris: { label: 'Non commence', color: '#9E9E9E', bgColor: '#F5F5F5' },
  vert: { label: 'Dans les temps', color: '#4CAF50', bgColor: '#E8F5E9' },
  jaune: { label: 'Attention', color: '#FFC107', bgColor: '#FFF8E1' },
  rouge: { label: 'Depassement', color: '#F44336', bgColor: '#FFEBEE' },
}

// Statuts de tache (TAC-13)
export const STATUTS_TACHE: Record<StatutTache, { label: string; icon: string; color: string }> = {
  a_faire: { label: 'A faire', icon: '☐', color: '#9E9E9E' },
  termine: { label: 'Termine', icon: '✅', color: '#4CAF50' },
}

// ===== FEUILLES D'HEURES / POINTAGES (FDH-01 à FDH-20) =====
export type StatutPointage = 'brouillon' | 'soumis' | 'valide' | 'rejete'
export type TypeVariablePaie =
  | 'heures_normales' | 'heures_supplementaires' | 'heures_nuit' | 'heures_dimanche' | 'heures_ferie'
  | 'panier_repas' | 'indemnite_transport' | 'prime_intemperies' | 'prime_salissure' | 'prime_outillage'
  | 'conges_payes' | 'rtt' | 'maladie' | 'accident_travail' | 'absence_injustifiee' | 'absence_justifiee'
  | 'formation' | 'deplacement'

export interface Pointage {
  id: number
  utilisateur_id: number
  chantier_id: number
  date_pointage: string
  heures_normales: string // Format HH:MM
  heures_supplementaires: string // Format HH:MM
  total_heures: string // Format HH:MM
  total_heures_decimal: number
  statut: StatutPointage
  commentaire?: string
  signature_utilisateur?: string
  signature_date?: string
  validateur_id?: number
  validation_date?: string
  motif_rejet?: string
  affectation_id?: number
  created_by?: number
  created_at: string
  updated_at: string
  // Enrichissement
  utilisateur_nom?: string
  chantier_nom?: string
  chantier_couleur?: string
  is_editable?: boolean
}

export interface PointageCreate {
  utilisateur_id: number
  chantier_id: number
  date_pointage: string
  heures_normales: string // Format HH:MM
  heures_supplementaires?: string // Format HH:MM
  commentaire?: string
  affectation_id?: number
}

export interface PointageUpdate {
  heures_normales?: string
  heures_supplementaires?: string
  commentaire?: string
}

export interface PointageJour {
  id: number
  chantier_id: number
  chantier_nom?: string
  chantier_couleur?: string
  date_pointage: string
  jour_semaine: string
  heures_normales: string
  heures_supplementaires: string
  total_heures: string
  statut: StatutPointage
  is_editable: boolean
}

export interface FeuilleHeures {
  id: number
  utilisateur_id: number
  semaine_debut: string
  semaine_fin: string
  annee: number
  numero_semaine: number
  label_semaine: string
  statut_global: StatutPointage
  commentaire_global?: string
  total_heures_normales: string
  total_heures_supplementaires: string
  total_heures: string
  total_heures_decimal: number
  is_complete: boolean
  is_all_validated: boolean
  created_at: string
  updated_at: string
  utilisateur_nom?: string
  pointages: PointageJour[]
  variables_paie: VariablePaieSemaine[]
  totaux_par_jour: Record<string, string>
  totaux_par_chantier: Record<number, string>
}

export interface VariablePaieSemaine {
  id: number
  pointage_id: number
  type_variable: TypeVariablePaie
  valeur: number
  date_application: string
  commentaire?: string
  created_at: string
  updated_at: string
}

export interface VariablePaieCreate {
  pointage_id: number
  type_variable: TypeVariablePaie
  valeur: number
  date_application: string
  commentaire?: string
}

// Vue par chantiers (FDH-01)
export interface VueChantier {
  chantier_id: number
  chantier_nom: string
  chantier_couleur?: string
  total_heures: string
  total_heures_decimal: number
  pointages_par_jour: Record<string, Pointage[]>
  total_par_jour: Record<string, string>
}

// Vue par compagnons (FDH-01)
export interface VueCompagnon {
  utilisateur_id: number
  utilisateur_nom: string
  total_heures: string
  total_heures_decimal: number
  chantiers: VueCompagnonChantier[]
  totaux_par_jour: Record<string, string>
}

export interface VueCompagnonChantier {
  chantier_id: number
  chantier_nom: string
  chantier_couleur?: string
  total_heures: string
  pointages_par_jour: Record<string, Pointage[]>
}

// Navigation semaine (FDH-02)
export interface NavigationSemaine {
  semaine_courante: string
  semaine_precedente: string
  semaine_suivante: string
  numero_semaine: number
  annee: number
  label: string
}

// Jauge d'avancement (FDH-14)
export interface JaugeAvancement {
  utilisateur_id: number
  semaine: string
  heures_planifiees: number
  heures_realisees: number
  taux_completion: number
  status: 'en_avance' | 'normal' | 'en_retard'
}

// Export (FDH-03, FDH-17)
export interface ExportFeuilleHeuresRequest {
  format_export: 'csv' | 'xlsx' | 'pdf' | 'erp'
  date_debut: string
  date_fin: string
  utilisateur_ids?: number[]
  chantier_ids?: number[]
  inclure_variables_paie?: boolean
  inclure_signatures?: boolean
}

// Filtres de recherche
export interface PointageFilters {
  utilisateur_id?: number
  chantier_id?: number
  date_debut?: string
  date_fin?: string
  statut?: StatutPointage
  page?: number
  page_size?: number
}

export interface FeuilleHeuresFilters {
  utilisateur_id?: number
  annee?: number
  numero_semaine?: number
  statut?: StatutPointage
  page?: number
  page_size?: number
}

// Constantes
export const STATUTS_POINTAGE: Record<StatutPointage, { label: string; color: string; bgColor: string }> = {
  brouillon: { label: 'Brouillon', color: '#9E9E9E', bgColor: '#F5F5F5' },
  soumis: { label: 'En attente', color: '#FFC107', bgColor: '#FFF8E1' },
  valide: { label: 'Valide', color: '#4CAF50', bgColor: '#E8F5E9' },
  rejete: { label: 'Rejete', color: '#F44336', bgColor: '#FFEBEE' },
}

export const TYPES_VARIABLES_PAIE: Record<TypeVariablePaie, { label: string; categorie: string }> = {
  heures_normales: { label: 'Heures normales', categorie: 'Heures' },
  heures_supplementaires: { label: 'Heures supplementaires', categorie: 'Heures' },
  heures_nuit: { label: 'Heures de nuit', categorie: 'Heures' },
  heures_dimanche: { label: 'Heures dimanche', categorie: 'Heures' },
  heures_ferie: { label: 'Heures ferie', categorie: 'Heures' },
  panier_repas: { label: 'Panier repas', categorie: 'Indemnites' },
  indemnite_transport: { label: 'Indemnite transport', categorie: 'Indemnites' },
  prime_intemperies: { label: 'Prime intemperies', categorie: 'Indemnites' },
  prime_salissure: { label: 'Prime salissure', categorie: 'Indemnites' },
  prime_outillage: { label: 'Prime outillage', categorie: 'Indemnites' },
  conges_payes: { label: 'Conges payes', categorie: 'Absences' },
  rtt: { label: 'RTT', categorie: 'Absences' },
  maladie: { label: 'Maladie', categorie: 'Absences' },
  accident_travail: { label: 'Accident travail', categorie: 'Absences' },
  absence_injustifiee: { label: 'Absence injustifiee', categorie: 'Absences' },
  absence_justifiee: { label: 'Absence justifiee', categorie: 'Absences' },
  formation: { label: 'Formation', categorie: 'Autres' },
  deplacement: { label: 'Deplacement', categorie: 'Autres' },
}

export const JOURS_SEMAINE_LABELS: Record<string, string> = {
  lundi: 'Lundi',
  mardi: 'Mardi',
  mercredi: 'Mercredi',
  jeudi: 'Jeudi',
  vendredi: 'Vendredi',
  samedi: 'Samedi',
  dimanche: 'Dimanche',
}

// Tableau ordonne des jours de la semaine (pour iteration)
export const JOURS_SEMAINE_ARRAY = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'] as const
