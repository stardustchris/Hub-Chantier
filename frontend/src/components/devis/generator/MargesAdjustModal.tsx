import { useState } from 'react'
import { X, Save } from 'lucide-react'
import type { DevisDetail, DevisUpdate } from '../../../types'
import { devisService } from '../../../services/devis'

interface Props {
  devis: DevisDetail
  onClose: () => void
  onSaved: () => void
}

interface MargeField {
  key: keyof DevisUpdate
  label: string
  value: number
}

export default function MargesAdjustModal({ devis, onClose, onSaved }: Props) {
  const globalFields: MargeField[] = [
    { key: 'taux_marge_global', label: 'Marge globale', value: devis.taux_marge_global || 0 },
    { key: 'coefficient_frais_generaux', label: 'Frais generaux', value: devis.coefficient_frais_generaux || 0 },
  ]

  const categorieFields: MargeField[] = [
    { key: 'taux_marge_moe', label: "Main d'oeuvre", value: devis.taux_marge_moe || 0 },
    { key: 'taux_marge_materiaux', label: 'Materiaux', value: devis.taux_marge_materiaux || 0 },
    { key: 'taux_marge_sous_traitance', label: 'Sous-traitance', value: devis.taux_marge_sous_traitance || 0 },
    { key: 'taux_marge_materiel', label: 'Materiel', value: devis.taux_marge_materiel || 0 },
    { key: 'taux_marge_deplacement', label: 'Deplacement', value: devis.taux_marge_deplacement || 0 },
  ]

  const [globalValues, setGlobalValues] = useState<Record<string, number>>(
    Object.fromEntries(globalFields.map(f => [f.key, f.value]))
  )
  const [catValues, setCatValues] = useState<Record<string, number>>(
    Object.fromEntries(categorieFields.map(f => [f.key, f.value]))
  )
  const [lotMarges, setLotMarges] = useState<Record<number, number>>(
    Object.fromEntries(devis.lots.map(lot => [lot.id, lot.marge_lot_pct || 0]))
  )
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      const update: DevisUpdate = {}
      for (const [key, val] of Object.entries(globalValues)) {
        ;(update as Record<string, number>)[key] = val
      }
      for (const [key, val] of Object.entries(catValues)) {
        ;(update as Record<string, number>)[key] = val
      }
      await devisService.updateDevis(devis.id, update)

      for (const lot of devis.lots) {
        const newMarge = lotMarges[lot.id]
        if (newMarge !== (lot.marge_lot_pct || 0)) {
          await devisService.updateLot(lot.id, { marge_lot_pct: newMarge })
        }
      }

      onSaved()
    } catch {
      setError('Erreur lors de la sauvegarde des marges')
    } finally {
      setSaving(false)
    }
  }

  const renderRow = (label: string, key: string, value: number, onChange: (key: string, val: number) => void) => (
    <div key={key} className="flex items-center justify-between py-2">
      <span className="text-sm text-gray-700">{label}</span>
      <div className="flex items-center gap-1">
        <input
          type="number"
          step="0.1"
          min="0"
          max="100"
          className="w-20 text-right text-sm border border-gray-300 rounded-lg px-2 py-1 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          value={value}
          onChange={e => onChange(key, parseFloat(e.target.value) || 0)}
        />
        <span className="text-sm text-gray-500">%</span>
      </div>
    </div>
  )

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Ajustement des marges</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Global margins */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">
              Marges globales
            </h3>
            <div className="divide-y divide-gray-50">
              {globalFields.map(f =>
                renderRow(f.label, f.key, globalValues[f.key] ?? 0, (k, v) =>
                  setGlobalValues(prev => ({ ...prev, [k]: v }))
                )
              )}
            </div>
          </div>

          {/* Category margins */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">
              Marges par categorie
            </h3>
            <div className="divide-y divide-gray-50">
              {categorieFields.map(f =>
                renderRow(f.label, f.key, catValues[f.key] ?? 0, (k, v) =>
                  setCatValues(prev => ({ ...prev, [k]: v }))
                )
              )}
            </div>
          </div>

          {/* Per-lot margins */}
          {devis.lots.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-2">
                Marges par lot
              </h3>
              <div className="divide-y divide-gray-50">
                {devis.lots.map(lot =>
                  renderRow(
                    `${lot.numero} - ${lot.titre}`,
                    String(lot.id),
                    lotMarges[lot.id] ?? 0,
                    (k, v) => setLotMarges(prev => ({ ...prev, [Number(k)]: v }))
                  )
                )}
              </div>
            </div>
          )}

          {error && (
            <p className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>
          )}
        </div>

        <div className="flex justify-end gap-3 p-6 border-t border-gray-100">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
          >
            Annuler
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Enregistrement...' : 'Enregistrer'}
          </button>
        </div>
      </div>
    </div>
  )
}
