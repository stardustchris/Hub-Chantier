/**
 * BudgetTab - Onglet principal Budget dans ChantierDetailPage
 *
 * Orchestrateur qui affiche :
 * 1. BudgetDashboard (KPI + graphiques)
 * 2. SuggestionsPanel (suggestions IA)
 * 3. Sections collapsables: Lots, Achats, Avenants, Situations, Factures, Couts, Alertes
 * 4. JournalFinancier (toggle)
 *
 * Si pas de budget, affiche un bouton "Creer le budget" (conducteur/admin).
 */

import { useState, useEffect, useCallback } from 'react'
import {
  DollarSign,
  Plus,
  History,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  Package,
  ShoppingCart,
  FileText,
  ClipboardList,
  Receipt,
  Wrench,
  Bell,
} from 'lucide-react'
import { financierService } from '../../services/financier'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { logger } from '../../services/logger'
import BudgetDashboard from './BudgetDashboard'
import SuggestionsPanel from './SuggestionsPanel'
import LotsBudgetairesTable from './LotsBudgetairesTable'
import AchatsList from './AchatsList'
import JournalFinancier from './JournalFinancier'
import AvenantsList from './AvenantsList'
import SituationsList from './SituationsList'
import FacturesList from './FacturesList'
import CoutsMainOeuvrePanel from './CoutsMainOeuvrePanel'
import CoutsMaterielPanel from './CoutsMaterielPanel'
import AlertesPanel from './AlertesPanel'
import type { Budget, BudgetCreate } from '../../types'

interface BudgetTabProps {
  chantierId: number
}

interface SectionConfig {
  key: string
  label: string
  icon: typeof Package
}

const SECTIONS: SectionConfig[] = [
  { key: 'lots', label: 'Lots Budgetaires', icon: Package },
  { key: 'achats', label: 'Achats', icon: ShoppingCart },
  { key: 'avenants', label: 'Avenants', icon: FileText },
  { key: 'situations', label: 'Situations de Travaux', icon: ClipboardList },
  { key: 'factures', label: 'Factures', icon: Receipt },
  { key: 'couts', label: 'Couts', icon: Wrench },
  { key: 'alertes', label: 'Alertes', icon: Bell },
]

export default function BudgetTab({ chantierId }: BudgetTabProps) {
  const { user } = useAuth()
  const { addToast } = useToast()
  const [budget, setBudget] = useState<Budget | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showJournal, setShowJournal] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [createLoading, setCreateLoading] = useState(false)
  const [montantInitial, setMontantInitial] = useState('')
  const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>({})

  const canEdit = user?.role === 'admin' || user?.role === 'conducteur'

  const toggleSection = useCallback((key: string) => {
    setCollapsedSections((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }, [])

  const loadBudget = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.getBudgetByChantier(chantierId)
      setBudget(data)
    } catch (err) {
      setError('Erreur lors du chargement du budget')
      logger.error('Erreur chargement budget', err, { context: 'BudgetTab' })
    } finally {
      setLoading(false)
    }
  }, [chantierId])

  useEffect(() => {
    loadBudget()
  }, [loadBudget])

  const handleCreateBudget = useCallback(async () => {
    const montant = parseFloat(montantInitial)
    if (isNaN(montant) || montant <= 0) {
      addToast({ message: 'Le montant initial doit etre positif', type: 'error' })
      return
    }

    try {
      setCreateLoading(true)
      const data: BudgetCreate = {
        chantier_id: chantierId,
        montant_initial_ht: montant,
      }
      const newBudget = await financierService.createBudget(data)
      setBudget(newBudget)
      setShowCreateForm(false)
      setMontantInitial('')
      addToast({ message: 'Budget cree avec succes', type: 'success' })
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } }; message?: string }
      const message = apiError.response?.data?.detail || apiError.message || 'Erreur lors de la creation'
      addToast({ message, type: 'error' })
      logger.error('Erreur creation budget', err, { context: 'BudgetTab' })
    } finally {
      setCreateLoading(false)
    }
  }, [montantInitial, chantierId, addToast])

  const renderSectionContent = (key: string): React.ReactNode => {
    if (!budget) return null

    switch (key) {
      case 'lots':
        return <LotsBudgetairesTable budgetId={budget.id} onRefresh={loadBudget} />
      case 'achats':
        return <AchatsList chantierId={chantierId} budgetId={budget.id} />
      case 'avenants':
        return <AvenantsList budgetId={budget.id} />
      case 'situations':
        return <SituationsList chantierId={chantierId} budgetId={budget.id} />
      case 'factures':
        return <FacturesList chantierId={chantierId} />
      case 'couts':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <CoutsMainOeuvrePanel chantierId={chantierId} />
            <CoutsMaterielPanel chantierId={chantierId} />
          </div>
        )
      case 'alertes':
        return <AlertesPanel chantierId={chantierId} />
      default:
        return null
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12" aria-label="Chargement du budget">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
        <div>
          <p>{error}</p>
          <button
            onClick={loadBudget}
            className="text-sm underline mt-1"
          >
            Reessayer
          </button>
        </div>
      </div>
    )
  }

  // Pas de budget : proposer la creation
  if (!budget) {
    return (
      <div className="text-center py-12">
        <DollarSign className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Aucun budget defini
        </h3>
        <p className="text-gray-500 mb-6 max-w-md mx-auto">
          Definissez le budget initial de ce chantier pour suivre les depenses, lots budgetaires et achats.
        </p>

        {canEdit && !showCreateForm && (
          <button
            onClick={() => setShowCreateForm(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={18} />
            Creer le budget
          </button>
        )}

        {showCreateForm && (
          <div className="max-w-sm mx-auto bg-white border rounded-xl p-6 mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2 text-left">
              Montant initial HT
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                value={montantInitial}
                onChange={(e) => setMontantInitial(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ex: 250000"
                min={0}
                step="0.01"
                autoFocus
                aria-label="Montant initial HT en euros"
              />
              <button
                onClick={handleCreateBudget}
                disabled={createLoading || !montantInitial}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {createLoading ? 'Creation...' : 'Creer'}
              </button>
            </div>
            <button
              onClick={() => { setShowCreateForm(false); setMontantInitial('') }}
              className="mt-2 text-sm text-gray-500 hover:text-gray-700"
            >
              Annuler
            </button>
          </div>
        )}

        {!canEdit && (
          <p className="text-sm text-gray-400">
            Seul un administrateur ou conducteur peut creer le budget.
          </p>
        )}
      </div>
    )
  }

  // Budget existant : afficher le contenu complet
  return (
    <div className="space-y-6" role="region" aria-label="Budget du chantier">
      {/* Dashboard KPI */}
      <BudgetDashboard chantierId={chantierId} budget={budget} />

      {/* Suggestions IA */}
      <SuggestionsPanel chantierId={chantierId} />

      {/* Sections collapsables */}
      {SECTIONS.map((section) => {
        const isCollapsed = !!collapsedSections[section.key]
        const SectionIcon = section.icon

        return (
          <div
            key={section.key}
            className="bg-white border border-gray-200 rounded-xl overflow-hidden"
          >
            <button
              onClick={() => toggleSection(section.key)}
              className="w-full flex items-center gap-3 p-4 text-left hover:bg-gray-50 transition-colors"
              aria-expanded={!isCollapsed}
              aria-controls={`section-${section.key}`}
            >
              {isCollapsed ? (
                <ChevronRight size={18} className="text-gray-400 flex-shrink-0" />
              ) : (
                <ChevronDown size={18} className="text-gray-400 flex-shrink-0" />
              )}
              <SectionIcon size={18} className="text-blue-600 flex-shrink-0" />
              <h3 className="text-sm font-semibold text-gray-900">{section.label}</h3>
            </button>

            {!isCollapsed && (
              <div id={`section-${section.key}`} className="px-4 pb-4">
                {renderSectionContent(section.key)}
              </div>
            )}
          </div>
        )
      })}

      {/* Toggle Journal */}
      <div>
        <button
          onClick={() => setShowJournal(!showJournal)}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          aria-expanded={showJournal}
        >
          <History size={16} />
          {showJournal ? 'Masquer l\'historique' : 'Voir l\'historique des modifications'}
        </button>

        {showJournal && (
          <div className="mt-3">
            <JournalFinancier />
          </div>
        )}
      </div>
    </div>
  )
}
