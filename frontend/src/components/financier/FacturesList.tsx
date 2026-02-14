/**
 * FacturesList - Liste des factures client (FIN-08)
 *
 * Affiche les factures d'un chantier avec :
 * - Colonnes: numero, type, montant_ttc, montant_net, date_emission, statut, actions
 * - Actions: Emettre, Envoyer, Payer, Annuler (selon statut)
 * - Boutons: "Creer depuis situation" et "Acompte"
 */

import { useState, useEffect, useCallback } from 'react'
import { Loader2, Plus, Send, Mail, CreditCard, XCircle, X } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useAuth } from '../../contexts/AuthContext'
import { logger } from '../../services/logger'
import type { FactureClient, FactureAcompteCreate } from '../../types'
import { STATUT_FACTURE_CONFIG, TYPE_FACTURE_LABELS } from '../../types'
import { formatEUR } from '../../utils/format'

interface FacturesListProps {
  chantierId: number
}

const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export default function FacturesList({ chantierId }: FacturesListProps) {
  const { user } = useAuth()
  const [factures, setFactures] = useState<FactureClient[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAcompteModal, setShowAcompteModal] = useState(false)
  const [saving, setSaving] = useState(false)

  // Acompte form
  const [acompteMontant, setAcompteMontant] = useState('')
  const [acompteEcheance, setAcompteEcheance] = useState('')
  const [acompteNotes, setAcompteNotes] = useState('')

  const canManage = user?.role === 'admin' || user?.role === 'conducteur'

  const loadFactures = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.listFactures(chantierId)
      setFactures(data)
    } catch (err) {
      setError('Erreur lors du chargement des factures')
      logger.error('Erreur chargement factures', err, { context: 'FacturesList' })
    } finally {
      setLoading(false)
    }
  }, [chantierId])

  useEffect(() => {
    loadFactures()
  }, [loadFactures])

  const handleEmettre = async (id: number) => {
    try {
      const updated = await financierService.emettreFacture(id)
      setFactures(prev => prev.map(f => f.id === updated.id ? updated : f))
    } catch (err) {
      console.error('Erreur emission facture:', err)
    }
  }

  const handleEnvoyer = async (id: number) => {
    try {
      const updated = await financierService.envoyerFacture(id)
      setFactures(prev => prev.map(f => f.id === updated.id ? updated : f))
    } catch (err) {
      console.error('Erreur envoi facture:', err)
    }
  }

  const handlePayer = async (id: number) => {
    try {
      const updated = await financierService.payerFacture(id)
      setFactures(prev => prev.map(f => f.id === updated.id ? updated : f))
    } catch (err) {
      console.error('Erreur paiement facture:', err)
    }
  }

  const handleAnnuler = async (id: number) => {
    if (!confirm('Annuler cette facture ?')) return
    try {
      const updated = await financierService.annulerFacture(id)
      setFactures(prev => prev.map(f => f.id === updated.id ? updated : f))
    } catch (err) {
      console.error('Erreur annulation facture:', err)
    }
  }

  const handleCreateAcompte = async () => {
    const montant = parseFloat(acompteMontant)
    if (isNaN(montant) || montant <= 0) return

    try {
      setSaving(true)
      const data: FactureAcompteCreate = {
        chantier_id: chantierId,
        montant_ht: montant,
        date_echeance: acompteEcheance || undefined,
        notes: acompteNotes.trim() || undefined,
      }
      await financierService.createFactureAcompte(data)
      setShowAcompteModal(false)
      setAcompteMontant('')
      setAcompteEcheance('')
      setAcompteNotes('')
      await loadFactures()
    } catch (err) {
      console.error('Erreur creation facture acompte:', err)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    )
  }

  return (
    <div className="bg-white border rounded-xl">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 border-b">
        <h3 className="font-semibold text-gray-900">Factures client</h3>
        {canManage && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAcompteModal(true)}
              className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm transition-colors"
            >
              <Plus size={14} />
              Acompte
            </button>
          </div>
        )}
      </div>

      {factures.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Aucune facture pour ce chantier
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Numero</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Type</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Montant TTC</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Net</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Emission</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Echeance</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Statut</th>
                {canManage && (
                  <th className="text-center px-4 py-3 font-medium text-gray-500">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {factures.map((facture) => {
                const statutConfig = STATUT_FACTURE_CONFIG[facture.statut]
                return (
                  <tr key={facture.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-gray-700">{facture.numero_facture}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {TYPE_FACTURE_LABELS[facture.type_facture]}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      {formatEUR(facture.montant_ttc)}
                    </td>
                    <td className="px-4 py-3 text-right font-medium whitespace-nowrap">
                      {formatEUR(facture.montant_net)}
                    </td>
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                      {formatDate(facture.date_emission)}
                    </td>
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                      {formatDate(facture.date_echeance)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: statutConfig.couleur + '20',
                          color: statutConfig.couleur,
                        }}
                      >
                        {statutConfig.label}
                      </span>
                    </td>
                    {canManage && (
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1">
                          {facture.statut === 'brouillon' && (
                            <button
                              onClick={() => handleEmettre(facture.id)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                              title="Emettre" aria-label="Emettre la facture"
                            >
                              <Send size={16} />
                            </button>
                          )}
                          {facture.statut === 'emise' && (
                            <button
                              onClick={() => handleEnvoyer(facture.id)}
                              className="p-2 text-indigo-600 hover:bg-indigo-50 rounded"
                              title="Envoyer" aria-label="Envoyer la facture"
                            >
                              <Mail size={16} />
                            </button>
                          )}
                          {facture.statut === 'envoyee' && (
                            <button
                              onClick={() => handlePayer(facture.id)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded"
                              title="Marquer comme payee" aria-label="Marquer la facture comme payee"
                            >
                              <CreditCard size={16} />
                            </button>
                          )}
                          {facture.statut !== 'annulee' && facture.statut !== 'payee' && (
                            <button
                              onClick={() => handleAnnuler(facture.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded"
                              title="Annuler" aria-label="Annuler la facture"
                            >
                              <XCircle size={16} />
                            </button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal Acompte */}
      {showAcompteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold text-gray-900">Nouvelle facture d'acompte</h3>
              <button onClick={() => setShowAcompteModal(false)} className="text-gray-600 hover:text-gray-800">
                <X size={20} />
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Montant HT (EUR) *</label>
                <input
                  type="number"
                  value={acompteMontant}
                  onChange={(e) => setAcompteMontant(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Montant HT"
                  min={0}
                  step="0.01"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date d'echeance</label>
                <input
                  type="date"
                  value={acompteEcheance}
                  onChange={(e) => setAcompteEcheance(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={acompteNotes}
                  onChange={(e) => setAcompteNotes(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Notes..."
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 p-4 border-t">
              <button
                onClick={() => setShowAcompteModal(false)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={handleCreateAcompte}
                disabled={saving || !acompteMontant}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {saving ? 'Creation...' : 'Creer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
