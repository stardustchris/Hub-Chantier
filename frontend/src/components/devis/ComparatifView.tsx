/**
 * ComparatifView - Affiche le resultat d'un comparatif entre 2 versions de devis
 * Module Devis (Module 20) - DEV-08
 */

import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'
import type { ComparatifDevis, ComparatifLigne, TypeEcart } from '../../types'
import { TYPE_ECART_CONFIG } from '../../types'
import { formatEUR } from '../../utils/format'

const formatPct = (value: number) =>
  new Intl.NumberFormat('fr-FR', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value / 100)

interface ComparatifViewProps {
  comparatif: ComparatifDevis
}

function VariationBar({ value, label }: { value: number; label: string }) {
  const isPositive = value > 0
  const isZero = Math.abs(value) < 0.01
  const width = Math.min(Math.abs(value), 100)

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-gray-600">{label}</span>
        <span
          className={`font-medium ${
            isZero
              ? 'text-gray-500'
              : isPositive
                ? 'text-red-600'
                : 'text-green-600'
          }`}
        >
          {isPositive ? '+' : ''}{formatPct(value)}
        </span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
        <div
          className={`h-2 rounded-full transition-all ${
            isZero
              ? 'bg-gray-300'
              : isPositive
                ? 'bg-red-400'
                : 'bg-green-400'
          }`}
          style={{ width: `${Math.max(width, 2)}%` }}
        />
      </div>
    </div>
  )
}

function EcartCell({ value, isAmount }: { value?: number; isAmount?: boolean }) {
  if (value === undefined || value === null) {
    return <span className="text-gray-400">-</span>
  }
  const isPositive = value > 0
  const isZero = Math.abs(value) < 0.01

  if (isZero) {
    return (
      <span className="inline-flex items-center gap-1 text-gray-500">
        <Minus className="w-3 h-3" />
        {isAmount ? formatEUR(0) : '0'}
      </span>
    )
  }

  return (
    <span
      className={`inline-flex items-center gap-1 font-medium ${
        isPositive ? 'text-red-600' : 'text-green-600'
      }`}
    >
      {isPositive ? (
        <ArrowUpRight className="w-3 h-3" />
      ) : (
        <ArrowDownRight className="w-3 h-3" />
      )}
      {isAmount
        ? `${isPositive ? '+' : ''}${formatEUR(value)}`
        : `${isPositive ? '+' : ''}${value}`}
    </span>
  )
}

function TypeEcartBadge({ type }: { type: TypeEcart }) {
  const config = TYPE_ECART_CONFIG[type]
  return (
    <span
      className="inline-flex px-2 py-0.5 rounded-full text-xs font-medium"
      style={{
        backgroundColor: config.bgColor,
        color: config.couleur,
      }}
    >
      {config.label}
    </span>
  )
}

export default function ComparatifView({ comparatif }: ComparatifViewProps) {
  const lignesParType = comparatif.lignes.reduce(
    (acc, ligne) => {
      acc[ligne.type_ecart] = (acc[ligne.type_ecart] || 0) + 1
      return acc
    },
    {} as Record<TypeEcart, number>
  )

  return (
    <div className="space-y-4">
      {/* En-tete : versions comparees */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
          <div className="text-sm">
            <span className="text-gray-500">Source :</span>{' '}
            <span className="font-medium text-gray-900">
              {comparatif.source_numero}
            </span>
            <span className="mx-2 text-gray-400">→</span>
            <span className="text-gray-500">Cible :</span>{' '}
            <span className="font-medium text-gray-900">
              {comparatif.cible_numero}
            </span>
          </div>
          <span className="text-xs text-gray-500">
            {new Date(comparatif.created_at).toLocaleDateString('fr-FR', {
              day: '2-digit',
              month: 'short',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        {/* Ecarts globaux */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500 mb-1">Ecart montant HT</p>
            <EcartCell value={comparatif.ecart_montant_ht} isAmount />
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500 mb-1">Ecart montant TTC</p>
            <EcartCell value={comparatif.ecart_montant_ttc} isAmount />
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500 mb-1">Ecart marge</p>
            <EcartCell value={comparatif.ecart_marge} isAmount />
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <p className="text-xs text-gray-500 mb-1">Ecart debourse</p>
            <EcartCell value={comparatif.ecart_debourse} isAmount />
          </div>
        </div>

        {/* Barres de variation en % */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
          <VariationBar
            value={comparatif.variation_montant_ht_pct}
            label="Variation montant HT"
          />
          <VariationBar
            value={comparatif.variation_montant_ttc_pct}
            label="Variation montant TTC"
          />
          <VariationBar
            value={comparatif.variation_marge_pct}
            label="Variation marge"
          />
          <VariationBar
            value={comparatif.variation_debourse_pct}
            label="Variation debourse"
          />
        </div>
      </div>

      {/* Resume par type d'ecart */}
      <div className="flex flex-wrap gap-3">
        <div className="text-xs text-gray-500">
          <span className="font-medium text-gray-700">Lots :</span>{' '}
          {comparatif.nb_lots_ajoutes > 0 && (
            <span className="text-green-600">+{comparatif.nb_lots_ajoutes} </span>
          )}
          {comparatif.nb_lots_supprimes > 0 && (
            <span className="text-red-600">-{comparatif.nb_lots_supprimes} </span>
          )}
          {comparatif.nb_lots_modifies > 0 && (
            <span className="text-amber-600">~{comparatif.nb_lots_modifies}</span>
          )}
          {comparatif.nb_lots_ajoutes === 0 &&
            comparatif.nb_lots_supprimes === 0 &&
            comparatif.nb_lots_modifies === 0 && (
              <span className="text-gray-400">aucun changement</span>
            )}
        </div>
        <div className="text-xs text-gray-500">
          <span className="font-medium text-gray-700">Lignes :</span>{' '}
          {comparatif.nb_lignes_ajoutees > 0 && (
            <span className="text-green-600">+{comparatif.nb_lignes_ajoutees} </span>
          )}
          {comparatif.nb_lignes_supprimees > 0 && (
            <span className="text-red-600">-{comparatif.nb_lignes_supprimees} </span>
          )}
          {comparatif.nb_lignes_modifiees > 0 && (
            <span className="text-amber-600">~{comparatif.nb_lignes_modifiees}</span>
          )}
          {comparatif.nb_lignes_ajoutees === 0 &&
            comparatif.nb_lignes_supprimees === 0 &&
            comparatif.nb_lignes_modifiees === 0 && (
              <span className="text-gray-400">aucun changement</span>
            )}
        </div>
        {Object.entries(lignesParType).map(([type, count]) => (
          <span
            key={type}
            className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded"
            style={{
              backgroundColor: TYPE_ECART_CONFIG[type as TypeEcart].bgColor,
              color: TYPE_ECART_CONFIG[type as TypeEcart].couleur,
            }}
          >
            {TYPE_ECART_CONFIG[type as TypeEcart].label}: {count}
          </span>
        ))}
      </div>

      {/* Tableau detail ligne par ligne */}
      {comparatif.lignes.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">
                  Designation
                </th>
                <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase hidden md:table-cell">
                  Lot
                </th>
                <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">
                  Qte source
                </th>
                <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">
                  Qte cible
                </th>
                <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase">
                  Ecart qte
                </th>
                <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">
                  Montant source
                </th>
                <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">
                  Montant cible
                </th>
                <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase">
                  Ecart montant
                </th>
                <th className="text-center py-2 px-3 text-xs font-medium text-gray-500 uppercase">
                  Type
                </th>
              </tr>
            </thead>
            <tbody>
              {comparatif.lignes.map((ligne: ComparatifLigne, idx: number) => (
                <tr
                  key={idx}
                  className="border-b border-gray-100 hover:bg-gray-50"
                  style={{
                    backgroundColor:
                      ligne.type_ecart !== 'identique'
                        ? `${TYPE_ECART_CONFIG[ligne.type_ecart].bgColor}40`
                        : undefined,
                  }}
                >
                  <td className="py-2 px-3 text-gray-900 font-medium max-w-[200px] truncate">
                    {ligne.designation}
                  </td>
                  <td className="py-2 px-3 text-gray-500 hidden md:table-cell">
                    {ligne.lot_titre || '-'}
                  </td>
                  <td className="py-2 px-3 text-right text-gray-600 hidden lg:table-cell">
                    {ligne.quantite_source ?? '-'}
                  </td>
                  <td className="py-2 px-3 text-right text-gray-600 hidden lg:table-cell">
                    {ligne.quantite_cible ?? '-'}
                  </td>
                  <td className="py-2 px-3 text-right">
                    <EcartCell value={ligne.ecart_quantite} />
                  </td>
                  <td className="py-2 px-3 text-right text-gray-600 hidden sm:table-cell">
                    {ligne.montant_source !== undefined
                      ? formatEUR(ligne.montant_source)
                      : '-'}
                  </td>
                  <td className="py-2 px-3 text-right text-gray-600 hidden sm:table-cell">
                    {ligne.montant_cible !== undefined
                      ? formatEUR(ligne.montant_cible)
                      : '-'}
                  </td>
                  <td className="py-2 px-3 text-right">
                    <EcartCell value={ligne.ecart_montant} isAmount />
                  </td>
                  <td className="py-2 px-3 text-center">
                    <TypeEcartBadge type={ligne.type_ecart} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {comparatif.lignes.length === 0 && (
        <p className="text-sm text-gray-500 text-center py-4">
          Aucune difference detectee entre les deux versions.
        </p>
      )}
    </div>
  )
}
