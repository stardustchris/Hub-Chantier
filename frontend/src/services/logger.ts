/**
 * Service de logging centralise
 *
 * En developpement: affiche dans la console
 * En production: peut etre connecte a un service de monitoring (Sentry, etc.)
 *
 * Usage:
 *   import { logger } from '../services/logger'
 *   logger.error('Error loading data', error)
 *   logger.error('Error loading data', error, { showToast: true })
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

interface LogOptions {
  /** Contexte additionnel (ex: composant, action) */
  context?: string
  /** Afficher un toast a l'utilisateur (pour les erreurs user-facing) */
  showToast?: boolean
  /** Metadata additionnelle */
  metadata?: Record<string, unknown>
  /** ID du devis pour le contexte */
  devisId?: number
  /** ID de la piece jointe pour le contexte */
  pieceId?: number
  /** Visibilite (pour les pieces jointes) */
  visible?: boolean
  /** Nouveau statut (pour les transitions de statut) */
  newStatut?: string
  /** Nombre de fichiers (pour les uploads) */
  fileCount?: number
}

interface LogEntry {
  level: LogLevel
  message: string
  error?: Error | unknown
  timestamp: string
  options?: LogOptions
}

// Callbacks pour integration externe (toast, monitoring)
type LogCallback = (entry: LogEntry) => void
const callbacks: Set<LogCallback> = new Set()

/**
 * Enregistre un callback pour recevoir les logs
 * Utile pour integrer avec un systeme de toast ou monitoring
 */
export function onLog(callback: LogCallback): () => void {
  callbacks.add(callback)
  return () => callbacks.delete(callback)
}

function formatError(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return String(error)
}

function createLogEntry(
  level: LogLevel,
  message: string,
  error?: unknown,
  options?: LogOptions
): LogEntry {
  return {
    level,
    message,
    error,
    timestamp: new Date().toISOString(),
    options,
  }
}

function notifyCallbacks(entry: LogEntry): void {
  callbacks.forEach((callback) => {
    try {
      callback(entry)
    } catch {
      // Ignore callback errors to prevent infinite loops
    }
  })
}

const isDev = import.meta.env.DEV

export const logger = {
  /**
   * Log de debug (dev seulement)
   */
  debug(message: string, data?: unknown, options?: LogOptions): void {
    if (!isDev) return

    const entry = createLogEntry('debug', message, data, options)
    console.debug(`[DEBUG] ${message}`, data)
    notifyCallbacks(entry)
  },

  /**
   * Log d'information
   */
  info(message: string, data?: unknown, options?: LogOptions): void {
    const entry = createLogEntry('info', message, data, options)

    if (isDev) {
      console.info(`[INFO] ${message}`, data)
    }

    notifyCallbacks(entry)
  },

  /**
   * Log d'avertissement
   */
  warn(message: string, data?: unknown, options?: LogOptions): void {
    const entry = createLogEntry('warn', message, data, options)

    if (isDev) {
      console.warn(`[WARN] ${message}`, data)
    }

    notifyCallbacks(entry)
  },

  /**
   * Log d'erreur
   *
   * @param message - Message d'erreur descriptif
   * @param error - L'objet erreur (Error, string, ou autre)
   * @param options - Options (context, showToast, metadata)
   *
   * @example
   * // Simple
   * logger.error('Failed to load data', error)
   *
   * // Avec contexte
   * logger.error('Failed to load data', error, { context: 'DashboardPage' })
   *
   * // Avec toast pour l'utilisateur
   * logger.error('Failed to save', error, { showToast: true })
   */
  error(message: string, error?: unknown, options?: LogOptions): void {
    const entry = createLogEntry('error', message, error, options)
    const fullMessage = options?.context
      ? `[${options.context}] ${message}`
      : message

    if (isDev) {
      console.error(fullMessage, error)
    }

    // En production, on pourrait envoyer a un service de monitoring
    // if (!isDev && typeof window !== 'undefined') {
    //   Sentry.captureException(error, { extra: { message, ...options?.metadata } })
    // }

    notifyCallbacks(entry)
  },

  /**
   * Retourne le message d'erreur formatte pour affichage utilisateur
   */
  getUserMessage(error: unknown, fallback = 'Une erreur est survenue'): string {
    // En dev, on peut montrer plus de details
    if (isDev) {
      return formatError(error)
    }

    // En prod, seulement les erreurs metier
    if (error instanceof Error) {
      if (error.name === 'ValidationError' || error.name === 'BusinessError') {
        return error.message
      }
    }
    return fallback
  },
}

export default logger
