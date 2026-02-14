/**
 * Card component - Conteneur de carte réutilisable
 * Supporte différents niveaux de padding et effet hover optionnel
 */

import type { ReactNode } from 'react'

export interface CardProps {
  children: ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
}

export default function Card({
  children,
  className = '',
  padding = 'md',
  hover = false,
}: CardProps) {
  // Base classes pour toutes les cartes
  const baseClasses = 'bg-white rounded-2xl shadow-sm border border-gray-200'

  // Classes de padding
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  }

  // Classes hover optionnelles
  const hoverClasses = hover
    ? 'hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200'
    : ''

  const classes = `${baseClasses} ${paddingClasses[padding]} ${hoverClasses} ${className}`

  return <div className={classes}>{children}</div>
}
