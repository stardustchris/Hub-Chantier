/**
 * ClockCard - Carte de pointage avec horloge temps reel
 * CDC Section 2.3.1 - Carte Pointage (verte/orange)
 */

import { useState, useEffect } from 'react'
import { Clock, Plus } from 'lucide-react'
import { formatDateWeekdayFull, formatTime } from '../../utils/dates'

interface ClockCardProps {
  lastClockIn?: string
  onClockIn?: () => void
}

export default function ClockCard({ lastClockIn = 'Hier 17:32', onClockIn }: ClockCardProps) {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-5 text-white relative overflow-hidden shadow-lg">
      <div className="absolute top-4 right-4 opacity-30">
        <Clock className="w-16 h-16" />
      </div>
      <p className="text-sm text-white/80">
        {formatDateWeekdayFull(currentTime)}
      </p>
      <p className="text-4xl font-bold mt-1 mb-4">
        {formatTime(currentTime)}
      </p>
      <button
        onClick={onClockIn}
        className="w-full bg-white text-orange-600 font-semibold py-3 rounded-xl flex items-center justify-center gap-2 hover:bg-orange-50 transition-colors shadow-md"
      >
        <Plus className="w-5 h-5" />
        Pointer l'arrivee
      </button>
      <p className="text-xs text-white/70 mt-3 text-center">
        Derniere pointee : {lastClockIn}
      </p>
    </div>
  )
}
