import { useState } from 'react'
import {
  ChevronDown,
  ChevronRight,
  Plus,
  Trash2,
  Edit2,
  GripVertical,
  Loader2,
  Check,
  X,
} from 'lucide-react'
import type { LotDevis, LotDevisCreate, LotDevisUpdate, LigneDevisCreate, LigneDevisUpdate, LigneDevis } from '../../types'
import LigneDevisTable from './LigneDevisTable'

const formatEUR = (value: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

interface LotDevisPanelProps {
  lots: LotDevis[]
  devisId: number
  editable?: boolean
  onCreateLot?: (data: LotDevisCreate) => Promise<void>
  onUpdateLot?: (id: number, data: LotDevisUpdate) => Promise<void>
  onDeleteLot?: (id: number) => Promise<void>
  onCreateLigne?: (data: LigneDevisCreate) => Promise<void>
  onUpdateLigne?: (id: number, data: LigneDevisUpdate) => Promise<void>
  onDeleteLigne?: (id: number) => Promise<void>
  onSelectLigne?: (ligne: LigneDevis) => void
}

export default function LotDevisPanel({
  lots,
  devisId,
  editable = false,
  onCreateLot,
  onUpdateLot,
  onDeleteLot,
  onCreateLigne,
  onUpdateLigne,
  onDeleteLigne,
  onSelectLigne,
}: LotDevisPanelProps) {
  const [expandedLots, setExpandedLots] = useState<Set<number>>(new Set(lots.map(l => l.id)))
  const [showAddLot, setShowAddLot] = useState(false)
  const [newLotTitre, setNewLotTitre] = useState('')
  const [editingLotId, setEditingLotId] = useState<number | null>(null)
  const [editLotTitre, setEditLotTitre] = useState('')
  const [loading, setLoading] = useState(false)

  const toggleLot = (lotId: number) => {
    setExpandedLots((prev) => {
      const next = new Set(prev)
      if (next.has(lotId)) next.delete(lotId)
      else next.add(lotId)
      return next
    })
  }

  const handleCreateLot = async () => {
    if (!onCreateLot || !newLotTitre.trim()) return
    try {
      setLoading(true)
      await onCreateLot({ devis_id: devisId, titre: newLotTitre.trim() })
      setNewLotTitre('')
      setShowAddLot(false)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateLot = async (id: number) => {
    if (!onUpdateLot || !editLotTitre.trim()) return
    try {
      setLoading(true)
      await onUpdateLot(id, { titre: editLotTitre.trim() })
      setEditingLotId(null)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteLot = async (id: number) => {
    if (!onDeleteLot) return
    if (!window.confirm('Supprimer ce lot et toutes ses lignes ?')) return
    try {
      setLoading(true)
      await onDeleteLot(id)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-3">
      {lots.map((lot) => {
        const isExpanded = expandedLots.has(lot.id)
        const isEditing = editingLotId === lot.id

        return (
          <div key={lot.id} className="border border-gray-200 rounded-lg overflow-hidden">
            {/* Lot header */}
            <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 border-b border-gray-200">
              {editable && (
                <GripVertical className="w-4 h-4 text-gray-400 cursor-grab flex-shrink-0" />
              )}
              <button
                onClick={() => toggleLot(lot.id)}
                className="flex-shrink-0 p-0.5 hover:bg-gray-200 rounded"
              >
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4 text-gray-600" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-600" />
                )}
              </button>

              {isEditing ? (
                <div className="flex items-center gap-2 flex-1">
                  <input
                    type="text"
                    value={editLotTitre}
                    onChange={(e) => setEditLotTitre(e.target.value)}
                    className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
                    maxLength={300}
                    autoFocus
                  />
                  <button
                    onClick={() => handleUpdateLot(lot.id)}
                    disabled={loading}
                    className="p-1 text-green-600 hover:bg-green-50 rounded"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => setEditingLotId(null)}
                    className="p-1 text-gray-400 hover:bg-gray-100 rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <>
                  <div className="flex-1 min-w-0">
                    <span className="text-xs font-mono text-gray-400 mr-2">{lot.numero}</span>
                    <span className="font-medium text-gray-900">{lot.titre}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="text-right">
                      <span className="text-gray-500 text-xs">Debourse</span>
                      <p className="font-medium text-orange-600">{formatEUR(Number(lot.debourse_sec))}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-gray-500 text-xs">Vente HT</span>
                      <p className="font-medium text-green-600">{formatEUR(Number(lot.total_ht))}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-gray-500 text-xs">Marge</span>
                      <p className={`font-medium ${Number(lot.marge_lot_pct ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {Number(lot.marge_lot_pct ?? 0).toFixed(1)}%
                      </p>
                    </div>
                    {editable && (
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => { setEditingLotId(lot.id); setEditLotTitre(lot.titre) }}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteLot(lot.id)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            {/* Lot content (lignes) */}
            {isExpanded && (
              <div className="p-2">
                <LigneDevisTable
                  lignes={lot.lignes}
                  lotId={lot.id}
                  editable={editable}
                  onCreateLigne={onCreateLigne}
                  onUpdateLigne={onUpdateLigne}
                  onDeleteLigne={onDeleteLigne}
                  onSelectLigne={onSelectLigne}
                />
              </div>
            )}
          </div>
        )
      })}

      {/* Ajout lot */}
      {editable && (
        <>
          {showAddLot ? (
            <div className="flex items-center gap-2 p-3 border border-dashed border-blue-300 rounded-lg bg-blue-50">
              <input
                type="text"
                value={newLotTitre}
                onChange={(e) => setNewLotTitre(e.target.value)}
                placeholder="Titre du nouveau lot"
                maxLength={300}
                className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm"
                autoFocus
                onKeyDown={(e) => { if (e.key === 'Enter') handleCreateLot() }}
              />
              <button
                onClick={handleCreateLot}
                disabled={loading || !newLotTitre.trim()}
                className="px-3 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 flex items-center gap-1"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                Ajouter
              </button>
              <button
                onClick={() => { setShowAddLot(false); setNewLotTitre('') }}
                className="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                Annuler
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowAddLot(true)}
              className="flex items-center gap-2 w-full px-4 py-3 text-sm text-blue-600 border border-dashed border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Ajouter un lot
            </button>
          )}
        </>
      )}

      {lots.length === 0 && !showAddLot && (
        <div className="text-center py-8 text-gray-400">
          <p>Aucun lot dans ce devis</p>
          {editable && <p className="text-sm mt-1">Ajoutez un premier lot pour commencer</p>}
        </div>
      )}
    </div>
  )
}
