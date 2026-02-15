/**
 * EmptyState component - État vide réutilisable avec icône, titre et action optionnelle
 * Utilisé pour afficher un message quand il n'y a pas de données
 */

import type { LucideIcon } from 'lucide-react'
import Button from './Button'

export interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description?: string
  actionLabel?: string
  onAction?: () => void
  className?: string
}

export default function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  className = '',
}: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center text-center py-12 ${className}`}>
      {/* Icône */}
      <Icon className="w-12 h-12 text-neutral-text-muted mb-4" aria-hidden="true" />

      {/* Titre */}
      <h3 className="text-neutral-text-secondary font-medium text-lg mb-1">{title}</h3>

      {/* Description optionnelle */}
      {description && <p className="text-neutral-text-muted text-sm mb-4 max-w-md">{description}</p>}

      {/* Bouton d'action optionnel */}
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction} className="mt-2">
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
