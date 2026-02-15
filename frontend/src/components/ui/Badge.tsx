/**
 * Badge component - Badge de statut/information réutilisable
 * Supporte différentes variantes sémantiques (success, warning, error, info, neutral)
 */

import type { ReactNode } from 'react'

export interface BadgeProps {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral'
  size?: 'sm' | 'md'
  children: ReactNode
  className?: string
}

export default function Badge({
  variant = 'neutral',
  size = 'md',
  children,
  className = '',
}: BadgeProps) {
  // Base classes pour tous les badges
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-full'

  // Classes selon la variante (couleurs sémantiques)
  const variantClasses = {
    success: 'bg-success-light text-success-text',
    warning: 'bg-warning-light text-warning-text',
    error: 'bg-danger-light text-danger-text',
    info: 'bg-info-light text-info-text',
    neutral: 'bg-neutral-hover text-neutral-text',
  }

  // Classes selon la taille
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  }

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`

  return <span className={classes}>{children}</span>
}
