/**
 * MentionInput - Champ de texte avec autocomplete pour les mentions @
 *
 * Permet de mentionner des utilisateurs avec @ suivi du nom.
 * Affiche une liste filtree des utilisateurs au fur et a mesure de la saisie.
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { AtSign, Loader2 } from 'lucide-react'
import { usersService } from '../../services/users'
import type { User } from '../../types'

interface MentionInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  rows?: number
  disabled?: boolean
}

interface MentionSuggestion {
  id: string
  prenom: string
  nom: string
  role: string
  couleur: string
}

export default function MentionInput({
  value,
  onChange,
  placeholder = 'Ecrivez votre commentaire... Utilisez @ pour mentionner quelqu\'un',
  className = '',
  rows = 3,
  disabled = false,
}: MentionInputProps) {
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [suggestions, setSuggestions] = useState<MentionSuggestion[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [mentionQuery, setMentionQuery] = useState('')
  const [mentionStartPos, setMentionStartPos] = useState(-1)

  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  // Detecter le @ et charger les suggestions
  const handleInputChange = useCallback(async (newValue: string) => {
    onChange(newValue)

    const textarea = textareaRef.current
    if (!textarea) return

    const cursorPos = textarea.selectionStart
    const textBeforeCursor = newValue.slice(0, cursorPos)

    // Chercher le dernier @ avant le curseur
    const lastAtIndex = textBeforeCursor.lastIndexOf('@')

    if (lastAtIndex !== -1) {
      // Verifier qu'il n'y a pas d'espace entre @ et le curseur (sinon la mention est finie)
      const textAfterAt = textBeforeCursor.slice(lastAtIndex + 1)

      // Si on est juste apres le @ ou en train de taper un nom (sans espace)
      if (textAfterAt === '' || /^[a-zA-ZÀ-ÿ0-9_-]*$/.test(textAfterAt)) {
        setMentionQuery(textAfterAt.toLowerCase())
        setMentionStartPos(lastAtIndex)
        setShowSuggestions(true)
        setSelectedIndex(0)

        // Charger les utilisateurs
        setLoading(true)
        try {
          const response = await usersService.list({ search: textAfterAt, size: 10 })
          setSuggestions(
            response.items.map((u: User) => ({
              id: u.id,
              prenom: u.prenom,
              nom: u.nom,
              role: u.role,
              couleur: u.couleur || '#3498DB',
            }))
          )
        } catch (error) {
          console.error('Erreur chargement utilisateurs:', error)
          setSuggestions([])
        } finally {
          setLoading(false)
        }
        return
      }
    }

    // Pas de mention en cours
    setShowSuggestions(false)
    setMentionQuery('')
    setMentionStartPos(-1)
  }, [onChange])

  // Inserer une mention
  const insertMention = useCallback((user: MentionSuggestion) => {
    if (mentionStartPos === -1) return

    const beforeMention = value.slice(0, mentionStartPos)
    const afterMention = value.slice(mentionStartPos + 1 + mentionQuery.length)
    const mentionText = `@${user.prenom} `

    const newValue = beforeMention + mentionText + afterMention
    onChange(newValue)

    setShowSuggestions(false)
    setMentionQuery('')
    setMentionStartPos(-1)

    // Repositionner le curseur apres la mention
    setTimeout(() => {
      if (textareaRef.current) {
        const newPos = mentionStartPos + mentionText.length
        textareaRef.current.focus()
        textareaRef.current.setSelectionRange(newPos, newPos)
      }
    }, 0)
  }, [value, onChange, mentionStartPos, mentionQuery])

  // Navigation clavier dans les suggestions
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((prev) => (prev + 1) % suggestions.length)
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((prev) => (prev - 1 + suggestions.length) % suggestions.length)
        break
      case 'Enter':
        if (showSuggestions) {
          e.preventDefault()
          insertMention(suggestions[selectedIndex])
        }
        break
      case 'Escape':
        setShowSuggestions(false)
        break
      case 'Tab':
        if (showSuggestions) {
          e.preventDefault()
          insertMention(suggestions[selectedIndex])
        }
        break
    }
  }, [showSuggestions, suggestions, selectedIndex, insertMention])

  // Fermer les suggestions au clic externe
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(e.target as Node) &&
        textareaRef.current &&
        !textareaRef.current.contains(e.target as Node)
      ) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Filtrer les suggestions selon la query
  const filteredSuggestions = suggestions.filter((s) => {
    if (!mentionQuery) return true
    const fullName = `${s.prenom} ${s.nom}`.toLowerCase()
    return (
      s.prenom.toLowerCase().startsWith(mentionQuery) ||
      s.nom.toLowerCase().startsWith(mentionQuery) ||
      fullName.includes(mentionQuery)
    )
  })

  return (
    <div className="relative">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => handleInputChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={rows}
        disabled={disabled}
        className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none ${className}`}
      />

      {/* Indicateur @ */}
      <div className="absolute right-2 bottom-2 text-gray-400 text-xs flex items-center gap-1">
        <AtSign className="w-3 h-3" />
        pour mentionner
      </div>

      {/* Liste des suggestions */}
      {showSuggestions && (
        <div
          ref={suggestionsRef}
          className="absolute left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto"
        >
          {loading ? (
            <div className="px-4 py-3 text-center text-gray-500">
              <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
              Chargement...
            </div>
          ) : filteredSuggestions.length === 0 ? (
            <div className="px-4 py-3 text-center text-gray-500">
              Aucun utilisateur trouve
            </div>
          ) : (
            filteredSuggestions.map((user, index) => (
              <div
                key={user.id}
                onClick={() => insertMention(user)}
                className={`px-4 py-2 cursor-pointer flex items-center gap-3 ${
                  index === selectedIndex ? 'bg-primary-50' : 'hover:bg-gray-50'
                }`}
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold"
                  style={{ backgroundColor: user.couleur }}
                >
                  {user.prenom[0]}
                  {user.nom[0]}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    {user.prenom} {user.nom}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">{user.role}</p>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
