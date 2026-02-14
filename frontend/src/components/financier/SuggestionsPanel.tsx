/**
 * SuggestionsPanel - Affiche les suggestions IA et indicateurs predictifs
 *
 * Charge les suggestions via financierService.getSuggestions(chantierId).
 * Affiche les indicateurs predictifs et les suggestions en cards colorees.
 */

import { useState, useEffect, useCallback } from 'react'
import { AlertTriangle, AlertCircle, Info, Loader2, TrendingDown, Clock, Flame, Sparkles, ChevronDown, ChevronUp, HelpCircle } from 'lucide-react'
import { financierService } from '../../services/financier'
import { logger } from '../../services/logger'
import { formatEUR } from '../../utils/format'
import type { SuggestionsFinancieres, Suggestion } from '../../types'

interface SuggestionsPanelProps {
  chantierId: number
}

const SEVERITY_CONFIG: Record<Suggestion['severity'], {
  borderClass: string
  bgClass: string
  textClass: string
  Icon: typeof AlertTriangle
}> = {
  CRITICAL: {
    borderClass: 'border-red-500',
    bgClass: 'bg-red-50',
    textClass: 'text-red-700',
    Icon: AlertTriangle,
  },
  WARNING: {
    borderClass: 'border-orange-500',
    bgClass: 'bg-orange-50',
    textClass: 'text-orange-700',
    Icon: AlertCircle,
  },
  INFO: {
    borderClass: 'border-blue-500',
    bgClass: 'bg-blue-50',
    textClass: 'text-blue-700',
    Icon: Info,
  },
}

export default function SuggestionsPanel({ chantierId }: SuggestionsPanelProps) {
  const [data, setData] = useState<SuggestionsFinancieres | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showRulesExplainer, setShowRulesExplainer] = useState(false)
  const [showTooltip, setShowTooltip] = useState(false)

  const loadSuggestions = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await financierService.getSuggestions(chantierId)
      setData(result)
    } catch (err) {
      setError('Erreur lors du chargement des suggestions')
      logger.error('Erreur chargement suggestions', err, { context: 'SuggestionsPanel' })
    } finally {
      setLoading(false)
    }
  }, [chantierId])

  useEffect(() => {
    loadSuggestions()
  }, [loadSuggestions])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-6">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" aria-label="Chargement des suggestions" />
      </div>
    )
  }

  if (error || !data) {
    return null
  }

  if (data.suggestions.length === 0) {
    return null
  }

  const { indicateurs, suggestions, ai_available, source } = data

  return (
    <div role="region" aria-label="Suggestions et indicateurs predictifs">
      {/* Badge source IA avec tooltip et toggle */}
      <div className="mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          {ai_available ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700 border border-green-200">
              <Sparkles size={14} />
              IA Gemini
            </span>
          ) : (
            <div className="inline-flex items-center gap-1.5">
              <div className="relative">
                <span
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200 cursor-help"
                  onMouseEnter={() => setShowTooltip(true)}
                  onMouseLeave={() => setShowTooltip(false)}
                >
                  <Sparkles size={14} />
                  Regles algorithmiques
                  <HelpCircle size={12} className="text-gray-600" />
                </span>

                {/* Tooltip */}
                {showTooltip && (
                  <div className="absolute z-10 bottom-full left-0 mb-2 w-72 bg-gray-900 text-white text-xs rounded-lg p-3 shadow-lg">
                    <p className="font-medium mb-1">Suggestions basées sur des règles métier prédéfinies :</p>
                    <ul className="space-y-1 text-gray-500">
                      <li>• Budget &gt; 100k€ → Créer situation</li>
                      <li>• Dépassement &gt; 10% → Alerte burn rate</li>
                      <li>• Marge &lt; 15% → Optimiser coûts</li>
                    </ul>
                    <p className="mt-2 text-gray-600 italic">
                      ℹ️ L'IA Gemini peut être activée pour des suggestions plus contextuelles.
                    </p>
                    {/* Triangle pointer */}
                    <div className="absolute top-full left-4 -mt-1">
                      <div className="border-4 border-transparent border-t-gray-900"></div>
                    </div>
                  </div>
                )}
              </div>

              <button
                onClick={() => setShowRulesExplainer(!showRulesExplainer)}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                aria-expanded={showRulesExplainer}
              >
                {showRulesExplainer ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                <span>Voir les règles</span>
              </button>
            </div>
          )}
          {source === 'gemini' && (
            <span className="text-xs text-gray-600">Analyse enrichie par intelligence artificielle</span>
          )}
        </div>

        {/* Section dépliable : Règles déclenchées */}
        {!ai_available && showRulesExplainer && (
          <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
              📋 Règles déclenchées ({suggestions.length})
            </h4>
            <div className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <div key={index} className="flex items-start gap-2 text-sm">
                  <span className="text-green-600 font-bold flex-shrink-0">✓</span>
                  <div className="flex-1">
                    <p className="text-gray-700">
                      <span className="font-medium">{suggestion.type.replace(/_/g, ' ')}</span>
                      {' → '}
                      {suggestion.titre}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-3 pt-3 border-t border-blue-200">
              <p className="text-xs text-blue-700">
                💡 <span className="font-medium">Astuce :</span> Activez Gemini pour des suggestions adaptées à votre contexte spécifique (type de chantier, avancement, historique).
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Indicateurs predictifs */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <TrendingDown size={16} className="text-purple-600" />
          Indicateurs predictifs
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="text-center p-2 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Flame size={14} className="text-orange-500" />
              <span className="text-xs text-gray-500">Burn rate</span>
            </div>
            <p className="text-sm font-bold text-gray-900">
              {formatEUR(Number(indicateurs.burn_rate_mensuel))}
              <span className="text-xs font-normal text-gray-500">/mois</span>
            </p>
            {Number(indicateurs.ecart_burn_rate_pct) !== 0 && (
              <p className={`text-xs mt-0.5 ${Number(indicateurs.ecart_burn_rate_pct) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {Number(indicateurs.ecart_burn_rate_pct) > 0 ? '+' : ''}{Number(indicateurs.ecart_burn_rate_pct).toFixed(1)}% vs budget
              </p>
            )}
          </div>

          <div className="text-center p-2 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Clock size={14} className="text-blue-500" />
              <span className="text-xs text-gray-500">Mois restants</span>
            </div>
            <p className="text-sm font-bold text-gray-900">
              {Number(indicateurs.mois_restants_budget).toFixed(1)}
            </p>
          </div>

          <div className="text-center p-2 bg-gray-50 rounded-lg">
            <span className="text-xs text-gray-500">Date epuisement</span>
            <p className="text-sm font-bold text-gray-900 mt-1">
              {indicateurs.date_epuisement_estimee
                ? new Date(indicateurs.date_epuisement_estimee).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })
                : '-'}
            </p>
          </div>

          <div className="text-center p-2 bg-gray-50 rounded-lg">
            <span className="text-xs text-gray-500">Avancement financier</span>
            <p className="text-sm font-bold text-gray-900 mt-1">
              {Number(indicateurs.avancement_financier_pct).toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      {/* Suggestions */}
      <div className="space-y-2">
        {suggestions.map((suggestion, index) => {
          const config = SEVERITY_CONFIG[suggestion.severity]
          const SeverityIcon = config.Icon

          return (
            <div
              key={`${suggestion.type}-${index}`}
              className={`border-l-4 ${config.borderClass} ${config.bgClass} rounded-r-lg p-3`}
              role="alert"
            >
              <div className="flex items-start gap-2">
                <SeverityIcon size={18} className={`flex-shrink-0 mt-0.5 ${config.textClass}`} />
                <div className="flex-1 min-w-0">
                  <h4 className={`text-sm font-semibold ${config.textClass}`}>
                    {suggestion.titre}
                  </h4>
                  <p className="text-sm text-gray-700 mt-0.5">
                    {suggestion.description}
                  </p>
                  {Number(suggestion.impact_estime_eur) > 0 && (
                    <p className="text-xs font-medium text-gray-600 mt-1">
                      Impact estime : {formatEUR(Number(suggestion.impact_estime_eur))}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
