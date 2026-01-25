/**
 * Utilitaire de sanitization pour prevenir les attaques XSS
 * Utilise DOMPurify pour nettoyer le contenu HTML potentiellement dangereux
 */

import DOMPurify from 'dompurify'

/**
 * Configuration par defaut pour DOMPurify
 * - Autorise uniquement les balises de formatage basique
 * - Bloque tous les attributs d'evenements (onclick, onerror, etc.)
 */
const DEFAULT_CONFIG = {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'span'],
  ALLOWED_ATTR: ['href', 'target', 'rel', 'class'],
  ALLOW_DATA_ATTR: false,
  ADD_ATTR: ['target'],
  FORBID_TAGS: ['script', 'style', 'iframe', 'form', 'input', 'object', 'embed'],
  FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur'],
}

/**
 * Sanitize du contenu HTML pour un affichage securise
 * @param dirty - Contenu HTML potentiellement dangereux
 * @param config - Configuration optionnelle de DOMPurify
 * @returns Contenu HTML nettoye
 */
export function sanitizeHTML(dirty: string, config?: Record<string, unknown>): string {
  return DOMPurify.sanitize(dirty, config ?? DEFAULT_CONFIG)
}

/**
 * Sanitize du texte brut - supprime toutes les balises HTML
 * @param dirty - Texte potentiellement dangereux
 * @returns Texte sans aucune balise HTML
 */
export function sanitizeText(dirty: string): string {
  return DOMPurify.sanitize(dirty, { ALLOWED_TAGS: [], ALLOWED_ATTR: [] })
}

/**
 * Sanitize d'une URL pour prevenir les attaques javascript:
 * @param url - URL potentiellement dangereuse
 * @returns URL securisee ou chaine vide si dangereuse
 */
export function sanitizeURL(url: string): string {
  const trimmed = url.trim().toLowerCase()

  // Bloquer les protocoles dangereux
  const dangerousProtocols = ['javascript:', 'data:', 'vbscript:']
  if (dangerousProtocols.some((protocol) => trimmed.startsWith(protocol))) {
    return ''
  }

  return url
}

/**
 * Echappe les caracteres speciaux HTML pour un affichage en texte brut
 * @param text - Texte a echapper
 * @returns Texte echappe
 */
export function escapeHTML(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  }
  return text.replace(/[&<>"']/g, (char) => map[char])
}

export default {
  sanitizeHTML,
  sanitizeText,
  sanitizeURL,
  escapeHTML,
}
