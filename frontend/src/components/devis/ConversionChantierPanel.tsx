/**
 * ConversionChantierPanel - Conversion d'un devis accepte en chantier
 * Module Devis (Module 20) - DEV-16
 *
 * Fonctionnalites :
 * - Verification des pre-requis (devis accepte, signe)
 * - Affichage du recapitulatif de conversion (client, montants, lots)
 * - Modale de confirmation avant conversion
 * - Lien vers le chantier cree apres conversion
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { devisService } from '../../services/devis'
import type { ConversionInfo, ConversionDevis, StatutDevis } from '../../types'
import {
  CheckCircle2,
  XCircle,
  ArrowRight,
  Loader2,
  AlertCircle,
  Building2,
  X,
  Package,
  Euro,
  Users,
  ShieldCheck,
} from 'lucide-react'

// ===== Props =====
interface ConversionChantierPanelProps {
  devisId: number
  devisStatut: StatutDevis
}

// ===== Formateur EUR =====
const formatEUR = (value: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

// ===== Composant principal =====
// Statuts qui permettent la conversion
const STATUTS_CONVERTIBLES: StatutDevis[] = ['accepte']

export default function ConversionChantierPanel({
  devisId,
  devisStatut,
}: ConversionChantierPanelProps) {
  const navigate = useNavigate()
  const [info, setInfo] = useState<ConversionInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [converting, setConverting] = useState(false)
  const [showConfirmModal, setShowConfirmModal] = useState(false)
  const [conversionResult, setConversionResult] = useState<ConversionDevis | null>(null)

  const isEligible = STATUTS_CONVERTIBLES.includes(devisStatut)

  const loadConversionInfo = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await devisService.getConversionInfo(devisId)
      setInfo(data)
    } catch {
      setError('Impossible de verifier les conditions de conversion')
    } finally {
      setLoading(false)
    }
  }, [devisId])

  useEffect(() => {
    loadConversionInfo()
  }, [loadConversionInfo])

  const handleConvertir = async () => {
    try {
      setConverting(true)
      setError(null)
      const result = await devisService.convertirEnChantier(devisId)
      setConversionResult(result)
      setShowConfirmModal(false)
      // Recharger les infos pour afficher l'etat "deja converti"
      await loadConversionInfo()
    } catch {
      setError('Erreur lors de la conversion en chantier')
    } finally {
      setConverting(false)
    }
  }

  // Si le statut ne permet pas la conversion et pas encore charge
  if (!isEligible && !info?.deja_converti && !loading) {
    return null
  }

  // --- Loading ---
  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-sm text-gray-500">Verification des pre-requis...</span>
      </div>
    )
  }

  // --- Erreur ---
  if (error && !info) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
        <div>
          <p className="text-sm">{error}</p>
          <button onClick={loadConversionInfo} className="text-sm underline mt-1">
            Reessayer
          </button>
        </div>
      </div>
    )
  }

  if (!info) return null

  // --- Resultat de conversion (succes) ---
  if (conversionResult) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-green-800">
              Chantier cree avec succes
            </h3>
            <p className="text-sm text-green-700 mt-1">
              Le devis <span className="font-medium">{conversionResult.numero}</span> a ete
              converti en chantier pour le client{' '}
              <span className="font-medium">{conversionResult.client}</span>.
            </p>
            <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="bg-white/60 rounded-lg px-3 py-2">
                <p className="text-xs text-green-600">Budget</p>
                <p className="text-sm font-semibold text-green-800">
                  {formatEUR(conversionResult.budget)}
                </p>
              </div>
              <div className="bg-white/60 rounded-lg px-3 py-2">
                <p className="text-xs text-green-600">Lots transferes</p>
                <p className="text-sm font-semibold text-green-800">
                  {conversionResult.lots.length} lot{conversionResult.lots.length > 1 ? 's' : ''}
                </p>
              </div>
              <div className="bg-white/60 rounded-lg px-3 py-2">
                <p className="text-xs text-green-600">Retenue de garantie</p>
                <p className="text-sm font-semibold text-green-800">
                  {conversionResult.retenue_garantie_pct}%
                </p>
              </div>
            </div>
            {conversionResult.chantier_id && (
              <button
                onClick={() => navigate(`/chantiers/${conversionResult.chantier_id}`)}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                <Building2 className="w-4 h-4" />
                Voir le chantier
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  // --- Deja converti ---
  if (info.deja_converti) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <Building2 className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-base font-semibold text-blue-800">
              Ce devis a deja ete converti en chantier
            </h3>
            {info.chantier_numero && (
              <p className="text-sm text-blue-700 mt-1">
                Chantier : <span className="font-medium">{info.chantier_numero}</span>
              </p>
            )}
            {info.chantier_id && (
              <button
                onClick={() => navigate(`/chantiers/${info.chantier_id}`)}
                className="mt-3 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Building2 className="w-4 h-4" />
                Voir le chantier
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  // --- Non convertible : afficher pre-requis manquants ---
  if (!info.conversion_possible) {
    return (
      <div className="space-y-4">
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <p className="text-sm font-medium text-amber-800 mb-3">
            Pre-requis pour la conversion en chantier :
          </p>
          <ul className="space-y-2">
            <li className="flex items-center gap-2 text-sm">
              {info.est_accepte ? (
                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
              )}
              <span className={info.est_accepte ? 'text-green-700' : 'text-red-700'}>
                Devis accepte
              </span>
            </li>
            <li className="flex items-center gap-2 text-sm">
              {info.est_signe ? (
                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
              )}
              <span className={info.est_signe ? 'text-green-700' : 'text-red-700'}>
                Devis signe
              </span>
            </li>
          </ul>
          {info.pre_requis_manquants.length > 0 && (
            <div className="mt-3 pt-3 border-t border-amber-200">
              <p className="text-xs text-amber-700">
                {info.pre_requis_manquants.join(' - ')}
              </p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // --- Convertible : recapitulatif + bouton ---
  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2">
          <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
          <p className="text-sm">{error}</p>
        </div>
      )}

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-green-800">
              Tous les pre-requis sont remplis. Ce devis peut etre converti en chantier.
            </p>
            <ul className="mt-2 space-y-1">
              <li className="flex items-center gap-2 text-sm text-green-700">
                <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                Devis accepte
              </li>
              <li className="flex items-center gap-2 text-sm text-green-700">
                <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                Devis signe
              </li>
            </ul>
          </div>
        </div>
      </div>

      <button
        onClick={() => setShowConfirmModal(true)}
        className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Building2 className="w-5 h-5" />
        Convertir en chantier
        <ArrowRight className="w-4 h-4" />
      </button>

      {/* Modale de confirmation */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                Confirmer la conversion en chantier
              </h3>
              <button
                onClick={() => setShowConfirmModal(false)}
                className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                disabled={converting}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <p className="text-sm text-gray-600">
                Cette action va creer un nouveau chantier a partir de ce devis. Les elements
                suivants seront transferes :
              </p>

              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Users className="w-5 h-5 text-gray-500 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-gray-500">Client</p>
                    <p className="text-sm font-medium text-gray-900">
                      Selon les informations du devis
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Euro className="w-5 h-5 text-gray-500 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-gray-500">Montant HT / TTC</p>
                    <p className="text-sm font-medium text-gray-900">
                      Budget initial du chantier
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Package className="w-5 h-5 text-gray-500 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-gray-500">Lots du devis</p>
                    <p className="text-sm font-medium text-gray-900">
                      Transferes en lots budgetaires du chantier
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <ShieldCheck className="w-5 h-5 text-gray-500 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-gray-500">Retenue de garantie</p>
                    <p className="text-sm font-medium text-gray-900">
                      Pourcentage conserve
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                <p className="text-xs text-amber-700">
                  Cette operation est irreversible. Le devis ne pourra plus etre modifie
                  apres conversion.
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
              <button
                onClick={() => setShowConfirmModal(false)}
                disabled={converting}
                className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Annuler
              </button>
              <button
                onClick={handleConvertir}
                disabled={converting}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {converting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Conversion en cours...
                  </>
                ) : (
                  <>
                    <Building2 className="w-4 h-4" />
                    Confirmer la conversion
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
