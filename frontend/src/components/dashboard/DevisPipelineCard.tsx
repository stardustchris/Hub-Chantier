/**
 * DevisPipelineCard - Widget Pipeline Devis pour le dashboard
 * CDC Module 20 - DEV-17
 *
 * Affiche les KPI devis, une barre de pipeline visuelle,
 * le detail par statut actif et les derniers devis.
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Loader2, TrendingUp, Hash, Euro } from 'lucide-react'
import { devisService } from '../../services/devis'
import type { DashboardDevis, KPIDevis, DevisRecent, StatutDevis } from '../../types'
import { STATUT_DEVIS_CONFIG } from '../../types'
import { formatEUR } from '../../utils/format'

/** Statuts du pipeline actif (barre visuelle) */
const PIPELINE_STATUTS: StatutDevis[] = [
  'brouillon',
  'en_validation',
  'envoye',
  'vu',
  'en_negociation',
  'accepte',
]

/** Statuts inactifs (affiches separement si > 0) */
const INACTIVE_STATUTS: StatutDevis[] = ['refuse', 'perdu', 'expire']

/** Extraire le count d'un statut depuis les KPI */
function getCountForStatut(kpi: KPIDevis, statut: StatutDevis): number {
  const key = `nb_${statut}` as keyof KPIDevis
  return Number(kpi[key]) || 0
}

export default function DevisPipelineCard() {
  const navigate = useNavigate()
  const [data, setData] = useState<DashboardDevis | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDashboard = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const result = await devisService.getDashboard()
      setData(result)
    } catch {
      setError('Erreur lors du chargement des devis')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

  // Total devis actifs pour calculer les proportions de la barre
  const totalPipeline = data
    ? PIPELINE_STATUTS.reduce((sum, s) => sum + getCountForStatut(data.kpi, s), 0)
    : 0

  // Statuts inactifs avec count > 0
  const activeInactiveStatuts = data
    ? INACTIVE_STATUTS.filter((s) => getCountForStatut(data.kpi, s) > 0)
    : []

  // Derniers devis (max 5)
  const derniersDevis: DevisRecent[] = data?.derniers_devis?.slice(0, 5) ?? []

  return (
    <div className="bg-white rounded-2xl p-5 shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-600" />
          Pipeline Devis
        </h2>
        <button
          onClick={() => navigate('/devis')}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          aria-label="Voir tous les devis"
        >
          Voir tout
        </button>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
        </div>
      )}

      {/* Error */}
      {error && !isLoading && (
        <div className="text-center py-6">
          <p className="text-red-500 text-sm">{error}</p>
          <button
            onClick={loadDashboard}
            className="text-sm text-blue-600 hover:text-blue-700 mt-2"
            aria-label="Réessayer de charger les devis"
          >
            Réessayer
          </button>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !error && data && data.kpi.nb_total === 0 && (
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">Aucun devis en cours</p>
          <button
            onClick={() => navigate('/devis')}
            className="mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
            aria-label="Créer un nouveau devis"
          >
            Créer un devis
          </button>
        </div>
      )}

      {/* Content */}
      {!isLoading && !error && data && data.kpi.nb_total > 0 && (
        <div className="space-y-4">
          {/* KPI principaux */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-blue-50 rounded-xl p-3 text-center">
              <Euro className="w-4 h-4 text-blue-600 mx-auto mb-1" />
              <p className="text-lg font-bold text-gray-900">
                {formatEUR(data.kpi.total_pipeline_ht)}
              </p>
              <p className="text-xs text-gray-500">Pipeline HT</p>
            </div>
            <div className="bg-green-50 rounded-xl p-3 text-center">
              <TrendingUp className="w-4 h-4 text-green-600 mx-auto mb-1" />
              <p className="text-lg font-bold text-gray-900">
                {Number(data.kpi.taux_conversion).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">Conversion</p>
            </div>
            <div className="bg-purple-50 rounded-xl p-3 text-center">
              <Hash className="w-4 h-4 text-purple-600 mx-auto mb-1" />
              <p className="text-lg font-bold text-gray-900">
                {data.kpi.nb_total}
              </p>
              <p className="text-xs text-gray-500">Total devis</p>
            </div>
          </div>

          {/* Barre de pipeline visuelle */}
          {totalPipeline > 0 && (
            <div>
              <div className="flex rounded-full overflow-hidden h-3">
                {PIPELINE_STATUTS.map((statut) => {
                  const count = getCountForStatut(data.kpi, statut)
                  if (count === 0) return null
                  const pct = (count / totalPipeline) * 100
                  const config = STATUT_DEVIS_CONFIG[statut]
                  return (
                    <div
                      key={statut}
                      className="transition-all duration-300"
                      style={{
                        width: `${pct}%`,
                        backgroundColor: config.couleur,
                        minWidth: count > 0 ? '8px' : '0',
                      }}
                      title={`${config.label}: ${count}`}
                    />
                  )
                })}
              </div>
            </div>
          )}

          {/* Detail par statut actif */}
          <div className="space-y-1.5">
            {PIPELINE_STATUTS.map((statut) => {
              const count = getCountForStatut(data.kpi, statut)
              if (count === 0) return null
              const config = STATUT_DEVIS_CONFIG[statut]
              return (
                <div key={statut} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ backgroundColor: config.couleur }}
                    />
                    <span className="text-gray-600">{config.label}</span>
                  </div>
                  <span className="font-medium text-gray-900">{count}</span>
                </div>
              )
            })}
          </div>

          {/* Statuts inactifs (refuse, perdu, expire) */}
          {activeInactiveStatuts.length > 0 && (
            <div className="border-t border-gray-100 pt-3">
              <div className="space-y-1.5">
                {activeInactiveStatuts.map((statut) => {
                  const count = getCountForStatut(data.kpi, statut)
                  const config = STATUT_DEVIS_CONFIG[statut]
                  return (
                    <div key={statut} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-2.5 h-2.5 rounded-full"
                          style={{ backgroundColor: config.couleur }}
                        />
                        <span className="text-gray-600">{config.label}</span>
                      </div>
                      <span className="font-medium text-gray-600">{count}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Derniers devis */}
          {derniersDevis.length > 0 && (
            <div className="border-t border-gray-100 pt-3">
              <p className="text-xs font-medium text-gray-500 uppercase mb-2">Derniers devis</p>
              <div className="space-y-2 max-h-[200px] overflow-y-auto">
                {derniersDevis.map((devis) => {
                  const config = STATUT_DEVIS_CONFIG[devis.statut]
                  return (
                    <button
                      key={devis.id}
                      onClick={() => navigate(`/devis/${devis.id}`)}
                      className="w-full flex items-center gap-3 p-2 rounded-xl hover:bg-gray-50 transition-colors text-left"
                      aria-label={`Voir devis ${devis.numero} pour ${devis.client_nom}`}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono text-gray-500">{devis.numero}</span>
                          <span
                            className="text-xs px-1.5 py-0.5 rounded-full font-medium"
                            style={{
                              backgroundColor: `${config.couleur}20`,
                              color: config.couleur,
                            }}
                          >
                            {config.label}
                          </span>
                        </div>
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {devis.client_nom}
                        </p>
                      </div>
                      <span className="text-sm font-medium text-gray-700 whitespace-nowrap">
                        {formatEUR(devis.montant_total_ht)}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
