/**
 * Skeleton component - Indicateur de chargement squelette
 * Supporte différentes variantes (text, circular, rectangular) et respecte prefers-reduced-motion
 */

export interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  lines?: number
}

export default function Skeleton({
  className = '',
  variant = 'rectangular',
  width,
  height,
  lines = 1,
}: SkeletonProps) {
  // Base classes pour tous les skeletons
  const baseClasses = 'bg-gray-200 animate-pulse motion-reduce:animate-none'

  // Classes selon la variante
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  }

  // Style inline pour width/height personnalisés
  const style: React.CSSProperties = {}
  if (width) {
    style.width = typeof width === 'number' ? `${width}px` : width
  }
  if (height) {
    style.height = typeof height === 'number' ? `${height}px` : height
  }

  // Pour la variante text avec plusieurs lignes
  if (variant === 'text' && lines > 1) {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={`${baseClasses} ${variantClasses.text} ${
              index === lines - 1 ? 'w-3/4' : 'w-full'
            }`}
            style={style}
          />
        ))}
      </div>
    )
  }

  // Cas par défaut : un seul skeleton
  const classes = `${baseClasses} ${variantClasses[variant]} ${
    variant === 'text' ? 'w-full' : ''
  } ${className}`

  return <div className={classes} style={style} />
}
