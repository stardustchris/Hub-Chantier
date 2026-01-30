// Types pour Hub Chantier - Réexportation centralisée

// ===== UTILISATEURS =====
export type UserRole = 'admin' | 'conducteur' | 'chef_chantier' | 'compagnon'
export type UserType = 'employe' | 'interimaire' | 'sous_traitant'
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

// Couleurs disponibles pour les utilisateurs
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

// Metiers avec labels et couleurs
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

// Roles avec labels et couleurs
export const ROLES: Record<UserRole, { label: string; color: string }> = {
  admin: { label: 'Administrateur', color: '#9B59B6' },
  conducteur: { label: 'Conducteur de travaux', color: '#3498DB' },
  chef_chantier: { label: 'Chef de chantier', color: '#27AE60' },
  compagnon: { label: 'Compagnon', color: '#607D8B' },
}

// Types d'utilisateur avec labels et couleurs
export const TYPES_UTILISATEUR: Record<UserType, { label: string; color: string }> = {
  employe: { label: 'Employe', color: '#3498DB' },
  interimaire: { label: 'Interimaire', color: '#FF9800' },
  sous_traitant: { label: 'Sous-traitant', color: '#9C27B0' },
}

// ===== CHANTIERS =====
export type ChantierStatut = 'ouvert' | 'en_cours' | 'receptionne' | 'ferme'

// Contact de chantier (multi-contacts avec profession)
export interface ContactChantier {
  id?: number
  nom: string
  telephone?: string
  profession?: string
}

export interface ContactChantierCreate {
  nom: string
  telephone: string
  profession?: string
}

// Phase de chantier (chantiers en plusieurs étapes)
export interface PhaseChantier {
  id: number
  nom: string
  description?: string
  ordre: number
  date_debut?: string
  date_fin?: string
}

export interface PhaseChantierCreate {
  nom: string
  description?: string
  ordre?: number
  date_debut?: string
  date_fin?: string
}

export interface Chantier {
  id: string
  code: string
  nom: string
  adresse: string
  statut: ChantierStatut
  couleur?: string
  latitude?: number
  longitude?: number
  contact_nom?: string  // Legacy
  contact_telephone?: string  // Legacy
  contacts?: ContactChantier[]  // Multi-contacts
  phases?: PhaseChantier[]  // Phases du chantier
  maitre_ouvrage?: string  // Maître d'ouvrage
  heures_estimees?: number
  date_debut_prevue?: string
  date_fin_prevue?: string
  description?: string
  conducteurs: User[]
  chefs: User[]
  ouvriers?: User[]  // Ouvriers, intérimaires, sous-traitants assignés
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
  contacts?: ContactChantier[]
  heures_estimees?: number
  date_debut_prevue?: string
  date_fin_prevue?: string
  description?: string
}

export interface ChantierUpdate {
  nom?: string
  adresse?: string
  couleur?: string
  statut?: ChantierStatut
  latitude?: number
  longitude?: number
  contact_nom?: string
  contact_telephone?: string
  contacts?: ContactChantier[]
  // Note: phases sont gérées via l'API dédiée /api/chantiers/{id}/phases
  heures_estimees?: number
  date_debut_prevue?: string
  date_fin_prevue?: string
  description?: string
  maitre_ouvrage?: string
}

// Statuts de chantier avec labels, couleurs et icones
export const CHANTIER_STATUTS: Record<ChantierStatut, { label: string; color: string; icon: string }> = {
  ouvert: { label: 'A lancer', color: '#3498DB', icon: 'circle' },
  en_cours: { label: 'En cours', color: '#27AE60', icon: 'play' },
  receptionne: { label: 'Receptionne', color: '#F1C40F', icon: 'check' },
  ferme: { label: 'Ferme', color: '#E74C3C', icon: 'lock' },
}

// ===== DASHBOARD / FEED =====
// Types canoniques pour le dashboard : voir types/dashboard.ts (modèle API backend)
// Les types ci-dessous sont le modèle "enrichi" côté frontend (objets imbriqués)
// Ils seront unifiés avec dashboard.ts dans une future itération.

export type PostType = 'message' | 'photo' | 'urgent'

/**
 * TargetType pour le modèle enrichi frontend (valeurs en français).
 * Le modèle API backend utilise DashboardTargetType ('everyone' | 'specific_chantiers' | 'specific_people')
 * défini dans types/dashboard.ts.
 */
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

/**
 * Post enrichi côté frontend (avec objets User/Chantier imbriqués).
 * Pour le modèle API brut, voir PostDetail dans types/dashboard.ts.
 */
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

// ===== PLANNING / AFFECTATIONS =====
export type TypeAffectation = 'unique' | 'recurrente'
export type JourSemaine = 0 | 1 | 2 | 3 | 4 | 5 | 6
export type PlanningCategory = 'conducteur' | 'chef_chantier' | 'compagnon' | 'interimaire' | 'sous_traitant'

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
  utilisateur_role?: string
  utilisateur_type?: string
  chantier_nom?: string
  chantier_couleur?: string
}

export interface AffectationCreate {
  utilisateur_id: string
  chantier_id: string
  date: string
  date_fin?: string  // Pour affectations uniques multi-jours
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

// Jours de la semaine avec labels
export const JOURS_SEMAINE: Record<JourSemaine, { label: string; short: string }> = {
  0: { label: 'Lundi', short: 'Lun' },
  1: { label: 'Mardi', short: 'Mar' },
  2: { label: 'Mercredi', short: 'Mer' },
  3: { label: 'Jeudi', short: 'Jeu' },
  4: { label: 'Vendredi', short: 'Ven' },
  5: { label: 'Samedi', short: 'Sam' },
  6: { label: 'Dimanche', short: 'Dim' },
}

// Categories de planning
export const PLANNING_CATEGORIES: Record<PlanningCategory, { label: string; color: string; order: number }> = {
  conducteur: { label: 'Conducteurs de travaux', color: '#3498DB', order: 1 },
  chef_chantier: { label: 'Chefs de chantier', color: '#27AE60', order: 2 },
  compagnon: { label: 'Compagnons', color: '#607D8B', order: 3 },
  interimaire: { label: 'Interimaires', color: '#FF9800', order: 4 },
  sous_traitant: { label: 'Sous-traitants', color: '#9C27B0', order: 5 },
}

// ===== TACHES =====
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

// ===== FEUILLES D'HEURES / POINTAGES =====
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

// Constantes de pointages
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

// ===== FORMULAIRES =====
export type TypeChamp = 'texte' | 'texte_long' | 'nombre' | 'date' | 'heure' | 'date_heure' | 'select' | 'checkbox' | 'radio' | 'multi_select' | 'auto_date' | 'auto_heure' | 'auto_localisation' | 'auto_intervenant' | 'photo' | 'photo_multiple' | 'signature' | 'titre_section' | 'separateur'
export type CategorieFormulaire = 'intervention' | 'reception' | 'securite' | 'incident' | 'approvisionnement' | 'administratif' | 'gros_oeuvre' | 'autre'
export type StatutFormulaire = 'brouillon' | 'soumis' | 'valide'

// Structure d'un champ de template (FOR-01)
export interface ChampTemplate {
  id?: number
  nom: string
  label: string
  type_champ: TypeChamp
  obligatoire: boolean
  ordre: number
  placeholder?: string
  options?: string[]
  valeur_defaut?: string
  validation_regex?: string
  min_value?: number
  max_value?: number
}

// Template de formulaire (FOR-01)
export interface TemplateFormulaire {
  id: number
  nom: string
  categorie: CategorieFormulaire
  description?: string
  champs: ChampTemplate[]
  is_active: boolean
  version: number
  nombre_champs: number
  a_signature: boolean
  a_photo: boolean
  created_by?: number
  created_at: string
  updated_at: string
}

export interface TemplateFormulaireCreate {
  nom: string
  categorie: CategorieFormulaire
  description?: string
  champs?: ChampTemplate[]
}

export interface TemplateFormulaireUpdate {
  nom?: string
  categorie?: CategorieFormulaire
  description?: string
  champs?: ChampTemplate[]
  is_active?: boolean
}

// Photo horodatee (FOR-04)
export interface PhotoFormulaire {
  id?: number
  url: string
  nom_fichier: string
  champ_nom: string
  timestamp?: string
  latitude?: number
  longitude?: number
}

// Champ rempli dans un formulaire
export interface ChampRempli {
  nom: string
  type_champ: TypeChamp
  valeur?: string | number | boolean | string[]
  timestamp?: string
}

// Formulaire rempli (FOR-02 à FOR-11)
export interface FormulaireRempli {
  id: number
  template_id: number
  template_nom?: string
  template_categorie?: CategorieFormulaire
  chantier_id: number
  chantier_nom?: string
  user_id: number
  user_nom?: string
  statut: StatutFormulaire
  champs: ChampRempli[]
  photos: PhotoFormulaire[]
  est_signe: boolean
  signature_url?: string
  signature_nom?: string
  signature_timestamp?: string
  est_geolocalise: boolean
  localisation_latitude?: number
  localisation_longitude?: number
  soumis_at?: string
  valide_by?: number
  valide_at?: string
  version: number
  parent_id?: number
  created_at: string
  updated_at: string
}

export interface FormulaireCreate {
  template_id: number
  chantier_id: number
  latitude?: number
  longitude?: number
}

export interface FormulaireUpdate {
  champs?: { nom: string; valeur: string | number | boolean | string[]; type_champ: TypeChamp }[]
  latitude?: number
  longitude?: number
}

// Historique des versions (FOR-08)
export interface FormulaireHistorique {
  id: number
  version: number
  statut: StatutFormulaire
  modified_at: string
  modified_by?: number
}

// Constantes pour les types de champs
export const TYPES_CHAMPS: Record<TypeChamp, { label: string; icon: string }> = {
  texte: { label: 'Texte court', icon: 'Type' },
  texte_long: { label: 'Texte long', icon: 'FileText' },
  nombre: { label: 'Nombre', icon: 'Hash' },
  date: { label: 'Date', icon: 'Calendar' },
  heure: { label: 'Heure', icon: 'Clock' },
  date_heure: { label: 'Date et heure', icon: 'Calendar' },
  select: { label: 'Liste deroulante', icon: 'List' },
  checkbox: { label: 'Case a cocher', icon: 'CheckSquare' },
  radio: { label: 'Choix unique', icon: 'Circle' },
  multi_select: { label: 'Selection multiple', icon: 'List' },
  auto_date: { label: 'Date automatique', icon: 'Calendar' },
  auto_heure: { label: 'Heure automatique', icon: 'Clock' },
  auto_localisation: { label: 'Localisation auto', icon: 'MapPin' },
  auto_intervenant: { label: 'Intervenant auto', icon: 'User' },
  photo: { label: 'Photo', icon: 'Camera' },
  photo_multiple: { label: 'Photos multiples', icon: 'Camera' },
  signature: { label: 'Signature', icon: 'PenTool' },
  titre_section: { label: 'Titre de section', icon: 'Type' },
  separateur: { label: 'Separateur', icon: 'Minus' },
}

// Categories de formulaires (Section 8.3 du CDC)
export const CATEGORIES_FORMULAIRES: Record<CategorieFormulaire, { label: string; color: string; description: string }> = {
  intervention: { label: 'Interventions', color: '#3498DB', description: 'Rapport d\'intervention, Bon de SAV, Fiche depannage' },
  reception: { label: 'Reception', color: '#27AE60', description: 'PV de reception, Constat de reserves, Attestation fin travaux' },
  securite: { label: 'Securite', color: '#E74C3C', description: 'Formulaire securite, Visite PPSPS, Auto-controle' },
  incident: { label: 'Incidents', color: '#E67E22', description: 'Declaration sinistre, Fiche non-conformite, Rapport accident' },
  approvisionnement: { label: 'Approvisionnement', color: '#9B59B6', description: 'Commande materiel, Bon de livraison, Reception materiaux' },
  administratif: { label: 'Administratif', color: '#607D8B', description: 'Demande de conges, CERFA, Attestation diverse' },
  gros_oeuvre: { label: 'Gros Oeuvre', color: '#795548', description: 'Rapport journalier, Bon de betonnage, Controle ferraillage' },
  autre: { label: 'Autre', color: '#95A5A6', description: 'Formulaires divers' },
}

// Statuts de formulaire
export const STATUTS_FORMULAIRE: Record<StatutFormulaire, { label: string; color: string; bgColor: string }> = {
  brouillon: { label: 'Brouillon', color: '#9E9E9E', bgColor: '#F5F5F5' },
  soumis: { label: 'Soumis', color: '#FFC107', bgColor: '#FFF8E1' },
  valide: { label: 'Valide', color: '#4CAF50', bgColor: '#E8F5E9' },
}

// ===== RÉEXPORTS DES TYPES DEPUIS LES MODULES SÉPARÉS =====
// Les types de dashboard, documents, logistique et signalements sont définis dans des fichiers séparés
export type {
  TargetType as DashboardTargetType,
  PostStatus,
  PostDetail,
  Comment,
  Like,
  CreatePostData,
  CreateCommentData,
  FeedResponse,
  Author,
} from './dashboard'
