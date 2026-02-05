import { useState } from 'react'
import { devisService } from '../../../services/devis'
import type { DevisDetail } from '../../../types'

interface Props {
  devis: DevisDetail
  isEditable: boolean
  onSaved: () => void
}

export default function OptionsInternesSidebar({ devis, isEditable, onSaved }: Props) {
  const [nomInterne, setNomInterne] = useState(devis.nom_interne || '')
  const [notes, setNotes] = useState(devis.notes || '')
  const [saving, setSaving] = useState(false)

  const handleBlur = async (field: string, value: string | null) => {
    if (!isEditable) return
    setSaving(true)
    try {
      await devisService.updateDevis(devis.id, { [field]: value || null })
      onSaved()
    } finally {
      setSaving(false)
    }
  }

  const inputClass = 'w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm disabled:bg-gray-50'

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="font-semibold text-gray-900 mb-1">Options internes</h3>
      <p className="text-xs text-gray-500 mb-4">Non visible par le client</p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nom interne</label>
          <input
            value={nomInterne}
            onChange={e => setNomInterne(e.target.value)}
            onBlur={() => handleBlur('nom_interne', nomInterne)}
            disabled={!isEditable || saving}
            className={inputClass}
            placeholder="ex: Dupont Reno Cuisine"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Notes internes</label>
          <textarea
            value={notes}
            onChange={e => setNotes(e.target.value)}
            onBlur={() => handleBlur('notes', notes)}
            disabled={!isEditable || saving}
            className={`${inputClass} h-20 resize-none`}
            placeholder="Notes pour l'equipe..."
          />
        </div>
      </div>
    </div>
  )
}
