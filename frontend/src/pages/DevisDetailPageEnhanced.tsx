/**
 * DevisDetailPageEnhanced - Page de détail de devis avec upload multimédia
 * DEV-07: Insertion multimédia
 *
 * Démontre l'intégration du composant DevisMediaUpload
 */

import { useParams, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react'
import Layout from '../components/Layout'
import DevisMediaUpload from '../components/devis/DevisMediaUpload'
import DevisStatusBadge from '../components/devis/DevisStatusBadge'
import { useDevisMediaUpload } from '../hooks/useDevisMediaUpload'
import { useDevisDetail } from '../hooks/useDevisDetail'
import { formatEUR } from '../utils/format'

export default function DevisDetailPageEnhanced() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const devisId = id ? Number(id) : 0
  const { devis, loading, error, loadDevis } = useDevisDetail(devisId)

  const {
    pieces,
    uploading,
    uploadProgress,
    error: uploadError,
    uploadFiles,
    removeFile,
    toggleVisibility,
    reload: reloadPieces,
  } = useDevisMediaUpload({
    devisId,
    onUploadComplete: (pieces) => {
      console.log('Upload completed:', pieces)
    },
  })

  useEffect(() => {
    if (!devisId) return
    loadDevis().then(() => reloadPieces())
  }, [devisId, loadDevis, reloadPieces])

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      </Layout>
    )
  }

  if (error || !devis) {
    return (
      <Layout>
        <div
          className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2"
          role="alert"
        >
          <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
          <div>
            <p>{error || 'Devis introuvable'}</p>
            <button
              onClick={() => navigate('/devis')}
              className="text-sm underline mt-1"
            >
              Retour à la liste
            </button>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6" role="main">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/devis')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Retour"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900">{devis.objet}</h1>
            <p className="text-sm text-gray-600 mt-1">
              Devis {devis.numero} - {devis.client_nom}
            </p>
          </div>
          <DevisStatusBadge statut={devis.statut} />
        </div>

        {/* Informations principales */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Informations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Montant HT</p>
              <p className="text-lg font-semibold text-gray-900">
                {formatEUR(devis.montant_total_ht)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Montant TTC</p>
              <p className="text-lg font-semibold text-gray-900">
                {formatEUR(devis.montant_total_ttc)}
              </p>
            </div>
            {devis.date_creation && (
              <div>
                <p className="text-sm text-gray-600">Date de création</p>
                <p className="text-sm text-gray-900">
                  {new Date(devis.date_creation).toLocaleDateString('fr-FR')}
                </p>
              </div>
            )}
            {devis.date_validite && (
              <div>
                <p className="text-sm text-gray-600">Date de validité</p>
                <p className="text-sm text-gray-900">
                  {new Date(devis.date_validite).toLocaleDateString('fr-FR')}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Section multimédia - DEV-07 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Photos et fiches techniques
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            Ajoutez des photos, fiches techniques ou documents à ce devis. Vous pouvez
            choisir de les rendre visibles ou non pour le client.
          </p>

          <DevisMediaUpload
            pieces={pieces}
            uploading={uploading}
            uploadProgress={uploadProgress}
            error={uploadError}
            onUpload={uploadFiles}
            onRemove={removeFile}
            onToggleVisibility={toggleVisibility}
          />
        </div>

        {/* Lots (si existants) */}
        {devis.lots && devis.lots.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Lots ({devis.lots.length})
            </h2>
            <div className="space-y-2">
              {devis.lots.map((lot) => (
                <div
                  key={lot.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">{lot.titre}</p>
                    <p className="text-xs text-gray-600">
                      {lot.lignes.length} ligne{lot.lignes.length > 1 ? 's' : ''}
                    </p>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">
                    {formatEUR(lot.total_ht)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
