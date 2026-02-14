/**
 * RelancesPanel - Gestion des relances automatiques pour un devis
 * Module Devis (Module 20) - DEV-24
 */

import { useState, useEffect, useCallback } from 'react'
import { devisService } from '../../services/devis'
import type {
  RelanceDevis,
  RelancesHistorique,
  TypeRelance,
  StatutDevis,
} from '../../types'
import { STATUT_RELANCE_CONFIG, TYPE_RELANCE_LABELS } from '../../types'
import {
  Bell,
  BellOff,
  Send,
  XCircle,
  Loader2,
  AlertCircle,
  Clock,
  CheckCircle,
  MinusCircle,
  AlertTriangle,
  Plus,
  Trash2,
} from 'lucide-react'

interface RelancesPanelProps {
  devisId: number
  devisStatut: StatutDevis
}

/** Determine si une relance planifiee est en retard */
function isEnRetard(relance: RelanceDevis): boolean {
  if (relance.statut !== 'planifiee') return false
  const now = new Date()
  const datePrevue = new Date(relance.date_prevue)
  return datePrevue < now
}

/** Formater une date en francais */
function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
}

/** Formater une date avec heure */
function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function RelancesPanel({ devisId, devisStatut }: RelancesPanelProps) {
  const [historique, setHistorique] = useState<RelancesHistorique | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState(false)

  // Etat local pour edition de la config
  const [editActif, setEditActif] = useState(false)
  const [editDelais, setEditDelais] = useState<number[]>([7, 15, 30])
  const [editTypeRelance, setEditTypeRelance] = useState<TypeRelance>('email')
  const [configModified, setConfigModified] = useState(false)

  const statutsVisibles: StatutDevis[] = ['envoye', 'vu', 'en_negociation']
  const isVisible = statutsVisibles.includes(devisStatut)

  const loadData = useCallback(async () => {
    if (!isVisible) return
    try {
      setLoading(true)
      setError(null)
      const [hist, cfg] = await Promise.all([
        devisService.getRelances(devisId),
        devisService.getConfigRelances(devisId),
      ])
      setHistorique(hist)
      setEditActif(cfg.actif)
      setEditDelais([...cfg.delais])
      setEditTypeRelance(cfg.type_relance_defaut)
      setConfigModified(false)
    } catch {
      setError('Erreur lors du chargement des relances')
    } finally {
      setLoading(false)
    }
  }, [devisId, isVisible])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Handlers config
  const handleToggleActif = (checked: boolean) => {
    setEditActif(checked)
    setConfigModified(true)
  }

  const handleDelaiChange = (index: number, value: number) => {
    const newDelais = [...editDelais]
    newDelais[index] = value
    setEditDelais(newDelais)
    setConfigModified(true)
  }

  const handleAddDelai = () => {
    const lastDelai = editDelais.length > 0 ? editDelais[editDelais.length - 1] : 0
    setEditDelais([...editDelais, lastDelai + 15])
    setConfigModified(true)
  }

  const handleRemoveDelai = (index: number) => {
    if (editDelais.length <= 1) return
    const newDelais = editDelais.filter((_, i) => i !== index)
    setEditDelais(newDelais)
    setConfigModified(true)
  }

  const handleTypeRelanceChange = (type: TypeRelance) => {
    setEditTypeRelance(type)
    setConfigModified(true)
  }

  const handleSaveConfig = async () => {
    try {
      setActionLoading(true)
      await devisService.updateConfigRelances(devisId, {
        actif: editActif,
        delais: editDelais,
        type_relance_defaut: editTypeRelance,
      })
      setConfigModified(false)
      await loadData()
    } catch {
      setError('Erreur lors de la sauvegarde de la configuration')
    } finally {
      setActionLoading(false)
    }
  }

  const handlePlanifier = async () => {
    try {
      setActionLoading(true)
      setError(null)
      await devisService.planifierRelances(devisId, {
        actif: editActif,
        delais: editDelais,
        type_relance_defaut: editTypeRelance,
      })
      await loadData()
    } catch {
      setError('Erreur lors de la planification des relances')
    } finally {
      setActionLoading(false)
    }
  }

  const handleAnnuler = async () => {
    try {
      setActionLoading(true)
      setError(null)
      await devisService.annulerRelances(devisId)
      await loadData()
    } catch {
      setError('Erreur lors de l\'annulation des relances')
    } finally {
      setActionLoading(false)
    }
  }

  if (!isVisible) {
    return null
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
        <div>
          <p>{error}</p>
          <button onClick={loadData} className="text-sm underline mt-1">Reessayer</button>
        </div>
      </div>
    )
  }

  const relances = historique?.relances ?? []
  const nbPlanifiees = historique?.nb_planifiees ?? 0
  const nbEnvoyees = historique?.nb_envoyees ?? 0
  const nbAnnulees = historique?.nb_annulees ?? 0
  const hasRelancesPlanifiees = relances.some((r) => r.statut === 'planifiee')

  return (
    <div className="space-y-6">
      {/* Compteurs */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-blue-700">{nbPlanifiees}</p>
          <p className="text-xs text-blue-600">Planifiees</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-green-700">{nbEnvoyees}</p>
          <p className="text-xs text-green-600">Envoyees</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-gray-500">{nbAnnulees}</p>
          <p className="text-xs text-gray-500">Annulees</p>
        </div>
      </div>

      {/* Section configuration */}
      <div className="border border-gray-200 rounded-lg p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-700">Configuration des relances</h3>
          {configModified && (
            <button
              onClick={handleSaveConfig}
              disabled={actionLoading}
              className="text-xs px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {actionLoading ? 'Sauvegarde...' : 'Sauvegarder'}
            </button>
          )}
        </div>

        {/* Toggle activer/desactiver */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleToggleActif(!editActif)}
            className={`
              relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent
              transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              ${editActif ? 'bg-blue-600' : 'bg-gray-200'}
            `}
            role="switch"
            aria-checked={editActif}
            aria-label="Activer les relances automatiques"
          >
            <span
              className={`
                pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0
                transition duration-200 ease-in-out
                ${editActif ? 'translate-x-5' : 'translate-x-0'}
              `}
            />
          </button>
          <span className="text-sm text-gray-700">
            {editActif ? (
              <span className="flex items-center gap-1 text-blue-700">
                <Bell className="w-4 h-4" />
                Relances activees
              </span>
            ) : (
              <span className="flex items-center gap-1 text-gray-500">
                <BellOff className="w-4 h-4" />
                Relances desactivees
              </span>
            )}
          </span>
        </div>

        {editActif && (
          <>
            {/* Delais */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-2">
                Delais de relance (jours apres envoi)
              </label>
              <div className="space-y-2">
                {editDelais.map((delai, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 w-16">Relance {index + 1}</span>
                    <span className="text-xs text-gray-600">J+</span>
                    <input
                      type="number"
                      min={1}
                      max={365}
                      value={delai}
                      onChange={(e) => handleDelaiChange(index, Number(e.target.value))}
                      className="w-20 px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <span className="text-xs text-gray-600">jours</span>
                    {editDelais.length > 1 && (
                      <button
                        onClick={() => handleRemoveDelai(index)}
                        className="text-red-400 hover:text-red-600 transition-colors"
                        aria-label={`Supprimer le delai ${index + 1}`}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                ))}
                <button
                  onClick={handleAddDelai}
                  className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 mt-1"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Ajouter un delai
                </button>
              </div>
            </div>

            {/* Type de relance */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-2">
                Type de relance
              </label>
              <div className="flex flex-wrap gap-2">
                {(Object.keys(TYPE_RELANCE_LABELS) as TypeRelance[]).map((type) => (
                  <button
                    key={type}
                    onClick={() => handleTypeRelanceChange(type)}
                    className={`
                      px-3 py-1.5 text-xs rounded-md border transition-colors
                      ${editTypeRelance === type
                        ? 'bg-blue-50 border-blue-300 text-blue-700 font-medium'
                        : 'border-gray-200 text-gray-600 hover:bg-gray-50'}
                    `}
                  >
                    {TYPE_RELANCE_LABELS[type]}
                  </button>
                ))}
              </div>
            </div>

            {/* Bouton planifier */}
            <div className="flex flex-wrap gap-2 pt-2">
              <button
                onClick={handlePlanifier}
                disabled={actionLoading || editDelais.length === 0}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {actionLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                Planifier les relances
              </button>
              {hasRelancesPlanifiees && (
                <button
                  onClick={handleAnnuler}
                  disabled={actionLoading}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 border border-red-300 rounded-lg hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {actionLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <XCircle className="w-4 h-4" />
                  )}
                  Annuler les relances
                </button>
              )}
            </div>
          </>
        )}
      </div>

      {/* Timeline des relances */}
      {relances.length > 0 && (
        <div className="border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Timeline des relances</h3>
          <div className="relative">
            {/* Ligne verticale */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />

            <div className="space-y-4">
              {relances
                .sort((a, b) => a.numero_relance - b.numero_relance)
                .map((relance) => {
                  const enRetard = isEnRetard(relance)
                  const statutConfig = STATUT_RELANCE_CONFIG[relance.statut]

                  // Couleur du point selon statut
                  let dotColor = statutConfig.couleur
                  let DotIcon = Clock
                  if (relance.statut === 'envoyee') {
                    DotIcon = CheckCircle
                  } else if (relance.statut === 'annulee') {
                    DotIcon = MinusCircle
                  } else if (enRetard) {
                    dotColor = '#EF4444'
                    DotIcon = AlertTriangle
                  }

                  return (
                    <div key={relance.id} className="relative flex items-start gap-4 pl-1">
                      {/* Point de la timeline */}
                      <div
                        className="relative z-10 flex items-center justify-center w-8 h-8 rounded-full bg-white border-2 flex-shrink-0"
                        style={{ borderColor: dotColor }}
                      >
                        <DotIcon className="w-4 h-4" style={{ color: dotColor }} />
                      </div>

                      {/* Contenu */}
                      <div className="flex-1 min-w-0 pb-2">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-sm font-medium text-gray-900">
                            Relance n{'\u00B0'}{relance.numero_relance}
                          </span>
                          {/* Badge statut */}
                          <span
                            className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                            style={{
                              backgroundColor: `${enRetard ? '#EF4444' : dotColor}15`,
                              color: enRetard ? '#EF4444' : dotColor,
                            }}
                          >
                            {enRetard ? 'En retard' : statutConfig.label}
                          </span>
                          {/* Type de relance */}
                          <span className="text-xs text-gray-600">
                            {TYPE_RELANCE_LABELS[relance.type_relance]}
                          </span>
                        </div>

                        {/* Dates */}
                        <div className="mt-1 text-xs text-gray-500">
                          <span>Prevue : {formatDate(relance.date_prevue)}</span>
                          {relance.date_envoi && (
                            <span className="ml-3">
                              Envoyee : {formatDateTime(relance.date_envoi)}
                            </span>
                          )}
                        </div>

                        {/* Message personnalise */}
                        {relance.message_personnalise && (
                          <p className="mt-1 text-xs text-gray-600 italic">
                            {relance.message_personnalise}
                          </p>
                        )}
                      </div>
                    </div>
                  )
                })}
            </div>
          </div>
        </div>
      )}

      {/* Message si aucune relance */}
      {relances.length === 0 && !loading && (
        <div className="text-center py-6 text-sm text-gray-500">
          <Bell className="w-8 h-8 mx-auto mb-2 text-gray-500" />
          <p>Aucune relance planifiee pour ce devis.</p>
          <p className="text-xs mt-1">Configurez et planifiez les relances ci-dessus.</p>
        </div>
      )}
    </div>
  )
}
