/**
 * CommentModal - Modal pour ajouter un commentaire avec mentions @
 *
 * Permet de commenter un post et de mentionner des utilisateurs.
 */

import { useState } from 'react'
import { X, Send, Loader2 } from 'lucide-react'
import MentionInput from '../common/MentionInput'
import { dashboardService } from '../../services/dashboard'

interface CommentModalProps {
  isOpen: boolean
  onClose: () => void
  postId: number
  postAuthor: string
  onCommentAdded?: () => void
}

export default function CommentModal({
  isOpen,
  onClose,
  postId,
  postAuthor,
  onCommentAdded,
}: CommentModalProps) {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!content.trim()) {
      setError('Le commentaire ne peut pas etre vide')
      return
    }

    setLoading(true)
    setError(null)

    try {
      await dashboardService.addComment(String(postId), { contenu: content.trim() })
      setContent('')
      onCommentAdded?.()
      onClose()
    } catch (err) {
      console.error('Erreur ajout commentaire:', err)
      setError('Erreur lors de l\'ajout du commentaire')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="px-4 py-3 border-b flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">
              Repondre a {postAuthor}
            </h3>
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-100 rounded"
              disabled={loading}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-4">
            <MentionInput
              value={content}
              onChange={setContent}
              placeholder="Ecrivez votre commentaire... Utilisez @ pour mentionner quelqu'un"
              rows={4}
              disabled={loading}
            />

            {error && (
              <p className="mt-2 text-sm text-red-600">{error}</p>
            )}

            {/* Footer */}
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={onClose}
                disabled={loading}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading || !content.trim()}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Envoi...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Envoyer
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}
