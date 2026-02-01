/**
 * DevisDetailPage - Detail complet d'un devis avec lots, marges et workflow
 * Module Devis (Module 20) - DEV-03 / DEV-05 / DEV-15
 */

import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import DevisStatusBadge from '../components/devis/DevisStatusBadge'
import DevisWorkflowActions from '../components/devis/DevisWorkflowActions'
import LotDevisPanel from '../components/devis/LotDevisPanel'
import MargesPanel from '../components/devis/MargesPanel'
import JournalDevis from '../components/devis/JournalDevis'
import DevisForm from '../components/devis/DevisForm'
import { devisService } from '../services/devis'
import type {
  DevisDetail,
  DevisCreate,
  DevisUpdate,
  LotDevisCreate,
  LotDevisUpdate,
  LigneDevisCreate,
  LigneDevisUpdate,
} from '../types'
import {
  Loader2,
  AlertCircle,
  ArrowLeft,
  Edit2,
  User,
  Calendar,
  Mail,
  Phone,
  MapPin,
  FileText,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'

const formatEUR = (value: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

export default function DevisDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [devis, setDevis] = useState<DevisDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showEditForm, setShowEditForm] = useState(false)
  const [journalOpen, setJournalOpen] = useState(false)

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

  // Workflow actions
  const handleSoumettre = async () => {
    await devisService.soumettreDevis(devisId)
    await loadDevis()
  }
  const handleValider = async () => {
    await devisService.validerDevis(devisId)
    await loadDevis()
  }
  const handleRetournerBrouillon = async () => {
    await devisService.retournerBrouillon(devisId)
    await loadDevis()
  }
  const handleAccepter = async () => {
    await devisService.accepterDevis(devisId)
    await loadDevis()
  }
  const handleRefuser = async (motif?: string) => {
    if (motif) {
      await devisService.refuserDevis(devisId, motif)
      await loadDevis()
    }
  }
  const handlePerdu = async (motif?: string) => {
    if (motif) {
      await devisService.marquerPerdu(devisId, motif)
      await loadDevis()
    }
  }

  // Edition devis
  const handleUpdateDevis = async (data: DevisCreate | DevisUpdate) => {
    await devisService.updateDevis(devisId, data as DevisUpdate)
    setShowEditForm(false)
    await loadDevis()
  }

  // CRUD lots
  const handleCreateLot = async (data: LotDevisCreate) => {
    await devisService.createLot(data)
    await loadDevis()
  }
  const handleUpdateLot = async (lotId: number, data: LotDevisUpdate) => {
    await devisService.updateLot(lotId, data)
    await loadDevis()
  }
  const handleDeleteLot = async (lotId: number) => {
    await devisService.deleteLot(lotId)
    await loadDevis()
  }

  // CRUD lignes
  const handleCreateLigne = async (data: LigneDevisCreate) => {
    await devisService.createLigne(data)
    await loadDevis()
  }
  const handleUpdateLigne = async (ligneId: number, data: LigneDevisUpdate) => {
    await devisService.updateLigne(ligneId, data)
    await loadDevis()
  }
  const handleDeleteLigne = async (ligneId: number) => {
    await devisService.deleteLigne(ligneId)
    await loadDevis()
  }

  return (
    <Layout>
      <div className="space-y-6" role="main" aria-label="Detail du devis">
        {/* Bouton retour */}
        <button
          onClick={() => navigate('/devis')}
          className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour a la liste
        </button>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
            <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
            <div>
              <p>{error}</p>
              <button onClick={loadDevis} className="text-sm underline mt-1">Reessayer</button>
            </div>
          </div>
        )}

        {/* Content */}
        {!loading && !error && devis && (
          <>
            {/* Header */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h1 className="text-xl font-bold text-gray-900">{devis.numero}</h1>
                    <DevisStatusBadge statut={devis.statut} size="md" />
                  </div>
                  <p className="text-gray-700 font-medium">{devis.objet}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {devis.date_creation && `Cree le ${new Date(devis.date_creation).toLocaleDateString('fr-FR')}`}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-3">
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Montant HT</p>
                    <p className="text-2xl font-bold text-gray-900">{formatEUR(Number(devis.montant_total_ht))}</p>
                    <p className="text-sm text-gray-500">TTC: {formatEUR(Number(devis.montant_total_ttc))}</p>
                  </div>
                  {isEditable && (
                    <button
                      onClick={() => setShowEditForm(true)}
                      className="inline-flex items-center gap-2 px-3 py-1.5 text-sm text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                      Modifier
                    </button>
                  )}
                </div>
              </div>

              {/* Workflow actions */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <DevisWorkflowActions
                  statut={devis.statut}
                  onSoumettre={handleSoumettre}
                  onValider={handleValider}
                  onRetournerBrouillon={handleRetournerBrouillon}
                  onAccepter={handleAccepter}
                  onRefuser={handleRefuser}
                  onPerdu={handlePerdu}
                />
              </div>
            </div>

            {/* Section info client */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Informations</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="flex items-start gap-3">
                  <User className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-gray-500">Client</p>
                    <p className="text-sm font-medium text-gray-900">{devis.client_nom}</p>
                  </div>
                </div>
                {devis.client_email && (
                  <div className="flex items-start gap-3">
                    <Mail className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-xs text-gray-500">Email</p>
                      <p className="text-sm text-gray-900">{devis.client_email}</p>
                    </div>
                  </div>
                )}
                {devis.client_telephone && (
                  <div className="flex items-start gap-3">
                    <Phone className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-xs text-gray-500">Telephone</p>
                      <p className="text-sm text-gray-900">{devis.client_telephone}</p>
                    </div>
                  </div>
                )}
                {devis.client_adresse && (
                  <div className="flex items-start gap-3">
                    <MapPin className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-xs text-gray-500">Adresse</p>
                      <p className="text-sm text-gray-900">{devis.client_adresse}</p>
                    </div>
                  </div>
                )}
                {devis.date_validite && (
                  <div className="flex items-start gap-3">
                    <Calendar className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-xs text-gray-500">Validite</p>
                      <p className="text-sm text-gray-900">
                        {new Date(devis.date_validite).toLocaleDateString('fr-FR')}
                      </p>
                    </div>
                  </div>
                )}
                {devis.conditions_generales && (
                  <div className="flex items-start gap-3">
                    <FileText className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-xs text-gray-500">Conditions generales</p>
                      <p className="text-sm text-gray-900">{devis.conditions_generales}</p>
                    </div>
                  </div>
                )}
              </div>
              {devis.notes && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-xs text-gray-500 mb-1">Notes internes</p>
                  <p className="text-sm text-gray-700">{devis.notes}</p>
                </div>
              )}
            </div>

            {/* Section lots */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">
                Lots et lignes ({devis.lots.length} lot{devis.lots.length > 1 ? 's' : ''})
              </h2>
              <LotDevisPanel
                lots={devis.lots}
                devisId={devisId}
                editable={isEditable}
                onCreateLot={handleCreateLot}
                onUpdateLot={handleUpdateLot}
                onDeleteLot={handleDeleteLot}
                onCreateLigne={handleCreateLigne}
                onUpdateLigne={handleUpdateLigne}
                onDeleteLigne={handleDeleteLigne}
              />
            </div>

            {/* Section marges */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Recapitulatif marges</h2>
              <MargesPanel devis={devis} />
            </div>

            {/* Section journal (collapsible) */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <button
                onClick={() => setJournalOpen(!journalOpen)}
                className="w-full flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
              >
                <h2 className="text-sm font-semibold text-gray-700">Historique des modifications</h2>
                {journalOpen ? (
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                )}
              </button>
              {journalOpen && (
                <div className="px-6 pb-6">
                  <JournalDevis devisId={devisId} />
                </div>
              )}
            </div>
          </>
        )}

        {/* Modal edition */}
        {showEditForm && devis && (
          <DevisForm
            devis={devis}
            onSubmit={handleUpdateDevis}
            onCancel={() => setShowEditForm(false)}
          />
        )}
      </div>
    </Layout>
  )
}
