/**
 * FraisChantierPanel - Gestion des frais de chantier (compte prorata, frais generaux, installations)
 * Module Devis (Module 20) - DEV-25
 */

import { useState, useEffect, useCallback } from 'react'
import {
  Plus,
  Trash2,
  Edit2,
  Check,
  X,
  Loader2,
  Building2,
  Percent,
  Landmark,
  HardHat,
  MoreHorizontal,
  PieChart,
} from 'lucide-react'
import { devisService } from '../../services/devis'
import type {
  FraisChantierDevis,
  FraisChantierCreate,
  FraisChantierUpdate,
  RepartitionFraisLot,
  TypeFraisChantier,
  ModeRepartition,
  LotDevis,
} from '../../types'
import {
  TYPE_FRAIS_LABELS,
  MODE_REPARTITION_LABELS,
  TAUX_TVA_OPTIONS,
} from '../../types'
import { formatEUR } from '../../utils/format'

const TYPE_FRAIS_ICONS: Record<TypeFraisChantier, typeof Building2> = {
  compte_prorata: Landmark,
  frais_generaux: Percent,
  installation_chantier: HardHat,
  autre: MoreHorizontal,
}

interface FraisChantierPanelProps {
  devisId: number
  isEditable: boolean
  lots?: LotDevis[]
}

export default function FraisChantierPanel({ devisId, isEditable, lots = [] }: FraisChantierPanelProps) {
  const [fraisList, setFraisList] = useState<FraisChantierDevis[]>([])
  const [repartition, setRepartition] = useState<RepartitionFraisLot[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Formulaire ajout / edition
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<FraisChantierCreate>({
    type_frais: 'frais_generaux',
    libelle: '',
    montant_ht: 0,
    mode_repartition: 'prorata_lots',
    taux_tva: 20,
  })

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const [frais, rep] = await Promise.all([
        devisService.listFraisChantier(devisId),
        devisService.getRepartitionFrais(devisId),
      ])
      setFraisList(frais)
      setRepartition(rep)
    } catch {
      setError('Erreur lors du chargement des frais de chantier')
    } finally {
      setLoading(false)
    }
  }, [devisId])

  useEffect(() => {
    loadData()
  }, [loadData])

  const resetForm = () => {
    setFormData({
      type_frais: 'frais_generaux',
      libelle: '',
      montant_ht: 0,
      mode_repartition: 'prorata_lots',
      taux_tva: 20,
    })
    setEditingId(null)
    setShowForm(false)
  }

  const handleSubmit = async () => {
    if (!formData.libelle.trim() || formData.montant_ht <= 0) return
    try {
      setActionLoading(true)
      if (editingId !== null) {
        const updateData: FraisChantierUpdate = { ...formData }
        await devisService.updateFraisChantier(editingId, updateData)
      } else {
        await devisService.createFraisChantier(devisId, formData)
      }
      resetForm()
      await loadData()
    } catch {
      setError('Erreur lors de la sauvegarde')
    } finally {
      setActionLoading(false)
    }
  }

  const handleEdit = (frais: FraisChantierDevis) => {
    setEditingId(frais.id)
    setFormData({
      type_frais: frais.type_frais,
      libelle: frais.libelle,
      montant_ht: frais.montant_ht,
      mode_repartition: frais.mode_repartition,
      taux_tva: frais.taux_tva,
      ordre: frais.ordre,
      lot_devis_id: frais.lot_devis_id,
    })
    setShowForm(true)
  }

  const handleDelete = async (fraisId: number) => {
    if (!window.confirm('Supprimer ce frais de chantier ?')) return
    try {
      setActionLoading(true)
      await devisService.deleteFraisChantier(fraisId)
      await loadData()
    } catch {
      setError('Erreur lors de la suppression')
    } finally {
      setActionLoading(false)
    }
  }

  const totalHT = fraisList.reduce((sum, f) => sum + Number(f.montant_ht), 0)
  const totalTTC = fraisList.reduce((sum, f) => sum + Number(f.montant_ttc), 0)
  const hasProrataFrais = fraisList.some((f) => f.mode_repartition === 'prorata_lots')

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm">
          {error}
          <button onClick={() => setError(null)} className="ml-2 underline">Fermer</button>
        </div>
      )}

      {/* Liste des frais */}
      {fraisList.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Libelle</th>
                <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase">Montant HT</th>
                <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase">TVA</th>
                <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase">Montant TTC</th>
                <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Repartition</th>
                {isEditable && (
                  <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
                )}
              </tr>
            </thead>
            <tbody>
              {fraisList.map((frais) => {
                const Icon = TYPE_FRAIS_ICONS[frais.type_frais]
                return (
                  <tr key={frais.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-3">
                      <div className="flex items-center gap-2">
                        <Icon className="w-4 h-4 text-gray-600 flex-shrink-0" />
                        <span className="text-gray-700">{TYPE_FRAIS_LABELS[frais.type_frais]}</span>
                      </div>
                    </td>
                    <td className="py-2 px-3 text-gray-900 font-medium">{frais.libelle}</td>
                    <td className="py-2 px-3 text-right text-gray-900">{formatEUR(Number(frais.montant_ht))}</td>
                    <td className="py-2 px-3 text-right text-gray-500">{Number(frais.taux_tva)}%</td>
                    <td className="py-2 px-3 text-right text-gray-900">{formatEUR(Number(frais.montant_ttc))}</td>
                    <td className="py-2 px-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        frais.mode_repartition === 'prorata_lots'
                          ? 'bg-blue-50 text-blue-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {MODE_REPARTITION_LABELS[frais.mode_repartition]}
                      </span>
                    </td>
                    {isEditable && (
                      <td className="py-2 px-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => handleEdit(frais)}
                            className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                            title="Modifier"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(frais.id)}
                            disabled={actionLoading}
                            className="p-1 text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
                            title="Supprimer"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
            <tfoot>
              <tr className="border-t-2 border-gray-300 font-semibold">
                <td colSpan={2} className="py-3 px-3 text-gray-700">
                  Total frais de chantier
                </td>
                <td className="py-3 px-3 text-right text-gray-900">{formatEUR(totalHT)}</td>
                <td className="py-3 px-3"></td>
                <td className="py-3 px-3 text-right text-gray-900">{formatEUR(totalTTC)}</td>
                <td colSpan={isEditable ? 2 : 1}></td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}

      {fraisList.length === 0 && !showForm && (
        <div className="text-center py-8 text-gray-600">
          <Building2 className="w-8 h-8 mx-auto mb-2 text-gray-500" />
          <p>Aucun frais de chantier</p>
          {isEditable && <p className="text-sm mt-1">Ajoutez des frais (compte prorata, installations, etc.)</p>}
        </div>
      )}

      {/* Formulaire inline ajout / edition */}
      {isEditable && showForm && (
        <div className="border border-blue-200 rounded-lg bg-blue-50 p-4 space-y-3">
          <h4 className="text-sm font-semibold text-gray-700">
            {editingId !== null ? 'Modifier le frais' : 'Ajouter un frais de chantier'}
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {/* Type de frais */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Type de frais</label>
              <select
                value={formData.type_frais}
                onChange={(e) => setFormData({ ...formData, type_frais: e.target.value as TypeFraisChantier })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
              >
                {(Object.keys(TYPE_FRAIS_LABELS) as TypeFraisChantier[]).map((type) => (
                  <option key={type} value={type}>{TYPE_FRAIS_LABELS[type]}</option>
                ))}
              </select>
            </div>

            {/* Libelle */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Libelle</label>
              <input
                type="text"
                value={formData.libelle}
                onChange={(e) => setFormData({ ...formData, libelle: e.target.value })}
                placeholder="Ex: Base vie chantier"
                maxLength={300}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              />
            </div>

            {/* Montant HT */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Montant HT</label>
              <input
                type="number"
                value={formData.montant_ht || ''}
                onChange={(e) => setFormData({ ...formData, montant_ht: parseFloat(e.target.value) || 0 })}
                placeholder="0.00"
                min={0}
                step={0.01}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              />
            </div>

            {/* Taux TVA */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Taux TVA</label>
              <select
                value={formData.taux_tva ?? 20}
                onChange={(e) => setFormData({ ...formData, taux_tva: parseFloat(e.target.value) })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
              >
                {TAUX_TVA_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>

            {/* Mode de repartition */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Mode de repartition</label>
              <select
                value={formData.mode_repartition}
                onChange={(e) => setFormData({
                  ...formData,
                  mode_repartition: e.target.value as ModeRepartition,
                  lot_devis_id: e.target.value === 'prorata_lots' ? undefined : formData.lot_devis_id,
                })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
              >
                {(Object.keys(MODE_REPARTITION_LABELS) as ModeRepartition[]).map((mode) => (
                  <option key={mode} value={mode}>{MODE_REPARTITION_LABELS[mode]}</option>
                ))}
              </select>
            </div>

            {/* Lot specifique (si global) */}
            {formData.mode_repartition === 'global' && lots.length > 0 && (
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Affecter a un lot (optionnel)</label>
                <select
                  value={formData.lot_devis_id ?? ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    lot_devis_id: e.target.value ? Number(e.target.value) : undefined,
                  })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
                >
                  <option value="">Aucun lot</option>
                  {lots.map((lot) => (
                    <option key={lot.id} value={lot.id}>{lot.numero} - {lot.titre}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Actions formulaire */}
          <div className="flex items-center gap-2 pt-2">
            <button
              onClick={handleSubmit}
              disabled={actionLoading || !formData.libelle.trim() || formData.montant_ht <= 0}
              className="inline-flex items-center gap-1 px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 transition-colors"
            >
              {actionLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Check className="w-4 h-4" />
              )}
              {editingId !== null ? 'Enregistrer' : 'Ajouter'}
            </button>
            <button
              onClick={resetForm}
              className="inline-flex items-center gap-1 px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
              Annuler
            </button>
          </div>
        </div>
      )}

      {/* Bouton ajouter */}
      {isEditable && !showForm && (
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 w-full px-4 py-3 text-sm text-blue-600 border border-dashed border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Ajouter un frais de chantier
        </button>
      )}

      {/* Section repartition par lot */}
      {hasProrataFrais && repartition.length > 0 && (
        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
          <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
            <PieChart className="w-4 h-4 text-blue-500" />
            Repartition des frais par lot (prorata)
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Lot</th>
                  <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase">Total lot HT</th>
                  <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase">Poids</th>
                  <th className="text-right py-2 px-3 text-xs font-medium text-gray-500 uppercase">Frais repercutes</th>
                </tr>
              </thead>
              <tbody>
                {repartition.map((rep) => (
                  <tr key={rep.lot_id} className="border-b border-gray-100">
                    <td className="py-2 px-3 text-gray-900 font-medium">{rep.lot_libelle}</td>
                    <td className="py-2 px-3 text-right text-gray-700">{formatEUR(Number(rep.lot_total_ht))}</td>
                    <td className="py-2 px-3 text-right text-gray-500">{Number(rep.poids_pct).toFixed(1)}%</td>
                    <td className="py-2 px-3 text-right text-blue-700 font-medium">
                      {formatEUR(Number(rep.montant_frais_repercute))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
