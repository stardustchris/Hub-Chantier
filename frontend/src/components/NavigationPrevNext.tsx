import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface NavigationPrevNextProps {
  /** ID précédent (null si premier) */
  prevId?: string | null
  /** ID suivant (null si dernier) */
  nextId?: string | null
  /** Préfixe d'URL (ex: /utilisateurs, /chantiers) */
  baseUrl: string
  /** Label court pour l'entité (ex: "utilisateur", "chantier") */
  entityLabel?: string
}

/**
 * Composant de navigation précédent/suivant.
 * Implémente USR-09 et CHT-14.
 */
export default function NavigationPrevNext({
  prevId,
  nextId,
  baseUrl,
  entityLabel = 'élément',
}: NavigationPrevNextProps) {
  return (
    <div className="flex items-center gap-2">
      {prevId ? (
        <Link
          to={`${baseUrl}/${prevId}`}
          className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-colors"
          title={`${entityLabel} précédent`}
          aria-label={`${entityLabel} précédent`}
        >
          <ChevronLeft className="w-5 h-5 text-gray-600" />
        </Link>
      ) : (
        <button
          disabled
          className="p-2 rounded-lg border border-gray-100 opacity-40 cursor-not-allowed"
          title={`Pas de ${entityLabel} précédent`}
          aria-label={`Pas de ${entityLabel} précédent`}
          aria-disabled="true"
        >
          <ChevronLeft className="w-5 h-5 text-gray-400" />
        </button>
      )}

      {nextId ? (
        <Link
          to={`${baseUrl}/${nextId}`}
          className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-colors"
          title={`${entityLabel} suivant`}
          aria-label={`${entityLabel} suivant`}
        >
          <ChevronRight className="w-5 h-5 text-gray-600" />
        </Link>
      ) : (
        <button
          disabled
          className="p-2 rounded-lg border border-gray-100 opacity-40 cursor-not-allowed"
          title={`Pas de ${entityLabel} suivant`}
          aria-label={`Pas de ${entityLabel} suivant`}
          aria-disabled="true"
        >
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </button>
      )}
    </div>
  )
}
