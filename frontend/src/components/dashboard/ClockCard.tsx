/**
 * ClockCard - Carte de pointage avec horloge temps reel
 * CDC Section 2.3.1 - Carte Pointage (verte/orange)
 */

import { useState, useEffect } from 'react'
import { Clock, Plus, LogOut, Pencil } from 'lucide-react'
import { formatDateWeekdayFull, formatTime } from '../../utils/dates'

interface ClockCardProps {
  lastClockIn?: string
  isClockedIn?: boolean
  clockInTime?: string
  canEdit?: boolean
  onClockIn?: () => void
  onClockOut?: () => void
  onEditTime?: (type: 'arrival' | 'departure', currentTime?: string) => void
}

export default function ClockCard({
  lastClockIn = 'Hier 17:32',
  isClockedIn = false,
  clockInTime,
  canEdit = false,
  onClockIn,
  onClockOut,
  onEditTime
}: ClockCardProps) {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Couleur de fond selon l'etat
  const bgGradient = isClockedIn
    ? 'from-green-500 to-green-600'
    : 'from-orange-500 to-orange-600'

  const buttonBg = isClockedIn
    ? 'bg-white text-green-600 hover:bg-green-50'
    : 'bg-white text-orange-600 hover:bg-orange-50'

  return (
    <div className={`bg-gradient-to-br ${bgGradient} rounded-2xl p-5 text-white relative overflow-hidden shadow-lg`}>
      <div className="absolute top-4 right-4 opacity-30">
        <Clock className="w-16 h-16" />
      </div>
      <p className="text-sm text-white/80">
        {formatDateWeekdayFull(currentTime)}
      </p>
      <p className="text-4xl font-bold mt-1 mb-4">
        {formatTime(currentTime)}
      </p>

      {isClockedIn ? (
        <>
          {/* Afficher l'heure d'arrivee */}
          <div className="flex items-center justify-between mb-3 bg-white/20 rounded-lg px-3 py-2">
            <div>
              <p className="text-xs text-white/80">Arrivee pointee a</p>
              <p className="font-semibold">{clockInTime || '--:--'}</p>
            </div>
            {canEdit && (
              <button
                onClick={() => onEditTime?.('arrival', clockInTime)}
                className="p-1.5 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
                title="Modifier l'heure d'arrivee"
              >
                <Pencil className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Bouton pointer le depart */}
          <button
            onClick={onClockOut}
            className={`w-full ${buttonBg} font-semibold py-3 rounded-xl flex items-center justify-center gap-2 transition-colors shadow-md`}
          >
            <LogOut className="w-5 h-5" />
            Pointer le depart
          </button>
        </>
      ) : (
        <>
          {/* Bouton pointer l'arrivee */}
          <button
            onClick={onClockIn}
            className={`w-full ${buttonBg} font-semibold py-3 rounded-xl flex items-center justify-center gap-2 transition-colors shadow-md`}
          >
            <Plus className="w-5 h-5" />
            Pointer l'arrivee
          </button>
        </>
      )}

      <p className="text-xs text-white/70 mt-3 text-center">
        Derniere pointee : {lastClockIn}
      </p>
    </div>
  )
}
