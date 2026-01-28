/**
 * Banner RGPD pour demander le consentement utilisateur
 *
 * Conformité RGPD :
 * - Demande explicite de consentement avant toute collecte de données
 * - Options granulaires (géolocalisation, notifications, analytics)
 * - Possibilité de tout accepter ou tout refuser
 * - Possibilité de personnaliser les choix
 * - Ne se réaffiche pas si l'utilisateur a déjà répondu
 */

import { useState, useEffect } from 'react'
import { consentService, ConsentPreferences } from '../../services/consent'
import { logger } from '../../services/logger'

export function GDPRBanner() {
  const [showBanner, setShowBanner] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  const [preferences, setPreferences] = useState<ConsentPreferences>({
    geolocation: false,
    notifications: false,
    analytics: false,
    timestamp: null,
    ip_address: null,
    user_agent: null,
  })

  useEffect(() => {
    // Vérifier si le banner doit être affiché
    const checkConsents = async () => {
      try {
        const hasAnswered = await consentService.hasAnswered()
        const wasShown = consentService.wasBannerShown()

        // Afficher le banner si l'utilisateur n'a pas encore répondu ET pas déjà affiché dans cette session
        if (!hasAnswered && !wasShown) {
          setShowBanner(true)
          consentService.markBannerAsShown()
        }
      } catch (error) {
        logger.error('Error checking consents', error)
      }
    }

    checkConsents()
  }, [])

  const handleAcceptAll = async () => {
    try {
      await consentService.setConsents({
        geolocation: true,
        notifications: true,
        analytics: true,
      })
      setShowBanner(false)
      logger.info('User accepted all consents')
    } catch (error) {
      logger.error('Error accepting all consents', error)
    }
  }

  const handleRejectAll = async () => {
    try {
      await consentService.setConsents({
        geolocation: false,
        notifications: false,
        analytics: false,
      })
      setShowBanner(false)
      logger.info('User rejected all consents')
    } catch (error) {
      logger.error('Error rejecting all consents', error)
    }
  }

  const handleSavePreferences = async () => {
    try {
      await consentService.setConsents(preferences)
      setShowBanner(false)
      logger.info('User saved custom consents', preferences)
    } catch (error) {
      logger.error('Error saving custom consents', error)
    }
  }

  const togglePreference = (key: keyof ConsentPreferences) => {
    setPreferences(prev => ({ ...prev, [key]: !prev[key] }))
  }

  if (!showBanner) {
    return null
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white shadow-lg border-t-2 border-blue-500 z-50 animate-slide-up">
      <div className="container mx-auto px-4 py-4 max-w-4xl">
        {/* Banner principal */}
        <div className="flex flex-col gap-4">
          <div className="flex items-start gap-3">
            <div className="text-2xl">🍪</div>
            <div className="flex-1">
              <h3 className="font-bold text-lg mb-2">Protection de vos données personnelles</h3>
              <p className="text-sm text-gray-700">
                Nous respectons votre vie privée. Pour améliorer votre expérience, nous aimerions
                utiliser certaines fonctionnalités qui nécessitent votre consentement explicite :
                géolocalisation pour la météo, notifications pour les alertes, et analytics pour
                améliorer notre service.
              </p>
              <button
                type="button"
                onClick={() => setShowDetails(!showDetails)}
                className="text-blue-600 text-sm mt-2 underline hover:text-blue-800"
              >
                {showDetails ? 'Masquer les détails' : 'Personnaliser mes choix'}
              </button>
            </div>
          </div>

          {/* Options détaillées */}
          {showDetails && (
            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              <label className="flex items-start gap-3 cursor-pointer hover:bg-gray-100 p-2 rounded">
                <input
                  type="checkbox"
                  checked={preferences.geolocation}
                  onChange={() => togglePreference('geolocation')}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium">Géolocalisation</div>
                  <div className="text-sm text-gray-600">
                    Permet d&apos;afficher la météo locale et les alertes météo pour vos chantiers
                  </div>
                </div>
              </label>

              <label className="flex items-start gap-3 cursor-pointer hover:bg-gray-100 p-2 rounded">
                <input
                  type="checkbox"
                  checked={preferences.notifications}
                  onChange={() => togglePreference('notifications')}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium">Notifications push</div>
                  <div className="text-sm text-gray-600">
                    Recevez des alertes en cas de conditions météo dangereuses sur vos chantiers
                  </div>
                </div>
              </label>

              <label className="flex items-start gap-3 cursor-pointer hover:bg-gray-100 p-2 rounded">
                <input
                  type="checkbox"
                  checked={preferences.analytics}
                  onChange={() => togglePreference('analytics')}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium">Analytics</div>
                  <div className="text-sm text-gray-600">
                    Nous aide à comprendre comment vous utilisez l&apos;application pour l&apos;améliorer
                  </div>
                </div>
              </label>
            </div>
          )}

          {/* Boutons d'action */}
          <div className="flex flex-wrap gap-2 justify-end">
            {showDetails ? (
              <>
                <button
                  type="button"
                  onClick={handleRejectAll}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded border border-gray-300"
                >
                  Tout refuser
                </button>
                <button
                  type="button"
                  onClick={handleSavePreferences}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Enregistrer mes choix
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={handleRejectAll}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded border border-gray-300"
                >
                  Refuser
                </button>
                <button
                  type="button"
                  onClick={handleAcceptAll}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Tout accepter
                </button>
              </>
            )}
          </div>

          {/* Lien politique de confidentialité */}
          <p className="text-xs text-gray-500 text-center">
            En utilisant notre service, vous acceptez notre{' '}
            <a href="/privacy-policy" className="underline hover:text-gray-700">
              politique de confidentialité
            </a>
            . Vous pouvez modifier vos préférences à tout moment dans les paramètres.
          </p>
        </div>
      </div>
    </div>
  )
}
