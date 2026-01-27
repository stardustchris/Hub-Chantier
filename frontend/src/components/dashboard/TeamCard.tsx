/**
 * TeamCard - Carte equipe du jour
 * CDC Section 2 - Affichage equipe affectee
 * Affiche les membres de l'équipe du chantier en cours (synchro planning)
 */

import { Users, Phone, UserX, MapPin } from 'lucide-react'
import type { TeamMember } from '../../hooks/useTodayTeam'

interface TeamCardProps {
  members?: TeamMember[]
  /** Nom du chantier en cours */
  chantierName?: string
  onCall?: (memberId: string) => void
}

export default function TeamCard({ members = [], chantierName, onCall }: TeamCardProps) {
  const getInitials = (firstName: string, lastName: string) =>
    `${firstName[0] || ''}${lastName[0] || ''}`.toUpperCase()

  return (
    <div className="bg-white rounded-2xl p-5 shadow-lg">
      <h2 className="font-semibold text-gray-800 flex items-center gap-2 mb-1">
        <Users className="w-5 h-5 text-green-600" />
        Equipe du jour
      </h2>
      {chantierName && (
        <p className="text-xs text-gray-500 flex items-center gap-1 mb-4 ml-7">
          <MapPin className="w-3 h-3" />
          {chantierName}
        </p>
      )}
      {!chantierName && <div className="mb-3" />}

      {/* Aucun membre dans l'équipe */}
      {members.length === 0 && (
        <div className="text-center py-8">
          <UserX className="w-10 h-10 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500">Aucun collegue affecte aujourd'hui</p>
        </div>
      )}

      {/* Liste des membres */}
      {members.length > 0 && (
        <div className="space-y-3">
          {members.map((member) => (
            <div key={`${member.id}-${member.chantierId}`} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm"
                  style={{ backgroundColor: member.color }}
                >
                  {getInitials(member.firstName, member.lastName)}
                </div>
                <div>
                  <p className="font-medium text-gray-900 text-sm">
                    {member.firstName} {member.lastName}
                  </p>
                  <p className="text-xs text-gray-500">{member.role}</p>
                </div>
              </div>
              {member.phone && (
                <button
                  onClick={() => onCall?.(member.id)}
                  className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                >
                  <Phone className="w-5 h-5" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
