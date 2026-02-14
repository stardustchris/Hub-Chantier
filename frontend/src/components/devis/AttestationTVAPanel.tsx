/**
 * AttestationTVAPanel - Verification eligibilite TVA reduite et generation attestation CERFA
 * Module Devis (Module 20) - DEV-23
 */

import { useState, useEffect, useCallback } from 'react'
import { devisService } from '../../services/devis'
import type {
  DevisDetail,
  EligibiliteTVA,
  AttestationTVA,
  AttestationTVACreate,
  NatureImmeuble,
  NatureTravaux,
} from '../../types'
import { NATURE_IMMEUBLE_LABELS, NATURE_TRAVAUX_LABELS } from '../../types'
import {
  Loader2,
  AlertCircle,
  CheckCircle2,
  FileText,
  Info,
  Building2,
  UserCircle,
  Hammer,
} from 'lucide-react'

interface AttestationTVAPanelProps {
  devisId: number
  devis: DevisDetail
}

const formatDate = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })

export default function AttestationTVAPanel({ devisId, devis }: AttestationTVAPanelProps) {
  const [eligibilite, setEligibilite] = useState<EligibiliteTVA | null>(null)
  const [attestation, setAttestation] = useState<AttestationTVA | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingAttestation, setLoadingAttestation] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Formulaire
  const [formData, setFormData] = useState<AttestationTVACreate>({
    nom_client: devis.client_nom || '',
    adresse_client: devis.client_adresse || '',
    telephone_client: devis.client_telephone || '',
    adresse_immeuble: devis.client_adresse || '',
    nature_immeuble: 'maison',
    date_construction_plus_2ans: true,
    description_travaux: devis.objet || '',
    nature_travaux: 'amelioration',
    atteste_par: devis.client_nom || '',
  })

  const checkEligibilite = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await devisService.verifierEligibiliteTVA(devisId)
      setEligibilite(data)

      // Si eligible, tenter de charger l'attestation existante
      if (data.eligible) {
        try {
          setLoadingAttestation(true)
          const att = await devisService.getAttestationTVA(devisId)
          setAttestation(att)
        } catch {
          // Pas d'attestation existante, c'est normal
          setAttestation(null)
        } finally {
          setLoadingAttestation(false)
        }
      }
    } catch {
      setError('Erreur lors de la verification de l\'eligibilite TVA')
    } finally {
      setLoading(false)
    }
  }, [devisId])

  useEffect(() => {
    checkEligibilite()
  }, [checkEligibilite])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSubmitting(true)
      setError(null)
      const result = await devisService.genererAttestationTVA(devisId, formData)
      setAttestation(result)
    } catch {
      setError('Erreur lors de la generation de l\'attestation')
    } finally {
      setSubmitting(false)
    }
  }

  const updateForm = (field: keyof AttestationTVACreate, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  // Loading
  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-sm text-gray-500">Verification de l'eligibilite TVA...</span>
      </div>
    )
  }

  // Erreur
  if (error && !eligibilite) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
        <div>
          <p>{error}</p>
          <button onClick={checkEligibilite} className="text-sm underline mt-1">Reessayer</button>
        </div>
      </div>
    )
  }

  if (!eligibilite) return null

  // TVA standard 20% - pas d'attestation requise
  if (!eligibilite.eligible) {
    return (
      <div className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <Info className="w-5 h-5 text-gray-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-gray-700">TVA standard ({eligibilite.taux_tva}%)</p>
          <p className="text-sm text-gray-500 mt-1">{eligibilite.message}</p>
        </div>
      </div>
    )
  }

  // Eligible TVA reduite
  return (
    <div className="space-y-4">
      {/* Badge eligibilite */}
      <div className="flex items-start gap-3 p-4 bg-green-50 rounded-lg border border-green-200">
        <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800">
              Eligible TVA reduite {eligibilite.taux_tva}%
            </span>
            {eligibilite.type_cerfa && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                <FileText className="w-3 h-3" />
                CERFA {eligibilite.type_cerfa}
              </span>
            )}
          </div>
          <p className="text-sm text-green-700 mt-1">{eligibilite.message}</p>
        </div>
      </div>

      {/* Erreur formulaire */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
          <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Attestation existante */}
      {loadingAttestation ? (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
          <span className="ml-2 text-sm text-gray-500">Chargement de l'attestation...</span>
        </div>
      ) : attestation ? (
        <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-4">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-5 h-5 text-blue-600" />
            <h3 className="text-sm font-semibold text-gray-900">Attestation CERFA {attestation.type_cerfa}</h3>
            <span className="text-xs text-gray-500">- Generee le {formatDate(attestation.generee_at)}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            {/* Client */}
            <div className="space-y-1">
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Client</p>
              <p className="text-gray-900">{attestation.nom_client}</p>
              <p className="text-gray-600">{attestation.adresse_client}</p>
              {attestation.telephone_client && (
                <p className="text-gray-600">{attestation.telephone_client}</p>
              )}
            </div>

            {/* Immeuble */}
            <div className="space-y-1">
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Immeuble</p>
              <p className="text-gray-900">{attestation.adresse_immeuble}</p>
              <p className="text-gray-600">
                {NATURE_IMMEUBLE_LABELS[attestation.nature_immeuble]}
                {attestation.date_construction_plus_2ans && ' - Plus de 2 ans'}
              </p>
            </div>

            {/* Travaux */}
            <div className="space-y-1">
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Travaux</p>
              <p className="text-gray-900">{attestation.description_travaux}</p>
              <p className="text-gray-600">{NATURE_TRAVAUX_LABELS[attestation.nature_travaux]}</p>
            </div>

            {/* Attestation */}
            <div className="space-y-1">
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Attestation</p>
              <p className="text-gray-900">Atteste par : {attestation.atteste_par}</p>
              <p className="text-gray-600">
                TVA : {attestation.taux_tva}% - Le {formatDate(attestation.date_attestation)}
              </p>
            </div>
          </div>
        </div>
      ) : (
        /* Formulaire attestation */
        <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-4 space-y-6">
          <h3 className="text-sm font-semibold text-gray-900">Generer l'attestation CERFA</h3>

          {/* Section 1 : Informations client */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <UserCircle className="w-4 h-4 text-blue-500" />
              Informations client
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label htmlFor="att-nom-client" className="block text-xs text-gray-500 mb-1">
                  Nom du client *
                </label>
                <input
                  id="att-nom-client"
                  type="text"
                  required
                  value={formData.nom_client}
                  onChange={(e) => updateForm('nom_client', e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label htmlFor="att-tel-client" className="block text-xs text-gray-500 mb-1">
                  Telephone
                </label>
                <input
                  id="att-tel-client"
                  type="tel"
                  value={formData.telephone_client || ''}
                  onChange={(e) => updateForm('telephone_client', e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="md:col-span-2">
                <label htmlFor="att-adresse-client" className="block text-xs text-gray-500 mb-1">
                  Adresse du client *
                </label>
                <input
                  id="att-adresse-client"
                  type="text"
                  required
                  value={formData.adresse_client}
                  onChange={(e) => updateForm('adresse_client', e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Section 2 : Informations immeuble */}
          <div className="space-y-3 pt-3 border-t border-gray-100">
            <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <Building2 className="w-4 h-4 text-blue-500" />
              Informations immeuble
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="md:col-span-2">
                <label htmlFor="att-adresse-immeuble" className="block text-xs text-gray-500 mb-1">
                  Adresse de l'immeuble *
                </label>
                <input
                  id="att-adresse-immeuble"
                  type="text"
                  required
                  value={formData.adresse_immeuble}
                  onChange={(e) => updateForm('adresse_immeuble', e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label htmlFor="att-nature-immeuble" className="block text-xs text-gray-500 mb-1">
                  Nature de l'immeuble *
                </label>
                <select
                  id="att-nature-immeuble"
                  required
                  value={formData.nature_immeuble}
                  onChange={(e) => updateForm('nature_immeuble', e.target.value as NatureImmeuble)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  {(Object.entries(NATURE_IMMEUBLE_LABELS) as [NatureImmeuble, string][]).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-center">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.date_construction_plus_2ans}
                    onChange={(e) => updateForm('date_construction_plus_2ans', e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">
                    Immeuble acheve depuis plus de 2 ans
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* Section 3 : Nature des travaux */}
          <div className="space-y-3 pt-3 border-t border-gray-100">
            <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <Hammer className="w-4 h-4 text-blue-500" />
              Nature des travaux
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="md:col-span-2">
                <label htmlFor="att-description-travaux" className="block text-xs text-gray-500 mb-1">
                  Description des travaux *
                </label>
                <textarea
                  id="att-description-travaux"
                  required
                  rows={3}
                  value={formData.description_travaux}
                  onChange={(e) => updateForm('description_travaux', e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
              </div>
              <div>
                <label htmlFor="att-nature-travaux" className="block text-xs text-gray-500 mb-1">
                  Nature des travaux *
                </label>
                <select
                  id="att-nature-travaux"
                  required
                  value={formData.nature_travaux}
                  onChange={(e) => updateForm('nature_travaux', e.target.value as NatureTravaux)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  {(Object.entries(NATURE_TRAVAUX_LABELS) as [NatureTravaux, string][]).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="att-atteste-par" className="block text-xs text-gray-500 mb-1">
                  Atteste par (nom du signataire) *
                </label>
                <input
                  id="att-atteste-par"
                  type="text"
                  required
                  value={formData.atteste_par}
                  onChange={(e) => updateForm('atteste_par', e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Bouton soumettre */}
          <div className="pt-3 border-t border-gray-100">
            <button
              type="submit"
              disabled={submitting}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generation en cours...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Generer l'attestation CERFA
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  )
}
