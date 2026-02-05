import { useState } from 'react'
import { devisService } from '../../../services/devis'
import type { DevisDetail } from '../../../types'

interface Props {
  devis: DevisDetail
  isEditable: boolean
  onSaved: () => void
}

export default function NotesBasPageCard({ devis, isEditable, onSaved }: Props) {
  const [notes, setNotes] = useState(devis.notes_bas_page || devis.conditions_generales || '')
  const [saving, setSaving] = useState(false)

  const handleBlur = async () => {
    if (!isEditable) return
    setSaving(true)
    try {
      await devisService.updateDevis(devis.id, { notes_bas_page: notes || null })
      onSaved()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">Notes de bas de page</h3>
      <textarea
        value={notes}
        onChange={e => setNotes(e.target.value)}
        onBlur={handleBlur}
        disabled={!isEditable || saving}
        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm h-24 resize-none disabled:bg-gray-50"
        placeholder="Texte affiche en bas du devis (conditions particulieres, mentions legales complementaires...)"
      />
    </div>
  )
}
