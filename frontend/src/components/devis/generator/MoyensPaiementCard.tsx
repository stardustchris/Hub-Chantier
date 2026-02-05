import { useState } from 'react'
import { CreditCard, FileCheck, Banknote } from 'lucide-react'
import { devisService } from '../../../services/devis'
import type { DevisDetail } from '../../../types'

interface Props {
  devis: DevisDetail
  isEditable: boolean
  onSaved: () => void
}

const MOYENS = [
  { id: 'virement', label: 'Virement bancaire', icon: CreditCard, desc: 'IBAN de l\'entreprise' },
  { id: 'cheque', label: 'Cheque', icon: FileCheck, desc: 'A l\'ordre de Greg Construction' },
  { id: 'especes', label: 'Especes', icon: Banknote, desc: 'Limite a 1 000 EUR (reglementation)' },
]

export default function MoyensPaiementCard({ devis, isEditable, onSaved }: Props) {
  const [selected, setSelected] = useState<string[]>(devis.moyens_paiement || ['virement'])

  const handleToggle = async (moyenId: string) => {
    if (!isEditable) return
    const next = selected.includes(moyenId)
      ? selected.filter(m => m !== moyenId)
      : [...selected, moyenId]
    setSelected(next)
    try {
      await devisService.updateDevis(devis.id, { moyens_paiement: next })
      onSaved()
    } catch { /* silent */ }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">Moyens de paiement acceptes</h3>
      <div className="space-y-3">
        {MOYENS.map(moyen => {
          const isChecked = selected.includes(moyen.id)
          return (
            <label
              key={moyen.id}
              className={`flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                isChecked
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-gray-200 hover:border-indigo-300'
              } ${!isEditable ? 'opacity-60 cursor-default' : ''}`}
            >
              <input
                type="checkbox"
                checked={isChecked}
                onChange={() => handleToggle(moyen.id)}
                disabled={!isEditable}
                className="mt-0.5 rounded border-gray-300 text-indigo-600 shrink-0"
              />
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <moyen.icon className={`w-4 h-4 shrink-0 ${isChecked ? 'text-indigo-600' : 'text-gray-400'}`} />
                  <span className="font-medium text-sm text-gray-900 truncate">{moyen.label}</span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5 truncate">{moyen.desc}</p>
              </div>
            </label>
          )
        })}
      </div>
    </div>
  )
}
