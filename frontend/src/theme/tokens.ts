/**
 * Design Tokens - Hub Chantier
 * Système de tokens centralisé pour une cohérence visuelle
 *
 * Usage: Ces tokens sont injectés dans Tailwind via tailwind.config.js
 * et utilisables comme classes: bg-primary, text-success, border-neutral-border, etc.
 */

/**
 * Palette de couleurs sémantiques
 * Basée sur les couleurs actuelles de l'application
 */
export const colors = {
  // Couleur primaire (bleu) - Actions principales, navigation, liens
  primary: {
    DEFAULT: '#2563eb',      // primary-600
    hover: '#1d4ed8',        // primary-700
    active: '#1e40af',       // primary-800
    light: '#eff6ff',        // primary-50
    lighter: '#dbeafe',      // primary-100
  },

  // Couleur secondaire (amber) - Actions secondaires, accents
  secondary: {
    DEFAULT: '#f59e0b',      // amber-400
    hover: '#d97706',        // amber-500 (secondary-500)
    active: '#b45309',       // amber-600 (secondary-600)
    light: '#fef3c7',        // amber-50 (secondary-50)
  },

  // Couleur de succès (vert) - Confirmations, états positifs
  success: {
    DEFAULT: '#22c55e',      // green-500
    hover: '#16a34a',        // green-600
    light: '#dcfce7',        // green-100
    text: '#166534',         // green-800
  },

  // Couleur de danger (rouge) - Erreurs, suppressions, alertes critiques
  danger: {
    DEFAULT: '#ef4444',      // red-500
    hover: '#dc2626',        // red-600
    active: '#b91c1c',       // red-800
    light: '#fee2e2',        // red-100
    text: '#991b1b',         // red-800
  },

  // Couleur d'avertissement (amber) - Warnings, actions qui nécessitent attention
  warning: {
    DEFAULT: '#f59e0b',      // amber-500
    hover: '#d97706',        // amber-600
    light: '#fef3c7',        // amber-100
    text: '#92400e',         // amber-800
  },

  // Couleur d'information (bleu) - Messages informatifs, tooltips
  info: {
    DEFAULT: '#3b82f6',      // blue-500
    hover: '#2563eb',        // blue-600
    light: '#dbeafe',        // blue-100
    text: '#1e40af',         // blue-800
  },

  // Couleurs neutres - Textes, bordures, backgrounds
  neutral: {
    // Surfaces
    'surface-primary': '#ffffff',    // Fond principal (cards, modals)
    'surface-secondary': '#f9fafb',  // gray-50 - Fond secondaire
    'surface-tertiary': '#f3f4f6',   // gray-100 - Fond tertiaire

    // Bordures
    border: '#e5e7eb',               // gray-200 - Bordure par défaut
    'border-light': '#f3f4f6',       // gray-100 - Bordure légère
    'border-dark': '#d1d5db',        // gray-300 - Bordure accentuée

    // Textes
    text: '#374151',                 // gray-700 - Texte principal
    'text-secondary': '#6b7280',     // gray-600 - Texte secondaire
    'text-muted': '#9ca3af',         // gray-500 - Texte désactivé/placeholder
    'text-inverse': '#ffffff',       // Texte sur fond sombre

    // États
    hover: '#f3f4f6',                // gray-100 - Hover state
    active: '#e5e7eb',               // gray-200 - Active/pressed state
    disabled: '#f9fafb',             // gray-50 - Disabled background
    skeleton: '#e5e7eb',             // gray-200 - Loading skeleton
  },

  // Statuts chantier (couleurs métier spécifiques)
  chantier: {
    planifie: '#6366f1',    // indigo
    'en-cours': '#22c55e',  // green
    pause: '#f59e0b',       // amber
    termine: '#6b7280',     // gray
    annule: '#ef4444',      // red
  },

  // Statuts devis (couleurs métier spécifiques)
  devis: {
    brouillon: '#94a3b8',   // slate
    envoye: '#3b82f6',      // blue
    accepte: '#22c55e',     // green
    refuse: '#ef4444',      // red
    expire: '#f59e0b',      // amber
  },
} as const

/**
 * Espacements (optionnel - Tailwind a déjà un bon système)
 * Peut être étendu si besoin de valeurs custom
 */
export const spacing = {
  // Conserve les espacements Tailwind par défaut
  // Ajouter ici uniquement des valeurs custom si nécessaire
} as const

/**
 * Border radius (optionnel - Tailwind a déjà un bon système)
 * Valeurs actuelles utilisées dans les composants
 */
export const borderRadius = {
  card: '1rem',        // 16px - rounded-2xl utilisé dans Card
  button: '0.5rem',    // 8px - rounded-lg utilisé dans Button
  badge: '9999px',     // rounded-full utilisé dans Badge
  input: '0.5rem',     // 8px - rounded-lg standard
} as const

/**
 * Type exports pour TypeScript
 */
export type ColorToken = typeof colors
export type SpacingToken = typeof spacing
export type BorderRadiusToken = typeof borderRadius
