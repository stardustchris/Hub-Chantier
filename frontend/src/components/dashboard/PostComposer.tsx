/**
 * Composant PostComposer - Zone de publication
 * Selon CDC Section 2.2.1 - Zone de publication avec ciblage
 * Supporte les mentions @ pour taguer des utilisateurs
 */

import { useState } from 'react'
import type { TargetType, CreatePostData } from '../../types/dashboard'
import MentionInput from '../common/MentionInput'

interface PostComposerProps {
  onSubmit: (data: CreatePostData) => Promise<void>
  isCompagnon?: boolean
  defaultChantier?: number
}

export default function PostComposer({
  onSubmit,
  isCompagnon = false,
  defaultChantier,
}: PostComposerProps) {
  const [content, setContent] = useState('')
  const [targetType, setTargetType] = useState<TargetType>(
    isCompagnon ? 'specific_chantiers' : 'everyone'
  )
  const [isUrgent, setIsUrgent] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showTargeting, setShowTargeting] = useState(false)

  const handleSubmit = async () => {
    if (!content.trim()) return

    setIsSubmitting(true)
    try {
      await onSubmit({
        content: content.trim(),
        target_type: targetType,
        is_urgent: isUrgent,
        chantier_ids: defaultChantier ? [defaultChantier] : undefined,
      })
      setContent('')
      setIsUrgent(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      {/* Zone de saisie avec mentions @ */}
      <div className="flex gap-3">
        <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold flex-shrink-0">
          👤
        </div>
        <div className="flex-1">
          <MentionInput
            value={content}
            onChange={setContent}
            placeholder={
              isCompagnon
                ? 'Partager une photo, signaler un problème... Utilisez @ pour mentionner'
                : "Quoi de neuf ? Utilisez @ pour mentionner quelqu'un..."
            }
            rows={3}
            className="border-0 focus:ring-0"
          />
        </div>
      </div>

      {/* Barre d'actions */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t">
        <div className="flex items-center gap-2">

          {/* Ciblage - seulement pour Direction/Conducteur (FEED-03) */}
          {!isCompagnon && (
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowTargeting(!showTargeting)}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm text-gray-600 hover:bg-gray-100"
                aria-label="Choisir le ciblage"
                aria-expanded={showTargeting}
              >
                {targetType === 'everyone' && '📢'}
                {targetType === 'specific_chantiers' && '🏗️'}
                {targetType === 'specific_people' && '👥'}
                <span>
                  {targetType === 'everyone' && 'Tout le monde'}
                  {targetType === 'specific_chantiers' && 'Chantiers'}
                  {targetType === 'specific_people' && 'Personnes'}
                </span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown ciblage */}
              {showTargeting && (
                <div className="absolute top-full left-0 mt-1 bg-white rounded-lg shadow-lg border py-1 z-10 min-w-48">
                  <button
                    onClick={() => { setTargetType('everyone'); setShowTargeting(false) }}
                    className={`w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2 ${
                      targetType === 'everyone' ? 'bg-primary-50 text-primary-700' : ''
                    }`}
                  >
                    📢 Tout le monde
                  </button>
                  <button
                    onClick={() => { setTargetType('specific_chantiers'); setShowTargeting(false) }}
                    className={`w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2 ${
                      targetType === 'specific_chantiers' ? 'bg-primary-50 text-primary-700' : ''
                    }`}
                  >
                    🏗️ Chantiers spécifiques
                  </button>
                  <button
                    onClick={() => { setTargetType('specific_people'); setShowTargeting(false) }}
                    className={`w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2 ${
                      targetType === 'specific_people' ? 'bg-primary-50 text-primary-700' : ''
                    }`}
                  >
                    👥 Personnes spécifiques
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Urgent (FEED-08) */}
          {!isCompagnon && (
            <button
              type="button"
              onClick={() => setIsUrgent(!isUrgent)}
              aria-label={isUrgent ? 'Retirer le marquage urgent' : 'Marquer comme urgent'}
              aria-pressed={isUrgent}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm ${
                isUrgent
                  ? 'bg-red-100 text-red-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <svg className="w-5 h-5" fill={isUrgent ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Urgent
            </button>
          )}
        </div>

        {/* Boutons action: Publier puis Photo */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleSubmit}
            disabled={!content.trim() || isSubmitting}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Publication...' : 'Publier'}
          </button>

          {/* Bouton photo (FEED-02) */}
          <button
            type="button"
            aria-label={isCompagnon ? 'Prendre une photo' : 'Ajouter une photo'}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium ${
              isCompagnon
                ? 'bg-orange-500 text-white hover:bg-orange-600'
                : 'text-gray-600 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {isCompagnon ? 'Prendre une photo' : 'Photo'}
          </button>
        </div>
      </div>
    </div>
  )
}
