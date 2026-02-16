import Layout from '../components/Layout'
import { DossierTree, DocumentList, FileUploadZone, DossierModal, DocumentPreviewModal } from '../components/documents'
import { useDocuments, documentsApi } from '../hooks/useDocuments'
import { FolderOpen, Search, Loader2, FileText, ChevronDown, RefreshCw } from 'lucide-react'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export default function DocumentsPage() {
  useDocumentTitle('Documents')
  const docs = useDocuments()

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
            <p className="text-gray-500">Gestion electronique des documents (GED)</p>
          </div>

          {/* Chantier selector */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <select
                value={docs.selectedChantier?.id || ''}
                onChange={(e) => {
                  const chantier = docs.chantiers.find((c) => c.id === e.target.value)
                  docs.selectChantier(chantier || null)
                }}
                className="input pr-10 min-w-[250px]"
                disabled={docs.isLoadingChantiers}
              >
                <option value="">Selectionner un chantier...</option>
                {docs.chantiers.map((chantier) => (
                  <option key={chantier.id} value={chantier.id}>
                    {chantier.code} - {chantier.nom}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600 pointer-events-none" />
            </div>

            {docs.selectedChantier && (
              <button onClick={docs.refreshArborescence} className="btn btn-outline p-2" title="Rafraichir">
                <RefreshCw className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        {docs.isLoadingChantiers ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : !docs.selectedChantier ? (
          <div className="card text-center py-12">
            <FolderOpen className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Selectionnez un chantier</h3>
            <p className="text-gray-500">Choisissez un chantier pour acceder a ses documents</p>
          </div>
        ) : docs.isLoadingArborescence ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : docs.arborescence?.dossiers.length === 0 ? (
          <div className="card text-center py-12">
            <FolderOpen className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun dossier</h3>
            <p className="text-gray-500 mb-4">Ce chantier n'a pas encore d'arborescence de documents</p>
            {docs.canManage && (
              <button onClick={docs.handleInitArborescence} className="btn btn-primary">
                Initialiser l'arborescence standard
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar - Dossiers */}
            <div className="lg:col-span-1">
              <DossierTree
                dossiers={docs.arborescence?.dossiers || []}
                selectedDossierId={docs.selectedDossier?.id || null}
                onSelectDossier={docs.handleSelectDossier}
                onCreateDossier={docs.canManage ? docs.handleCreateDossier : undefined}
                onEditDossier={docs.canManage ? docs.handleEditDossier : undefined}
                onDeleteDossier={docs.canManage ? docs.handleDeleteDossier : undefined}
                userRole={docs.user?.role}
              />

              {docs.arborescence && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500">
                    <div className="flex justify-between">
                      <span>Total documents:</span>
                      <span className="font-medium">{docs.arborescence.total_documents}</span>
                    </div>
                    <div className="flex justify-between mt-1">
                      <span>Taille totale:</span>
                      <span className="font-medium">{documentsApi.formatFileSize(docs.arborescence.total_taille)}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Main content - Documents */}
            <div className="lg:col-span-3">
              {/* Search bar */}
              <div className="card mb-4">
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
                    <input
                      type="text"
                      placeholder="Rechercher un document..."
                      value={docs.searchQuery}
                      onChange={(e) => docs.setSearchQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && docs.handleSearchDocuments()}
                      className="input pl-10 w-full"
                    />
                  </div>
                  <button onClick={docs.handleSearchDocuments} className="btn btn-primary" disabled={!docs.searchQuery.trim()}>
                    Rechercher
                  </button>
                </div>
              </div>

              {/* Upload zone */}
              {docs.selectedDossier && docs.canManage && (
                <div className="mb-4">
                  <FileUploadZone onFilesSelected={docs.handleUploadFiles} uploading={docs.isUploading} />
                </div>
              )}

              {/* Documents list */}
              {!docs.selectedDossier && docs.documents.length === 0 ? (
                <div className="card text-center py-12">
                  <FileText className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-500">Selectionnez un dossier pour voir ses documents</p>
                </div>
              ) : docs.isLoadingDocuments ? (
                <div className="card flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
                </div>
              ) : (
                <DocumentList
                  documents={docs.documents}
                  onDocumentPreview={(doc) => docs.setPreviewDocument(doc)}
                  onDocumentDownload={docs.handleDownloadDocument}
                  onDocumentDelete={docs.canManage ? docs.handleDeleteDocument : undefined}
                />
              )}
            </div>
          </div>
        )}

        {/* Modals */}
        {docs.showDossierModal && docs.selectedChantier && (
          <DossierModal
            isOpen={docs.showDossierModal}
            chantierId={parseInt(docs.selectedChantier.id)}
            parentId={docs.parentDossierId}
            dossier={docs.editingDossier}
            onClose={docs.closeDossierModal}
            onSubmit={docs.handleDossierSaved}
          />
        )}

        {docs.previewDocument && (
          <DocumentPreviewModal
            document={docs.previewDocument}
            isOpen={!!docs.previewDocument}
            onClose={docs.closePreviewModal}
            onDownload={docs.handleDownloadDocument}
          />
        )}
      </div>
    </Layout>
  )
}
