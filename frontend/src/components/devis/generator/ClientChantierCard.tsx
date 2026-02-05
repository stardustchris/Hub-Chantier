import { useState } from 'react'
import { User, Building2, Save, X } from 'lucide-react'
import { devisService } from '../../../services/devis'
import type { DevisDetail } from '../../../types'

interface Props {
  devis: DevisDetail
  isEditable: boolean
  onSaved: () => void
}

export default function ClientChantierCard({ devis, isEditable, onSaved }: Props) {
  const [editing, setEditing] = useState(false)
  const [clientNom, setClientNom] = useState(devis.client_nom)
  const [clientAdresse, setClientAdresse] = useState(devis.client_adresse || '')
  const [clientEmail, setClientEmail] = useState(devis.client_email || '')
  const [clientTelephone, setClientTelephone] = useState(devis.client_telephone || '')
  const [chantierRef, setChantierRef] = useState(devis.chantier_ref || '')
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    try {
      await devisService.updateDevis(devis.id, {
        client_nom: clientNom,
        client_adresse: clientAdresse || undefined,
        client_email: clientEmail || undefined,
        client_telephone: clientTelephone || undefined,
        chantier_ref: chantierRef || undefined,
      })
      setEditing(false)
      onSaved()
    } finally {
      setSaving(false)
    }
  }

  if (!editing) {
    return (
      <div
        className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 cursor-pointer hover:border-indigo-200 transition-colors"
        onClick={() => isEditable && setEditing(true)}
      >
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <span className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-indigo-600" />
              </span>
              Client
            </label>
            <p className="font-medium text-gray-900">{devis.client_nom}</p>
            {devis.client_adresse && <p className="text-sm text-gray-500 mt-1">{devis.client_adresse}</p>}
            {devis.client_email && <p className="text-sm text-gray-500">{devis.client_email}</p>}
            {devis.client_telephone && <p className="text-sm text-gray-500">{devis.client_telephone}</p>}
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <span className="w-6 h-6 bg-orange-100 rounded-full flex items-center justify-center">
                <Building2 className="w-4 h-4 text-orange-600" />
              </span>
              Chantier
            </label>
            <p className="font-medium text-gray-900">{devis.chantier_ref || 'Non lie'}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-indigo-200 p-6">
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-3">
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <span className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-indigo-600" />
            </span>
            Client
          </label>
          <input
            value={clientNom}
            onChange={e => setClientNom(e.target.value)}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm"
            placeholder="Nom du client"
          />
          <input
            value={clientAdresse}
            onChange={e => setClientAdresse(e.target.value)}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm"
            placeholder="Adresse"
          />
          <div className="grid grid-cols-2 gap-2">
            <input
              value={clientEmail}
              onChange={e => setClientEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm"
              placeholder="Email"
              type="email"
            />
            <input
              value={clientTelephone}
              onChange={e => setClientTelephone(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm"
              placeholder="Telephone"
            />
          </div>
        </div>
        <div className="space-y-3">
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <span className="w-6 h-6 bg-orange-100 rounded-full flex items-center justify-center">
              <Building2 className="w-4 h-4 text-orange-600" />
            </span>
            Chantier
          </label>
          <input
            value={chantierRef}
            onChange={e => setChantierRef(e.target.value)}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm"
            placeholder="Reference chantier"
          />
        </div>
      </div>
      <div className="flex justify-end gap-2 mt-4">
        <button
          onClick={() => setEditing(false)}
          className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
        >
          <X className="w-4 h-4" /> Annuler
        </button>
        <button
          onClick={handleSave}
          disabled={saving || !clientNom.trim()}
          className="flex items-center gap-1 px-3 py-1.5 text-sm text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50"
        >
          <Save className="w-4 h-4" /> {saving ? 'Enregistrement...' : 'Enregistrer'}
        </button>
      </div>
    </div>
  )
}
