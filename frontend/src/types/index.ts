// Types pour Hub Chantier - Réexportation centralisée

// ===== UTILISATEURS =====
export type UserRole = 'admin' | 'conducteur' | 'chef_chantier' | 'compagnon'
export type UserType = 'employe' | 'cadre' | 'interimaire' | 'sous_traitant'
export type Metier = 'macon' | 'coffreur' | 'ferrailleur' | 'grutier' | 'charpentier' | 'couvreur' | 'terrassier' | 'administratif' | 'autre'

export interface User {
  id: string
  email: string
  nom: string
  prenom: string
  role: UserRole
  type_utilisateur: UserType
  telephone?: string
  metier?: Metier
  taux_horaire?: number
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
  taux_horaire?: number
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
  taux_horaire?: number
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
  terrassier: { label: 'Terrassier', color: '#FF9800' },
  administratif: { label: 'Administratif', color: '#9C27B0' },
  autre: { label: 'Autre', color: '#95A5A6' },
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
  cadre: { label: 'Cadre', color: '#2E86C1' },
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
  // DEV-TVA: Contexte TVA
  type_travaux?: string  // "renovation", "renovation_energetique", "construction_neuve"
  batiment_plus_2ans?: boolean
  usage_habitation?: boolean
}

// DEV-TVA: Options pour le type de travaux
export type TypeTravaux = 'renovation' | 'renovation_energetique' | 'construction_neuve'
export const TYPE_TRAVAUX_OPTIONS: { value: TypeTravaux; label: string; tva: string }[] = [
  { value: 'renovation', label: 'Renovation', tva: '10%' },
  { value: 'renovation_energetique', label: 'Renovation energetique', tva: '5.5%' },
  { value: 'construction_neuve', label: 'Construction neuve', tva: '20%' },
]

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
  // DEV-TVA: Contexte TVA
  type_travaux?: TypeTravaux
  batiment_plus_2ans?: boolean
  usage_habitation?: boolean
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
  // DEV-TVA: Contexte TVA
  type_travaux?: TypeTravaux
  batiment_plus_2ans?: boolean
  usage_habitation?: boolean
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

// =====================================================
// MODULE FINANCIER (Module 17)
// =====================================================

// Fournisseurs (FIN-14)
export type TypeFournisseur = 'negoce_materiaux' | 'loueur' | 'sous_traitant' | 'service'
export type TypeAchat = 'materiau' | 'materiel' | 'sous_traitance' | 'service'
export type StatutAchat = 'demande' | 'valide' | 'refuse' | 'commande' | 'livre' | 'facture'
export type UniteMesureFinancier = 'm2' | 'm3' | 'forfait' | 'kg' | 'heure' | 'ml' | 'u'

export interface Fournisseur {
  id: number
  raison_sociale: string
  type: TypeFournisseur
  siret: string | null
  adresse: string | null
  contact_principal: string | null
  telephone: string | null
  email: string | null
  conditions_paiement: string | null
  notes: string | null
  actif: boolean
  created_at: string
}

export interface FournisseurCreate {
  raison_sociale: string
  type: TypeFournisseur
  siret?: string
  adresse?: string
  contact_principal?: string
  telephone?: string
  email?: string
  conditions_paiement?: string
  notes?: string
}

export interface FournisseurUpdate extends Partial<FournisseurCreate> {
  actif?: boolean
}

// Budgets (FIN-01)
export interface Budget {
  id: number
  chantier_id: number
  montant_initial_ht: number
  montant_avenants_ht: number
  montant_revise_ht: number
  retenue_garantie_pct: number
  seuil_alerte_pct: number
  seuil_validation_achat: number
  notes: string | null
  created_at: string
}

export interface BudgetCreate {
  chantier_id: number
  montant_initial_ht: number
  retenue_garantie_pct?: number
  seuil_alerte_pct?: number
  seuil_validation_achat?: number
  notes?: string
}

export interface BudgetUpdate {
  montant_initial_ht?: number
  retenue_garantie_pct?: number
  seuil_alerte_pct?: number
  seuil_validation_achat?: number
  notes?: string
}

// Lots budgetaires (FIN-02)
export interface LotBudgetaire {
  id: number
  budget_id: number
  code_lot: string
  libelle: string
  unite: UniteMesureFinancier
  quantite_prevue: number
  prix_unitaire_ht: number
  total_prevu_ht: number
  engage: number
  realise: number
  ecart: number
  parent_lot_id: number | null
  ordre: number
}

export interface LotBudgetaireCreate {
  budget_id: number
  code_lot: string
  libelle: string
  unite: UniteMesureFinancier
  quantite_prevue: number
  prix_unitaire_ht: number
  parent_lot_id?: number
  ordre?: number
}

export interface LotBudgetaireUpdate extends Partial<Omit<LotBudgetaireCreate, 'budget_id'>> {}

// Achats (FIN-05, FIN-06)
export interface Achat {
  id: number
  chantier_id: number
  fournisseur_id: number
  lot_budgetaire_id: number | null
  type_achat: TypeAchat
  libelle: string
  quantite: number
  unite: UniteMesureFinancier
  prix_unitaire_ht: number
  taux_tva: number
  total_ht: number
  montant_tva: number
  total_ttc: number
  date_commande: string
  date_livraison_prevue: string | null
  statut: StatutAchat
  numero_facture: string | null
  motif_refus: string | null
  commentaire: string | null
  demandeur_id: number
  valideur_id: number | null
  fournisseur_nom?: string
  chantier_nom?: string
  lot_code?: string
  demandeur_nom?: string
  valideur_nom?: string
  statut_label?: string
  statut_couleur?: string
  created_at: string
}

export interface AchatCreate {
  chantier_id: number
  fournisseur_id: number
  lot_budgetaire_id?: number
  type_achat: TypeAchat
  libelle: string
  quantite: number
  unite: UniteMesureFinancier
  prix_unitaire_ht: number
  taux_tva: number
  date_commande: string
  date_livraison_prevue?: string
  commentaire?: string
}

export interface AchatUpdate extends Partial<Omit<AchatCreate, 'chantier_id'>> {}

// Dashboard financier (FIN-11)
export interface KPIFinancier {
  montant_revise_ht: number
  total_engage: number
  total_realise: number
  reste_a_depenser: number
  marge_estimee: number
  marge_statut: string  // "calculee" | "estimee"
  pct_engage: number
  pct_realise: number
  pct_reste: number
}

export interface RepartitionLot {
  lot_id: number
  code_lot: string
  libelle: string
  total_prevu_ht: number
  engage: number
  realise: number
}

export interface DashboardFinancier {
  kpi: KPIFinancier
  derniers_achats: Achat[]
  repartition_par_lot: RepartitionLot[]
}

// Evolution financiere (FIN-17)
export interface EvolutionMensuelle {
  mois: string
  prevu_cumule: number
  engage_cumule: number
  realise_cumule: number
}

export interface EvolutionFinanciere {
  chantier_id: number
  points: EvolutionMensuelle[]
}

// Journal financier (FIN-15)
export interface JournalFinancierEntry {
  id: number
  entite_type: string
  entite_id: number
  action: string
  champ_modifie: string | null
  ancienne_valeur: string | null
  nouvelle_valeur: string | null
  motif: string | null
  auteur_id: number
  auteur_nom?: string
  created_at: string
}

// ===== Phase 2 Types =====

// Avenants (FIN-04)
export type StatutAvenant = 'brouillon' | 'valide'

export interface AvenantBudgetaire {
  id: number
  budget_id: number
  numero: string
  motif: string
  montant_ht: number
  impact_description: string | null
  statut: StatutAvenant
  created_by: number | null
  validated_by: number | null
  validated_at: string | null
  created_at: string
}

export interface AvenantCreate {
  budget_id: number
  motif: string
  montant_ht: number
  impact_description?: string
}

export interface AvenantUpdate {
  motif?: string
  montant_ht?: number
  impact_description?: string
}

// Situations de travaux (FIN-07)
export type StatutSituation = 'brouillon' | 'en_validation' | 'emise' | 'validee' | 'facturee'

export interface LigneSituation {
  id: number
  situation_id: number
  lot_budgetaire_id: number
  pourcentage_avancement: number
  montant_marche_ht: number
  montant_cumule_precedent_ht: number
  montant_periode_ht: number
  montant_cumule_ht: number
  code_lot?: string
  libelle_lot?: string
}

export interface LigneSituationCreate {
  lot_budgetaire_id: number
  pourcentage_avancement: number
}

export interface SituationTravaux {
  id: number
  chantier_id: number
  budget_id: number
  numero: string
  periode_debut: string
  periode_fin: string
  montant_cumule_precedent_ht: number
  montant_periode_ht: number
  montant_cumule_ht: number
  retenue_garantie_pct: number
  taux_tva: number
  statut: StatutSituation
  notes: string | null
  montant_retenue_garantie: number
  montant_tva: number
  montant_ttc: number
  montant_net: number
  lignes: LigneSituation[]
  created_at: string
}

export interface SituationCreate {
  chantier_id: number
  budget_id: number
  periode_debut: string
  periode_fin: string
  lignes: LigneSituationCreate[]
  retenue_garantie_pct?: number
  taux_tva?: number
  notes?: string
}

export interface SituationUpdate {
  lignes: LigneSituationCreate[]
  notes?: string
}

// Factures client (FIN-08)
export type TypeFacture = 'acompte' | 'situation' | 'solde'
export type StatutFacture = 'brouillon' | 'emise' | 'envoyee' | 'payee' | 'annulee'

export interface FactureClient {
  id: number
  chantier_id: number
  situation_id: number | null
  numero_facture: string
  type_facture: TypeFacture
  montant_ht: number
  taux_tva: number
  montant_tva: number
  montant_ttc: number
  retenue_garantie_montant: number
  montant_net: number
  date_emission: string | null
  date_echeance: string | null
  statut: StatutFacture
  notes: string | null
  created_at: string
}

export interface FactureFromSituationCreate {
  situation_id: number
  date_echeance?: string
  notes?: string
}

export interface FactureAcompteCreate {
  chantier_id: number
  montant_ht: number
  taux_tva?: number
  retenue_garantie_pct?: number
  date_echeance?: string
  notes?: string
}

// Couts main-d'oeuvre (FIN-09)
export interface CoutEmploye {
  user_id: number
  nom: string
  prenom: string
  heures_validees: number
  taux_horaire: number
  cout_total: number
}

export interface CoutMainOeuvreSummary {
  chantier_id: number
  total_heures: number
  cout_total: number
  details: CoutEmploye[]
}

// Couts materiel (FIN-10)
export interface CoutMateriel {
  ressource_id: number
  nom: string
  code: string
  jours_reservation: number
  tarif_journalier: number
  cout_total: number
}

export interface CoutMaterielSummary {
  chantier_id: number
  cout_total: number
  details: CoutMateriel[]
}

// Alertes depassement (FIN-12)
export type TypeAlerte = 'seuil_engage' | 'seuil_realise' | 'depassement_lot'

export interface AlerteDepassement {
  id: number
  chantier_id: number
  budget_id: number
  type_alerte: TypeAlerte
  message: string
  pourcentage_atteint: number
  seuil_configure: number
  montant_budget_ht: number
  montant_atteint_ht: number
  est_acquittee: boolean
  acquittee_par: number | null
  acquittee_at: string | null
  created_at: string
}

// Phase 2 constants
export const STATUT_AVENANT_CONFIG: Record<StatutAvenant, { label: string; couleur: string }> = {
  brouillon: { label: 'Brouillon', couleur: '#F59E0B' },
  valide: { label: 'Valide', couleur: '#10B981' },
}

export const STATUT_SITUATION_CONFIG: Record<StatutSituation, { label: string; couleur: string }> = {
  brouillon: { label: 'Brouillon', couleur: '#F59E0B' },
  en_validation: { label: 'En validation', couleur: '#3B82F6' },
  emise: { label: 'Emise', couleur: '#8B5CF6' },
  validee: { label: 'Validee', couleur: '#10B981' },
  facturee: { label: 'Facturee', couleur: '#6B7280' },
}

export const STATUT_FACTURE_CONFIG: Record<StatutFacture, { label: string; couleur: string }> = {
  brouillon: { label: 'Brouillon', couleur: '#F59E0B' },
  emise: { label: 'Emise', couleur: '#3B82F6' },
  envoyee: { label: 'Envoyee', couleur: '#8B5CF6' },
  payee: { label: 'Payee', couleur: '#10B981' },
  annulee: { label: 'Annulee', couleur: '#EF4444' },
}

export const TYPE_FACTURE_LABELS: Record<TypeFacture, string> = {
  acompte: 'Acompte',
  situation: 'Situation',
  solde: 'Solde',
}

export const TYPE_ALERTE_LABELS: Record<TypeAlerte, string> = {
  seuil_engage: 'Seuil engage',
  seuil_realise: 'Seuil realise',
  depassement_lot: 'Depassement lot',
}

// Constantes financieres
export const TYPE_FOURNISSEUR_LABELS: Record<TypeFournisseur, string> = {
  negoce_materiaux: 'Negoce materiaux',
  loueur: 'Loueur',
  sous_traitant: 'Sous-traitant',
  service: 'Service',
}

export const TYPE_ACHAT_LABELS: Record<TypeAchat, string> = {
  materiau: 'Materiau',
  materiel: 'Materiel',
  sous_traitance: 'Sous-traitance',
  service: 'Service',
}

export const STATUT_ACHAT_CONFIG: Record<StatutAchat, { label: string; couleur: string }> = {
  demande: { label: 'Demande', couleur: '#F59E0B' },
  valide: { label: 'Valide', couleur: '#10B981' },
  refuse: { label: 'Refuse', couleur: '#EF4444' },
  commande: { label: 'Commande', couleur: '#3B82F6' },
  livre: { label: 'Livre', couleur: '#8B5CF6' },
  facture: { label: 'Facture', couleur: '#6B7280' },
}

export const UNITE_MESURE_FINANCIER_LABELS: Record<UniteMesureFinancier, string> = {
  m2: 'm2', m3: 'm3', forfait: 'Forfait', kg: 'kg', heure: 'h', ml: 'ml', u: 'u',
}

export const TAUX_TVA_OPTIONS = [
  { value: 20, label: '20% (Normal)' },
  { value: 10, label: '10% (Intermediaire)' },
  { value: 5.5, label: '5,5% (Reduit)' },
  { value: 0, label: '0% (Exonere)' },
]

// Options retenue de garantie (DEV-22)
export const RETENUE_GARANTIE_OPTIONS = [
  { value: 0, label: '0% (Aucune)' },
  { value: 5, label: '5%' },
  { value: 10, label: '10%' },
]

// ===== Phase 3 Types =====

// Vue consolidee multi-chantiers (FIN-20)
export interface ChantierFinancierSummary {
  chantier_id: number
  nom_chantier: string
  montant_revise_ht: number
  total_engage: number
  total_realise: number
  reste_a_depenser: number
  marge_estimee_pct: number
  pct_engage: number
  pct_realise: number
  statut: 'ok' | 'attention' | 'depassement'
  nb_alertes: number
}

export interface KPIGlobaux {
  total_budget_revise: number
  total_engage: number
  total_realise: number
  total_reste_a_depenser: number
  marge_moyenne_pct: number
  nb_chantiers: number
  nb_chantiers_ok: number
  nb_chantiers_attention: number
  nb_chantiers_depassement: number
}

export interface VueConsolidee {
  kpi_globaux: KPIGlobaux
  chantiers: ChantierFinancierSummary[]
  top_rentables: ChantierFinancierSummary[]
  top_derives: ChantierFinancierSummary[]
}

// Analyse IA consolidée multi-chantiers (Gemini 3 Flash)
export interface AnalyseIAConsolidee {
  synthese: string
  alertes: string[]
  recommandations: string[]
  tendance: 'hausse' | 'stable' | 'baisse'
  score_sante: number
  source: 'gemini-3-flash' | 'regles'
  ai_available: boolean
}

// Suggestions IA (FIN-21)
export interface Suggestion {
  type: string
  severity: 'CRITICAL' | 'WARNING' | 'INFO'
  titre: string
  description: string
  impact_estime_eur: number
}

export interface IndicateursPredictif {
  burn_rate_mensuel: number
  budget_moyen_mensuel: number
  ecart_burn_rate_pct: number
  mois_restants_budget: number
  date_epuisement_estimee: string
  avancement_financier_pct: number
}

export interface SuggestionsFinancieres {
  chantier_id: number
  suggestions: Suggestion[]
  indicateurs: IndicateursPredictif
  ai_available: boolean
  source: 'gemini' | 'algorithmic'
}

// Affectations budget-tache (FIN-03)
export interface AffectationBudgetTache {
  id: number
  lot_budgetaire_id: number
  tache_id: number
  pourcentage_allocation: number
  code_lot?: string
  libelle_lot?: string
  total_prevu_ht?: string
  created_at: string
}

export interface AffectationBudgetTacheCreate {
  tache_id: number
  pourcentage_allocation: number
}

// =====================================================
// MODULE DEVIS (Module 20)
// =====================================================

// Enums et types de base
export type StatutDevis = 'brouillon' | 'en_validation' | 'envoye' | 'vu' | 'en_negociation' | 'accepte' | 'refuse' | 'perdu' | 'expire' | 'converti'
export type TypeDebourse = 'moe' | 'materiaux' | 'materiel' | 'sous_traitance' | 'deplacement'

// Configuration des statuts devis (label + couleur) - 9 valeurs (backend)
export const STATUT_DEVIS_CONFIG: Record<StatutDevis, { label: string; couleur: string }> = {
  brouillon: { label: 'Brouillon', couleur: '#6B7280' },
  en_validation: { label: 'En validation', couleur: '#F59E0B' },
  envoye: { label: 'Envoye', couleur: '#3B82F6' },
  vu: { label: 'Vu', couleur: '#8B5CF6' },
  en_negociation: { label: 'En negociation', couleur: '#F97316' },
  accepte: { label: 'Accepte', couleur: '#059669' },
  refuse: { label: 'Refuse', couleur: '#EF4444' },
  perdu: { label: 'Perdu', couleur: '#991B1B' },
  expire: { label: 'Expire', couleur: '#9CA3AF' },
  converti: { label: 'Converti', couleur: '#009688' },
}

export const TYPE_DEBOURSE_LABELS: Record<TypeDebourse, string> = {
  moe: 'Main d\'oeuvre',
  materiaux: 'Materiaux',
  materiel: 'Materiel',
  sous_traitance: 'Sous-traitance',
  deplacement: 'Deplacement',
}

// Articles (bibliotheque de prix)
export interface Article {
  id: number
  code: string
  designation: string
  unite: string
  prix_unitaire_ht: number
  type_debourse: TypeDebourse
  categorie?: string
  description?: string
  actif: boolean
  created_at: string
  updated_at?: string
}

export interface ArticleCreate {
  code: string
  designation: string
  unite: string
  prix_unitaire_ht: number
  type_debourse: TypeDebourse
  categorie?: string
  description?: string
}

export interface ArticleUpdate {
  code?: string
  designation?: string
  unite?: string
  prix_unitaire_ht?: number
  type_debourse?: TypeDebourse
  categorie?: string
  description?: string
  actif?: boolean
}

// Versions et variantes (DEV-08)
export type TypeVersion = 'originale' | 'revision' | 'variante'
export type LabelVariante = 'ECO' | 'STD' | 'PREM' | 'ALT'
export type TypeEcart = 'ajout' | 'suppression' | 'modification' | 'identique'

export const LABEL_VARIANTE_CONFIG: Record<LabelVariante, { label: string; couleur: string }> = {
  ECO: { label: 'Economique', couleur: '#10B981' },
  STD: { label: 'Standard', couleur: '#3B82F6' },
  PREM: { label: 'Premium', couleur: '#8B5CF6' },
  ALT: { label: 'Alternative', couleur: '#F59E0B' },
}

export const TYPE_VERSION_CONFIG: Record<TypeVersion, { label: string; couleur: string }> = {
  originale: { label: 'Originale', couleur: '#6B7280' },
  revision: { label: 'Revision', couleur: '#3B82F6' },
  variante: { label: 'Variante', couleur: '#8B5CF6' },
}

export const TYPE_ECART_CONFIG: Record<TypeEcart, { label: string; couleur: string; bgColor: string }> = {
  ajout: { label: 'Ajout', couleur: '#10B981', bgColor: '#D1FAE5' },
  suppression: { label: 'Suppression', couleur: '#EF4444', bgColor: '#FEE2E2' },
  modification: { label: 'Modification', couleur: '#F59E0B', bgColor: '#FEF3C7' },
  identique: { label: 'Identique', couleur: '#6B7280', bgColor: '#F3F4F6' },
}

// Resume d'une version (retourne par GET /versions)
export interface VersionDevis {
  id: number
  numero: string
  type_version: TypeVersion
  numero_version: number
  label_variante?: LabelVariante
  version_commentaire?: string
  version_figee: boolean
  version_figee_at?: string
  statut: StatutDevis
  montant_total_ht: number
  montant_total_ttc: number
  date_creation?: string
  devis_parent_id?: number
}

// Resultat d'un comparatif entre 2 versions
export interface ComparatifDevis {
  id: number
  source_id: number
  cible_id: number
  source_numero: string
  cible_numero: string
  ecart_montant_ht: number
  ecart_montant_ttc: number
  ecart_marge: number
  ecart_debourse: number
  variation_montant_ht_pct: number
  variation_montant_ttc_pct: number
  variation_marge_pct: number
  variation_debourse_pct: number
  nb_lots_ajoutes: number
  nb_lots_supprimes: number
  nb_lots_modifies: number
  nb_lignes_ajoutees: number
  nb_lignes_supprimees: number
  nb_lignes_modifiees: number
  lignes: ComparatifLigne[]
  created_at: string
}

// Detail ligne par ligne du comparatif
export interface ComparatifLigne {
  designation: string
  lot_titre?: string
  type_ecart: TypeEcart
  quantite_source?: number
  quantite_cible?: number
  ecart_quantite?: number
  montant_source?: number
  montant_cible?: number
  ecart_montant?: number
}

// Devis (matches backend DevisDTO)
export interface Devis {
  id: number
  numero: string
  objet: string
  client_nom: string
  statut: StatutDevis
  montant_total_ht: number
  montant_total_ttc: number
  date_creation?: string
  date_validite?: string
  commercial_id?: number
  chantier_ref?: string
  // Champs retenue de garantie (DEV-22)
  retenue_garantie_pct?: number
  montant_retenue_garantie?: number
  montant_net_a_payer?: number
  // Champs version (DEV-08)
  type_version?: TypeVersion
  numero_version?: number
  version_figee?: boolean
  devis_parent_id?: number
  label_variante?: LabelVariante
  version_commentaire?: string
  version_figee_at?: string
}

export interface DevisCreate {
  objet: string
  client_nom: string
  chantier_ref?: string
  client_adresse?: string
  client_email?: string
  client_telephone?: string
  date_validite?: string
  taux_tva_defaut?: number
  taux_marge_global?: number
  taux_marge_moe?: number
  taux_marge_materiaux?: number
  taux_marge_sous_traitance?: number
  taux_marge_materiel?: number
  taux_marge_deplacement?: number
  coefficient_frais_generaux?: number
  retenue_garantie_pct?: number
  notes?: string
  commercial_id?: number
  conducteur_id?: number
  acompte_pct?: number
  echeance?: string
  moyens_paiement?: string[]
  date_visite?: string | null
  date_debut_travaux?: string | null
  duree_estimee_jours?: number | null
  notes_bas_page?: string | null
  nom_interne?: string | null
}

export interface DevisUpdate {
  objet?: string
  client_nom?: string
  chantier_ref?: string
  client_adresse?: string
  client_email?: string
  client_telephone?: string
  date_validite?: string
  taux_tva_defaut?: number
  taux_marge_global?: number
  taux_marge_moe?: number
  taux_marge_materiaux?: number
  taux_marge_sous_traitance?: number
  taux_marge_materiel?: number
  taux_marge_deplacement?: number
  coefficient_frais_generaux?: number
  retenue_garantie_pct?: number
  notes?: string
  conditions_generales?: string
  commercial_id?: number
  conducteur_id?: number
  acompte_pct?: number
  echeance?: string
  moyens_paiement?: string[]
  date_visite?: string | null
  date_debut_travaux?: string | null
  duree_estimee_jours?: number | null
  notes_bas_page?: string | null
  nom_interne?: string | null
}

// DEV-TVA: Ventilation TVA par taux (art. 242 nonies A CGI)
export interface VentilationTVA {
  taux: number
  base_ht: number
  montant_tva: number
}

// DevisDetail (matches backend DevisDetailDTO)
export interface DevisDetail {
  id: number
  numero: string
  client_nom: string
  client_adresse?: string
  client_email?: string
  client_telephone?: string
  objet: string
  statut: StatutDevis
  montant_total_ht: number
  montant_total_ttc: number
  taux_marge_global: number
  taux_marge_moe?: number
  taux_marge_materiaux?: number
  taux_marge_sous_traitance?: number
  taux_marge_materiel?: number
  taux_marge_deplacement?: number
  coefficient_frais_generaux: number
  retenue_garantie_pct: number
  montant_retenue_garantie?: number
  montant_net_a_payer?: number
  taux_tva_defaut: number
  date_creation?: string
  date_validite?: string
  updated_at?: string
  commercial_id?: number
  conducteur_id?: number
  chantier_ref?: string
  created_by?: number
  notes?: string
  conditions_generales?: string
  lots: LotDevis[]
  // Champs version (DEV-08)
  type_version?: TypeVersion
  numero_version?: number
  version_figee?: boolean
  devis_parent_id?: number
  label_variante?: LabelVariante
  version_commentaire?: string
  version_figee_at?: string
  // DEV-TVA: Ventilation TVA multi-taux et mention legale
  ventilation_tva?: VentilationTVA[]
  mention_tva_reduite?: string
  // Generateur de devis - nouveaux champs
  acompte_pct?: number
  echeance?: string
  moyens_paiement?: string[]
  date_visite?: string | null
  date_debut_travaux?: string | null
  duree_estimee_jours?: number | null
  notes_bas_page?: string | null
  nom_interne?: string | null
}

// Lots de devis (matches backend LotDevisDTO)
export interface LotDevis {
  id: number
  devis_id: number
  titre: string
  numero: string
  ordre: number
  marge_lot_pct?: number
  total_ht: number
  total_ttc: number
  debourse_sec: number
  lignes: LigneDevis[]
}

export interface LotDevisCreate {
  devis_id: number
  titre: string
  numero?: string
  ordre?: number
  marge_lot_pct?: number
}

export interface LotDevisUpdate {
  titre?: string
  numero?: string
  ordre?: number
  marge_lot_pct?: number
}

// Lignes de devis (matches backend LigneDevisDTO)
export interface LigneDevis {
  id: number
  lot_devis_id: number
  designation: string
  unite: string
  quantite: number
  prix_unitaire_ht: number
  montant_ht: number
  taux_tva: number
  montant_ttc: number
  ordre: number
  marge_ligne_pct?: number
  article_id?: number
  debourse_sec: number
  prix_revient: number
  debourses: DebourseDetail[]
}

export interface LigneDevisCreate {
  lot_devis_id: number
  designation: string
  unite?: string
  quantite?: number
  prix_unitaire_ht?: number
  taux_tva?: number
  ordre?: number
  marge_ligne_pct?: number
  article_id?: number
}

export interface LigneDevisUpdate {
  designation?: string
  unite?: string
  quantite?: number
  prix_unitaire_ht?: number
  taux_tva?: number
  ordre?: number
  marge_ligne_pct?: number
  article_id?: number
}

// Debourses detail par ligne (matches backend DebourseDetailDTO)
export interface DebourseDetail {
  id: number
  ligne_devis_id: number
  type_debourse: TypeDebourse
  designation: string
  quantite: number
  prix_unitaire: number
  montant: number
  unite: string
}

export interface DebourseDetailCreate {
  type_debourse: TypeDebourse
  designation: string
  quantite?: number
  prix_unitaire?: number
  unite?: string
}

// Journal devis (matches backend JournalDevisDTO)
export interface JournalDevisEntry {
  id: number
  devis_id: number
  action: string
  details?: string
  auteur_id: number
  created_at: string
}

// Dashboard devis (matches backend DashboardDevisDTO / KPIDevisDTO)
export interface KPIDevis {
  nb_brouillon: number
  nb_en_validation: number
  nb_envoye: number
  nb_vu: number
  nb_en_negociation: number
  nb_accepte: number
  nb_refuse: number
  nb_perdu: number
  nb_expire: number
  total_pipeline_ht: number
  total_accepte_ht: number
  taux_conversion: number
  nb_total: number
}

// DevisRecent (matches backend DevisRecentDTO)
export interface DevisRecent {
  id: number
  numero: string
  client_nom: string
  objet: string
  statut: StatutDevis
  montant_total_ht: number
  date_creation: string
}

export interface DashboardDevis {
  kpi: KPIDevis
  derniers_devis: DevisRecent[]
}

// Attestation TVA (DEV-23)
export type TypeCerfa = '1300-SD' | '1301-SD'
export type NatureImmeuble = 'maison' | 'appartement' | 'immeuble'
export type NatureTravaux = 'amelioration' | 'entretien' | 'transformation'

export interface EligibiliteTVA {
  eligible: boolean
  taux_tva: number
  type_cerfa?: TypeCerfa
  libelle_taux: string
  message: string
}

export interface AttestationTVA {
  id: number
  devis_id: number
  type_cerfa: TypeCerfa
  taux_tva: number
  nom_client: string
  adresse_client: string
  telephone_client?: string
  adresse_immeuble: string
  nature_immeuble: NatureImmeuble
  date_construction_plus_2ans: boolean
  description_travaux: string
  nature_travaux: NatureTravaux
  atteste_par: string
  date_attestation: string
  generee_at: string
}

export interface AttestationTVACreate {
  nom_client: string
  adresse_client: string
  telephone_client?: string
  adresse_immeuble: string
  nature_immeuble: NatureImmeuble
  date_construction_plus_2ans: boolean
  description_travaux: string
  nature_travaux: NatureTravaux
  atteste_par: string
}

export const NATURE_IMMEUBLE_LABELS: Record<NatureImmeuble, string> = {
  maison: 'Maison individuelle',
  appartement: 'Appartement',
  immeuble: 'Immeuble collectif',
}

export const NATURE_TRAVAUX_LABELS: Record<NatureTravaux, string> = {
  amelioration: 'Amelioration',
  entretien: 'Entretien / reparation',
  transformation: 'Transformation',
}

// Frais de chantier (DEV-25)
export type TypeFraisChantier = 'compte_prorata' | 'frais_generaux' | 'installation_chantier' | 'autre'
export type ModeRepartition = 'global' | 'prorata_lots'

export interface FraisChantierDevis {
  id: number
  devis_id: number
  type_frais: TypeFraisChantier
  libelle: string
  montant_ht: number
  montant_ttc: number
  mode_repartition: ModeRepartition
  taux_tva: number
  ordre: number
  lot_devis_id?: number
}

export interface FraisChantierCreate {
  type_frais: TypeFraisChantier
  libelle: string
  montant_ht: number
  mode_repartition: ModeRepartition
  taux_tva?: number
  ordre?: number
  lot_devis_id?: number
}

export interface FraisChantierUpdate {
  type_frais?: TypeFraisChantier
  libelle?: string
  montant_ht?: number
  mode_repartition?: ModeRepartition
  taux_tva?: number
  ordre?: number
  lot_devis_id?: number
}

export interface RepartitionFraisLot {
  lot_id: number
  lot_libelle: string
  lot_total_ht: number
  montant_frais_repercute: number
  poids_pct: number
}

export const TYPE_FRAIS_LABELS: Record<TypeFraisChantier, string> = {
  compte_prorata: 'Compte prorata',
  frais_generaux: 'Frais generaux',
  installation_chantier: 'Installation chantier',
  autre: 'Autre',
}

export const MODE_REPARTITION_LABELS: Record<ModeRepartition, string> = {
  global: 'Global',
  prorata_lots: 'Au prorata des lots',
}

// Relances automatiques (DEV-24)
export type StatutRelance = 'planifiee' | 'envoyee' | 'annulee'
export type TypeRelance = 'email' | 'push' | 'les_deux'

export interface RelanceDevis {
  id: number
  devis_id: number
  numero_relance: number
  type_relance: TypeRelance
  date_envoi?: string
  date_prevue: string
  statut: StatutRelance
  message_personnalise?: string
}

export interface ConfigRelances {
  delais: number[]
  actif: boolean
  type_relance_defaut: TypeRelance
}

export interface RelancesHistorique {
  relances: RelanceDevis[]
  config: ConfigRelances
  nb_envoyees: number
  nb_planifiees: number
  nb_annulees: number
}

export const STATUT_RELANCE_CONFIG: Record<StatutRelance, { label: string; couleur: string }> = {
  planifiee: { label: 'Planifiee', couleur: '#3B82F6' },
  envoyee: { label: 'Envoyee', couleur: '#10B981' },
  annulee: { label: 'Annulee', couleur: '#9CA3AF' },
}

export const TYPE_RELANCE_LABELS: Record<TypeRelance, string> = {
  email: 'Email',
  push: 'Notification push',
  les_deux: 'Email + Push',
}

// Signature electronique (DEV-14)
export type TypeSignature = 'dessin_tactile' | 'upload_scan' | 'nom_prenom'

export interface SignatureDevis {
  id: number
  devis_id: number
  type_signature: TypeSignature
  signataire_nom: string
  signataire_email: string
  signataire_telephone?: string
  signature_data: string
  ip_adresse: string
  horodatage: string
  hash_document: string
  valide: boolean
  revoquee_at?: string
  motif_revocation?: string
}

export interface SignatureCreate {
  type_signature: TypeSignature
  signataire_nom: string
  signataire_email: string
  signataire_telephone?: string
  signature_data: string
}

export interface VerificationSignature {
  valide: boolean
  hash_actuel: string
  hash_signature: string
  integre: boolean
  message: string
}

export const TYPE_SIGNATURE_LABELS: Record<TypeSignature, string> = {
  dessin_tactile: 'Dessin tactile',
  upload_scan: 'Upload scan',
  nom_prenom: 'Nom et prenom',
}

// Options de presentation du devis PDF (DEV-11)
export interface OptionsPresentation {
  afficher_debourses: boolean
  afficher_composants: boolean
  afficher_quantites: boolean
  afficher_prix_unitaires: boolean
  afficher_tva_detaillee: boolean
  afficher_conditions_generales: boolean
  afficher_logo: boolean
  afficher_coordonnees_entreprise: boolean
  afficher_retenue_garantie: boolean
  afficher_frais_chantier_detail: boolean
  template_nom: string
}

export interface TemplatePresentation {
  nom: string
  description: string
  options: OptionsPresentation
}

// Conversion en chantier (DEV-16)
export interface ConversionInfo {
  conversion_possible: boolean
  deja_converti: boolean
  est_accepte: boolean
  est_signe: boolean
  pre_requis_manquants: string[]
  chantier_id?: number
  chantier_numero?: string
}

export interface ConversionDevis {
  devis_id: number
  numero: string
  client: string
  budget: number
  lots: { code_lot: string; libelle: string; montant_ht: number }[]
  retenue_garantie_pct: number
  date_conversion: string
  chantier_id?: number
}

// Resultat de la conversion devis -> chantier (DEV-16)
export interface ConvertirDevisResult {
  chantier_id: number
  code_chantier: string
  budget_id: number
  nb_lots_transferes: number
  montant_total_ht: number
  devis_id: number
  devis_numero: string
}

// DEV-07: Pieces jointes devis
export interface PieceJointeDevis {
  id: number
  devis_id: number
  document_id: number | null
  lot_devis_id: number | null
  ligne_devis_id: number | null
  visible_client: boolean
  ordre: number
  nom_fichier: string | null
  type_fichier: string | null
  taille_octets: number | null
  mime_type: string | null
  created_at: string | null
}
