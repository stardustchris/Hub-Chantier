/**
 * Utilitaires de validation et formatage de téléphone international (USR-08).
 */

// Codes pays courants avec format
export const COUNTRY_CODES = [
  { code: '+33', country: 'France', flag: '🇫🇷', format: '# ## ## ## ##' },
  { code: '+32', country: 'Belgique', flag: '🇧🇪', format: '### ## ## ##' },
  { code: '+41', country: 'Suisse', flag: '🇨🇭', format: '## ### ## ##' },
  { code: '+352', country: 'Luxembourg', flag: '🇱🇺', format: '### ### ###' },
  { code: '+377', country: 'Monaco', flag: '🇲🇨', format: '## ## ## ##' },
  { code: '+34', country: 'Espagne', flag: '🇪🇸', format: '### ### ###' },
  { code: '+39', country: 'Italie', flag: '🇮🇹', format: '### ### ####' },
  { code: '+49', country: 'Allemagne', flag: '🇩🇪', format: '#### ######' },
  { code: '+44', country: 'Royaume-Uni', flag: '🇬🇧', format: '#### ######' },
  { code: '+1', country: 'USA/Canada', flag: '🇺🇸', format: '(###) ###-####' },
] as const

// Expression régulière pour téléphone international
// Accepte: +33 6 12 34 56 78, +33612345678, 06 12 34 56 78, etc.
const PHONE_REGEX = /^(?:\+?[1-9]\d{0,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$/

/**
 * Valide un numéro de téléphone international.
 */
export function isValidPhone(phone: string): boolean {
  if (!phone || phone.trim().length === 0) return true // Optionnel
  const cleaned = phone.replace(/\s/g, '')
  if (cleaned.length < 8 || cleaned.length > 15) return false
  return PHONE_REGEX.test(phone)
}

/**
 * Normalise un numéro de téléphone (retire espaces et tirets).
 */
export function normalizePhone(phone: string): string {
  return phone.replace(/[-.\s()]/g, '')
}

/**
 * Formate un téléphone pour affichage.
 * @example formatPhone('+33612345678') => '+33 6 12 34 56 78'
 */
export function formatPhone(phone: string): string {
  const normalized = normalizePhone(phone)

  // Détection France
  if (normalized.startsWith('+33') || normalized.startsWith('33')) {
    const num = normalized.startsWith('+33') ? normalized.slice(3) : normalized.slice(2)
    if (num.length === 9) {
      return `+33 ${num[0]} ${num.slice(1, 3)} ${num.slice(3, 5)} ${num.slice(5, 7)} ${num.slice(7, 9)}`
    }
  }

  // Téléphone français sans indicatif (0612345678)
  if (normalized.startsWith('0') && normalized.length === 10) {
    return `${normalized[0]}${normalized[1]} ${normalized.slice(2, 4)} ${normalized.slice(4, 6)} ${normalized.slice(6, 8)} ${normalized.slice(8, 10)}`
  }

  // Autres : retourne tel quel avec espaces
  return phone
}

/**
 * Détecte le pays d'un numéro de téléphone.
 */
export function detectCountry(phone: string): typeof COUNTRY_CODES[number] | null {
  const normalized = normalizePhone(phone)

  for (const country of COUNTRY_CODES) {
    const codeWithoutPlus = country.code.slice(1)
    if (normalized.startsWith(country.code) || normalized.startsWith(codeWithoutPlus)) {
      return country
    }
  }

  // Par défaut France si commence par 0
  if (normalized.startsWith('0')) {
    return COUNTRY_CODES[0]
  }

  return null
}

/**
 * Message d'erreur de validation.
 */
export function getPhoneValidationError(phone: string): string | null {
  if (!phone || phone.trim().length === 0) return null

  const cleaned = normalizePhone(phone)

  if (cleaned.length < 8) {
    return 'Le numéro est trop court (minimum 8 chiffres)'
  }

  if (cleaned.length > 15) {
    return 'Le numéro est trop long (maximum 15 chiffres)'
  }

  if (!PHONE_REGEX.test(phone)) {
    return 'Format de téléphone invalide'
  }

  return null
}
