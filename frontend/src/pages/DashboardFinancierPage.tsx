/**
 * DashboardFinancierPage - Vue consolidee multi-chantiers
 * CDC Module 17 - FIN-11 / Phase 3
 *
 * Charge dynamiquement les donnees de consolidation financiere
 * via financierService.getConsolidation().
 */

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import Layout from '../components/Layout'
import { chantiersService } from '../services/chantiers'
import { financierService } from '../services/financier'
import { logger } from '../services/logger'
import { formatEUR, formatPct } from '../utils/format'
import ChartTooltip from '../components/financier/ChartTooltip'
import type { VueConsolidee, ChantierFinancierSummary, AnalyseIAConsolidee } from '../types'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import {
  Loader2,
  AlertCircle,
  Euro,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  AlertTriangle,
  Building2,
  ArrowUpDown,
  HelpCircle,
  Sparkles,
  Wallet,
} from 'lucide-react'

type SortField = 'nom_chantier' | 'montant_revise_ht' | 'pct_engage' | 'pct_realise' | 'marge_estimee_pct' | 'reste_a_depenser'
type SortDirection = 'asc' | 'desc'

// Définitions des termes financiers pour les tooltips
const DEFINITIONS: Record<string, { titre: string; definition: string }> = {
  budget: {
    titre: 'Budget',
    definition: 'Montant total prévu pour le chantier (HT). Inclut le montant initial + avenants validés.',
  },
  engage: {
    titre: 'Engagé',
    definition: 'Commandes passées et contrats signés. Dépenses futures certaines même si pas encore payées.',
  },
  realise: {
    titre: 'Réalisé / Déboursé',
    definition: 'Montants réellement payés. Factures fournisseurs réglées.',
  },
  reste: {
    titre: 'Reste à Dépenser',
    definition: 'Budget - Engagé = ce qu\'on peut encore commander sans dépasser le budget.',
  },
  marge: {
    titre: 'Marge',
    definition: '(Prix de Vente - Coût de Revient) / Prix de Vente × 100. Marge commerciale standard BTP.',
  },
}

// Composant Tooltip avec définition - affichage au survol du ?
function DefinitionTooltip({ term, children }: { term: keyof typeof DEFINITIONS; children: React.ReactNode }) {
  const [show, setShow] = useState(false)
  const [position, setPosition] = useState({ top: 0, left: 0 })
  const iconRef = useRef<HTMLSpanElement>(null)
  const def = DEFINITIONS[term]

  const handleMouseEnter = () => {
    if (iconRef.current) {
      const rect = iconRef.current.getBoundingClientRect()
      setPosition({
        top: rect.top - 8,
        left: Math.max(140, Math.min(rect.left + rect.width / 2, window.innerWidth - 140)),
      })
    }
    setShow(true)
  }

  return (
    <span className="inline-flex items-center gap-1">
      {children}
      <span
        ref={iconRef}
        className="cursor-help"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={() => setShow(false)}
        onClick={() => {
          handleMouseEnter()
          setShow(!show)
        }}
      >
        <HelpCircle size={14} className="text-gray-400 hover:text-blue-500 transition-colors" />
      </span>
      {show && (
        <div
          className="fixed bg-gray-900 text-white text-xs rounded-lg p-3 shadow-xl pointer-events-none"
          style={{
            zIndex: 9999,
            width: '280px',
            top: position.top,
            left: position.left,
            transform: 'translate(-50%, -100%)',
          }}
        >
          <p className="font-semibold mb-1 text-blue-300">{def.titre}</p>
          <p className="text-gray-300 leading-relaxed">{def.definition}</p>
          <div className="absolute left-1/2 -translate-x-1/2" style={{ top: '100%', marginTop: '-1px' }}>
            <div className="border-4 border-transparent border-t-gray-900" />
          </div>
        </div>
      )}
    </span>
  )
}

const STATUT_CONFIG: Record<ChantierFinancierSummary['statut'], { label: string; colorClass: string; Icon: typeof CheckCircle }> = {
  ok: { label: 'OK', colorClass: 'text-blue-600 bg-blue-100', Icon: CheckCircle },
  attention: { label: 'Attention', colorClass: 'text-orange-600 bg-orange-100', Icon: AlertTriangle },
  depassement: { label: 'Depassement', colorClass: 'text-red-600 bg-red-100', Icon: TrendingUp },
}

const STATUT_COLORS: Record<string, string> = {
  ok: '#3b82f6',
  attention: '#f59e0b',
  depassement: '#dc2626',
}

const CHART_COLORS = {
  budget: '#3b82f6',
  engage: '#f59e0b',
  realise: '#475569',
}

// Type local pour adapter l'interface de l'API à l'affichage
interface AnalyseIADisplay {
  synthese: string
  alertes_prioritaires: string[]
  recommandations: string[]
  source: 'gemini-3-flash' | 'regles'
  ai_available: boolean
  tendance?: 'hausse' | 'stable' | 'baisse'
  score_sante?: number
}

export default function DashboardFinancierPage() {
  const [data, setData] = useState<VueConsolidee | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sortField, setSortField] = useState<SortField>('nom_chantier')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')
  const [analyseIA, setAnalyseIA] = useState<AnalyseIADisplay | null>(null)
  const [loadingIA, setLoadingIA] = useState(false)

  // Charge l'analyse IA depuis Gemini 3 Flash (ou fallback règles)
  const loadAnalyseIA = useCallback(async (chantierIds: number[]) => {
    try {
      setLoadingIA(true)
      const analyse = await financierService.getAnalyseIAConsolidee(chantierIds)
      // Adapter la réponse API à l'interface d'affichage
      setAnalyseIA({
        synthese: analyse.synthese,
        alertes_prioritaires: analyse.alertes,
        recommandations: analyse.recommandations,
        source: analyse.source,
        ai_available: analyse.ai_available,
        tendance: analyse.tendance,
        score_sante: analyse.score_sante,
      })
    } catch (err) {
      logger.error('Erreur chargement analyse IA Gemini 3 Flash', err, { context: 'DashboardFinancierPage' })
      // En cas d'erreur, pas d'analyse IA
      setAnalyseIA(null)
    } finally {
      setLoadingIA(false)
    }
  }, [])

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // Charger la liste des chantiers pour obtenir les IDs
      const chantiersResponse = await chantiersService.list({ size: 100 })
      const chantierIds = chantiersResponse.items.map((c) => Number(c.id))

      if (chantierIds.length === 0) {
        setData({
          kpi_globaux: {
            total_budget_revise: 0,
            total_engage: 0,
            total_realise: 0,
            total_reste_a_depenser: 0,
            marge_moyenne_pct: 0,
            nb_chantiers: 0,
            nb_chantiers_ok: 0,
            nb_chantiers_attention: 0,
            nb_chantiers_depassement: 0,
          },
          chantiers: [],
          top_rentables: [],
          top_derives: [],
        })
        setAnalyseIA(null)
        return
      }

      const consolidation = await financierService.getConsolidation(chantierIds)
      setData(consolidation)

      // Charger l'analyse IA depuis Gemini 3 Flash en parallèle
      loadAnalyseIA(chantierIds)
    } catch (err) {
      setError('Erreur lors du chargement des donnees financieres')
      logger.error('Erreur chargement consolidation', err, { context: 'DashboardFinancierPage' })
    } finally {
      setLoading(false)
    }
  }, [loadAnalyseIA])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleSort = useCallback((field: SortField) => {
    setSortField((prev) => {
      if (prev === field) {
        setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'))
        return prev
      }
      setSortDirection('asc')
      return field
    })
  }, [])

  const sortedChantiers = useCallback((): ChantierFinancierSummary[] => {
    if (!data) return []
    const sorted = [...data.chantiers]
    sorted.sort((a, b) => {
      const aVal = a[sortField]
      const bVal = b[sortField]
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
      }
      const numA = Number(aVal)
      const numB = Number(bVal)
      return sortDirection === 'asc' ? numA - numB : numB - numA
    })
    return sorted
  }, [data, sortField, sortDirection])

  // Donnees pour le camembert des statuts
  const statutPieData = useMemo(() => {
    if (!data) return []
    return [
      { name: 'OK', value: data.kpi_globaux.nb_chantiers_ok, color: STATUT_COLORS.ok },
      { name: 'Attention', value: data.kpi_globaux.nb_chantiers_attention, color: STATUT_COLORS.attention },
      { name: 'Depassement', value: data.kpi_globaux.nb_chantiers_depassement, color: STATUT_COLORS.depassement },
    ].filter((d) => d.value > 0)
  }, [data])

  // Donnees pour le graphique barres Budget vs Engagé vs Réalisé
  const budgetBarData = useMemo(() => {
    if (!data) return []
    return data.chantiers.slice(0, 8).map((c) => ({
      name: c.nom_chantier.length > 15 ? c.nom_chantier.substring(0, 15) + '...' : c.nom_chantier,
      Budget: Number(c.montant_revise_ht),
      Engagé: Number(c.total_engage),
      Réalisé: Number(c.total_realise),
    }))
  }, [data])

  // Donnees pour le graphique marges par chantier
  const margesBarData = useMemo(() => {
    if (!data) return []
    return [...data.chantiers]
      .filter((c) => c.marge_estimee_pct !== null && c.marge_estimee_pct !== undefined)
      .sort((a, b) => Number(b.marge_estimee_pct) - Number(a.marge_estimee_pct))
      .slice(0, 8)
      .map((c) => ({
        name: c.nom_chantier.length > 15 ? c.nom_chantier.substring(0, 15) + '...' : c.nom_chantier,
        marge: Number(c.marge_estimee_pct),
        fill: Number(c.marge_estimee_pct) >= 0 ? '#3b82f6' : '#dc2626',
      }))
  }, [data])

  // Custom label pour le camembert
  const renderPieLabel = ({ name, percent }: { name: string; percent: number }) => {
    if (percent < 0.05) return null
    return `${name} (${(percent * 100).toFixed(0)}%)`
  }

  const renderChantierCard = (chantier: ChantierFinancierSummary, rank?: number) => {
    const config = STATUT_CONFIG[chantier.statut]
    const StatutIcon = config.Icon

    return (
      <div
        key={chantier.chantier_id}
        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
      >
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            {rank !== undefined && (
              <span className="text-xs font-bold text-gray-400">#{rank}</span>
            )}
            <Building2 size={16} className="text-purple-600" />
            <span className="font-medium text-sm text-gray-900">{chantier.nom_chantier}</span>
          </div>
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium flex items-center gap-1 ${config.colorClass}`}>
            <StatutIcon size={12} />
            {config.label}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-gray-500">Budget</span>
            <p className="font-medium">{formatEUR(chantier.montant_revise_ht)}</p>
          </div>
          <div>
            <span className="text-gray-500">Marge</span>
            <p className={`font-medium ${chantier.marge_estimee_pct === null || chantier.marge_estimee_pct === undefined ? 'text-gray-400' : Number(chantier.marge_estimee_pct) >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
              {formatPct(chantier.marge_estimee_pct)}
            </p>
          </div>
          <div>
            <span className="text-gray-500">Engagé</span>
            <p className="font-medium">{formatPct(chantier.pct_engage)}</p>
          </div>
          <div>
            <span className="text-gray-500">Déboursé</span>
            <p className="font-medium">{formatPct(chantier.pct_realise)}</p>
          </div>
        </div>
      </div>
    )
  }

  const renderSortButton = (field: SortField, label: string) => (
    <button
      onClick={() => handleSort(field)}
      className={`flex items-center gap-1 text-xs font-medium ${
        sortField === field ? 'text-blue-600' : 'text-gray-500 hover:text-gray-700'
      }`}
      aria-label={`Trier par ${label}`}
    >
      {label}
      <ArrowUpDown size={12} />
    </button>
  )

  return (
    <Layout>
      <div className="space-y-6" role="main" aria-label="Dashboard financier consolide">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Dashboard Financier</h1>
          {!loading && data && (
            <button
              onClick={loadData}
              className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
              aria-label="Actualiser les donnees"
            >
              Actualiser
            </button>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-16" aria-label="Chargement des donnees financieres">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
            <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
            <div>
              <p>{error}</p>
              <button onClick={loadData} className="text-sm underline mt-1">Reessayer</button>
            </div>
          </div>
        )}

        {/* Content */}
        {!loading && !error && data && (
          <>
            {/* Panel Analyse IA - Gemini 3 Flash */}
            {loadingIA && (
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-5 shadow-sm border border-purple-200 animate-pulse">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                  <span className="text-sm text-purple-600">Chargement de l'analyse Gemini 3 Flash...</span>
                </div>
              </div>
            )}
            {!loadingIA && analyseIA && (analyseIA.alertes_prioritaires.length > 0 || analyseIA.recommandations.length > 0 || analyseIA.synthese) && (
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-5 shadow-sm border border-purple-200" role="region" aria-label="Analyse IA Gemini 3 Flash">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-600" />
                    <h2 className="text-lg font-semibold text-purple-900">Analyse Intelligente</h2>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      analyseIA.ai_available
                        ? 'bg-green-100 text-green-700 border border-green-200'
                        : 'bg-gray-100 text-gray-600 border border-gray-200'
                    }`}>
                      {analyseIA.source === 'gemini-3-flash' ? '✨ Gemini 3 Flash' : 'Règles métier'}
                    </span>
                  </div>
                  {/* Score de santé et tendance */}
                  {analyseIA.score_sante !== undefined && (
                    <div className="flex items-center gap-3">
                      {analyseIA.tendance && (
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          analyseIA.tendance === 'hausse' ? 'bg-green-100 text-green-700' :
                          analyseIA.tendance === 'baisse' ? 'bg-red-100 text-red-700' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {analyseIA.tendance === 'hausse' ? '↗ Hausse' :
                           analyseIA.tendance === 'baisse' ? '↘ Baisse' : '→ Stable'}
                        </span>
                      )}
                      <div className="text-center">
                        <div className={`text-lg font-bold ${
                          analyseIA.score_sante >= 70 ? 'text-green-600' :
                          analyseIA.score_sante >= 40 ? 'text-orange-500' :
                          'text-red-600'
                        }`}>
                          {analyseIA.score_sante}%
                        </div>
                        <div className="text-xs text-gray-500">Santé</div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Synthèse */}
                <p className="text-sm text-gray-700 mb-4 bg-white/60 rounded-lg p-3">
                  {analyseIA.synthese}
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Alertes */}
                  {analyseIA.alertes_prioritaires.length > 0 && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <h3 className="text-sm font-semibold text-red-800 flex items-center gap-1 mb-2">
                        <AlertTriangle size={14} />
                        Alertes prioritaires
                      </h3>
                      <ul className="text-xs text-red-700 space-y-1">
                        {analyseIA.alertes_prioritaires.map((alerte, i) => (
                          <li key={i}>{alerte}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommandations */}
                  {analyseIA.recommandations.length > 0 && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <h3 className="text-sm font-semibold text-blue-800 flex items-center gap-1 mb-2">
                        <CheckCircle size={14} />
                        Recommandations
                      </h3>
                      <ul className="text-xs text-blue-700 space-y-1">
                        {analyseIA.recommandations.map((reco, i) => (
                          <li key={i}>• {reco}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* KPI globaux */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4" role="region" aria-label="Indicateurs cles">
              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <DefinitionTooltip term="budget">
                      <p className="text-sm text-gray-600">Budget Total</p>
                    </DefinitionTooltip>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatEUR(data.kpi_globaux.total_budget_revise)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {data.kpi_globaux.nb_chantiers} chantier{data.kpi_globaux.nb_chantiers > 1 ? 's' : ''}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Euro className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <DefinitionTooltip term="engage">
                      <p className="text-sm text-gray-600">Engagé Total</p>
                    </DefinitionTooltip>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatEUR(data.kpi_globaux.total_engage)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatPct(data.kpi_globaux.total_budget_revise > 0
                        ? (Number(data.kpi_globaux.total_engage) / Number(data.kpi_globaux.total_budget_revise)) * 100
                        : 0)} du budget
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-orange-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <DefinitionTooltip term="realise">
                      <p className="text-sm text-gray-600">Déboursé Total</p>
                    </DefinitionTooltip>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatEUR(data.kpi_globaux.total_realise)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatPct(data.kpi_globaux.total_budget_revise > 0
                        ? (Number(data.kpi_globaux.total_realise) / Number(data.kpi_globaux.total_budget_revise)) * 100
                        : 0)} du budget
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-slate-600" />
                  </div>
                </div>
              </div>

              {/* Nouvelle carte Reste à Dépenser */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-5 shadow-sm border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <DefinitionTooltip term="reste">
                      <p className="text-sm text-green-700 font-medium">Reste à Dépenser</p>
                    </DefinitionTooltip>
                    <p className="text-2xl font-bold text-green-800 mt-1">
                      {formatEUR(data.kpi_globaux.total_reste_a_depenser)}
                    </p>
                    <p className="text-xs text-green-600 mt-1">
                      {formatPct(data.kpi_globaux.total_budget_revise > 0
                        ? (Number(data.kpi_globaux.total_reste_a_depenser) / Number(data.kpi_globaux.total_budget_revise)) * 100
                        : 0)} disponible
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <Wallet className="w-6 h-6 text-green-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <DefinitionTooltip term="marge">
                      <p className="text-sm text-gray-600">Marge Moyenne</p>
                    </DefinitionTooltip>
                    <p className={`text-2xl font-bold mt-1 ${
                      data.kpi_globaux.marge_moyenne_pct === null || data.kpi_globaux.marge_moyenne_pct === undefined ? 'text-gray-400' : Number(data.kpi_globaux.marge_moyenne_pct) >= 0 ? 'text-blue-600' : 'text-red-600'
                    }`}>
                      {formatPct(data.kpi_globaux.marge_moyenne_pct)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Sur {data.kpi_globaux.nb_chantiers} chantier{data.kpi_globaux.nb_chantiers > 1 ? 's' : ''}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <TrendingDown className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
              </div>
            </div>

            {/* Compteurs statut */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4" role="region" aria-label="Repartition des chantiers par statut">
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-3">
                <CheckCircle className="w-8 h-8 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold text-blue-700">{data.kpi_globaux.nb_chantiers_ok}</p>
                  <p className="text-sm text-blue-600">Chantiers OK</p>
                </div>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 flex items-center gap-3">
                <AlertTriangle className="w-8 h-8 text-orange-600" />
                <div>
                  <p className="text-2xl font-bold text-orange-700">{data.kpi_globaux.nb_chantiers_attention}</p>
                  <p className="text-sm text-orange-600">Chantiers attention</p>
                </div>
              </div>
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
                <TrendingUp className="w-8 h-8 text-red-600" />
                <div>
                  <p className="text-2xl font-bold text-red-700">{data.kpi_globaux.nb_chantiers_depassement}</p>
                  <p className="text-sm text-red-600">Chantiers en depassement</p>
                </div>
              </div>
            </div>

            {/* Graphiques */}
            {data.chantiers.length > 0 && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4" role="region" aria-label="Graphiques financiers">
                {/* Camembert repartition statuts */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Repartition par statut</h3>
                  {statutPieData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={statutPieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={90}
                          paddingAngle={3}
                          dataKey="value"
                          label={renderPieLabel}
                          labelLine={false}
                        >
                          {statutPieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          content={({ active, payload }) => (
                            <ChartTooltip
                              active={active}
                              payload={payload?.map((p) => ({
                                name: String(p.name),
                                value: Number(p.value),
                                color: String(p.payload?.color || p.payload?.fill || '#374151'),
                              }))}
                            />
                          )}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-[250px] text-gray-400 text-sm">
                      Aucune donnee
                    </div>
                  )}
                </div>

                {/* Barres Budget vs Engage vs Réalisé */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 lg:col-span-2">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Budget / Engagé / Réalisé par chantier</h3>
                  {budgetBarData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={budgetBarData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                        <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-20} textAnchor="end" height={60} />
                        <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                        <Tooltip
                          formatter={(value: number, name: string) => [formatEUR(value), name]}
                          contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                        />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Bar dataKey="Budget" fill={CHART_COLORS.budget} radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Engagé" fill={CHART_COLORS.engage} radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Réalisé" fill={CHART_COLORS.realise} radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-[250px] text-gray-400 text-sm">
                      Aucune donnee
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Graphique marges */}
            {margesBarData.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4" role="region" aria-label="Graphique des marges">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Marges estimees par chantier</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={margesBarData} layout="vertical" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                    <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={80} />
                    <Tooltip
                      formatter={(value: number) => [`${value.toFixed(1)}%`, 'Marge']}
                      contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                    />
                    <Bar dataKey="marge" radius={[0, 4, 4, 0]}>
                      {margesBarData.map((entry, index) => (
                        <Cell key={`marge-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Tableau des chantiers */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden" role="region" aria-label="Tableau des chantiers">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Tous les chantiers</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm" aria-label="Chantiers financiers">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left">{renderSortButton('nom_chantier', 'Chantier')}</th>
                      <th className="px-4 py-3 text-right">
                        <DefinitionTooltip term="budget">
                          {renderSortButton('montant_revise_ht', 'Budget')}
                        </DefinitionTooltip>
                      </th>
                      <th className="px-4 py-3 text-right">
                        <DefinitionTooltip term="engage">
                          {renderSortButton('pct_engage', '% Engagé')}
                        </DefinitionTooltip>
                      </th>
                      <th className="px-4 py-3 text-right">
                        <DefinitionTooltip term="realise">
                          {renderSortButton('pct_realise', '% Déboursé')}
                        </DefinitionTooltip>
                      </th>
                      <th className="px-4 py-3 text-right">
                        <DefinitionTooltip term="reste">
                          {renderSortButton('reste_a_depenser', 'Reste')}
                        </DefinitionTooltip>
                      </th>
                      <th className="px-4 py-3 text-right">
                        <DefinitionTooltip term="marge">
                          {renderSortButton('marge_estimee_pct', 'Marge')}
                        </DefinitionTooltip>
                      </th>
                      <th className="px-4 py-3 text-center">Statut</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {sortedChantiers().map((chantier) => {
                      const config = STATUT_CONFIG[chantier.statut]
                      const StatutIcon = config.Icon

                      return (
                        <tr key={chantier.chantier_id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 font-medium text-gray-900">{chantier.nom_chantier}</td>
                          <td className="px-4 py-3 text-right">{formatEUR(chantier.montant_revise_ht)}</td>
                          <td className="px-4 py-3 text-right">
                            <div className="flex items-center justify-end gap-2">
                              <div className="w-16 bg-gray-200 rounded-full h-1.5">
                                <div
                                  className="h-1.5 rounded-full bg-blue-500"
                                  style={{ width: `${Math.min(Number(chantier.pct_engage), 100)}%` }}
                                />
                              </div>
                              <span>{formatPct(chantier.pct_engage)}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <div className="flex items-center justify-end gap-2">
                              <div className="w-16 bg-gray-200 rounded-full h-1.5">
                                <div
                                  className="h-1.5 rounded-full bg-blue-500"
                                  style={{ width: `${Math.min(Number(chantier.pct_realise), 100)}%` }}
                                />
                              </div>
                              <span>{formatPct(chantier.pct_realise)}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-right">{formatEUR(chantier.reste_a_depenser)}</td>
                          <td className={`px-4 py-3 text-right font-medium ${
                            chantier.marge_estimee_pct === null || chantier.marge_estimee_pct === undefined ? 'text-gray-400' : Number(chantier.marge_estimee_pct) >= 0 ? 'text-blue-600' : 'text-red-600'
                          }`}>
                            {formatPct(chantier.marge_estimee_pct)}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${config.colorClass}`}>
                              <StatutIcon size={12} />
                              {config.label}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
                {data.chantiers.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Building2 className="w-12 h-12 mx-auto text-gray-300 mb-2" />
                    <p>Aucun chantier avec budget</p>
                  </div>
                )}
              </div>
            </div>

            {/* Top Rentables / Top Derives */}
            {(data.top_rentables.length > 0 || data.top_derives.length > 0) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4" role="region" aria-label="Top chantiers">
                {/* Top Rentables */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                  <h3 className="text-sm font-semibold text-blue-700 mb-3 flex items-center gap-2">
                    <TrendingUp size={16} />
                    Top 3 Rentables
                  </h3>
                  <div className="space-y-3">
                    {data.top_rentables.map((chantier, index) =>
                      renderChantierCard(chantier, index + 1)
                    )}
                    {data.top_rentables.length === 0 && (
                      <p className="text-sm text-gray-400 text-center py-4">Aucune donnee</p>
                    )}
                  </div>
                </div>

                {/* Top Derives */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                  <h3 className="text-sm font-semibold text-red-700 mb-3 flex items-center gap-2">
                    <TrendingDown size={16} />
                    Top 3 Derives
                  </h3>
                  <div className="space-y-3">
                    {data.top_derives.map((chantier, index) =>
                      renderChantierCard(chantier, index + 1)
                    )}
                    {data.top_derives.length === 0 && (
                      <p className="text-sm text-gray-400 text-center py-4">Aucune donnee</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  )
}
