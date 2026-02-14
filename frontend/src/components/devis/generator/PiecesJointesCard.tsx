import { useState, useEffect, useRef } from 'react'
import { Plus, Trash2, FileText, Image } from 'lucide-react'
import { devisService } from '../../../services/devis'
import type { PieceJointeDevis } from '../../../types'

interface Props {
  devisId: number
  isEditable: boolean
}

export default function PiecesJointesCard({ devisId, isEditable }: Props) {
  const [pieces, setPieces] = useState<PieceJointeDevis[]>([])
  const [loading, setLoading] = useState(true)
  const fileRef = useRef<HTMLInputElement>(null)

  const loadPieces = async () => {
    try {
      const data = await devisService.listPiecesJointes(devisId)
      setPieces(data)
    } catch { /* silent */ }
    finally { setLoading(false) }
  }

  useEffect(() => { loadPieces() }, [devisId])

  // NOTE: Le backend attend des metadonnees (pas le binaire).
  // A terme, integrer un vrai upload via le module GED.
  // Pour l'instant on enregistre les metadonnees du fichier selectionne.
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      await devisService.uploadPieceJointe(devisId, {
        nom_fichier: file.name,
        type_fichier: file.name.split('.').pop() || 'pdf',
        taille_octets: file.size,
        mime_type: file.type,
        visible_client: true,
      })
      loadPieces()
    } catch { /* silent */ }
    if (fileRef.current) fileRef.current.value = ''
  }

  const handleDelete = async (pieceId: number) => {
    await devisService.deletePieceJointe(pieceId)
    loadPieces()
  }

  const handleToggleVisibility = async (piece: PieceJointeDevis) => {
    await devisService.toggleVisibilitePieceJointe(piece.id, !piece.visible_client)
    loadPieces()
  }

  const formatSize = (bytes: number | null) => {
    if (!bytes) return ''
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const fileIcon = (type: string | null) => {
    if (!type) return { Icon: FileText, bg: 'bg-gray-100', color: 'text-gray-600' }
    const t = type.toLowerCase()
    if (t === 'pdf') return { Icon: FileText, bg: 'bg-red-100', color: 'text-red-600' }
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(t)) return { Icon: Image, bg: 'bg-blue-100', color: 'text-blue-600' }
    return { Icon: FileText, bg: 'bg-gray-100', color: 'text-gray-600' }
  }

  if (loading) return null

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">Pieces jointes</h3>
        {isEditable && (
          <button
            onClick={() => fileRef.current?.click()}
            className="text-indigo-600 hover:text-indigo-700 text-sm font-medium flex items-center gap-1"
          >
            <Plus className="w-4 h-4" /> Ajouter
          </button>
        )}
        <input ref={fileRef} type="file" className="hidden" onChange={handleUpload} />
      </div>

      {pieces.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-4">Aucune piece jointe</p>
      ) : (
        <div className="space-y-2">
          {pieces.map(piece => {
            const { Icon, bg, color } = fileIcon(piece.type_fichier)
            return (
              <div key={piece.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 ${bg} rounded-lg flex items-center justify-center`}>
                    <Icon className={`w-5 h-5 ${color}`} />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{piece.nom_fichier}</p>
                    <p className="text-xs text-gray-500">{formatSize(piece.taille_octets)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <label className="flex items-center gap-1 text-xs text-gray-500">
                    <input
                      type="checkbox"
                      checked={piece.visible_client}
                      onChange={() => handleToggleVisibility(piece)}
                      disabled={!isEditable}
                      className="rounded border-gray-300 text-indigo-600 w-3 h-3"
                    />
                    Visible client
                  </label>
                  {isEditable && (
                    <button
                      onClick={() => handleDelete(piece.id)}
                      className="text-gray-600 hover:text-red-500"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
