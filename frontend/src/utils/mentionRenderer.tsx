import { Link } from 'react-router-dom'

/** Interface minimale pour le matching des mentions */
interface MentionUser {
  id: string | number
  prenom: string
  nom: string
}

/**
 * Parse le contenu d'un post et rend les mentions @Prénom cliquables.
 * Les mentions reconnues pointent vers /utilisateurs/:id.
 * Les mentions non reconnues sont affichées en bleu sans lien.
 */
export function renderContentWithMentions(
  content: string,
  authors: MentionUser[]
): React.ReactNode[] {
  const mentionRegex = /@([a-zA-ZÀ-ÿ][a-zA-ZÀ-ÿ0-9_-]*)/g
  const parts: React.ReactNode[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = mentionRegex.exec(content)) !== null) {
    // Texte avant la mention
    if (match.index > lastIndex) {
      parts.push(content.slice(lastIndex, match.index))
    }

    const mentionName = match[1]
    const matchedAuthor = findAuthorByName(mentionName, authors)

    if (matchedAuthor) {
      parts.push(
        <Link
          key={`mention-${match.index}`}
          to={`/utilisateurs/${matchedAuthor.id}`}
          className="text-blue-600 font-semibold hover:underline"
        >
          @{mentionName}
        </Link>
      )
    } else {
      parts.push(
        <span key={`mention-${match.index}`} className="text-blue-500 font-semibold">
          @{mentionName}
        </span>
      )
    }

    lastIndex = match.index + match[0].length
  }

  // Texte restant après la dernière mention
  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex))
  }

  return parts.length > 0 ? parts : [content]
}

function findAuthorByName(name: string, authors: MentionUser[]): MentionUser | undefined {
  const lower = name.toLowerCase()
  return authors.find(
    (a) =>
      a.prenom.toLowerCase() === lower ||
      a.nom.toLowerCase() === lower ||
      `${a.prenom}${a.nom}`.toLowerCase() === lower
  )
}
