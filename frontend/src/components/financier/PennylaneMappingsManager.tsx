/**
 * PennylaneMappingsManager - Gestion des mappings codes analytiques -> chantiers
 * Module 18.12 - CONN-14
 *
 * Permet de :
 * - Lister les mappings existants
 * - Creer un nouveau mapping
 * - Supprimer un mapping
 */

import { useState, useEffect, useCallback } from 'react'
import {
  Loader2,
  Plus,
  Trash2,
  Building2,
  Tag,
  AlertCircle,
} from 'lucide-react'
import { pennylaneService } from '../../services/pennylane'
import { chantiersService } from '../../services/chantiers'
import { logger } from '../../services/logger'
import type { PennylaneMapping } from '../../types/pennylane'
import type { Chantier } from '../../types'

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export default function PennylaneMappingsManager() {
  const [mappings, setMappings] = useState<PennylaneMapping[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [deleting, setDeleting] = useState<number | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Form state
  const [newCodeAnalytique, setNewCodeAnalytique] = useState('')
  const [newChantierId, setNewChantierId] = useState<number | ''>('')

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const [mappingsData, chantiersData] = await Promise.all([
        pennylaneService.getMappings(),
        chantiersService.list({ size: 200 }),
      ])

      setMappings(mappingsData)
      setChantiers(chantiersData.items)
    } catch (err) {
      setError('Erreur lors du chargement des mappings')
      logger.error('Erreur chargement mappings Pennylane', err, { context: 'PennylaneMappingsManager' })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newCodeAnalytique.trim() || !newChantierId) return

    try {
      setSubmitting(true)
      await pennylaneService.createMapping({
        code_analytique: newCodeAnalytique.trim().toUpperCase(),
        chantier_id: newChantierId,
      })

      // Reset form and reload
      setNewCodeAnalytique('')
      setNewChantierId('')
      setShowForm(false)
      await loadData()
    } catch (err) {
      setError('Erreur lors de la creation du mapping')
      logger.error('Erreur creation mapping', err, { context: 'PennylaneMappingsManager' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Supprimer ce mapping ? Les prochaines factures avec ce code analytique ne seront plus associees automatiquement.')) {
      return
    }

    try {
      setDeleting(id)
      await pennylaneService.deleteMapping(id)
      await loadData()
    } catch (err) {
      setError('Erreur lors de la suppression')
      logger.error('Erreur suppression mapping', err, { context: 'PennylaneMappingsManager' })
    } finally {
      setDeleting(null)
    }
  }

  // Chantiers non encore mappes
  const unmappedChantiers = chantiers.filter(
    (c) => !mappings.some((m) => m.chantier_id === Number(c.id))
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Mappings Analytiques</h2>
          <p className="text-sm text-gray-500">
            Associez les codes analytiques Pennylane aux chantiers Hub Chantier
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={16} />
          Nouveau mapping
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
          <AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
          <div>
            <p>{error}</p>
            <button onClick={() => setError(null)} className="text-sm underline mt-1">
              Fermer
            </button>
          </div>
        </div>
      )}

      {/* Create form */}
      {showForm && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <h3 className="font-medium text-blue-900 mb-3">Creer un nouveau mapping</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Code analytique Pennylane
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={newCodeAnalytique}
                    onChange={(e) => setNewCodeAnalytique(e.target.value.toUpperCase())}
                    placeholder="Ex: MONTMELIAN, LYON01"
                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                  <Tag size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600" />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Code tel qu'il apparait dans Pennylane
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Chantier Hub Chantier
                </label>
                <div className="relative">
                  <select
                    value={newChantierId}
                    onChange={(e) => setNewChantierId(e.target.value ? Number(e.target.value) : '')}
                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none"
                    required
                  >
                    <option value="">Selectionner un chantier</option>
                    {unmappedChantiers.map((chantier) => (
                      <option key={chantier.id} value={chantier.id}>
                        {chantier.code} - {chantier.nom}
                      </option>
                    ))}
                  </select>
                  <Building2 size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600" />
                </div>
                {unmappedChantiers.length === 0 && (
                  <p className="text-xs text-orange-600 mt-1">
                    Tous les chantiers ont deja un mapping
                  </p>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => { setShowForm(false); setNewCodeAnalytique(''); setNewChantierId('') }}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={submitting || !newCodeAnalytique.trim() || !newChantierId}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {submitting && <Loader2 size={16} className="animate-spin" />}
                Creer le mapping
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Mappings list */}
      {mappings.length === 0 ? (
        <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-xl">
          <Tag className="w-12 h-12 mx-auto text-gray-500 mb-3" />
          <p className="font-medium">Aucun mapping configure</p>
          <p className="text-sm">Creez des mappings pour associer automatiquement les factures aux chantiers</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Code analytique</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Chantier</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Date creation</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {mappings.map((mapping) => (
                <tr key={mapping.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                      <Tag size={14} />
                      {mapping.code_analytique}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Building2 size={16} className="text-gray-600" />
                      <span className="font-medium text-gray-900">{mapping.chantier_nom}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {formatDate(mapping.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(mapping.id)}
                      disabled={deleting === mapping.id}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg disabled:opacity-50 transition-colors"
                      title="Supprimer ce mapping"
                    >
                      {deleting === mapping.id ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <Trash2 size={16} />
                      )}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Help text */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Comment ca marche ?</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>1. Les factures Pennylane contiennent un code analytique (ex: MONTMELIAN)</li>
          <li>2. Les mappings permettent d'associer ce code a un chantier Hub Chantier</li>
          <li>3. Lors de la synchronisation, les factures sont automatiquement liees au bon chantier</li>
          <li>4. Si aucun mapping n'existe, la facture arrive en reconciliation manuelle</li>
        </ul>
      </div>
    </div>
  )
}
