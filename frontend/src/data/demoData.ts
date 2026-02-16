/**
 * Données de démonstration pour l'onboarding
 * Permet aux utilisateurs de tester l'app sans conséquence
 */

import type {
  User,
  Chantier,
  Affectation,
  Pointage,
  Post,
} from '../types'

// ===== UTILISATEURS DE DÉMO =====

export const demoUsers: User[] = [
  {
    id: 'demo-user-1',
    email: 'admin@demo.fr',
    nom: 'Dupont',
    prenom: 'Pierre',
    role: 'admin',
    type_utilisateur: 'cadre',
    telephone: '06 12 34 56 78',
    metier: 'administratif',
    taux_horaire: 35,
    code_utilisateur: 'ADM001',
    couleur: '#9B59B6',
    is_active: true,
    created_at: '2024-01-01T08:00:00Z',
  },
  {
    id: 'demo-user-2',
    email: 'conducteur@demo.fr',
    nom: 'Martin',
    prenom: 'Sophie',
    role: 'conducteur',
    type_utilisateur: 'cadre',
    telephone: '06 23 45 67 89',
    metier: 'administratif',
    taux_horaire: 32,
    code_utilisateur: 'CDT001',
    couleur: '#3498DB',
    is_active: true,
    created_at: '2024-01-01T08:00:00Z',
  },
  {
    id: 'demo-user-3',
    email: 'chef@demo.fr',
    nom: 'Bernard',
    prenom: 'Luc',
    role: 'chef_chantier',
    type_utilisateur: 'employe',
    telephone: '06 34 56 78 90',
    metier: 'macon',
    taux_horaire: 25,
    code_utilisateur: 'CHF001',
    couleur: '#27AE60',
    is_active: true,
    created_at: '2024-01-01T08:00:00Z',
  },
  {
    id: 'demo-user-4',
    email: 'compagnon1@demo.fr',
    nom: 'Moreau',
    prenom: 'Jean',
    role: 'compagnon',
    type_utilisateur: 'employe',
    telephone: '06 45 67 89 01',
    metier: 'coffreur',
    taux_horaire: 18,
    code_utilisateur: 'CMP001',
    couleur: '#E67E22',
    is_active: true,
    created_at: '2024-01-01T08:00:00Z',
  },
  {
    id: 'demo-user-5',
    email: 'compagnon2@demo.fr',
    nom: 'Petit',
    prenom: 'Marc',
    role: 'compagnon',
    type_utilisateur: 'employe',
    telephone: '06 56 78 90 12',
    metier: 'ferrailleur',
    taux_horaire: 18,
    code_utilisateur: 'CMP002',
    couleur: '#1ABC9C',
    is_active: true,
    created_at: '2024-01-01T08:00:00Z',
  },
]

// ===== CHANTIERS DE DÉMO =====

export const demoChantiers: Chantier[] = [
  {
    id: 'demo-chantier-1',
    code: 'CH-2024-001',
    nom: 'Rénovation Maison Martin',
    adresse: '12 Rue des Lilas, 75015 Paris',
    statut: 'en_cours',
    couleur: '#3498DB',
    contact_nom: 'M. Martin',
    contact_telephone: '06 11 22 33 44',
    heures_estimees: 320,
    date_debut_prevue: '2024-01-15',
    date_fin_prevue: '2024-04-30',
    description: 'Rénovation complète d\'une maison individuelle : isolation, électricité, plomberie',
    conducteurs: [demoUsers[1]], // Sophie Martin
    chefs: [demoUsers[2]], // Luc Bernard
    ouvriers: [demoUsers[3], demoUsers[4]], // Jean Moreau, Marc Petit
    created_at: '2024-01-01T09:00:00Z',
    maitre_ouvrage: 'M. et Mme Martin',
  },
  {
    id: 'demo-chantier-2',
    code: 'CH-2024-002',
    nom: 'Extension Villa Dupont',
    adresse: '45 Avenue du Parc, 92100 Boulogne',
    statut: 'ouvert',
    couleur: '#27AE60',
    contact_nom: 'Mme Dupont',
    contact_telephone: '06 22 33 44 55',
    heures_estimees: 480,
    date_debut_prevue: '2024-03-01',
    date_fin_prevue: '2024-07-31',
    description: 'Extension de 40m² : construction d\'une véranda et aménagement extérieur',
    conducteurs: [demoUsers[1]], // Sophie Martin
    chefs: [],
    ouvriers: [],
    created_at: '2024-01-10T10:00:00Z',
    maitre_ouvrage: 'Mme Dupont',
  },
  {
    id: 'demo-chantier-3',
    code: 'CH-2023-015',
    nom: 'Réhabilitation Immeuble Centre',
    adresse: '8 Place de la République, 75011 Paris',
    statut: 'en_cours',
    couleur: '#E74C3C',
    contact_nom: 'Syndic Immobilière Paris',
    contact_telephone: '01 45 67 89 01',
    heures_estimees: 1200,
    date_debut_prevue: '2023-10-01',
    date_fin_prevue: '2024-03-31',
    description: 'Réhabilitation façade et parties communes d\'un immeuble de 6 étages',
    conducteurs: [demoUsers[1]], // Sophie Martin
    chefs: [demoUsers[2]], // Luc Bernard
    ouvriers: [demoUsers[3], demoUsers[4]], // Jean Moreau, Marc Petit
    created_at: '2023-09-15T08:00:00Z',
    maitre_ouvrage: 'Copropriété 8 Place de la République',
  },
]

// ===== AFFECTATIONS DE DÉMO (semaine courante) =====

// Calcul des dates de la semaine courante
const today = new Date()
const dayOfWeek = today.getDay()
const monday = new Date(today)
monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1))

const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0]
}

const getMondayDate = () => formatDate(monday)
const getTuesdayDate = () => {
  const tuesday = new Date(monday)
  tuesday.setDate(monday.getDate() + 1)
  return formatDate(tuesday)
}
const getWednesdayDate = () => {
  const wednesday = new Date(monday)
  wednesday.setDate(monday.getDate() + 2)
  return formatDate(wednesday)
}
// getThursdayDate disponible si besoin pour demo
// const getThursdayDate = () => { ... }
const getFridayDate = () => {
  const friday = new Date(monday)
  friday.setDate(monday.getDate() + 4)
  return formatDate(friday)
}

export const demoAffectations: Affectation[] = [
  // Luc Bernard - Chef de chantier
  {
    id: 'demo-aff-1',
    utilisateur_id: 'demo-user-3',
    chantier_id: 'demo-chantier-1',
    date: getMondayDate(),
    heure_debut: '08:00',
    heure_fin: '17:00',
    type_affectation: 'unique',
    created_at: '2024-01-01T08:00:00Z',
    updated_at: '2024-01-01T08:00:00Z',
    created_by: 'demo-user-2',
    utilisateur_nom: 'Luc Bernard',
    utilisateur_couleur: '#27AE60',
    utilisateur_metier: 'macon',
    chantier_nom: 'Rénovation Maison Martin',
    chantier_couleur: '#3498DB',
  },
  {
    id: 'demo-aff-2',
    utilisateur_id: 'demo-user-3',
    chantier_id: 'demo-chantier-3',
    date: getTuesdayDate(),
    heure_debut: '08:00',
    heure_fin: '17:00',
    type_affectation: 'unique',
    created_at: '2024-01-01T08:00:00Z',
    updated_at: '2024-01-01T08:00:00Z',
    created_by: 'demo-user-2',
    utilisateur_nom: 'Luc Bernard',
    utilisateur_couleur: '#27AE60',
    utilisateur_metier: 'macon',
    chantier_nom: 'Réhabilitation Immeuble Centre',
    chantier_couleur: '#E74C3C',
  },
  // Jean Moreau - Compagnon
  {
    id: 'demo-aff-3',
    utilisateur_id: 'demo-user-4',
    chantier_id: 'demo-chantier-1',
    date: getMondayDate(),
    heure_debut: '08:00',
    heure_fin: '17:00',
    type_affectation: 'recurrente',
    jours_recurrence: [0, 1, 2, 3, 4], // Lun-Ven
    created_at: '2024-01-01T08:00:00Z',
    updated_at: '2024-01-01T08:00:00Z',
    created_by: 'demo-user-2',
    utilisateur_nom: 'Jean Moreau',
    utilisateur_couleur: '#E67E22',
    utilisateur_metier: 'coffreur',
    chantier_nom: 'Rénovation Maison Martin',
    chantier_couleur: '#3498DB',
  },
  // Marc Petit - Compagnon
  {
    id: 'demo-aff-4',
    utilisateur_id: 'demo-user-5',
    chantier_id: 'demo-chantier-3',
    date: getWednesdayDate(),
    heure_debut: '08:00',
    heure_fin: '17:00',
    type_affectation: 'unique',
    created_at: '2024-01-01T08:00:00Z',
    updated_at: '2024-01-01T08:00:00Z',
    created_by: 'demo-user-2',
    utilisateur_nom: 'Marc Petit',
    utilisateur_couleur: '#1ABC9C',
    utilisateur_metier: 'ferrailleur',
    chantier_nom: 'Réhabilitation Immeuble Centre',
    chantier_couleur: '#E74C3C',
  },
]

// ===== POINTAGES DE DÉMO (semaine courante) =====

export const demoPointages: Pointage[] = [
  // Jean Moreau - Lundi
  {
    id: 1001,
    utilisateur_id: 4,
    chantier_id: 1,
    date_pointage: getMondayDate(),
    heures_normales: '08:00',
    heures_supplementaires: '00:00',
    total_heures: '08:00',
    total_heures_decimal: 8.0,
    statut: 'valide',
    created_by: 4,
    created_at: getMondayDate() + 'T18:00:00Z',
    updated_at: getMondayDate() + 'T18:00:00Z',
    utilisateur_nom: 'Jean Moreau',
    chantier_nom: 'Rénovation Maison Martin',
    chantier_couleur: '#3498DB',
    is_editable: false,
  },
  // Jean Moreau - Mardi
  {
    id: 1002,
    utilisateur_id: 4,
    chantier_id: 1,
    date_pointage: getTuesdayDate(),
    heures_normales: '08:00',
    heures_supplementaires: '01:00',
    total_heures: '09:00',
    total_heures_decimal: 9.0,
    statut: 'valide',
    created_by: 4,
    created_at: getTuesdayDate() + 'T18:00:00Z',
    updated_at: getTuesdayDate() + 'T18:00:00Z',
    utilisateur_nom: 'Jean Moreau',
    chantier_nom: 'Rénovation Maison Martin',
    chantier_couleur: '#3498DB',
    is_editable: false,
  },
  // Marc Petit - Mercredi
  {
    id: 1003,
    utilisateur_id: 5,
    chantier_id: 3,
    date_pointage: getWednesdayDate(),
    heures_normales: '07:30',
    heures_supplementaires: '00:00',
    total_heures: '07:30',
    total_heures_decimal: 7.5,
    statut: 'soumis',
    created_by: 5,
    created_at: getWednesdayDate() + 'T17:00:00Z',
    updated_at: getWednesdayDate() + 'T17:00:00Z',
    utilisateur_nom: 'Marc Petit',
    chantier_nom: 'Réhabilitation Immeuble Centre',
    chantier_couleur: '#E74C3C',
    is_editable: true,
  },
]

// ===== POSTS DE DÉMO (Dashboard) =====

export const demoPosts: Post[] = [
  {
    id: 'demo-post-1',
    contenu: 'Début des travaux de rénovation chez M. Martin ce lundi. Tout le monde est prêt !',
    type: 'message',
    auteur: demoUsers[2], // Luc Bernard
    target_type: 'tous',
    medias: [],
    commentaires: [],
    likes: [],
    likes_count: 3,
    commentaires_count: 0,
    is_pinned: false,
    is_urgent: false,
    created_at: getMondayDate() + 'T07:30:00Z',
  },
  {
    id: 'demo-post-2',
    contenu: 'URGENT : Livraison de béton reportée à demain matin sur le chantier Immeuble Centre',
    type: 'urgent',
    auteur: demoUsers[1], // Sophie Martin
    target_type: 'chantiers',
    target_chantiers: [demoChantiers[2]],
    medias: [],
    commentaires: [],
    likes: [],
    likes_count: 0,
    commentaires_count: 1,
    is_pinned: true,
    is_urgent: true,
    created_at: getTuesdayDate() + 'T14:20:00Z',
    pinned_until: getFridayDate() + 'T23:59:59Z',
  },
]

// ===== STRUCTURE GLOBALE DES DONNÉES DE DÉMO =====

export interface DemoData {
  users: User[]
  chantiers: Chantier[]
  affectations: Affectation[]
  pointages: Pointage[]
  posts: Post[]
}

export const demoData: DemoData = {
  users: demoUsers,
  chantiers: demoChantiers,
  affectations: demoAffectations,
  pointages: demoPointages,
  posts: demoPosts,
}
