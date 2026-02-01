import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import type { Article, ArticleCreate, ArticleUpdate, TypeDebourse } from '../../types'
import { TYPE_DEBOURSE_LABELS } from '../../types'

interface ArticleModalProps {
  article?: Article | null
  onSubmit: (data: ArticleCreate | ArticleUpdate) => Promise<void>
  onClose: () => void
}

export default function ArticleModal({ article, onSubmit, onClose }: ArticleModalProps) {
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    code: article?.code || '',
    designation: article?.designation || '',
    unite: article?.unite || 'u',
    prix_unitaire_ht: article?.prix_unitaire_ht || 0,
    type_debourse: article?.type_debourse || ('materiaux' as TypeDebourse),
    categorie: article?.categorie || '',
    description: article?.description || '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setLoading(true)
      await onSubmit({
        code: form.code,
        designation: form.designation,
        unite: form.unite,
        prix_unitaire_ht: form.prix_unitaire_ht,
        type_debourse: form.type_debourse,
        categorie: form.categorie || undefined,
        description: form.description || undefined,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">
            {article ? 'Modifier l\'article' : 'Nouvel article'}
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Code *</label>
              <input
                type="text"
                required
                value={form.code}
                onChange={(e) => setForm({ ...form, code: e.target.value })}
                placeholder="Ex: MAT-001"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type debourse</label>
              <select
                value={form.type_debourse}
                onChange={(e) => setForm({ ...form, type_debourse: e.target.value as TypeDebourse })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {(Object.keys(TYPE_DEBOURSE_LABELS) as TypeDebourse[]).map((t) => (
                  <option key={t} value={t}>{TYPE_DEBOURSE_LABELS[t]}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Designation *</label>
            <input
              type="text"
              required
              value={form.designation}
              onChange={(e) => setForm({ ...form, designation: e.target.value })}
              placeholder="Ex: Parpaing 20x20x50"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Unite *</label>
              <input
                type="text"
                required
                value={form.unite}
                onChange={(e) => setForm({ ...form, unite: e.target.value })}
                placeholder="Ex: u, m2, h, kg"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prix unitaire HT *</label>
              <input
                type="number"
                required
                min="0"
                step="0.01"
                value={form.prix_unitaire_ht}
                onChange={(e) => setForm({ ...form, prix_unitaire_ht: Number(e.target.value) })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Categorie</label>
            <input
              type="text"
              value={form.categorie}
              onChange={(e) => setForm({ ...form, categorie: e.target.value })}
              placeholder="Ex: Gros oeuvre, Electricite, Plomberie"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={2}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading || !form.code || !form.designation}
              className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 flex items-center gap-2"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {article ? 'Enregistrer' : 'Creer l\'article'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
