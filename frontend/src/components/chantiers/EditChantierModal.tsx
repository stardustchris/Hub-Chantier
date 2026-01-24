import { useState } from 'react'
import { X, Plus, Trash2, Loader2 } from 'lucide-react'
import type { Chantier, ChantierUpdate, ContactChantier } from '../../types'
import { CHANTIER_STATUTS, USER_COLORS } from '../../types'

interface EditChantierModalProps {
  chantier: Chantier
  onClose: () => void
  onSubmit: (data: ChantierUpdate) => void
}

export default function EditChantierModal({ chantier, onClose, onSubmit }: EditChantierModalProps) {
  const [formData, setFormData] = useState<ChantierUpdate>({
    nom: chantier.nom,
    adresse: chantier.adresse,
    couleur: chantier.couleur,
    statut: chantier.statut,
    heures_estimees: chantier.heures_estimees,
    date_debut_prevue: chantier.date_debut_prevue,
    date_fin_prevue: chantier.date_fin_prevue,
    description: chantier.description,
  })

  // Initialiser les contacts depuis les données existantes
  const initialContacts: ContactChantier[] = chantier.contacts?.length
    ? chantier.contacts
    : chantier.contact_nom
      ? [{ nom: chantier.contact_nom, profession: '', telephone: chantier.contact_telephone || '' }]
      : [{ nom: '', profession: '', telephone: '' }]

  const [contacts, setContacts] = useState<ContactChantier[]>(initialContacts)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const addContact = () => {
    setContacts([...contacts, { nom: '', profession: '', telephone: '' }])
  }

  const removeContact = (index: number) => {
    if (contacts.length > 1) {
      setContacts(contacts.filter((_, i) => i !== index))
    }
  }

  const updateContact = (index: number, field: keyof ContactChantier, value: string) => {
    const updated = [...contacts]
    updated[index] = { ...updated[index], [field]: value }
    setContacts(updated)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      // Filtrer les contacts vides
      const validContacts = contacts.filter(c => c.nom.trim())
      const dataToSubmit = {
        ...formData,
        contacts: validContacts.length > 0 ? validContacts : undefined,
        // Pour compatibilité avec l'ancien format
        contact_nom: validContacts[0]?.nom || undefined,
        contact_telephone: validContacts[0]?.telephone || undefined,
      }
      await onSubmit(dataToSubmit)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 id="modal-title" className="text-lg font-semibold">Modifier le chantier</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg" aria-label="Fermer">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom du chantier
            </label>
            <input
              type="text"
              value={formData.nom || ''}
              onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
              className="input"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Adresse
            </label>
            <textarea
              value={formData.adresse || ''}
              onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
              className="input"
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Couleur
            </label>
            <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Couleur du chantier">
              {USER_COLORS.map((color) => (
                <button
                  key={color.code}
                  type="button"
                  onClick={() => setFormData({ ...formData, couleur: color.code })}
                  className={`w-8 h-8 rounded-full border-2 transition-all ${
                    formData.couleur === color.code
                      ? 'border-gray-900 scale-110'
                      : 'border-transparent'
                  }`}
                  style={{ backgroundColor: color.code }}
                  title={color.name}
                  aria-label={color.name}
                  aria-pressed={formData.couleur === color.code}
                />
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Statut
            </label>
            <select
              value={formData.statut || chantier.statut}
              onChange={(e) => setFormData({ ...formData, statut: e.target.value as Chantier['statut'] })}
              className="input"
            >
              {Object.entries(CHANTIER_STATUTS).map(([key, info]) => (
                <option key={key} value={key}>
                  {info.label}
                </option>
              ))}
            </select>
          </div>

          {/* Contacts dynamiques */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Contacts sur place
              </label>
              <button
                type="button"
                onClick={addContact}
                className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
                Ajouter
              </button>
            </div>
            <div className="space-y-3">
              {contacts.map((contact, index) => (
                <div key={index} className="flex gap-2 items-start bg-gray-50 p-3 rounded-lg">
                  <div className="flex-1 grid grid-cols-3 gap-2">
                    <input
                      type="text"
                      value={contact.nom}
                      onChange={(e) => updateContact(index, 'nom', e.target.value)}
                      className="input"
                      placeholder="Nom"
                      aria-label={`Nom du contact ${index + 1}`}
                    />
                    <input
                      type="text"
                      value={contact.profession || ''}
                      onChange={(e) => updateContact(index, 'profession', e.target.value)}
                      className="input"
                      placeholder="Profession"
                      aria-label={`Profession du contact ${index + 1}`}
                    />
                    <input
                      type="tel"
                      value={contact.telephone || ''}
                      onChange={(e) => updateContact(index, 'telephone', e.target.value)}
                      className="input"
                      placeholder="Telephone"
                      aria-label={`Telephone du contact ${index + 1}`}
                    />
                  </div>
                  {contacts.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeContact(index)}
                      className="p-2 text-gray-400 hover:text-red-500"
                      aria-label={`Supprimer le contact ${index + 1}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date debut prevue
              </label>
              <input
                type="date"
                value={formData.date_debut_prevue || ''}
                onChange={(e) => setFormData({ ...formData, date_debut_prevue: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date fin prevue
              </label>
              <input
                type="date"
                value={formData.date_fin_prevue || ''}
                onChange={(e) => setFormData({ ...formData, date_fin_prevue: e.target.value })}
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Heures estimees
            </label>
            <input
              type="number"
              value={formData.heures_estimees || ''}
              onChange={(e) =>
                setFormData({ ...formData, heures_estimees: parseInt(e.target.value) || undefined })
              }
              className="input"
              min={0}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
              rows={3}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="flex-1 btn btn-outline">
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 btn btn-primary flex items-center justify-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
