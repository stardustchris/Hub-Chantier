import { useState } from 'react'
import {
  Plus,
  X,
  Trash2,
  Loader2,
  Info,
} from 'lucide-react'
import type { ChantierCreate, TypeTravaux } from '../../types'
import { USER_COLORS, TYPE_TRAVAUX_OPTIONS } from '../../types'

// Types pour les contacts et phases temporaires
export interface TempContact {
  nom: string
  telephone: string
  profession: string
}

export interface TempPhase {
  nom: string
  date_debut: string
  date_fin: string
}

interface CreateChantierModalProps {
  onClose: () => void
  onSubmit: (
    data: ChantierCreate,
    contacts: TempContact[],
    phases: TempPhase[]
  ) => Promise<void>
  usedColors: string[]
}

export function CreateChantierModal({ onClose, onSubmit, usedColors }: CreateChantierModalProps) {
  // Trouver la premiere couleur non utilisee
  const getAvailableColor = () => {
    const availableColor = USER_COLORS.find(c => !usedColors.includes(c.code))
    return availableColor?.code || USER_COLORS[0].code
  }

  const [formData, setFormData] = useState<ChantierCreate>({
    nom: '',
    adresse: '',
    couleur: getAvailableColor(),
  })
  const [contacts, setContacts] = useState<TempContact[]>([{ nom: '', telephone: '', profession: '' }])
  const [phases, setPhases] = useState<TempPhase[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Gestion des contacts
  const addContact = () => {
    setContacts([...contacts, { nom: '', telephone: '', profession: '' }])
  }

  const removeContact = (index: number) => {
    if (contacts.length > 1) {
      setContacts(contacts.filter((_, i) => i !== index))
    }
  }

  const updateContact = (index: number, field: keyof TempContact, value: string) => {
    const newContacts = [...contacts]
    newContacts[index][field] = value
    setContacts(newContacts)
  }

  // Gestion des phases
  const addPhase = () => {
    setPhases([...phases, { nom: '', date_debut: '', date_fin: '' }])
  }

  const removePhase = (index: number) => {
    setPhases(phases.filter((_, i) => i !== index))
  }

  const updatePhase = (index: number, field: keyof TempPhase, value: string) => {
    const newPhases = [...phases]
    newPhases[index][field] = value
    setPhases(newPhases)
  }

  // Validation des dates
  const validateDates = (): boolean => {
    if (formData.date_debut_prevue && formData.date_fin_prevue) {
      if (formData.date_fin_prevue < formData.date_debut_prevue) {
        setError('La date de fin doit etre apres la date de debut')
        return false
      }
    }
    setError(null)
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateDates()) {
      return
    }

    setIsSubmitting(true)
    setError(null)
    try {
      await onSubmit(formData, contacts, phases)
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } } }
      setError(apiError?.response?.data?.detail || 'Erreur lors de la creation du chantier')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Nouveau chantier</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom du chantier *
            </label>
            <input
              type="text"
              required
              value={formData.nom}
              onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
              className="input"
              placeholder="Ex: Residence Les Pins"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Adresse *
            </label>
            <textarea
              required
              value={formData.adresse}
              onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
              className="input"
              rows={2}
              placeholder="Ex: 12 rue des Lilas, 69003 Lyon"
            />
          </div>

          {/* Section Contacts */}
          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Contacts sur le chantier
              </label>
              <button
                type="button"
                onClick={addContact}
                className="text-primary-600 hover:text-primary-700 text-sm flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
                Ajouter
              </button>
            </div>
            {contacts.map((contact, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={contact.nom}
                  onChange={(e) => updateContact(index, 'nom', e.target.value)}
                  className="input flex-1"
                  placeholder="Nom"
                />
                <input
                  type="tel"
                  value={contact.telephone}
                  onChange={(e) => updateContact(index, 'telephone', e.target.value)}
                  className="input flex-1"
                  placeholder="Telephone"
                />
                <input
                  type="text"
                  value={contact.profession}
                  onChange={(e) => updateContact(index, 'profession', e.target.value)}
                  className="input flex-1"
                  placeholder="Profession"
                />
                {contacts.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeContact(index)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Section Phases/Dates */}
          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Phases du chantier (optionnel)
              </label>
              <button
                type="button"
                onClick={addPhase}
                className="text-primary-600 hover:text-primary-700 text-sm flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
                Ajouter une phase
              </button>
            </div>
            {phases.length === 0 ? (
              <p className="text-sm text-gray-500 italic">Aucune phase definie. Ajoutez des phases si le chantier se fait en plusieurs etapes.</p>
            ) : (
              phases.map((phase, index) => (
                <div key={index} className="border rounded-lg p-3 mb-2 bg-gray-50">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Phase {index + 1}</span>
                    <button
                      type="button"
                      onClick={() => removePhase(index)}
                      className="p-1 text-red-500 hover:bg-red-100 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <input
                    type="text"
                    value={phase.nom}
                    onChange={(e) => updatePhase(index, 'nom', e.target.value)}
                    className="input w-full mb-2"
                    placeholder="Nom de la phase (ex: Gros oeuvre)"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-xs text-gray-500">Debut</label>
                      <input
                        type="date"
                        value={phase.date_debut}
                        onChange={(e) => updatePhase(index, 'date_debut', e.target.value)}
                        className="input w-full"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">Fin</label>
                      <input
                        type="date"
                        value={phase.date_fin}
                        onChange={(e) => updatePhase(index, 'date_fin', e.target.value)}
                        className="input w-full"
                      />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Dates globales du chantier (si pas de phases) */}
          {phases.length === 0 && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date debut prevue
                </label>
                <input
                  type="date"
                  value={formData.date_debut_prevue || ''}
                  onChange={(e) => {
                    setFormData({ ...formData, date_debut_prevue: e.target.value })
                    setError(null)
                  }}
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
                  onChange={(e) => {
                    setFormData({ ...formData, date_fin_prevue: e.target.value })
                    setError(null)
                  }}
                  className="input"
                />
              </div>
            </div>
          )}

          {/* DEV-TVA: Contexte TVA pour pre-remplissage devis */}
          <div className="border-t pt-4">
            <label className="block text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-500" />
              Contexte TVA (optionnel)
            </label>
            <div className="space-y-3 bg-blue-50 p-4 rounded-lg">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Type de travaux</label>
                <select
                  value={formData.type_travaux || ''}
                  onChange={(e) => setFormData({ ...formData, type_travaux: e.target.value as TypeTravaux || undefined })}
                  className="input"
                >
                  <option value="">Non defini</option>
                  {TYPE_TRAVAUX_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label} (TVA {opt.tva})</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={formData.batiment_plus_2ans || false}
                    onChange={(e) => setFormData({ ...formData, batiment_plus_2ans: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600"
                  />
                  Batiment &gt; 2 ans
                </label>
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={formData.usage_habitation || false}
                    onChange={(e) => setFormData({ ...formData, usage_habitation: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600"
                  />
                  Usage habitation
                </label>
              </div>
              {formData.type_travaux && formData.batiment_plus_2ans && formData.usage_habitation && formData.type_travaux !== 'construction_neuve' && (
                <div className="text-xs text-amber-700 bg-amber-50 px-3 py-2 rounded">
                  Les devis lies a ce chantier auront un taux TVA par defaut de <strong>{formData.type_travaux === 'renovation_energetique' ? '5.5%' : '10%'}</strong>
                </div>
              )}
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
              placeholder="Ex: 500"
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
              placeholder="Description du chantier..."
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 btn btn-outline"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.nom || !formData.adresse}
              className="flex-1 btn btn-primary flex items-center justify-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              Creer
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateChantierModal
