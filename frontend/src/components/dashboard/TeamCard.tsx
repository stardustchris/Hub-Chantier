/**
 * TeamCard - Carte equipe du jour
 * CDC Section 2 - Affichage equipe affectee
 */

import { Users, Phone } from 'lucide-react'

interface TeamMember {
  id: string
  firstName: string
  lastName: string
  role: string
  color: string
  phone?: string
}

interface TeamCardProps {
  members?: TeamMember[]
  onCall?: (memberId: string) => void
}

const defaultMembers: TeamMember[] = [
  { id: '1', firstName: 'Marc', lastName: 'Dubois', role: 'Chef de chantier', color: '#2563eb', phone: '+33612345678' },
  { id: '2', firstName: 'Luc', lastName: 'Martin', role: 'Macon', color: '#16a34a' },
  { id: '3', firstName: 'Thomas', lastName: 'Bernard', role: 'Coffreur', color: '#f97316' },
]

export default function TeamCard({ members = defaultMembers, onCall }: TeamCardProps) {
  const getInitials = (firstName: string, lastName: string) =>
    `${firstName[0] || ''}${lastName[0] || ''}`.toUpperCase()

  return (
    <div className="bg-white rounded-2xl p-5 shadow-lg">
      <h2 className="font-semibold text-gray-800 flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-green-600" />
        Equipe du jour
      </h2>
      <div className="space-y-3">
        {members.map((member) => (
          <div key={member.id} className="flex items-center justify-between">
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
    </div>
  )
}
