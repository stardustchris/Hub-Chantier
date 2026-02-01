/**
 * CircularGauge - Jauge circulaire SVG pour indicateurs financiers
 *
 * FIN-16 Phase 1 : Remplace les barres de progression horizontales
 * par des jauges circulaires visuelles avec code couleur dynamique.
 */

interface CircularGaugeProps {
  /** Valeur actuelle (pourcentage 0-100+) */
  value: number
  /** Valeur max affichee (defaut 100) */
  max?: number
  /** Taille en pixels (defaut 48) */
  size?: number
  /** Epaisseur du trait (defaut 4) */
  strokeWidth?: number
  /** Couleur forcee (sinon dynamique selon valeur) */
  color?: string
  /** Seuils pour couleur dynamique */
  thresholds?: { warning: number; danger: number }
}

function getColor(value: number, thresholds: { warning: number; danger: number }): string {
  if (value >= thresholds.danger) return '#ef4444' // red-500
  if (value >= thresholds.warning) return '#f59e0b' // amber-500
  return '#22c55e' // green-500
}

export default function CircularGauge({
  value,
  max = 100,
  size = 48,
  strokeWidth = 4,
  color,
  thresholds = { warning: 80, danger: 100 },
}: CircularGaugeProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const clampedValue = Math.min(Math.max(value, 0), max)
  const progress = (clampedValue / max) * circumference
  const offset = circumference - progress
  const displayColor = color || getColor(value, thresholds)

  return (
    <div className="inline-flex items-center gap-2">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={displayColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-500 ease-out"
        />
      </svg>
      <span className="text-xs font-medium" style={{ color: displayColor }}>
        {value.toFixed(1)}%
      </span>
    </div>
  )
}
