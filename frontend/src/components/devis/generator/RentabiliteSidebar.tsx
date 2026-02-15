import { useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import type { DevisDetail } from '../../../types'
import MargesAdjustModal from './MargesAdjustModal'
import { formatEUR } from '../../../utils/format'

interface Props {
  devis: DevisDetail
  onSaved?: () => void
}

const COLORS = ['#3B82F6', '#8B5CF6', '#10B981']

export default function RentabiliteSidebar({ devis, onSaved }: Props) {
  const [showMarges, setShowMarges] = useState(false)

  // Calcul indicatif cote client pour affichage temps reel.
  // SSOT = backend (calcul_financier.py + calcul_totaux_use_cases.py).
  // Formule : Marge (%) = (Vente HT - Debourse Sec - Frais Generaux) / Vente HT x 100
  const totalDebourse = devis.lots.reduce((sum, lot) => sum + Number(lot.debourse_sec || 0), 0)
  const totalVente = Number(devis.montant_total_ht || 0)
  const fraisGeneraux = totalDebourse * Number(devis.coefficient_frais_generaux || 0) / 100
  const benefice = totalVente - totalDebourse - fraisGeneraux
  const margePct = totalVente > 0 ? Math.round(((benefice / totalVente) * 100) * 100) / 100 : null

  const data = [
    { name: 'Debourse sec', value: Math.max(totalDebourse, 0) },
    { name: 'Frais generaux', value: Math.max(fraisGeneraux, 0) },
    { name: 'Benefice', value: Math.max(benefice, 0) },
  ].filter(d => d.value > 0)

  const labels = [
    { name: 'Debourse sec', value: totalDebourse, color: '#3B82F6' },
    { name: 'Frais generaux', value: fraisGeneraux, color: '#8B5CF6' },
    { name: 'Benefice', value: benefice, color: '#10B981' },
  ]

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Rentabilite</h3>
          <button
            onClick={() => setShowMarges(true)}
            className="text-indigo-600 hover:text-indigo-700 text-sm"
          >
            Details
          </button>
        </div>

        <div className="relative mx-auto w-40 h-40 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={70}
                dataKey="value"
                strokeWidth={0}
              >
                {data.map((entry, i) => (
                  <Cell key={entry.name} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-2xl font-bold ${margePct === null ? 'text-gray-500' : 'text-gray-900'}`}>
              {margePct === null ? 'N/D' : `${margePct.toFixed(2)}\u00a0%`}
            </span>
            <span className="text-xs text-gray-500">Coeff. majoration</span>
          </div>
        </div>

        <div className="space-y-2">
          {labels.map(item => (
            <div key={item.name} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-gray-600">{item.name}</span>
              </div>
              <span className="font-medium text-gray-900">{formatEUR(item.value)}</span>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Total vente HT</span>
            <span className="font-semibold text-gray-900">{formatEUR(totalVente)}</span>
          </div>
        </div>
      </div>

      {showMarges && (
        <MargesAdjustModal
          devis={devis}
          onClose={() => setShowMarges(false)}
          onSaved={() => {
            setShowMarges(false)
            onSaved?.()
          }}
        />
      )}
    </>
  )
}
