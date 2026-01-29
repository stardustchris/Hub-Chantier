import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { logger } from '../services/logger'
import { chantiersService } from '../services/chantiers'
import * as documentsApi from '../services/documents'
import type { Chantier } from '../types'
import type { DossierTree, Document, Arborescence } from '../types/documents'

export function useDocuments() {
  const { user } = useAuth()
  const { addToast } = useToast()
  const [searchParams, setSearchParams] = useSearchParams()

  // State
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [selectedChantier, setSelectedChantier] = useState<Chantier | null>(null)
  const [arborescence, setArborescence] = useState<Arborescence | null>(null)
  const [selectedDossier, setSelectedDossier] = useState<DossierTree | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [searchQuery, setSearchQuery] = useState('')

  const [isLoadingChantiers, setIsLoadingChantiers] = useState(true)
  const [isLoadingArborescence, setIsLoadingArborescence] = useState(false)
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const [showDossierModal, setShowDossierModal] = useState(false)
  const [editingDossier, setEditingDossier] = useState<DossierTree | null>(null)
  const [parentDossierId, setParentDossierId] = useState<number | null>(null)
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null)

  const isAdmin = user?.role === 'admin'
  const isConducteur = user?.role === 'conducteur'
  const canManage = isAdmin || isConducteur

  // Load chantiers on mount
  const loadChantiers = useCallback(async () => {
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
  }, [addToast])

  const loadArborescence = useCallback(async (chantierId: string) => {
    try {
      setIsLoadingArborescence(true)
      const data = await documentsApi.getArborescence(parseInt(chantierId))
      setArborescence(data)
      setSelectedDossier(null)
      setDocuments([])
    } catch (error: unknown) {
      const axiosError = error as { response?: { status?: number } }
      if (axiosError.response?.status === 404) {
        setArborescence({ chantier_id: parseInt(chantierId), dossiers: [], total_documents: 0, total_taille: 0 })
      } else {
        logger.error('Error loading arborescence', error, { context: 'DocumentsPage' })
        addToast({ message: 'Erreur lors du chargement des dossiers', type: 'error' })
      }
    } finally {
      setIsLoadingArborescence(false)
    }
  }, [addToast])

  const loadDocuments = useCallback(async (dossierId: number) => {
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
  }, [addToast])

  useEffect(() => {
    loadChantiers()
  }, [loadChantiers])

  useEffect(() => {
    if (selectedChantier) {
      loadArborescence(selectedChantier.id)
      setSearchParams({ chantier: selectedChantier.id })
    }
  }, [selectedChantier, loadArborescence, setSearchParams])

  useEffect(() => {
    if (selectedDossier) {
      loadDocuments(selectedDossier.id)
    } else {
      setDocuments([])
    }
  }, [selectedDossier, loadDocuments])

  useEffect(() => {
    const chantierId = searchParams.get('chantier')
    if (chantierId && chantiers.length > 0 && !selectedChantier) {
      const chantier = chantiers.find((c) => c.id === chantierId)
      if (chantier) {
        setSelectedChantier(chantier)
      }
    }
  }, [chantiers, searchParams, selectedChantier])

  const handleInitArborescence = useCallback(async () => {
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
  }, [selectedChantier, loadArborescence, addToast])

  const handleSelectDossier = useCallback((dossier: DossierTree) => {
    setSelectedDossier(dossier)
  }, [])

  const handleCreateDossier = useCallback((parentId: number | null) => {
    setParentDossierId(parentId)
    setEditingDossier(null)
    setShowDossierModal(true)
  }, [])

  const handleEditDossier = useCallback((dossier: DossierTree) => {
    setEditingDossier(dossier)
    setParentDossierId(dossier.parent_id)
    setShowDossierModal(true)
  }, [])

  const handleDeleteDossier = useCallback(async (dossier: DossierTree) => {
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
  }, [selectedChantier, selectedDossier, loadArborescence, addToast])

  const handleDossierSaved = useCallback(async (data: Parameters<typeof documentsApi.createDossier>[0] | Parameters<typeof documentsApi.updateDossier>[1]) => {
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
  }, [editingDossier, selectedChantier, loadArborescence, addToast])

  const handleUploadFiles = useCallback(async (files: File[]) => {
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
  }, [selectedDossier, selectedChantier, loadDocuments, addToast])

  const handleDownloadDocument = useCallback(async (doc: Document) => {
    try {
      const blob = await documentsApi.downloadDocument(doc.id)

      // Créer un lien temporaire pour forcer le téléchargement avec le nom original
      const url = window.URL.createObjectURL(blob)
      const link = window.document.createElement('a')
      link.href = url
      link.download = doc.nom_original || doc.nom
      window.document.body.appendChild(link)
      link.click()
      window.document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      logger.error('Error downloading document', error, { context: 'DocumentsPage' })
      addToast({ message: 'Erreur lors du telechargement', type: 'error' })
    }
  }, [addToast])

  const handleDeleteDocument = useCallback(async (document: Document) => {
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
  }, [selectedDossier, loadDocuments, addToast])

  const handleSearchDocuments = useCallback(async () => {
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
  }, [selectedChantier, searchQuery, addToast])

  const closeDossierModal = useCallback(() => {
    setShowDossierModal(false)
  }, [])

  const closePreviewModal = useCallback(() => {
    setPreviewDocument(null)
  }, [])

  const selectChantier = useCallback((chantier: Chantier | null) => {
    setSelectedChantier(chantier)
  }, [])

  const refreshArborescence = useCallback(() => {
    if (selectedChantier) {
      loadArborescence(selectedChantier.id)
    }
  }, [selectedChantier, loadArborescence])

  return {
    // State
    user,
    chantiers,
    selectedChantier,
    arborescence,
    selectedDossier,
    documents,
    searchQuery,
    isLoadingChantiers,
    isLoadingArborescence,
    isLoadingDocuments,
    isUploading,
    showDossierModal,
    editingDossier,
    parentDossierId,
    previewDocument,
    canManage,

    // Setters
    setSearchQuery,
    setPreviewDocument,

    // Actions
    selectChantier,
    refreshArborescence,
    handleInitArborescence,
    handleSelectDossier,
    handleCreateDossier,
    handleEditDossier,
    handleDeleteDossier,
    handleDossierSaved,
    handleUploadFiles,
    handleDownloadDocument,
    handleDeleteDocument,
    handleSearchDocuments,
    closeDossierModal,
    closePreviewModal,
  }
}

export { documentsApi }
