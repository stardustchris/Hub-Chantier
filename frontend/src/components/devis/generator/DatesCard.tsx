import { useState } from 'react'
import { devisService } from '../../../services/devis'
import type { DevisDetail } from '../../../types'

interface Props {
  devis: DevisDetail
  isEditable: boolean
  onSaved: () => void
}

export default function DatesCard({ devis, isEditable, onSaved }: Props) {
  const [dateValidite, setDateValidite] = useState(devis.date_validite?.split('T')[0] || '')
  const [dateVisite, setDateVisite] = useState(devis.date_visite?.split('T')[0] || '')
  const [dateDebut, setDateDebut] = useState(devis.date_debut_travaux?.split('T')[0] || '')
  const [duree, setDuree] = useState<number | ''>(devis.duree_estimee_jours ?? '')
  const [saving, setSaving] = useState(false)

  const handleBlur = async (field: string, value: string | number | null) => {
    if (!isEditable) return
    setSaving(true)
    try {
      await devisService.updateDevis(devis.id, { [field]: value || null })
      onSaved()
    } finally {
      setSaving(false)
    }
  }

  const inputClass = 'w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm disabled:bg-gray-50 disabled:text-gray-500'

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="grid grid-cols-5 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Date d&apos;emission</label>
          <input type="date" value={devis.date_creation?.split('T')[0] || ''} disabled className={inputClass} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Date d&apos;expiration</label>
          <input
            type="date"
            value={dateValidite}
            onChange={e => setDateValidite(e.target.value)}
            onBlur={() => handleBlur('date_validite', dateValidite)}
            disabled={!isEditable || saving}
            className={inputClass}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Visite prealable</label>
          <input
            type="date"
            value={dateVisite}
            onChange={e => setDateVisite(e.target.value)}
            onBlur={() => handleBlur('date_visite', dateVisite)}
            disabled={!isEditable || saving}
            className={inputClass}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Debut travaux</label>
          <input
            type="date"
            value={dateDebut}
            onChange={e => setDateDebut(e.target.value)}
            onBlur={() => handleBlur('date_debut_travaux', dateDebut)}
            disabled={!isEditable || saving}
            className={inputClass}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Duree estimee</label>
          <div className="flex">
            <input
              type="number"
              value={duree}
              onChange={e => setDuree(e.target.value ? Number(e.target.value) : '')}
              onBlur={() => handleBlur('duree_estimee_jours', duree === '' ? null : Number(duree))}
              disabled={!isEditable || saving}
              className={`${inputClass} rounded-r-none border-r-0 w-20`}
              min={0}
            />
            <span className="px-3 py-2 bg-gray-100 border border-gray-200 rounded-r-lg text-gray-600 text-sm">jours</span>
          </div>
        </div>
      </div>
    </div>
  )
}
