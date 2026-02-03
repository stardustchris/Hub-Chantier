import { useState } from 'react'
import { Plus, Trash2, Edit2, Check, X, Loader2 } from 'lucide-react'
import type { LigneDevis, LigneDevisCreate, LigneDevisUpdate } from '../../types'

const formatEUR = (value: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

interface LigneDevisTableProps {
  lignes: LigneDevis[]
  lotId: number
  editable?: boolean
  onCreateLigne?: (data: LigneDevisCreate) => Promise<void>
  onUpdateLigne?: (id: number, data: LigneDevisUpdate) => Promise<void>
  onDeleteLigne?: (id: number) => Promise<void>
  onSelectLigne?: (ligne: LigneDevis) => void
}

export default function LigneDevisTable({
  lignes,
  lotId,
  editable = false,
  onCreateLigne,
  onUpdateLigne,
  onDeleteLigne,
  onSelectLigne,
}: LigneDevisTableProps) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [showAdd, setShowAdd] = useState(false)
  const [loading, setLoading] = useState(false)
  const [editForm, setEditForm] = useState({
    designation: '',
    unite: '',
    quantite: 0,
    prix_unitaire_ht: 0,
    marge_ligne_pct: undefined as number | undefined,
  })
  const [newForm, setNewForm] = useState({
    designation: '',
    unite: 'u',
    quantite: 1,
    prix_unitaire_ht: 0,
    marge_ligne_pct: undefined as number | undefined,
  })

  const startEdit = (ligne: LigneDevis) => {
    setEditingId(ligne.id)
    setEditForm({
      designation: ligne.designation,
      unite: ligne.unite,
      quantite: Number(ligne.quantite),
      prix_unitaire_ht: Number(ligne.prix_unitaire_ht),
      marge_ligne_pct: ligne.marge_ligne_pct != null ? Number(ligne.marge_ligne_pct) : undefined,
    })
  }

  const handleUpdate = async (id: number) => {
    if (!onUpdateLigne) return
    try {
      setLoading(true)
      await onUpdateLigne(id, editForm)
      setEditingId(null)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!onCreateLigne || !newForm.designation) return
    try {
      setLoading(true)
      await onCreateLigne({
        lot_devis_id: lotId,
        designation: newForm.designation,
        unite: newForm.unite,
        quantite: newForm.quantite,
        prix_unitaire_ht: newForm.prix_unitaire_ht,
        marge_ligne_pct: newForm.marge_ligne_pct,
      })
      setNewForm({ designation: '', unite: 'u', quantite: 1, prix_unitaire_ht: 0, marge_ligne_pct: undefined })
      setShowAdd(false)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!onDeleteLigne) return
    if (!window.confirm('Supprimer cette ligne ?')) return
    try {
      setLoading(true)
      await onDeleteLigne(id)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Designation</th>
            <th className="px-3 py-2 text-center text-xs font-medium text-gray-500">Unite</th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Qte</th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">PU HT</th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Total HT</th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Déboursé</th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">PV HT</th>
            {editable && <th className="px-3 py-2 text-center text-xs font-medium text-gray-500 w-20">Actions</th>}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {lignes.map((ligne) => (
            <tr
              key={ligne.id}
              className={`hover:bg-gray-50 transition-colors ${onSelectLigne ? 'cursor-pointer' : ''}`}
              onClick={() => onSelectLigne?.(ligne)}
            >
              {editingId === ligne.id ? (
                <>
                  <td className="px-3 py-2">
                    <input
                      type="text"
                      value={editForm.designation}
                      onChange={(e) => setEditForm({ ...editForm, designation: e.target.value })}
                      maxLength={500}
                      className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="text"
                      value={editForm.unite}
                      onChange={(e) => setEditForm({ ...editForm, unite: e.target.value })}
                      className="w-16 border border-gray-300 rounded px-2 py-1 text-sm text-center"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      value={editForm.quantite}
                      onChange={(e) => setEditForm({ ...editForm, quantite: Number(e.target.value) })}
                      className="w-20 border border-gray-300 rounded px-2 py-1 text-sm text-right"
                      step="0.01"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      value={editForm.prix_unitaire_ht}
                      onChange={(e) => setEditForm({ ...editForm, prix_unitaire_ht: Number(e.target.value) })}
                      className="w-24 border border-gray-300 rounded px-2 py-1 text-sm text-right"
                      step="0.01"
                    />
                  </td>
                  <td className="px-3 py-2 text-right text-gray-500">-</td>
                  <td className="px-3 py-2 text-right text-gray-500">-</td>
                  <td className="px-3 py-2 text-right text-gray-500">-</td>
                  <td className="px-3 py-2">
                    <div className="flex items-center justify-center gap-1">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleUpdate(ligne.id) }}
                        disabled={loading}
                        className="p-1 text-green-600 hover:bg-green-50 rounded"
                      >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); setEditingId(null) }}
                        className="p-1 text-gray-400 hover:bg-gray-100 rounded"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </>
              ) : (
                <>
                  <td className="px-3 py-2 text-gray-900">{ligne.designation}</td>
                  <td className="px-3 py-2 text-center text-gray-500">{ligne.unite}</td>
                  <td className="px-3 py-2 text-right">{Number(ligne.quantite)}</td>
                  <td className="px-3 py-2 text-right">{formatEUR(Number(ligne.prix_unitaire_ht))}</td>
                  <td className="px-3 py-2 text-right font-medium">{formatEUR(Number(ligne.montant_ht))}</td>
                  <td className="px-3 py-2 text-right text-orange-600">{formatEUR(Number(ligne.debourse_sec))}</td>
                  <td className="px-3 py-2 text-right text-green-600 font-medium">{formatEUR(Number(ligne.prix_revient))}</td>
                  {editable && (
                    <td className="px-3 py-2">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={(e) => { e.stopPropagation(); startEdit(ligne) }}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDelete(ligne.id) }}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  )}
                </>
              )}
            </tr>
          ))}

          {/* Ligne ajout */}
          {editable && showAdd && (
            <tr className="bg-blue-50">
              <td className="px-3 py-2">
                <input
                  type="text"
                  value={newForm.designation}
                  onChange={(e) => setNewForm({ ...newForm, designation: e.target.value })}
                  placeholder="Designation"
                  maxLength={500}
                  className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                />
              </td>
              <td className="px-3 py-2">
                <input
                  type="text"
                  value={newForm.unite}
                  onChange={(e) => setNewForm({ ...newForm, unite: e.target.value })}
                  className="w-16 border border-gray-300 rounded px-2 py-1 text-sm text-center"
                />
              </td>
              <td className="px-3 py-2">
                <input
                  type="number"
                  value={newForm.quantite}
                  onChange={(e) => setNewForm({ ...newForm, quantite: Number(e.target.value) })}
                  className="w-20 border border-gray-300 rounded px-2 py-1 text-sm text-right"
                  step="0.01"
                />
              </td>
              <td className="px-3 py-2">
                <input
                  type="number"
                  value={newForm.prix_unitaire_ht}
                  onChange={(e) => setNewForm({ ...newForm, prix_unitaire_ht: Number(e.target.value) })}
                  className="w-24 border border-gray-300 rounded px-2 py-1 text-sm text-right"
                  step="0.01"
                />
              </td>
              <td className="px-3 py-2 text-right text-gray-500">-</td>
              <td className="px-3 py-2 text-right text-gray-500">-</td>
              <td className="px-3 py-2 text-right text-gray-500">-</td>
              <td className="px-3 py-2">
                <div className="flex items-center justify-center gap-1">
                  <button
                    onClick={handleCreate}
                    disabled={loading || !newForm.designation}
                    className="p-1 text-green-600 hover:bg-green-50 rounded disabled:opacity-50"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => setShowAdd(false)}
                    className="p-1 text-gray-400 hover:bg-gray-100 rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Total lot */}
      {lignes.length > 0 && (
        <div className="flex justify-end px-3 py-2 bg-gray-50 border-t text-sm">
          <span className="text-gray-600 mr-4">Total:</span>
          <span className="font-semibold">
            {formatEUR(lignes.reduce((sum, l) => sum + Number(l.montant_ht), 0))}
          </span>
        </div>
      )}

      {/* Bouton ajout */}
      {editable && !showAdd && (
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-1 px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg mt-2"
        >
          <Plus className="w-4 h-4" />
          Ajouter une ligne
        </button>
      )}

      {lignes.length === 0 && !showAdd && (
        <div className="text-center py-4 text-gray-400 text-sm">
          Aucune ligne dans ce lot
        </div>
      )}
    </div>
  )
}
