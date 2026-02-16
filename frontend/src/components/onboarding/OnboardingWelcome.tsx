/**
 * OnboardingWelcome - Écran de bienvenue au premier lancement
 * Propose de commencer le tour guidé avec ou sans mode démo
 */

import { Sparkles, Play, TestTube } from 'lucide-react'
import type { UserRole } from '../../types'
import { ROLES } from '../../types'

interface OnboardingWelcomeProps {
  role: UserRole
  onStartTour: () => void
  onStartTourWithDemo: () => void
  onSkip: () => void
}

export default function OnboardingWelcome({
  role,
  onStartTour,
  onStartTourWithDemo,
  onSkip,
}: OnboardingWelcomeProps) {
  const roleLabel = ROLES[role]?.label || 'Utilisateur'

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/60 z-[10000] flex items-center justify-center p-4">
        {/* Modal */}
        <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-8 animate-fadeIn">
          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
          </div>

          {/* Content */}
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-3">
            Bienvenue sur Hub Chantier
          </h2>
          <p className="text-gray-600 text-center mb-6">
            Vous êtes connecté en tant que <strong>{roleLabel}</strong>.
            <br />
            Voulez-vous découvrir l'application avec un guide interactif ?
          </p>

          {/* Options */}
          <div className="space-y-3 mb-6">
            {/* Option 1: Démo */}
            <button
              onClick={onStartTourWithDemo}
              className="w-full p-4 border-2 border-primary-300 bg-primary-50 rounded-xl hover:border-primary-500 hover:bg-primary-100 transition-all text-left group"
            >
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                  <TestTube className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-gray-900 mb-1">
                    Essayer avec des données de démo
                  </div>
                  <div className="text-sm text-gray-600">
                    Recommandé • Découvrez l'app avec des chantiers et utilisateurs fictifs
                  </div>
                </div>
              </div>
            </button>

            {/* Option 2: Sans démo */}
            <button
              onClick={onStartTour}
              className="w-full p-4 border-2 border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50 transition-all text-left"
            >
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Play className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-gray-900 mb-1">
                    Commencer directement
                  </div>
                  <div className="text-sm text-gray-600">
                    Suivre le guide sans données de démo
                  </div>
                </div>
              </div>
            </button>
          </div>

          {/* Skip */}
          <button
            onClick={onSkip}
            className="w-full text-gray-500 hover:text-gray-700 text-sm font-medium transition-colors"
          >
            Passer le guide
          </button>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </>
  )
}
