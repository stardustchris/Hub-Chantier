import { STATUT_DEVIS_CONFIG } from '../../types'
import type { StatutDevis } from '../../types'

interface DevisStatusBadgeProps {
  statut: StatutDevis
  size?: 'sm' | 'md'
}

export default function DevisStatusBadge({ statut, size = 'sm' }: DevisStatusBadgeProps) {
  const config = STATUT_DEVIS_CONFIG[statut]
  if (!config) return null

  const sizeClasses = size === 'sm'
    ? 'px-2 py-0.5 text-xs'
    : 'px-3 py-1 text-sm'

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClasses}`}
      style={{
        backgroundColor: config.couleur + '20',
        color: config.couleur,
      }}
    >
      {config.label}
    </span>
  )
}
