/**
 * Utilitaires de formatage de dates centralisés
 * Évite la duplication de format() dans tout le codebase
 */

import { format, formatDistanceToNow, isToday, isYesterday, parseISO } from 'date-fns'
import { fr } from 'date-fns/locale'

/**
 * Formate une date au format complet français (ex: "24 janvier 2026")
 */
export function formatDateFull(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'dd MMMM yyyy', { locale: fr })
}

/**
 * Formate une date au format court (ex: "24/01/2026")
 */
export function formatDateShort(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'dd/MM/yyyy', { locale: fr })
}

/**
 * Formate une date avec l'heure (ex: "24 janvier 2026 a 14:30")
 */
export function formatDateTime(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, "dd MMMM yyyy 'a' HH:mm", { locale: fr })
}

/**
 * Formate une date relative (ex: "il y a 2 heures")
 */
export function formatRelative(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return formatDistanceToNow(d, { addSuffix: true, locale: fr })
}

/**
 * Formate une date intelligemment selon sa proximité
 * - Aujourd'hui: "Aujourd'hui a 14:30"
 * - Hier: "Hier a 14:30"
 * - Cette semaine: "Lundi a 14:30"
 * - Plus ancien: "24 janvier 2026"
 */
export function formatDateSmart(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date

  if (isToday(d)) {
    return `Aujourd'hui a ${format(d, 'HH:mm', { locale: fr })}`
  }

  if (isYesterday(d)) {
    return `Hier a ${format(d, 'HH:mm', { locale: fr })}`
  }

  // Dans les 7 derniers jours
  const daysDiff = Math.floor((Date.now() - d.getTime()) / (1000 * 60 * 60 * 24))
  if (daysDiff < 7) {
    return format(d, "EEEE 'a' HH:mm", { locale: fr })
  }

  return formatDateFull(d)
}

/**
 * Formate une heure (ex: "14:30")
 */
export function formatTime(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'HH:mm', { locale: fr })
}

/**
 * Formate un mois et année (ex: "Janvier 2026")
 */
export function formatMonthYear(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'MMMM yyyy', { locale: fr })
}

/**
 * Formate un jour de la semaine (ex: "Lundi")
 */
export function formatDayName(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'EEEE', { locale: fr })
}

/**
 * Formate une date au format jour mois abrégé (ex: "24 janv.")
 */
export function formatDateDayMonth(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'dd MMM', { locale: fr })
}

/**
 * Formate une date au format jour/mois (ex: "24/01")
 */
export function formatDateDayMonthShort(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'dd/MM', { locale: fr })
}

/**
 * Formate une date au format jour mois abrégé année (ex: "24 janv. 2026")
 */
export function formatDateDayMonthYear(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'dd MMM yyyy', { locale: fr })
}

/**
 * Formate une date complète avec heure (ex: "24/01/2026 14:30")
 */
export function formatDateTimeShort(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'dd/MM/yyyy HH:mm', { locale: fr })
}

/**
 * Formate une date jour mois abrégé année avec heure (ex: "24 janv. 2026 14:30")
 */
export function formatDateDayMonthYearTime(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'dd MMM yyyy HH:mm', { locale: fr })
}

/**
 * Formate une durée en heures:minutes (ex: "07:30")
 */
export function formatDuration(hours: number, minutes: number = 0): string {
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
}

/**
 * Formate une date au format jour de la semaine complet avec date (ex: "vendredi 24 janvier 2026")
 */
export function formatDateWeekdayFull(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'EEEE d MMMM yyyy', { locale: fr })
}

/**
 * Parse une chaîne "HH:mm" en minutes totales
 */
export function parseTimeToMinutes(time: string): number {
  const [hours, minutes] = time.split(':').map(Number)
  return hours * 60 + minutes
}

/**
 * Convertit des minutes en format "HH:mm"
 */
export function minutesToTime(totalMinutes: number): string {
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return formatDuration(hours, minutes)
}

/**
 * Formate une date relative courte pour les feeds/posts
 * - < 1 min: "A l'instant"
 * - < 1h: "Il y a X min"
 * - < 24h: "Il y a Xh"
 * - < 7j: "Il y a Xj"
 * - Plus ancien: date courte (ex: "24/01/2026")
 */
export function formatRelativeShort(date: Date | string): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return "A l'instant"
  if (diffMins < 60) return `Il y a ${diffMins} min`
  if (diffHours < 24) return `Il y a ${diffHours}h`
  if (diffDays < 7) return `Il y a ${diffDays}j`
  return formatDateShort(d)
}
