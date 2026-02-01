import { useState } from 'react'
import { Plus, Trash2, Loader2, Check, X } from 'lucide-react'
import type { DebourseDetail, DebourseDetailCreate, TypeDebourse } from '../../types'
import { TYPE_DEBOURSE_LABELS } from '../../types'

const formatEUR = (value: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

const TYPE_DEBOURSE_COLORS: Record<TypeDebourse, string> = {
  moe: '#3B82F6',
  materiaux: '#F59E0B',
  materiel: '#8B5CF6',
  sous_traitance: '#EF4444',
  deplacement: '#10B981',
}

interface DeboursePanelProps {
  debourses: DebourseDetail[]
  ligneId: number
  editable?: boolean
  onCreate?: (data: DebourseDetailCreate) => Promise<void>
  onDelete?: (id: number) => Promise<void>
}

export default function DeboursePanel({
  debourses,
  ligneId,
  editable = false,
  onCreate,
  onDelete,
}: DeboursePanelProps) {
  const [showAdd, setShowAdd] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState<{
    type_debourse: TypeDebourse
    designation: string
    unite: string
    quantite: number
    prix_unitaire: number
  }>({
    type_debourse: 'moe',
    designation: '',
    unite: 'h',
    quantite: 1,
    prix_unitaire: 0,
  })

  const totalDebourse = debourses.reduce((sum, d) => sum + d.montant, 0)
  const totalsByType = debourses.reduce((acc, d) => {
    acc[d.type_debourse] = (acc[d.type_debourse] || 0) + d.montant
    return acc
  }, {} as Record<string, number>)

  const handleCreate = async () => {
    if (!onCreate || !form.designation) return
    try {
      setLoading(true)
      await onCreate({
        ligne_id: ligneId,
        type_debourse: form.type_debourse,
        designation: form.designation,
        unite: form.unite,
        quantite: form.quantite,
        prix_unitaire: form.prix_unitaire,
      })
      setForm({ type_debourse: 'moe', designation: '', unite: 'h', quantite: 1, prix_unitaire: 0 })
      setShowAdd(false)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!onDelete) return
    try {
      setLoading(true)
      await onDelete(id)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-700">Detail des debourses</h4>
        <span className="text-sm font-bold text-orange-600">
          Total: {formatEUR(totalDebourse)}
        </span>
      </div>

      {/* Repartition par type */}
      {Object.keys(totalsByType).length > 0 && (
        <div className="flex flex-wrap gap-2">
          {(Object.entries(totalsByType) as [TypeDebourse, number][]).map(([type, total]) => (
            <div
              key={type}
              className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium"
              style={{
                backgroundColor: TYPE_DEBOURSE_COLORS[type] + '15',
                color: TYPE_DEBOURSE_COLORS[type],
              }}
            >
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: TYPE_DEBOURSE_COLORS[type] }} />
              {TYPE_DEBOURSE_LABELS[type]}: {formatEUR(total)}
            </div>
          ))}
        </div>
      )}

      {/* Tableau debourses */}
      {debourses.length > 0 && (
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Type</th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Designation</th>
              <th className="px-3 py-2 text-center text-xs font-medium text-gray-500">Unite</th>
              <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Qte</th>
              <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">PU</th>
              <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Montant</th>
              {editable && <th className="px-3 py-2 w-10"></th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {debourses.map((d) => (
              <tr key={d.id} className="hover:bg-gray-50">
                <td className="px-3 py-2">
                  <span
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                    style={{
                      backgroundColor: TYPE_DEBOURSE_COLORS[d.type_debourse] + '15',
                      color: TYPE_DEBOURSE_COLORS[d.type_debourse],
                    }}
                  >
                    {TYPE_DEBOURSE_LABELS[d.type_debourse]}
                  </span>
                </td>
                <td className="px-3 py-2 text-gray-900">{d.designation}</td>
                <td className="px-3 py-2 text-center text-gray-500">{d.unite}</td>
                <td className="px-3 py-2 text-right">{d.quantite}</td>
                <td className="px-3 py-2 text-right">{formatEUR(d.prix_unitaire)}</td>
                <td className="px-3 py-2 text-right font-medium">{formatEUR(d.montant)}</td>
                {editable && (
                  <td className="px-3 py-2">
                    <button
                      onClick={() => handleDelete(d.id)}
                      className="p-1 text-red-500 hover:bg-red-50 rounded"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Formulaire ajout */}
      {editable && showAdd && (
        <div className="border border-blue-200 rounded-lg p-3 bg-blue-50 space-y-3">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Type</label>
              <select
                value={form.type_debourse}
                onChange={(e) => setForm({ ...form, type_debourse: e.target.value as TypeDebourse })}
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
              >
                {(Object.keys(TYPE_DEBOURSE_LABELS) as TypeDebourse[]).map((t) => (
                  <option key={t} value={t}>{TYPE_DEBOURSE_LABELS[t]}</option>
                ))}
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Designation</label>
              <input
                type="text"
                value={form.designation}
                onChange={(e) => setForm({ ...form, designation: e.target.value })}
                placeholder="Ex: Macon qualifie"
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Unite</label>
              <input
                type="text"
                value={form.unite}
                onChange={(e) => setForm({ ...form, unite: e.target.value })}
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Quantite</label>
              <input
                type="number"
                value={form.quantite}
                onChange={(e) => setForm({ ...form, quantite: Number(e.target.value) })}
                step="0.01"
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Prix unitaire</label>
              <input
                type="number"
                value={form.prix_unitaire}
                onChange={(e) => setForm({ ...form, prix_unitaire: Number(e.target.value) })}
                step="0.01"
                className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setShowAdd(false)}
              className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded"
            >
              <X className="w-4 h-4 inline mr-1" />
              Annuler
            </button>
            <button
              onClick={handleCreate}
              disabled={loading || !form.designation}
              className="px-3 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded disabled:opacity-50 flex items-center gap-1"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
              Ajouter
            </button>
          </div>
        </div>
      )}

      {editable && !showAdd && (
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-1 text-sm text-blue-600 hover:bg-blue-50 rounded-lg px-3 py-1.5"
        >
          <Plus className="w-4 h-4" />
          Ajouter un debourse
        </button>
      )}

      {debourses.length === 0 && !showAdd && (
        <p className="text-center text-gray-400 text-sm py-3">Aucun debourse</p>
      )}
    </div>
  )
}
