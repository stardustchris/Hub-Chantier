/**
 * Constantes partagees de l'application
 *
 * Ce fichier centralise les valeurs magiques pour:
 * - Faciliter la maintenance
 * - Assurer la coherence dans toute l'application
 * - Permettre la configuration facile
 */

// =============================================================================
// Pagination
// =============================================================================

export const PAGINATION = {
  /** Nombre d'elements par page par defaut */
  DEFAULT_PAGE_SIZE: 20,
  /** Taille de page pour les grilles de cartes */
  CARD_GRID_PAGE_SIZE: 12,
  /** Taille de page pour les listes compactes */
  COMPACT_LIST_PAGE_SIZE: 50,
  /** Limite maximale pour les requetes API */
  MAX_API_LIMIT: 100,
} as const

// =============================================================================
// Durees et timeouts (en millisecondes)
// =============================================================================

export const DURATIONS: Record<string, number> = {
  /** Duree par defaut des notifications toast */
  TOAST_DEFAULT: 5000,
  /** Duree des notifications d'action annulable */
  TOAST_UNDO: 5000,
  /** Delai avant masquage automatique des toasts de succes */
  TOAST_SUCCESS: 3000,
  /** Debounce pour la recherche */
  SEARCH_DEBOUNCE: 300,
  /** Timeout pour les animations */
  ANIMATION_DURATION: 200,
  /** Intervalle de rafraichissement automatique (5 min) */
  AUTO_REFRESH_INTERVAL: 5 * 60 * 1000,
  /** Duree de validite du cache (5 min) */
  CACHE_TTL: 5 * 60 * 1000,
}

// =============================================================================
// Limites de validation
// =============================================================================

export const VALIDATION = {
  /** Longueur minimale du mot de passe */
  PASSWORD_MIN_LENGTH: 8,
  /** Longueur minimale pour la connexion */
  PASSWORD_LOGIN_MIN_LENGTH: 6,
  /** Longueur maximale des noms */
  NAME_MAX_LENGTH: 50,
  /** Longueur maximale des descriptions */
  DESCRIPTION_MAX_LENGTH: 500,
  /** Longueur maximale des commentaires */
  COMMENT_MAX_LENGTH: 2000,
  /** Longueur maximale du code chantier */
  CODE_MAX_LENGTH: 20,
  /** Longueur maximale d'une adresse */
  ADDRESS_MAX_LENGTH: 200,
  /** Longueur maximale d'une ville */
  CITY_MAX_LENGTH: 100,
  /** Longueur du code postal francais */
  POSTAL_CODE_LENGTH: 5,
} as const

// =============================================================================
// Couleurs par defaut
// =============================================================================

export const COLORS = {
  /** Couleur par defaut pour les utilisateurs */
  DEFAULT_USER: '#3498DB',
  /** Couleur par defaut pour les chantiers */
  DEFAULT_CHANTIER: '#3498DB',
  /** Couleurs predefinies pour les chantiers */
  CHANTIER_PALETTE: [
    '#3498DB', // Bleu
    '#E74C3C', // Rouge
    '#27AE60', // Vert
    '#9B59B6', // Violet
    '#F39C12', // Orange
    '#1ABC9C', // Turquoise
    '#E67E22', // Orange fonce
    '#2ECC71', // Vert clair
  ] as const,
} as const

// =============================================================================
// Horaires par defaut
// =============================================================================

export const SCHEDULE = {
  /** Heure de debut par defaut */
  DEFAULT_START_HOUR: 8,
  /** Heure de fin par defaut */
  DEFAULT_END_HOUR: 17,
  /** Duree de journee standard (heures) */
  STANDARD_DAY_HOURS: 8,
  /** Nombre de jours dans une semaine de travail */
  WORK_DAYS_PER_WEEK: 5,
} as const

// =============================================================================
// Tailles d'interface
// =============================================================================

export const UI = {
  /** Largeur minimale pour affichage desktop */
  BREAKPOINT_DESKTOP: 1024,
  /** Largeur minimale pour affichage tablette */
  BREAKPOINT_TABLET: 768,
  /** Nombre de colonnes dans la grille des cartes */
  GRID_COLUMNS: {
    MOBILE: 1,
    TABLET: 2,
    DESKTOP: 3,
    LARGE: 4,
  },
} as const

// =============================================================================
// Limites de fichiers
// =============================================================================

export const FILES = {
  /** Taille maximale d'upload en octets (10 MB) */
  MAX_UPLOAD_SIZE: 10 * 1024 * 1024,
  /** Types de fichiers acceptes pour les images */
  ACCEPTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'] as const,
  /** Types de fichiers acceptes pour les documents */
  ACCEPTED_DOCUMENT_TYPES: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] as const,
} as const
