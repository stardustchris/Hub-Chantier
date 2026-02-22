import { useState, useEffect } from 'react'
import { X, Loader2, AlertTriangle } from 'lucide-react'
import type { DevisCreate, DevisUpdate, DevisDetail } from '../../types'
import { TAUX_TVA_OPTIONS, RETENUE_GARANTIE_OPTIONS } from '../../types'
import api from '../../services/api'

interface DevisFormProps {
  devis?: DevisDetail | null
  onSubmit: (data: DevisCreate | DevisUpdate) => Promise<void>
  onCancel: () => void
}

const FALLBACK_COEFF_FG = 19

export default function DevisForm({ devis, onSubmit, onCancel }: DevisFormProps) {
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    objet: devis?.objet || '',
    client_nom: devis?.client_nom || '',
    client_adresse: devis?.client_adresse || '',
    client_email: devis?.client_email || '',
    client_telephone: devis?.client_telephone || '',
    chantier_ref: devis?.chantier_ref || '',
    date_validite: devis?.date_validite?.split('T')[0] || '',
    date_visite: devis?.date_visite?.split('T')[0] || '',
    date_debut_travaux: devis?.date_debut_travaux?.split('T')[0] || '',
    duree_estimee_jours: devis?.duree_estimee_jours ?? '',
    taux_tva_defaut: devis?.taux_tva_defaut ?? 20,
    coefficient_frais_generaux: devis?.coefficient_frais_generaux ?? FALLBACK_COEFF_FG,
    coefficient_productivite: devis?.coefficient_productivite ?? '',
    taux_marge_global: devis?.taux_marge_global ?? 15,
    retenue_garantie_pct: devis?.retenue_garantie_pct ?? 0,
    notes: devis?.notes || '',
    conditions_generales: devis?.conditions_generales || '',
    commentaire: devis?.commentaire || '',
  })

  // Nouveau devis : charger le coefficient FG depuis la config entreprise
  useEffect(() => {
    if (devis) return // En edition, on garde la valeur du devis
    const year = new Date().getFullYear()
    api.get<{ coeff_frais_generaux: string }>(`/api/financier/configuration/${year}`)
      .then((res) => {
        const coeff = Number(res.data.coeff_frais_generaux)
        if (coeff > 0) {
          setForm((prev) => ({ ...prev, coefficient_frais_generaux: coeff }))
        }
      })
      .catch(() => {
        // Config non trouvee : on garde le fallback
      })
  }, [devis])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setLoading(true)
      const data: DevisCreate | DevisUpdate = {
        objet: form.objet,
        client_nom: form.client_nom,
        client_adresse: form.client_adresse || undefined,
        client_email: form.client_email || undefined,
        client_telephone: form.client_telephone || undefined,
        chantier_ref: form.chantier_ref || undefined,
        date_validite: form.date_validite || undefined,
        date_visite: form.date_visite || undefined,
        date_debut_travaux: form.date_debut_travaux || undefined,
        duree_estimee_jours: form.duree_estimee_jours !== '' ? Number(form.duree_estimee_jours) : undefined,
        taux_tva_defaut: form.taux_tva_defaut,
        coefficient_frais_generaux: form.coefficient_frais_generaux,
        coefficient_productivite: form.coefficient_productivite ? Number(form.coefficient_productivite) : undefined,
        taux_marge_global: form.taux_marge_global,
        retenue_garantie_pct: form.retenue_garantie_pct,
        notes: form.notes || undefined,
        conditions_generales: form.conditions_generales || undefined,
        commentaire: form.commentaire || undefined,
      }
      await onSubmit(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">
            {devis ? 'Modifier le devis' : 'Nouveau devis'}
          </h2>
          <button onClick={onCancel} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Objet */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Objet du devis *
            </label>
            <input
              type="text"
              required
              maxLength={500}
              value={form.objet}
              onChange={(e) => setForm({ ...form, objet: e.target.value })}
              placeholder="Ex: Renovation maison individuelle"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Client */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-4">
            <h3 className="text-sm font-semibold text-gray-700">Informations client</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom du client *
                </label>
                <input
                  type="text"
                  required
                  maxLength={200}
                  value={form.client_nom}
                  onChange={(e) => setForm({ ...form, client_nom: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  maxLength={255}
                  value={form.client_email}
                  onChange={(e) => setForm({ ...form, client_email: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Telephone</label>
                <input
                  type="tel"
                  maxLength={30}
                  value={form.client_telephone}
                  onChange={(e) => setForm({ ...form, client_telephone: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Adresse</label>
                <input
                  type="text"
                  maxLength={500}
                  value={form.client_adresse}
                  onChange={(e) => setForm({ ...form, client_adresse: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Chantier et dates travaux */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-4">
            <h3 className="text-sm font-semibold text-gray-700">Chantier et planning</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Chantier associe
                </label>
                <input
                  type="text"
                  maxLength={100}
                  value={form.chantier_ref}
                  onChange={(e) => setForm({ ...form, chantier_ref: e.target.value })}
                  placeholder="Ex: CH-2026-001"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duree estimee (jours)
                </label>
                <input
                  type="number"
                  min="0"
                  value={form.duree_estimee_jours}
                  onChange={(e) => setForm({ ...form, duree_estimee_jours: e.target.value ? Number(e.target.value) : '' })}
                  placeholder="Ex: 30"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Visite prealable
                </label>
                <input
                  type="date"
                  value={form.date_visite}
                  onChange={(e) => setForm({ ...form, date_visite: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Debut des travaux
                </label>
                <input
                  type="date"
                  value={form.date_debut_travaux}
                  onChange={(e) => setForm({ ...form, date_debut_travaux: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Parametres financiers */}
          <div className="bg-blue-50 rounded-lg p-4 space-y-4">
            <h3 className="text-sm font-semibold text-blue-700">Parametres financiers</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Taux TVA</label>
                <select
                  value={form.taux_tva_defaut}
                  onChange={(e) => setForm({ ...form, taux_tva_defaut: Number(e.target.value) })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {TAUX_TVA_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Frais generaux (%)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={form.coefficient_frais_generaux}
                  onChange={(e) => setForm({ ...form, coefficient_frais_generaux: Number(e.target.value) })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Marge globale (%)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={form.taux_marge_global}
                  onChange={(e) => setForm({ ...form, taux_marge_global: Number(e.target.value) })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Coeff. productivite
                </label>
                <input
                  type="number"
                  min="0.5"
                  max="2.0"
                  step="0.05"
                  value={form.coefficient_productivite}
                  onChange={(e) => setForm({ ...form, coefficient_productivite: e.target.value })}
                  placeholder="1.0"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Retenue de garantie (DEV-22) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Retenue de garantie
              </label>
              <div className="space-y-2">
                <div className="flex gap-2">
                  {RETENUE_GARANTIE_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => setForm({ ...form, retenue_garantie_pct: opt.value })}
                      className={`flex-1 px-3 py-2 text-sm rounded-lg border transition-colors ${
                        form.retenue_garantie_pct === opt.value
                          ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                          : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
                <input
                  type="number"
                  min="0"
                  max="5"
                  step="0.5"
                  value={form.retenue_garantie_pct}
                  onChange={(e) => setForm({ ...form, retenue_garantie_pct: Number(e.target.value) })}
                  className="w-32 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Personnalisé"
                />
                {form.retenue_garantie_pct > 5 && (
                  <p className="text-xs text-orange-600 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    Retenue de garantie plafonnée à 5% (loi 71-584)
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Date validite */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date de validite
            </label>
            <input
              type="date"
              value={form.date_validite}
              onChange={(e) => setForm({ ...form, date_validite: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes internes</label>
            <textarea
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              rows={2}
              maxLength={2000}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Conditions generales */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Conditions generales
            </label>
            <textarea
              value={form.conditions_generales}
              onChange={(e) => setForm({ ...form, conditions_generales: e.target.value })}
              rows={2}
              maxLength={2000}
              placeholder="Ex: 30% a la commande, solde a la livraison"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Commentaire client */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Commentaire (visible client)
            </label>
            <textarea
              value={form.commentaire}
              onChange={(e) => setForm({ ...form, commentaire: e.target.value })}
              rows={3}
              maxLength={5000}
              placeholder="Commentaire libre visible sur le devis client..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading || !form.objet || !form.client_nom}
              className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 flex items-center gap-2"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {devis ? 'Enregistrer' : 'Creer le devis'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
