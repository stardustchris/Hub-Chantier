/**
 * API client pour le module Documents (GED)
 * Fusionné depuis /api/documents.ts
 */

import api from './api'
import type {
  Dossier,
  Document,
  Autorisation,
  Arborescence,
  DocumentListResponse,
  AutorisationListResponse,
  DossierCreateDTO,
  DossierUpdateDTO,
  DocumentUpdateDTO,
  AutorisationCreateDTO,
} from '../types/documents'

// ============ DOSSIERS ============

export const createDossier = async (data: DossierCreateDTO): Promise<Dossier> => {
  const response = await api.post('/api/documents/dossiers', data)
  return response.data
}

export const getDossier = async (dossierId: number): Promise<Dossier> => {
  const response = await api.get(`/api/documents/dossiers/${dossierId}`)
  return response.data
}

export const listDossiers = async (
  chantierId: number,
  parentId?: number | null
): Promise<Dossier[]> => {
  const params = parentId !== undefined ? { parent_id: parentId } : {}
  const response = await api.get(`/api/documents/chantiers/${chantierId}/dossiers`, { params })
  return response.data
}

export const getArborescence = async (chantierId: number): Promise<Arborescence> => {
  const response = await api.get(`/api/documents/chantiers/${chantierId}/arborescence`)
  return response.data
}

export const updateDossier = async (
  dossierId: number,
  data: DossierUpdateDTO
): Promise<Dossier> => {
  const response = await api.put(`/api/documents/dossiers/${dossierId}`, data)
  return response.data
}

export const deleteDossier = async (dossierId: number, force = false): Promise<void> => {
  await api.delete(`/api/documents/dossiers/${dossierId}`, { params: { force } })
}

export const initArborescence = async (chantierId: number): Promise<Dossier[]> => {
  const response = await api.post(`/api/documents/chantiers/${chantierId}/init-arborescence`)
  return response.data
}

// ============ DOCUMENTS ============

export const uploadDocument = async (
  dossierId: number,
  chantierId: number,
  file: File,
  description?: string,
  niveauAcces?: string
): Promise<Document> => {
  const formData = new FormData()
  formData.append('file', file)

  const params: Record<string, string | number> = { chantier_id: chantierId }
  if (description) params.description = description
  if (niveauAcces) params.niveau_acces = niveauAcces

  const response = await api.post(`/api/documents/dossiers/${dossierId}/documents`, formData, {
    params,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const uploadMultipleDocuments = async (
  dossierId: number,
  chantierId: number,
  files: File[],
  onProgress?: (index: number, progress: number) => void
): Promise<Document[]> => {
  const results: Document[] = []

  for (let i = 0; i < files.length; i++) {
    const doc = await uploadDocument(dossierId, chantierId, files[i])
    results.push(doc)
    if (onProgress) {
      onProgress(i, ((i + 1) / files.length) * 100)
    }
  }

  return results
}

export const getDocument = async (documentId: number): Promise<Document> => {
  const response = await api.get(`/api/documents/documents/${documentId}`)
  return response.data
}

export const listDocuments = async (
  dossierId: number,
  skip = 0,
  limit = 100
): Promise<DocumentListResponse> => {
  const response = await api.get(`/api/documents/dossiers/${dossierId}/documents`, {
    params: { skip, limit },
  })
  return response.data
}

export const searchDocuments = async (
  chantierId: number,
  query?: string,
  typeDocument?: string,
  dossierId?: number,
  skip = 0,
  limit = 100
): Promise<DocumentListResponse> => {
  const params: Record<string, string | number> = { skip, limit }
  if (query) params.query = query
  if (typeDocument) params.type_document = typeDocument
  if (dossierId) params.dossier_id = dossierId

  const response = await api.get(`/api/documents/chantiers/${chantierId}/documents/search`, {
    params,
  })
  return response.data
}

export const updateDocument = async (
  documentId: number,
  data: DocumentUpdateDTO
): Promise<Document> => {
  const response = await api.put(`/api/documents/documents/${documentId}`, data)
  return response.data
}

export const deleteDocument = async (documentId: number): Promise<void> => {
  await api.delete(`/api/documents/documents/${documentId}`)
}

export const downloadDocument = async (
  documentId: number
): Promise<{ url: string; filename: string; mime_type: string }> => {
  const response = await api.get(`/api/documents/${documentId}/download`)
  return response.data
}

/**
 * Télécharge plusieurs documents en archive ZIP (GED-16)
 */
export const downloadDocumentsZip = async (documentIds: number[]): Promise<Blob> => {
  const response = await api.post(
    '/api/documents/download-zip',
    { document_ids: documentIds },
    { responseType: 'blob' }
  )
  return response.data
}

/**
 * Télécharge et sauvegarde un ZIP de documents
 */
export const downloadAndSaveZip = async (
  documentIds: number[],
  filename = 'documents.zip'
): Promise<void> => {
  const blob = await downloadDocumentsZip(documentIds)
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

/**
 * Interface pour les informations de prévisualisation (GED-17)
 */
export interface DocumentPreview {
  id: number
  nom: string
  type_document: string
  mime_type: string
  taille: number
  can_preview: boolean
  preview_url: string | null
}

/**
 * Obtient les informations de prévisualisation d'un document (GED-17)
 */
export const getDocumentPreview = async (documentId: number): Promise<DocumentPreview> => {
  const response = await api.get(`/api/documents/documents/${documentId}/preview`)
  return response.data
}

/**
 * Obtient l'URL de prévisualisation directe d'un document
 */
export const getDocumentPreviewUrl = (documentId: number): string => {
  return `/api/documents/documents/${documentId}/preview/content`
}

// ============ AUTORISATIONS ============

export const createAutorisation = async (
  data: AutorisationCreateDTO
): Promise<Autorisation> => {
  const response = await api.post('/api/documents/autorisations', data)
  return response.data
}

export const listAutorisationsByDossier = async (
  dossierId: number
): Promise<AutorisationListResponse> => {
  const response = await api.get(`/api/documents/dossiers/${dossierId}/autorisations`)
  return response.data
}

export const listAutorisationsByDocument = async (
  documentId: number
): Promise<AutorisationListResponse> => {
  const response = await api.get(`/api/documents/documents/${documentId}/autorisations`)
  return response.data
}

export const revokeAutorisation = async (autorisationId: number): Promise<void> => {
  await api.delete(`/api/documents/autorisations/${autorisationId}`)
}

// ============ HELPERS ============

export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} o`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} Go`
}

export const getDocumentIcon = (typeDocument: string): string => {
  const icons: Record<string, string> = {
    pdf: '📄',
    image: '🖼️',
    excel: '📊',
    word: '📝',
    video: '🎬',
    autre: '📁',
  }
  return icons[typeDocument] || '📁'
}
