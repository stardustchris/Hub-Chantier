/**
 * Service de gestion du consentement RGPD
 * Gère le stockage et la validation des consentements utilisateur
 */

export type ConsentType = 'geolocation' | 'analytics' | 'notifications'

interface ConsentRecord {
  type: ConsentType
  granted: boolean
  timestamp: string
  version: string
}

interface ConsentStorage {
  consents: ConsentRecord[]
  lastUpdated: string
}

const CONSENT_STORAGE_KEY = 'hub_chantier_rgpd_consents'
const CONSENT_VERSION = '1.0'

/**
 * Charge les consentements depuis le localStorage
 */
function loadConsents(): ConsentStorage | null {
  try {
    const stored = localStorage.getItem(CONSENT_STORAGE_KEY)
    if (!stored) return null

    const parsed = JSON.parse(stored) as ConsentStorage
    // Validation basique du schema
    if (!parsed.consents || !Array.isArray(parsed.consents)) {
      localStorage.removeItem(CONSENT_STORAGE_KEY)
      return null
    }
    return parsed
  } catch {
    localStorage.removeItem(CONSENT_STORAGE_KEY)
    return null
  }
}

/**
 * Sauvegarde les consentements dans le localStorage
 */
function saveConsents(storage: ConsentStorage): void {
  try {
    localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify(storage))
  } catch {
    // Silently fail si localStorage non disponible
  }
}

export const consentService = {
  /**
   * Vérifie si un consentement a été donné
   */
  hasConsent(type: ConsentType): boolean {
    const storage = loadConsents()
    if (!storage) return false

    const consent = storage.consents.find(c => c.type === type && c.version === CONSENT_VERSION)
    return consent?.granted ?? false
  },

  /**
   * Vérifie si un consentement a déjà été demandé (peu importe la réponse)
   */
  wasAsked(type: ConsentType): boolean {
    const storage = loadConsents()
    if (!storage) return false

    return storage.consents.some(c => c.type === type && c.version === CONSENT_VERSION)
  },

  /**
   * Enregistre un consentement
   */
  setConsent(type: ConsentType, granted: boolean): void {
    const storage = loadConsents() || { consents: [], lastUpdated: '' }

    // Retirer l'ancien consentement de ce type
    storage.consents = storage.consents.filter(c => c.type !== type)

    // Ajouter le nouveau
    storage.consents.push({
      type,
      granted,
      timestamp: new Date().toISOString(),
      version: CONSENT_VERSION,
    })

    storage.lastUpdated = new Date().toISOString()
    saveConsents(storage)
  },

  /**
   * Révoque un consentement
   */
  revokeConsent(type: ConsentType): void {
    this.setConsent(type, false)
  },

  /**
   * Révoque tous les consentements (droit à l'oubli)
   */
  revokeAllConsents(): void {
    localStorage.removeItem(CONSENT_STORAGE_KEY)
  },

  /**
   * Récupère tous les consentements pour affichage
   */
  getAllConsents(): ConsentRecord[] {
    const storage = loadConsents()
    return storage?.consents ?? []
  },

  /**
   * Récupère le timestamp du dernier consentement pour un type
   */
  getConsentTimestamp(type: ConsentType): string | null {
    const storage = loadConsents()
    if (!storage) return null

    const consent = storage.consents.find(c => c.type === type && c.version === CONSENT_VERSION)
    return consent?.timestamp ?? null
  },
}

export default consentService
