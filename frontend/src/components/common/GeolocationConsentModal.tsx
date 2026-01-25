import { X, MapPin, Shield, Info } from 'lucide-react'

interface GeolocationConsentModalProps {
  isOpen: boolean
  onAccept: () => void
  onDecline: () => void
  onClose: () => void
}

/**
 * Modal de consentement RGPD pour la géolocalisation
 * Affiche les informations requises par le RGPD (finalité, durée, droits)
 */
export function GeolocationConsentModal({
  isOpen,
  onAccept,
  onDecline,
  onClose,
}: GeolocationConsentModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          className="relative w-full max-w-md transform rounded-xl bg-white shadow-2xl transition-all"
          role="dialog"
          aria-modal="true"
          aria-labelledby="consent-title"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b px-6 py-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
                <MapPin className="h-5 w-5 text-blue-600" />
              </div>
              <h2 id="consent-title" className="text-lg font-semibold text-gray-900">
                Autorisation de localisation
              </h2>
            </div>
            <button
              onClick={onClose}
              className="rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              aria-label="Fermer"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-4">
            {/* Finalité */}
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-blue-500 shrink-0 mt-0.5" />
              <div>
                <h3 className="font-medium text-gray-900">Pourquoi cette demande ?</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Votre position geographique sera enregistree avec le formulaire pour
                  tracer le lieu de saisie. Cela permet de verifier que les formulaires
                  sont remplis sur le chantier concerne.
                </p>
              </div>
            </div>

            {/* Données collectées */}
            <div className="flex gap-3">
              <Shield className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
              <div>
                <h3 className="font-medium text-gray-900">Donnees collectees</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Uniquement vos coordonnees GPS (latitude/longitude) au moment de la
                  creation du formulaire. Aucun suivi continu de votre position.
                </p>
              </div>
            </div>

            {/* Durée de conservation */}
            <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600">
              <strong>Duree de conservation :</strong> Les coordonnees sont conservees
              avec le formulaire pendant 5 ans (obligation legale BTP).
            </div>

            {/* Droits */}
            <p className="text-xs text-gray-500">
              Conformement au RGPD, vous pouvez refuser sans impact sur l&apos;utilisation
              de l&apos;application. Vous pouvez modifier ce choix a tout moment dans les
              parametres. Pour exercer vos droits (acces, rectification, suppression),
              contactez votre administrateur.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 border-t px-6 py-4">
            <button
              onClick={onDecline}
              className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Refuser
            </button>
            <button
              onClick={onAccept}
              className="flex-1 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
            >
              Accepter
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GeolocationConsentModal
