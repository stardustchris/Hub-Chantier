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
import VersionsPanel from '../components/devis/VersionsPanel'
import AttestationTVAPanel from '../components/devis/AttestationTVAPanel'
import FraisChantierPanel from '../components/devis/FraisChantierPanel'
import OptionsPresentationPanel from '../components/devis/OptionsPresentationPanel'
import SignaturePanel from '../components/devis/SignaturePanel'
import ConversionChantierPanel from '../components/devis/ConversionChantierPanel'
import RelancesPanel from '../components/devis/RelancesPanel'
import { devisService } from '../services/devis'
import { formatEUR } from '../utils/format'
import type {
  DevisDetail,
  DevisCreate,
  DevisUpdate,
  LotDevisCreate,
  LotDevisUpdate,
  LigneDevisCreate,
  LigneDevisUpdate,
  ConvertirDevisResult,
} from '../types'
import { TYPE_VERSION_CONFIG, LABEL_VARIANTE_CONFIG } from '../types'
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
  Lock,
  GitBranch,
  Copy,
  Building2,
  CheckCircle,
  X,
} from 'lucide-react'

export default function DevisDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [devis, setDevis] = useState<DevisDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showEditForm, setShowEditForm] = useState(false)
  const [journalOpen, setJournalOpen] = useState(false)
  const [showConvertModal, setShowConvertModal] = useState(false)
  const [convertLoading, setConvertLoading] = useState(false)
  const [convertError, setConvertError] = useState<string | null>(null)
  const [convertResult, setConvertResult] = useState<ConvertirDevisResult | null>(null)
  const [notifyClient, setNotifyClient] = useState(false)
  const [notifyTeam, setNotifyTeam] = useState(true)

  const devisId = Number(id)
  const isEditable = devis?.statut === 'brouillon'

  const loadDevis = useCallback(async () => {
    if (!devisId || isNaN(devisId)) return
    try {
      setLoading(true)
      setError(null)
      const data = await devisService.getDevis(devisId)
      setDevis(data)
    } catch (error) {
      console.error('Erreur lors du chargement du devis:', error)
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

  // Conversion devis -> chantier (DEV-16)
  const handleConvertir = async () => {
    try {
      setConvertLoading(true)
      setConvertError(null)
      const result = await devisService.convertirEnChantier(devisId, {
        notify_client: notifyClient,
        notify_team: notifyTeam,
      })
      setConvertResult(result)
      setShowConvertModal(false)
      await loadDevis()
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string; message?: string; error?: string } } }
      const message = axiosError.response?.data?.detail
        || axiosError.response?.data?.message
        || 'Erreur lors de la conversion du devis en chantier'
      setConvertError(message)
    } finally {
      setConvertLoading(false)
    }
  }

  // Recalculer les totaux et recharger le devis
  const recalculerEtRecharger = async () => {
    try {
      await devisService.calculerTotaux(devisId)
    } catch (error) {
      console.error('Erreur lors du recalcul des totaux du devis:', error)
      // Le recalcul peut echouer si le devis n'a pas de lignes, on continue
    }
    await loadDevis()
  }

  // Edition devis
  const handleUpdateDevis = async (data: DevisCreate | DevisUpdate) => {
    await devisService.updateDevis(devisId, data as DevisUpdate)
    setShowEditForm(false)
    await recalculerEtRecharger()
  }

  // CRUD lots
  const handleCreateLot = async (data: LotDevisCreate) => {
    await devisService.createLot(data)
    await recalculerEtRecharger()
  }
  const handleUpdateLot = async (lotId: number, data: LotDevisUpdate) => {
    await devisService.updateLot(lotId, data)
    await recalculerEtRecharger()
  }
  const handleDeleteLot = async (lotId: number) => {
    await devisService.deleteLot(lotId)
    await recalculerEtRecharger()
  }

  // CRUD lignes
  const handleCreateLigne = async (data: LigneDevisCreate) => {
    await devisService.createLigne(data)
    await recalculerEtRecharger()
  }
  const handleUpdateLigne = async (ligneId: number, data: LigneDevisUpdate) => {
    await devisService.updateLigne(ligneId, data)
    await recalculerEtRecharger()
  }
  const handleDeleteLigne = async (ligneId: number) => {
    await devisService.deleteLigne(ligneId)
    await recalculerEtRecharger()
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
                  <div className="flex flex-wrap items-center gap-3 mb-2">
                    <h1 className="text-xl font-bold text-gray-900">{devis.numero}</h1>
                    <DevisStatusBadge statut={devis.statut} size="md" />
                    {/* Version badge (DEV-08) */}
                    {devis.type_version && devis.type_version !== 'originale' && (
                      <span
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: `${TYPE_VERSION_CONFIG[devis.type_version].couleur}20`,
                          color: TYPE_VERSION_CONFIG[devis.type_version].couleur,
                        }}
                      >
                        <GitBranch className="w-3 h-3" />
                        {devis.type_version === 'variante' && devis.label_variante
                          ? LABEL_VARIANTE_CONFIG[devis.label_variante].label
                          : TYPE_VERSION_CONFIG[devis.type_version].label}
                      </span>
                    )}
                    {devis.numero_version !== undefined && devis.numero_version > 1 && (
                      <span className="text-xs text-gray-500">v{devis.numero_version}</span>
                    )}
                    {/* Indicateur fige (DEV-08) */}
                    {devis.version_figee && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        <Lock className="w-3 h-3" />
                        Version figee
                      </span>
                    )}
                  </div>
                  <p className="text-gray-700 font-medium">{devis.objet}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {devis.date_creation && `Cree le ${new Date(devis.date_creation).toLocaleDateString('fr-FR')}`}
                    {devis.version_commentaire && (
                      <span className="ml-2 italic text-gray-400">
                        - {devis.version_commentaire}
                      </span>
                    )}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-3">
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Montant HT</p>
                    <p className="text-2xl font-bold text-gray-900">{formatEUR(Number(devis.montant_total_ht))}</p>
                    <p className="text-sm text-gray-500">TTC: {formatEUR(Number(devis.montant_total_ttc))}</p>
                    {Number(devis.retenue_garantie_pct) > 0 && (
                      <p className="text-xs text-amber-600 mt-1">
                        Retenue de garantie : {devis.retenue_garantie_pct}%
                        {devis.montant_retenue_garantie != null && (
                          <span> ({formatEUR(Number(devis.montant_retenue_garantie))})</span>
                        )}
                      </p>
                    )}
                    {devis.montant_net_a_payer != null && Number(devis.retenue_garantie_pct) > 0 && (
                      <p className="text-sm font-semibold text-blue-700">
                        Net a payer : {formatEUR(Number(devis.montant_net_a_payer))}
                      </p>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {isEditable && (
                      <>
                        <button
                          onClick={() => setShowEditForm(true)}
                          className="inline-flex items-center gap-2 px-3 py-1.5 text-sm text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                        >
                          <Edit2 className="w-4 h-4" />
                          Modifier
                        </button>
                        <button
                          onClick={async () => {
                            const nouveau = await devisService.creerRevision(devisId)
                            navigate(`/devis/${nouveau.id}`)
                          }}
                          className="inline-flex items-center gap-2 px-3 py-1.5 text-sm text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
                        >
                          <Copy className="w-4 h-4" />
                          Creer revision
                        </button>
                      </>
                    )}
                  </div>
                  {devis.statut === 'accepte' && (
                    <button
                      onClick={() => {
                        setConvertError(null)
                        setShowConvertModal(true)
                      }}
                      className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors"
                      style={{ backgroundColor: '#009688' }}
                      onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#00796B' }}
                      onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#009688' }}
                    >
                      <Building2 className="w-4 h-4" />
                      Convertir en chantier
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

            {/* Section frais de chantier (DEV-25) */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Frais de chantier</h2>
              <FraisChantierPanel
                devisId={devisId}
                isEditable={isEditable ?? false}
                lots={devis.lots}
              />
            </div>

            {/* Section marges */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Recapitulatif financier et marges</h2>
              <MargesPanel devis={devis} />
            </div>

            {/* Section options de presentation (DEV-11) */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Mise en page du devis</h2>
              <OptionsPresentationPanel devisId={devisId} />
            </div>

            {/* Section attestation TVA (DEV-23) */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Attestation TVA</h2>
              <AttestationTVAPanel devisId={devisId} devis={devis} />
            </div>

            {/* Section signature electronique (DEV-14) */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Signature electronique</h2>
              <SignaturePanel
                devisId={devisId}
                statut={devis.statut}
                onSignatureChange={loadDevis}
              />
            </div>

            {/* Section relances automatiques (DEV-24) */}
            {(devis.statut === 'envoye' || devis.statut === 'vu' || devis.statut === 'en_negociation') && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-sm font-semibold text-gray-700 mb-4">Relances automatiques</h2>
                <RelancesPanel
                  devisId={devisId}
                  devisStatut={devis.statut}
                />
              </div>
            )}

            {/* Section conversion en chantier (DEV-16) */}
            {(devis.statut === 'accepte') && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-sm font-semibold text-gray-700 mb-4">Conversion en chantier</h2>
                <ConversionChantierPanel
                  devisId={devisId}
                  devisStatut={devis.statut}
                />
              </div>
            )}

            {/* Section versions et variantes (DEV-08) */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <VersionsPanel
                devisId={devisId}
                devisParentId={devis.devis_parent_id}
                isEditable={isEditable}
                onVersionCreated={loadDevis}
              />
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

        {/* Bandeau succes conversion */}
        {convertResult && (
          <div className="bg-teal-50 border border-teal-200 text-teal-800 px-4 py-4 rounded-lg" role="status">
            <div className="flex items-start gap-3">
              <CheckCircle className="flex-shrink-0 mt-0.5 text-teal-600" size={20} />
              <div className="flex-1">
                <p className="font-medium">
                  Chantier cree avec succes !
                </p>
                <p className="text-sm mt-1">
                  Code chantier : <span className="font-semibold">{convertResult.code_chantier}</span>
                  {' '}&mdash;{' '}
                  {convertResult.nb_lots_transferes} lot{convertResult.nb_lots_transferes > 1 ? 's' : ''} transfere{convertResult.nb_lots_transferes > 1 ? 's' : ''}
                  {' '}&mdash;{' '}
                  Montant : {formatEUR(convertResult.montant_total_ht)} HT
                </p>
                <button
                  onClick={() => navigate(`/chantiers/${convertResult.chantier_id}`)}
                  className="inline-flex items-center gap-2 mt-2 px-3 py-1.5 text-sm font-medium text-white rounded-lg transition-colors"
                  style={{ backgroundColor: '#009688' }}
                >
                  <Building2 className="w-4 h-4" />
                  Voir le chantier
                </button>
              </div>
              <button
                onClick={() => setConvertResult(null)}
                className="text-teal-400 hover:text-teal-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Modal edition */}
        {showEditForm && devis && (
          <DevisForm
            devis={devis}
            onSubmit={handleUpdateDevis}
            onCancel={() => setShowEditForm(false)}
          />
        )}

        {/* Modal confirmation conversion devis -> chantier */}
        {showConvertModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-full" style={{ backgroundColor: '#E0F2F1' }}>
                  <Building2 className="w-5 h-5" style={{ color: '#009688' }} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Convertir en chantier
                </h3>
              </div>

              <p className="text-sm text-gray-600 mb-4">
                Cette action va creer un chantier a partir du devis{' '}
                <span className="font-semibold">{devis?.numero}</span> et transferer les lots budgetaires.
                Le devis passera en statut &laquo; Converti &raquo;.
              </p>

              {convertError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm mb-4 flex items-start gap-2">
                  <AlertCircle className="flex-shrink-0 mt-0.5" size={16} />
                  <p>{convertError}</p>
                </div>
              )}

              <div className="space-y-3 mb-6">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notifyClient}
                    onChange={(e) => setNotifyClient(e.target.checked)}
                    className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
                  />
                  <span className="text-sm text-gray-700">Notifier le client</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notifyTeam}
                    onChange={(e) => setNotifyTeam(e.target.checked)}
                    className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
                  />
                  <span className="text-sm text-gray-700">Notifier l'equipe</span>
                </label>
              </div>

              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setShowConvertModal(false)
                    setConvertError(null)
                  }}
                  disabled={convertLoading}
                  className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={handleConvertir}
                  disabled={convertLoading}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors disabled:opacity-50"
                  style={{ backgroundColor: '#009688' }}
                >
                  {convertLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Building2 className="w-4 h-4" />
                  )}
                  {convertLoading ? 'Conversion en cours...' : 'Confirmer la conversion'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
