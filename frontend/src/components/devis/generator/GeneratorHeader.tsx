import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Eye, Send, Pencil, Check, X } from 'lucide-react'
import DevisStatusBadge from '../DevisStatusBadge'
import DevisWorkflowActions from '../DevisWorkflowActions'
import { devisService } from '../../../services/devis'
import type { DevisDetail } from '../../../types'

interface Props {
  devis: DevisDetail
  onSoumettre: () => Promise<void>
  onValider: () => Promise<void>
  onRetournerBrouillon: () => Promise<void>
  onAccepter: () => Promise<void>
  onRefuser: (motif?: string) => Promise<void>
  onPerdu: (motif?: string) => Promise<void>
  onSaved: () => void
}

export default function GeneratorHeader({
  devis, onSoumettre, onValider, onRetournerBrouillon,
  onAccepter, onRefuser, onPerdu, onSaved,
}: Props) {
  const navigate = useNavigate()
  const [editingObjet, setEditingObjet] = useState(false)
  const [objetValue, setObjetValue] = useState(devis.objet || '')
  const [saving, setSaving] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const isEditable = devis.statut === 'brouillon'

  const startEdit = () => {
    if (!isEditable) return
    setObjetValue(devis.objet || '')
    setEditingObjet(true)
    setTimeout(() => inputRef.current?.focus(), 30)
  }

  const cancelEdit = () => {
    setEditingObjet(false)
    setObjetValue(devis.objet || '')
  }

  const saveObjet = async () => {
    if (!objetValue.trim()) return
    setSaving(true)
    try {
      await devisService.updateDevis(devis.id, { objet: objetValue.trim() })
      setEditingObjet(false)
      onSaved()
    } finally {
      setSaving(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') saveObjet()
    if (e.key === 'Escape') cancelEdit()
  }

  return (
    <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/devis')}
            className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center hover:bg-white/30 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>

          <div>
            {editingObjet ? (
              <div className="flex items-center gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={objetValue}
                  onChange={(e) => setObjetValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="text-xl font-bold bg-white/20 text-white placeholder-white/60 border border-white/40 rounded-lg px-2 py-0.5 focus:outline-none focus:border-white w-72"
                  placeholder="Objet du devis"
                />
                <button
                  onClick={saveObjet}
                  disabled={saving || !objetValue.trim()}
                  className="w-7 h-7 bg-white/20 hover:bg-white/30 rounded-lg flex items-center justify-center disabled:opacity-50"
                  title="Valider"
                >
                  <Check className="w-4 h-4" />
                </button>
                <button
                  onClick={cancelEdit}
                  className="w-7 h-7 bg-white/20 hover:bg-white/30 rounded-lg flex items-center justify-center"
                  title="Annuler"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 group">
                <h1 className="text-xl font-bold">{devis.objet || 'Nouveau Devis'}</h1>
                {isEditable && (
                  <button
                    onClick={startEdit}
                    className="w-6 h-6 opacity-0 group-hover:opacity-100 bg-white/20 hover:bg-white/30 rounded flex items-center justify-center transition-opacity"
                    title="Modifier l'objet"
                  >
                    <Pencil className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            )}
            <p className="text-indigo-200 text-sm">{devis.numero} &bull; {devis.client_nom}</p>
          </div>

          <DevisStatusBadge statut={devis.statut} size="md" />
        </div>

        <div className="flex items-center gap-3">
          <DevisWorkflowActions
            statut={devis.statut}
            onSoumettre={onSoumettre}
            onValider={onValider}
            onRetournerBrouillon={onRetournerBrouillon}
            onAccepter={onAccepter}
            onRefuser={onRefuser}
            onPerdu={onPerdu}
          />
          <button
            onClick={() => window.open(`/devis/${devis.id}/preview`, '_blank')}
            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors"
          >
            <Eye className="w-4 h-4" />
            Apercu PDF
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-white text-indigo-600 hover:bg-indigo-50 rounded-lg text-sm font-medium transition-colors">
            <Send className="w-4 h-4" />
            Envoyer au client
          </button>
        </div>
      </div>
    </header>
  )
}
