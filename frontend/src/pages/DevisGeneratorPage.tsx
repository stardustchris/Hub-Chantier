/**
 * DevisGeneratorPage - Nouveau generateur de devis avec layout 12 colonnes
 * Remplace DevisDetailPage (conservee sur /devis/:id/legacy)
 */

import { useEffect, useCallback, useRef } from 'react'
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
import { useDevisDetail } from '../hooks/useDevisDetail'
import { Loader2, AlertCircle } from 'lucide-react'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { Breadcrumb } from '../components/ui/Breadcrumb'

export default function DevisGeneratorPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const recalcTimer = useRef<ReturnType<typeof setTimeout>>(undefined)

  const devisId = Number(id)
  const {
    devis,
    loading,
    error,
    loadDevis,
    soumettre,
    valider,
    retournerBrouillon,
    accepter,
    refuser,
    marquerPerdu,
    calculerTotaux,
  } = useDevisDetail(devisId)

  const isEditable = devis?.statut === 'brouillon'

  // Document title
  useDocumentTitle(devis ? `Devis ${devis.numero}` : 'Devis')

  useEffect(() => {
    loadDevis()
  }, [loadDevis])

  /** Debounced recalculation after mutations */
  const recalcAndReload = useCallback(() => {
    clearTimeout(recalcTimer.current)
    recalcTimer.current = setTimeout(async () => {
      await calculerTotaux()
      loadDevis()
    }, 500)
  }, [calculerTotaux, loadDevis])

  useEffect(() => {
    return () => clearTimeout(recalcTimer.current)
  }, [])

  // Workflow handlers
  const handleSoumettre = async () => { await soumettre() }
  const handleValider = async () => { await valider() }
  const handleRetournerBrouillon = async () => { await retournerBrouillon() }
  const handleAccepter = async () => { await accepter() }
  const handleRefuser = async (motif?: string) => { if (motif) { await refuser(motif) } }
  const handlePerdu = async (motif?: string) => { if (motif) { await marquerPerdu(motif) } }



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
      {/* Breadcrumb */}
      {devis && (
        <div className="max-w-7xl mx-auto px-6 pt-4">
          <Breadcrumb
            items={[
              { label: 'Accueil', href: '/' },
              { label: 'Devis', href: '/devis' },
              { label: devis.numero },
            ]}
          />
        </div>
      )}

      <GeneratorHeader
        devis={devis}
        onSoumettre={handleSoumettre}
        onValider={handleValider}
        onRetournerBrouillon={handleRetournerBrouillon}
        onAccepter={handleAccepter}
        onRefuser={handleRefuser}
        onPerdu={handlePerdu}
        onSaved={recalcAndReload}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Main content - 9 colonnes */}
          <div className="col-span-12 lg:col-span-9 space-y-6">
            <ClientChantierCard devis={devis} isEditable={isEditable ?? false} onSaved={recalcAndReload} />
            <DatesCard devis={devis} isEditable={isEditable ?? false} onSaved={recalcAndReload} />
            <DevisTableCard devis={devis} isEditable={isEditable ?? false} onChanged={recalcAndReload} />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ConditionsPaiementCard devis={devis} isEditable={isEditable ?? false} onSaved={recalcAndReload} />
              <MoyensPaiementCard devis={devis} isEditable={isEditable ?? false} onSaved={recalcAndReload} />
              <NotesBasPageCard devis={devis} isEditable={isEditable ?? false} onSaved={recalcAndReload} />
            </div>
          </div>

          {/* Sidebar - 3 colonnes */}
          <div className="col-span-12 lg:col-span-3 space-y-6">
            <RentabiliteSidebar devis={devis} onSaved={recalcAndReload} />
            <RecapitulatifSidebar devis={devis} />
            <OptionsInternesSidebar devis={devis} isEditable={isEditable ?? false} onSaved={recalcAndReload} />
            <BatiprixSidebar />
            <ActionsRapidesSidebar
              devis={devis}
              onReload={recalcAndReload}
            />
          </div>
        </div>
      </div>
    </Layout>
  )
}
