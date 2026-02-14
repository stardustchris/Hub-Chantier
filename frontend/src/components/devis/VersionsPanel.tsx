/**
 * VersionsPanel - Gestion des versions et variantes d'un devis
 * Module Devis (Module 20) - DEV-08
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  GitBranch,
  Copy,
  Lock,
  Loader2,
  AlertCircle,
  Plus,
  ArrowRightLeft,
  X,
  Check,
} from 'lucide-react'
import { devisService } from '../../services/devis'
import type {
  VersionDevis,
  ComparatifDevis,
  LabelVariante,
  TypeVersion,
} from '../../types'
import {
  LABEL_VARIANTE_CONFIG,
  TYPE_VERSION_CONFIG,
  STATUT_DEVIS_CONFIG,
} from '../../types'
import ComparatifView from './ComparatifView'
import { formatEUR } from '../../utils/format'

interface VersionsPanelProps {
  devisId: number
  devisParentId?: number
  isEditable: boolean
  onVersionCreated?: () => void
}

type ModalType = 'revision' | 'variante' | null

export default function VersionsPanel({
  devisId,
  devisParentId,
  isEditable,
  onVersionCreated,
}: VersionsPanelProps) {
  const navigate = useNavigate()
  const [versions, setVersions] = useState<VersionDevis[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  // Modal state
  const [modalType, setModalType] = useState<ModalType>(null)
  const [commentaire, setCommentaire] = useState('')
  const [selectedLabel, setSelectedLabel] = useState<LabelVariante>('STD')

  // Comparaison state
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [comparatif, setComparatif] = useState<ComparatifDevis | null>(null)
  const [comparatifLoading, setComparatifLoading] = useState(false)

  const sourceDevisId = devisParentId || devisId

  const loadVersions = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await devisService.listerVersions(sourceDevisId)
      setVersions(data)
    } catch {
      setError('Erreur lors du chargement des versions')
    } finally {
      setLoading(false)
    }
  }, [sourceDevisId])

  useEffect(() => {
    loadVersions()
  }, [loadVersions])

  const handleCreerRevision = async () => {
    try {
      setActionLoading('revision')
      const nouveau = await devisService.creerRevision(
        devisId,
        commentaire || undefined
      )
      setModalType(null)
      setCommentaire('')
      await loadVersions()
      onVersionCreated?.()
      navigate(`/devis/${nouveau.id}`)
    } catch {
      setError('Erreur lors de la creation de la revision')
    } finally {
      setActionLoading(null)
    }
  }

  const handleCreerVariante = async () => {
    try {
      setActionLoading('variante')
      const nouveau = await devisService.creerVariante(
        devisId,
        selectedLabel,
        commentaire || undefined
      )
      setModalType(null)
      setCommentaire('')
      setSelectedLabel('STD')
      await loadVersions()
      onVersionCreated?.()
      navigate(`/devis/${nouveau.id}`)
    } catch {
      setError('Erreur lors de la creation de la variante')
    } finally {
      setActionLoading(null)
    }
  }

  const handleFiger = async (versionId: number) => {
    try {
      setActionLoading(`figer-${versionId}`)
      await devisService.figerVersion(versionId)
      await loadVersions()
      onVersionCreated?.()
    } catch {
      setError('Erreur lors du figeage de la version')
    } finally {
      setActionLoading(null)
    }
  }

  const toggleSelection = (versionId: number) => {
    setSelectedIds((prev) => {
      if (prev.includes(versionId)) {
        return prev.filter((id) => id !== versionId)
      }
      if (prev.length >= 2) {
        return [prev[1], versionId]
      }
      return [...prev, versionId]
    })
    // Reset comparatif when selection changes
    setComparatif(null)
  }

  const handleComparer = async () => {
    if (selectedIds.length !== 2) return
    try {
      setComparatifLoading(true)
      const result = await devisService.genererComparatif(
        selectedIds[0],
        selectedIds[1]
      )
      setComparatif(result)
    } catch {
      setError('Erreur lors de la generation du comparatif')
    } finally {
      setComparatifLoading(false)
    }
  }

  const getVersionBadge = (version: VersionDevis) => {
    const typeConfig = TYPE_VERSION_CONFIG[version.type_version as TypeVersion]
    return (
      <span
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
        style={{
          backgroundColor: `${typeConfig.couleur}20`,
          color: typeConfig.couleur,
        }}
      >
        {version.type_version === 'variante' && version.label_variante
          ? LABEL_VARIANTE_CONFIG[version.label_variante].label
          : typeConfig.label}
      </span>
    )
  }

  const getStatutBadge = (version: VersionDevis) => {
    const config = STATUT_DEVIS_CONFIG[version.statut]
    return (
      <span
        className="inline-flex px-2 py-0.5 rounded-full text-xs font-medium"
        style={{
          backgroundColor: `${config.couleur}20`,
          color: config.couleur,
        }}
      >
        {config.label}
      </span>
    )
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
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
        <div>
          <p>{error}</p>
          <button onClick={loadVersions} className="text-sm underline mt-1">
            Reessayer
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Actions header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
          <GitBranch className="w-4 h-4" />
          Versions et variantes ({versions.length})
        </h3>
        <div className="flex flex-wrap gap-2">
          {isEditable && (
            <>
              <button
                onClick={() => setModalType('revision')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
              >
                <Copy className="w-3.5 h-3.5" />
                Creer revision
              </button>
              <button
                onClick={() => setModalType('variante')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-purple-600 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                Creer variante
              </button>
            </>
          )}
          {selectedIds.length === 2 && (
            <button
              onClick={handleComparer}
              disabled={comparatifLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-amber-700 bg-amber-50 hover:bg-amber-100 rounded-lg transition-colors disabled:opacity-50"
            >
              {comparatifLoading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <ArrowRightLeft className="w-3.5 h-3.5" />
              )}
              Comparer
            </button>
          )}
        </div>
      </div>

      {/* Aide selection */}
      {versions.length >= 2 && !comparatif && (
        <p className="text-xs text-gray-500">
          Selectionnez 2 versions pour les comparer.
        </p>
      )}

      {/* Versions list */}
      <div className="space-y-2">
        {versions.map((version) => {
          const isCurrent = version.id === devisId
          const isSelected = selectedIds.includes(version.id)
          return (
            <div
              key={version.id}
              className={`flex flex-col sm:flex-row sm:items-center gap-3 p-3 rounded-lg border transition-colors cursor-pointer ${
                isCurrent
                  ? 'border-blue-300 bg-blue-50'
                  : isSelected
                    ? 'border-amber-300 bg-amber-50'
                    : 'border-gray-200 bg-white hover:bg-gray-50'
              }`}
              onClick={() => toggleSelection(version.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  toggleSelection(version.id)
                }
              }}
            >
              {/* Checkbox */}
              <div className="flex-shrink-0">
                <div
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                    isSelected
                      ? 'border-amber-500 bg-amber-500'
                      : 'border-gray-300 bg-white'
                  }`}
                >
                  {isSelected && <Check className="w-3 h-3 text-white" />}
                </div>
              </div>

              {/* Version info */}
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      navigate(`/devis/${version.id}`)
                    }}
                    className="font-medium text-sm text-gray-900 hover:text-blue-600 transition-colors"
                  >
                    {version.numero}
                  </button>
                  {getVersionBadge(version)}
                  {getStatutBadge(version)}
                  {isCurrent && (
                    <span className="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                      Courante
                    </span>
                  )}
                  {version.version_figee && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                      <Lock className="w-3 h-3" />
                      Figee
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-gray-500">
                  <span>v{version.numero_version}</span>
                  <span>{formatEUR(version.montant_total_ht)} HT</span>
                  {version.version_commentaire && (
                    <span className="italic truncate max-w-[200px]">
                      {version.version_commentaire}
                    </span>
                  )}
                  {version.date_creation && (
                    <span>
                      {new Date(version.date_creation).toLocaleDateString('fr-FR')}
                    </span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 flex-shrink-0">
                {!version.version_figee && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleFiger(version.id)
                    }}
                    disabled={actionLoading === `figer-${version.id}`}
                    className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded transition-colors disabled:opacity-50"
                    title="Figer cette version"
                  >
                    {actionLoading === `figer-${version.id}` ? (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    ) : (
                      <Lock className="w-3 h-3" />
                    )}
                    Figer
                  </button>
                )}
              </div>
            </div>
          )
        })}

        {versions.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-4">
            Aucune version. Ce devis est l'original.
          </p>
        )}
      </div>

      {/* Comparatif */}
      {comparatif && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-gray-700">
              Comparatif
            </h4>
            <button
              onClick={() => {
                setComparatif(null)
                setSelectedIds([])
              }}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              Fermer
            </button>
          </div>
          <ComparatifView comparatif={comparatif} />
        </div>
      )}

      {/* Modal creation revision */}
      {modalType === 'revision' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Creer une revision
              </h3>
              <button
                onClick={() => {
                  setModalType(null)
                  setCommentaire('')
                }}
                className="text-gray-600 hover:text-gray-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Une revision duplique le devis actuel avec un nouveau numero de version.
            </p>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Commentaire (optionnel)
            </label>
            <textarea
              value={commentaire}
              onChange={(e) => setCommentaire(e.target.value)}
              placeholder="Ex: Correction suite retour client..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
              maxLength={500}
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => {
                  setModalType(null)
                  setCommentaire('')
                }}
                className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={handleCreerRevision}
                disabled={actionLoading === 'revision'}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
              >
                {actionLoading === 'revision' ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
                Creer la revision
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal creation variante */}
      {modalType === 'variante' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Creer une variante
              </h3>
              <button
                onClick={() => {
                  setModalType(null)
                  setCommentaire('')
                  setSelectedLabel('STD')
                }}
                className="text-gray-600 hover:text-gray-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Une variante duplique le devis avec un label specifique pour proposer des alternatives au client.
            </p>

            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type de variante
            </label>
            <div className="grid grid-cols-2 gap-2 mb-4">
              {(Object.entries(LABEL_VARIANTE_CONFIG) as [LabelVariante, { label: string; couleur: string }][]).map(
                ([key, config]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedLabel(key)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${
                      selectedLabel === key
                        ? 'border-2'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    style={
                      selectedLabel === key
                        ? {
                            borderColor: config.couleur,
                            backgroundColor: `${config.couleur}10`,
                            color: config.couleur,
                          }
                        : undefined
                    }
                  >
                    <span
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: config.couleur }}
                    />
                    {config.label}
                  </button>
                )
              )}
            </div>

            <label className="block text-sm font-medium text-gray-700 mb-1">
              Commentaire (optionnel)
            </label>
            <textarea
              value={commentaire}
              onChange={(e) => setCommentaire(e.target.value)}
              placeholder="Ex: Version economique sans finitions..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
              maxLength={500}
            />

            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => {
                  setModalType(null)
                  setCommentaire('')
                  setSelectedLabel('STD')
                }}
                className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={handleCreerVariante}
                disabled={actionLoading === 'variante'}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50"
              >
                {actionLoading === 'variante' ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
                Creer la variante
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
