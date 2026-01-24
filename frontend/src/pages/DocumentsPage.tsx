import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import Layout from '../components/Layout'
import { DossierTree, DocumentList, FileUploadZone, DossierModal, DocumentPreviewModal } from '../components/documents'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { logger } from '../services/logger'
import { chantiersService } from '../services/chantiers'
import * as documentsApi from '../services/documents'
import type { Chantier } from '../types'
import type { DossierTree as DossierTreeType, Document, Arborescence } from '../types/documents'
import {
  FolderOpen,
  Search,
  Loader2,
  FileText,
  ChevronDown,
  RefreshCw,
} from 'lucide-react'

export default function DocumentsPage() {
  const { user } = useAuth()
  const { addToast } = useToast()
  const [searchParams, setSearchParams] = useSearchParams()

  // State
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [selectedChantier, setSelectedChantier] = useState<Chantier | null>(null)
  const [arborescence, setArborescence] = useState<Arborescence | null>(null)
  const [selectedDossier, setSelectedDossier] = useState<DossierTreeType | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [searchQuery, setSearchQuery] = useState('')

  const [isLoadingChantiers, setIsLoadingChantiers] = useState(true)
  const [isLoadingArborescence, setIsLoadingArborescence] = useState(false)
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const [showDossierModal, setShowDossierModal] = useState(false)
  const [editingDossier, setEditingDossier] = useState<DossierTreeType | null>(null)
  const [parentDossierId, setParentDossierId] = useState<number | null>(null)
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null)

  const isAdmin = user?.role === 'admin'
  const isConducteur = user?.role === 'conducteur'
  const canManage = isAdmin || isConducteur

  // Load chantiers on mount
  useEffect(() => {
    loadChantiers()
  }, [])

  // Load arborescence when chantier changes
  useEffect(() => {
    if (selectedChantier) {
      loadArborescence(selectedChantier.id)
      setSearchParams({ chantier: selectedChantier.id })
    }
  }, [selectedChantier])

  // Load documents when dossier changes
  useEffect(() => {
    if (selectedDossier) {
      loadDocuments(selectedDossier.id)
    } else {
      setDocuments([])
    }
  }, [selectedDossier])

  // Restore chantier from URL
  useEffect(() => {
    const chantierId = searchParams.get('chantier')
    if (chantierId && chantiers.length > 0 && !selectedChantier) {
      const chantier = chantiers.find((c) => c.id === chantierId)
      if (chantier) {
        setSelectedChantier(chantier)
      }
    }
  }, [chantiers, searchParams])

  const loadChantiers = async () => {
    try {
      setIsLoadingChantiers(true)
      const response = await chantiersService.list({ size: 100 })
      setChantiers(response.items)
    } catch (error) {
      logger.error('Error loading chantiers', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors du chargement des chantiers', type: 'error' })
    } finally {
      setIsLoadingChantiers(false)
    }
  }

  const loadArborescence = async (chantierId: string) => {
    try {
      setIsLoadingArborescence(true)
      const data = await documentsApi.getArborescence(parseInt(chantierId))
      setArborescence(data)
      setSelectedDossier(null)
      setDocuments([])
    } catch (error: any) {
      // Si pas d'arborescence, proposer d'en creer une
      if (error.response?.status === 404) {
        setArborescence({ chantier_id: parseInt(chantierId), dossiers: [], total_documents: 0, total_taille: 0 })
      } else {
        logger.error('Error loading arborescence', error, { context: 'DocumentsPage' })
        addToast({ message: 'Erreur lors du chargement des dossiers', type: 'error' })
      }
    } finally {
      setIsLoadingArborescence(false)
    }
  }

  const loadDocuments = async (dossierId: number) => {
    try {
      setIsLoadingDocuments(true)
      const response = await documentsApi.listDocuments(dossierId)
      setDocuments(response.documents)
    } catch (error) {
      logger.error('Error loading documents', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors du chargement des documents', type: 'error' })
    } finally {
      setIsLoadingDocuments(false)
    }
  }

  const handleInitArborescence = async () => {
    if (!selectedChantier) return

    try {
      setIsLoadingArborescence(true)
      await documentsApi.initArborescence(parseInt(selectedChantier.id))
      await loadArborescence(selectedChantier.id)
      addToast({ message: 'Arborescence initialisee', type: 'success' })
    } catch (error) {
      logger.error('Error initializing arborescence', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors de l\'initialisation', type: 'error' })
    } finally {
      setIsLoadingArborescence(false)
    }
  }

  const handleSelectDossier = (dossier: DossierTreeType) => {
    setSelectedDossier(dossier)
  }

  const handleCreateDossier = (parentId: number | null) => {
    setParentDossierId(parentId)
    setEditingDossier(null)
    setShowDossierModal(true)
  }

  const handleEditDossier = (dossier: DossierTreeType) => {
    setEditingDossier(dossier)
    setParentDossierId(dossier.parent_id)
    setShowDossierModal(true)
  }

  const handleDeleteDossier = async (dossier: DossierTreeType) => {
    if (!confirm(`Supprimer le dossier "${dossier.nom}" ?`)) return

    try {
      await documentsApi.deleteDossier(dossier.id)
      if (selectedChantier) {
        await loadArborescence(selectedChantier.id)
      }
      if (selectedDossier?.id === dossier.id) {
        setSelectedDossier(null)
      }
      addToast({ message: 'Dossier supprime', type: 'success' })
    } catch (error) {
      logger.error('Error deleting dossier', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors de la suppression', type: 'error' })
    }
  }

  const handleDossierSaved = async (data: Parameters<typeof documentsApi.createDossier>[0] | Parameters<typeof documentsApi.updateDossier>[1]) => {
    try {
      if (editingDossier) {
        await documentsApi.updateDossier(editingDossier.id, data as Parameters<typeof documentsApi.updateDossier>[1])
        addToast({ message: 'Dossier modifie', type: 'success' })
      } else {
        await documentsApi.createDossier(data as Parameters<typeof documentsApi.createDossier>[0])
        addToast({ message: 'Dossier cree', type: 'success' })
      }
      setShowDossierModal(false)
      if (selectedChantier) {
        await loadArborescence(selectedChantier.id)
      }
    } catch (error) {
      logger.error('Error saving dossier', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors de l\'enregistrement', type: 'error' })
    }
  }

  const handleUploadFiles = async (files: File[]) => {
    if (!selectedDossier || !selectedChantier) {
      addToast({ message: 'Selectionnez un dossier', type: 'warning' })
      return
    }

    try {
      setIsUploading(true)
      await documentsApi.uploadMultipleDocuments(
        selectedDossier.id,
        parseInt(selectedChantier.id),
        files
      )
      await loadDocuments(selectedDossier.id)
      addToast({ message: `${files.length} document(s) telecharge(s)`, type: 'success' })
    } catch (error) {
      logger.error('Error uploading files', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors du telechargement', type: 'error' })
    } finally {
      setIsUploading(false)
    }
  }

  const handleDownloadDocument = async (document: Document) => {
    try {
      const { url } = await documentsApi.downloadDocument(document.id)
      window.open(url, '_blank')
    } catch (error) {
      logger.error('Error downloading document', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors du telechargement', type: 'error' })
    }
  }

  const handleDeleteDocument = async (document: Document) => {
    if (!confirm(`Supprimer "${document.nom}" ?`)) return

    try {
      await documentsApi.deleteDocument(document.id)
      if (selectedDossier) {
        await loadDocuments(selectedDossier.id)
      }
      addToast({ message: 'Document supprime', type: 'success' })
    } catch (error) {
      logger.error('Error deleting document', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors de la suppression', type: 'error' })
    }
  }

  const handleSearchDocuments = async () => {
    if (!selectedChantier || !searchQuery.trim()) return

    try {
      setIsLoadingDocuments(true)
      const response = await documentsApi.searchDocuments(
        parseInt(selectedChantier.id),
        searchQuery
      )
      setDocuments(response.documents)
      setSelectedDossier(null)
    } catch (error) {
      logger.error('Error searching documents', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors de la recherche', type: 'error' })
    } finally {
      setIsLoadingDocuments(false)
    }
  }

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
                value={selectedChantier?.id || ''}
                onChange={(e) => {
                  const chantier = chantiers.find((c) => c.id === e.target.value)
                  setSelectedChantier(chantier || null)
                }}
                className="input pr-10 min-w-[250px]"
                disabled={isLoadingChantiers}
              >
                <option value="">Selectionner un chantier...</option>
                {chantiers.map((chantier) => (
                  <option key={chantier.id} value={chantier.id}>
                    {chantier.code} - {chantier.nom}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>

            {selectedChantier && (
              <button
                onClick={() => loadArborescence(selectedChantier.id)}
                className="btn btn-outline p-2"
                title="Rafraichir"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        {isLoadingChantiers ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : !selectedChantier ? (
          <div className="card text-center py-12">
            <FolderOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Selectionnez un chantier
            </h3>
            <p className="text-gray-500">
              Choisissez un chantier pour acceder a ses documents
            </p>
          </div>
        ) : isLoadingArborescence ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : arborescence?.dossiers.length === 0 ? (
          <div className="card text-center py-12">
            <FolderOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Aucun dossier
            </h3>
            <p className="text-gray-500 mb-4">
              Ce chantier n'a pas encore d'arborescence de documents
            </p>
            {canManage && (
              <button
                onClick={handleInitArborescence}
                className="btn btn-primary"
              >
                Initialiser l'arborescence standard
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar - Dossiers */}
            <div className="lg:col-span-1">
              <DossierTree
                dossiers={arborescence?.dossiers || []}
                selectedDossierId={selectedDossier?.id || null}
                onSelectDossier={handleSelectDossier}
                onCreateDossier={canManage ? handleCreateDossier : undefined}
                onEditDossier={canManage ? handleEditDossier : undefined}
                onDeleteDossier={canManage ? handleDeleteDossier : undefined}
                userRole={user?.role}
              />

              {/* Stats */}
              {arborescence && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500">
                    <div className="flex justify-between">
                      <span>Total documents:</span>
                      <span className="font-medium">{arborescence.total_documents}</span>
                    </div>
                    <div className="flex justify-between mt-1">
                      <span>Taille totale:</span>
                      <span className="font-medium">
                        {documentsApi.formatFileSize(arborescence.total_taille)}
                      </span>
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
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Rechercher un document..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSearchDocuments()}
                      className="input pl-10 w-full"
                    />
                  </div>
                  <button
                    onClick={handleSearchDocuments}
                    className="btn btn-primary"
                    disabled={!searchQuery.trim()}
                  >
                    Rechercher
                  </button>
                </div>
              </div>

              {/* Upload zone */}
              {selectedDossier && canManage && (
                <div className="mb-4">
                  <FileUploadZone
                    onFilesSelected={handleUploadFiles}
                    uploading={isUploading}
                  />
                </div>
              )}

              {/* Documents list */}
              {!selectedDossier && documents.length === 0 ? (
                <div className="card text-center py-12">
                  <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">
                    Selectionnez un dossier pour voir ses documents
                  </p>
                </div>
              ) : isLoadingDocuments ? (
                <div className="card flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
                </div>
              ) : (
                <DocumentList
                  documents={documents}
                  onDocumentPreview={(doc) => setPreviewDocument(doc)}
                  onDocumentDownload={handleDownloadDocument}
                  onDocumentDelete={canManage ? handleDeleteDocument : undefined}
                />
              )}
            </div>
          </div>
        )}

        {/* Modals */}
        {showDossierModal && selectedChantier && (
          <DossierModal
            isOpen={showDossierModal}
            chantierId={parseInt(selectedChantier.id)}
            parentId={parentDossierId}
            dossier={editingDossier}
            onClose={() => setShowDossierModal(false)}
            onSubmit={handleDossierSaved}
          />
        )}

        {previewDocument && (
          <DocumentPreviewModal
            document={previewDocument}
            isOpen={!!previewDocument}
            onClose={() => setPreviewDocument(null)}
            onDownload={handleDownloadDocument}
          />
        )}
      </div>
    </Layout>
  )
}
