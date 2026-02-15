/**
 * BatchActionsBar - Barre d'actions en batch pour la validation multiple de pointages
 * Affichée en position fixe en bas de page quand des items sont sélectionnés
 */

import { Check, X } from 'lucide-react'
import Button from '../ui/Button'

interface BatchActionsBarProps {
  selectedCount: number
  totalCount: number
  onSelectAll: () => void
  onDeselectAll: () => void
  onValidate: () => void
  onReject: () => void
  isValidating?: boolean
  isRejecting?: boolean
}

export default function BatchActionsBar({
  selectedCount,
  totalCount,
  onSelectAll,
  onDeselectAll,
  onValidate,
  onReject,
  isValidating = false,
  isRejecting = false,
}: BatchActionsBarProps) {
  const allSelected = selectedCount === totalCount && totalCount > 0

  // Ne pas afficher si aucune sélection
  if (selectedCount === 0) {
    return null
  }

  return (
    <div
      className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 animate-slide-up"
      role="toolbar"
      aria-label="Actions en lot"
    >
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between gap-4 flex-wrap">
        {/* Compteur et sélection */}
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-gray-900">
            {selectedCount} pointage{selectedCount > 1 ? 's' : ''} sélectionné{selectedCount > 1 ? 's' : ''}
          </span>
          <button
            onClick={allSelected ? onDeselectAll : onSelectAll}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium min-h-[44px] px-3"
            aria-label={allSelected ? 'Tout désélectionner' : 'Tout sélectionner'}
          >
            {allSelected ? 'Tout désélectionner' : `Tout sélectionner (${totalCount})`}
          </button>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <Button
            variant="primary"
            size="md"
            onClick={onValidate}
            loading={isValidating}
            disabled={isRejecting}
            icon={Check}
            aria-label={`Valider ${selectedCount} pointage${selectedCount > 1 ? 's' : ''}`}
          >
            Valider la sélection
          </Button>
          <Button
            variant="danger"
            size="md"
            onClick={onReject}
            loading={isRejecting}
            disabled={isValidating}
            icon={X}
            aria-label={`Refuser ${selectedCount} pointage${selectedCount > 1 ? 's' : ''}`}
          >
            Refuser la sélection
          </Button>
        </div>
      </div>

      <style>{`
        @keyframes slide-up {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
        @media (prefers-reduced-motion: reduce) {
          .animate-slide-up {
            animation: none;
          }
        }
      `}</style>
    </div>
  )
}
