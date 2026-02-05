/**
 * DevisGeneratorPage - Nouveau generateur de devis avec layout 12 colonnes
 * Remplace DevisDetailPage (conservee sur /devis/:id/legacy)
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import GeneratorHeader from '../components/devis/generator/GeneratorHeader'
import ClientChantierCard from '../components/devis/generator/ClientChantierCard'
import DatesCard from '../components/devis/generator/DatesCard'
import DevisTableCard from '../components/devis/generator/DevisTableCard'
import ConditionsPaiementCard from '../components/devis/generator/ConditionsPaiementCard'
import MoyensPaiementCard from '../components/devis/generator/MoyensPaiementCard'
import NotesBasPageCard from '../components/devis/generator/NotesBasPageCard'
import RentabiliteSidebar from '../components/devis/generator/RentabiliteSidebar'
import RecapitulatifSidebar from '../components/devis/generator/RecapitulatifSidebar'
import OptionsInternesSidebar from '../components/devis/generator/OptionsInternesSidebar'
import BatiprixSidebar from '../components/devis/generator/BatiprixSidebar'
import ActionsRapidesSidebar from '../components/devis/generator/ActionsRapidesSidebar'
import { devisService } from '../services/devis'
import type { DevisDetail, DevisUpdate } from '../types'
import { Loader2, AlertCircle } from 'lucide-react'

export default function DevisGeneratorPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [devis, setDevis] = useState<DevisDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const recalcTimer = useRef<ReturnType<typeof setTimeout>>(undefined)

  const devisId = Number(id)
  const isEditable = devis?.statut === 'brouillon'

  const loadDevis = useCallback(async () => {
    if (!devisId || isNaN(devisId)) return
    try {
      setLoading(true)
      setError(null)
      const data = await devisService.getDevis(devisId)
      setDevis(data)
    } catch {
      setError('Erreur lors du chargement du devis')
    } finally {
      setLoading(false)
    }
  }, [devisId])

  useEffect(() => {
    loadDevis()
  }, [loadDevis])

  /** Debounced recalculation after mutations */
  const recalcAndReload = useCallback(() => {
    clearTimeout(recalcTimer.current)
    recalcTimer.current = setTimeout(async () => {
      try {
        await devisService.calculerTotaux(devisId)
      } catch { /* silent */ }
      loadDevis()
    }, 500)
  }, [devisId, loadDevis])

  useEffect(() => {
    return () => clearTimeout(recalcTimer.current)
  }, [])

  // Workflow handlers
  const handleSoumettre = async () => { await devisService.soumettreDevis(devisId); await loadDevis() }
  const handleValider = async () => { await devisService.validerDevis(devisId); await loadDevis() }
  const handleRetournerBrouillon = async () => { await devisService.retournerBrouillon(devisId); await loadDevis() }
  const handleAccepter = async () => { await devisService.accepterDevis(devisId); await loadDevis() }
  const handleRefuser = async (motif?: string) => { if (motif) { await devisService.refuserDevis(devisId, motif); await loadDevis() } }
  const handlePerdu = async (motif?: string) => { if (motif) { await devisService.marquerPerdu(devisId, motif); await loadDevis() } }

  // Generic devis field update handler for bottom cards
  const handleUpdateDevis = async (data: DevisUpdate) => {
    await devisService.updateDevis(devisId, data)
    recalcAndReload()
  }

  if (loading && !devis) {
    return (
      <Layout>
        <div className="min-h-[60vh] flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        </div>
      </Layout>
    )
  }

  if (error || !devis) {
    return (
      <Layout>
        <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
          <AlertCircle className="w-12 h-12 text-red-400" />
          <p className="text-red-600">{error || 'Devis introuvable'}</p>
          <button onClick={() => navigate('/devis')} className="text-indigo-600 hover:underline text-sm">
            Retour a la liste
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <GeneratorHeader
        devis={devis}
        onSoumettre={handleSoumettre}
        onValider={handleValider}
        onRetournerBrouillon={handleRetournerBrouillon}
        onAccepter={handleAccepter}
        onRefuser={handleRefuser}
        onPerdu={handlePerdu}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Main content - 9 colonnes */}
          <div className="col-span-12 lg:col-span-9 space-y-6">
            <ClientChantierCard devis={devis} isEditable={isEditable ?? false} onSaved={recalcAndReload} />
            <DatesCard devis={devis} isEditable={isEditable ?? false} onSaved={recalcAndReload} />
            <DevisTableCard devis={devis} isEditable={isEditable ?? false} onSaved={recalcAndReload} />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ConditionsPaiementCard devis={devis} editable={isEditable ?? false} onUpdate={handleUpdateDevis} />
              <MoyensPaiementCard devis={devis} editable={isEditable ?? false} onUpdate={handleUpdateDevis} />
              <NotesBasPageCard devis={devis} editable={isEditable ?? false} onUpdate={handleUpdateDevis} />
            </div>
          </div>

          {/* Sidebar - 3 colonnes */}
          <div className="col-span-12 lg:col-span-3 space-y-6">
            <RentabiliteSidebar devis={devis} onSaved={recalcAndReload} />
            <RecapitulatifSidebar devis={devis} />
            <OptionsInternesSidebar devis={devis} onSaved={recalcAndReload} />
            <BatiprixSidebar />
            <ActionsRapidesSidebar
              devis={devis}
              onNavigate={(newId: number) => navigate(`/devis/${newId}`)}
              onSaved={recalcAndReload}
            />
          </div>
        </div>
      </div>
    </Layout>
  )
}
