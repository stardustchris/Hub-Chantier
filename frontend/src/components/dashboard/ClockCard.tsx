/**
 * ClockCard - Carte de pointage avec horloge temps reel
 * CDC Section 2.3.1 - Carte Pointage (verte/orange/bleue)
 *
 * 3 etats visuels :
 * - Vert : pointe (clock-in fait, en attente du depart)
 * - Orange : non pointe (en attente de l'arrivee)
 * - Bleu-gris : journee terminee (depart pointe)
 */

import { useState, useEffect } from 'react'
import { Clock, Plus, LogOut, Pencil, CheckCircle } from 'lucide-react'
import { formatDateWeekdayFull, formatTime } from '../../utils/dates'

interface ClockCardProps {
  lastClockIn?: string
  isClockedIn?: boolean
  clockInTime?: string
  clockOutTime?: string
  canEdit?: boolean
  /** True si l'utilisateur a deja pointe le depart aujourd'hui */
  hasClockedOut?: boolean
  /** True si l'utilisateur peut modifier le pointage (conducteur/admin) */
  canReclockIn?: boolean
  onClockIn?: () => void
  onClockOut?: () => void
  onEditTime?: (type: 'arrival' | 'departure', currentTime?: string) => void
}

export default function ClockCard({
  lastClockIn = 'Hier 17:32',
  isClockedIn = false,
  clockInTime,
  clockOutTime,
  canEdit = false,
  hasClockedOut = false,
  canReclockIn = false,
  onClockIn,
  onClockOut,
  onEditTime
}: ClockCardProps) {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // 3 etats : journee terminee (bleu) > pointe (vert) > non pointe (orange)
  const bgGradient = hasClockedOut
    ? 'from-slate-500 to-slate-600'
    : isClockedIn
      ? 'from-green-500 to-green-600'
      : 'from-orange-500 to-orange-600'

  const buttonBg = hasClockedOut
    ? 'bg-white text-slate-600 hover:bg-slate-50'
    : isClockedIn
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

      {hasClockedOut ? (
        <>
          {/* Etat 3 : Journee terminee (depart pointe) */}
          <div className="mb-3 bg-white/20 rounded-lg px-3 py-2">
            <div className="flex items-center gap-2 mb-1">
              <CheckCircle className="w-4 h-4 text-white/90" />
              <p className="text-xs font-semibold text-white/90">Journee terminee</p>
            </div>
            {canEdit && canReclockIn ? (
              /* Admin/Conducteur : permet de modifier arrivée ET départ */
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onEditTime?.('arrival', clockInTime)}
                  className="flex-1 flex items-center justify-center gap-1 py-1.5 bg-white/20 rounded-lg hover:bg-white/30 transition-colors text-sm"
                  title="Modifier l'heure d'arrivee"
                >
                  <span>{clockInTime || '--:--'}</span>
                  <Pencil className="w-3 h-3" />
                </button>
                <span className="text-white/60">→</span>
                <button
                  onClick={() => onEditTime?.('departure', clockOutTime)}
                  className="flex-1 flex items-center justify-center gap-1 py-1.5 bg-white/20 rounded-lg hover:bg-white/30 transition-colors text-sm"
                  title="Modifier l'heure de depart"
                >
                  <span>{clockOutTime || '--:--'}</span>
                  <Pencil className="w-3 h-3" />
                </button>
              </div>
            ) : (
              /* Compagnon/Chef : affichage simple sans édition */
              <p className="text-sm text-white/80">
                {clockInTime || '--:--'} → {clockOutTime || '--:--'}
              </p>
            )}
          </div>

          {canReclockIn ? (
            /* Conducteur/Admin : bouton modifier global */
            <button
              onClick={() => onEditTime?.('arrival', clockInTime)}
              className={`w-full ${buttonBg} font-semibold py-3 rounded-xl flex items-center justify-center gap-2 transition-colors shadow-md`}
            >
              <Pencil className="w-5 h-5" />
              Modifier le pointage
            </button>
          ) : (
            /* Compagnon/Chef : message informatif, pas de bouton */
            <div className="w-full bg-white/10 font-medium py-3 rounded-xl flex items-center justify-center gap-2 text-white/70">
              <CheckCircle className="w-5 h-5" />
              Depart enregistre
            </div>
          )}
        </>
      ) : isClockedIn ? (
        <>
          {/* Etat 2 : Pointe (arrivee faite, en attente depart) */}
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
          {/* Etat 1 : Non pointe (en attente arrivee) */}
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
