/**
 * API client pour le module Documents (GED)
 */

import api from '../services/api';
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
} from '../types/documents';

// ============ DOSSIERS ============

export const createDossier = async (data: DossierCreateDTO): Promise<Dossier> => {
  const response = await api.post('/documents/dossiers', data);
  return response.data;
};

export const getDossier = async (dossierId: number): Promise<Dossier> => {
  const response = await api.get(`/documents/dossiers/${dossierId}`);
  return response.data;
};

export const listDossiers = async (
  chantierId: number,
  parentId?: number | null
): Promise<Dossier[]> => {
  const params = parentId !== undefined ? { parent_id: parentId } : {};
  const response = await api.get(`/documents/chantiers/${chantierId}/dossiers`, { params });
  return response.data;
};

export const getArborescence = async (chantierId: number): Promise<Arborescence> => {
  const response = await api.get(`/documents/chantiers/${chantierId}/arborescence`);
  return response.data;
};

export const updateDossier = async (
  dossierId: number,
  data: DossierUpdateDTO
): Promise<Dossier> => {
  const response = await api.put(`/documents/dossiers/${dossierId}`, data);
  return response.data;
};

export const deleteDossier = async (dossierId: number, force = false): Promise<void> => {
  await api.delete(`/documents/dossiers/${dossierId}`, { params: { force } });
};

export const initArborescence = async (chantierId: number): Promise<Dossier[]> => {
  const response = await api.post(`/documents/chantiers/${chantierId}/init-arborescence`);
  return response.data;
};

// ============ DOCUMENTS ============

export const uploadDocument = async (
  dossierId: number,
  chantierId: number,
  file: File,
  description?: string,
  niveauAcces?: string
): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);

  const params: Record<string, string | number> = { chantier_id: chantierId };
  if (description) params.description = description;
  if (niveauAcces) params.niveau_acces = niveauAcces;

  const response = await api.post(`/documents/dossiers/${dossierId}/documents`, formData, {
    params,
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const uploadMultipleDocuments = async (
  dossierId: number,
  chantierId: number,
  files: File[],
  onProgress?: (index: number, progress: number) => void
): Promise<Document[]> => {
  const results: Document[] = [];

  for (let i = 0; i < files.length; i++) {
    const doc = await uploadDocument(dossierId, chantierId, files[i]);
    results.push(doc);
    if (onProgress) {
      onProgress(i, ((i + 1) / files.length) * 100);
    }
  }

  return results;
};

export const getDocument = async (documentId: number): Promise<Document> => {
  const response = await api.get(`/documents/documents/${documentId}`);
  return response.data;
};

export const listDocuments = async (
  dossierId: number,
  skip = 0,
  limit = 100
): Promise<DocumentListResponse> => {
  const response = await api.get(`/documents/dossiers/${dossierId}/documents`, {
    params: { skip, limit },
  });
  return response.data;
};

export const searchDocuments = async (
  chantierId: number,
  query?: string,
  typeDocument?: string,
  dossierId?: number,
  skip = 0,
  limit = 100
): Promise<DocumentListResponse> => {
  const params: Record<string, string | number> = { skip, limit };
  if (query) params.query = query;
  if (typeDocument) params.type_document = typeDocument;
  if (dossierId) params.dossier_id = dossierId;

  const response = await api.get(`/documents/chantiers/${chantierId}/documents/search`, {
    params,
  });
  return response.data;
};

export const updateDocument = async (
  documentId: number,
  data: DocumentUpdateDTO
): Promise<Document> => {
  const response = await api.put(`/documents/documents/${documentId}`, data);
  return response.data;
};

export const deleteDocument = async (documentId: number): Promise<void> => {
  await api.delete(`/documents/documents/${documentId}`);
};

export const downloadDocument = async (
  documentId: number
): Promise<{ url: string; filename: string; mime_type: string }> => {
  const response = await api.get(`/documents/documents/${documentId}/download`);
  return response.data;
};

// ============ AUTORISATIONS ============

export const createAutorisation = async (
  data: AutorisationCreateDTO
): Promise<Autorisation> => {
  const response = await api.post('/documents/autorisations', data);
  return response.data;
};

export const listAutorisationsByDossier = async (
  dossierId: number
): Promise<AutorisationListResponse> => {
  const response = await api.get(`/documents/dossiers/${dossierId}/autorisations`);
  return response.data;
};

export const listAutorisationsByDocument = async (
  documentId: number
): Promise<AutorisationListResponse> => {
  const response = await api.get(`/documents/documents/${documentId}/autorisations`);
  return response.data;
};

export const revokeAutorisation = async (autorisationId: number): Promise<void> => {
  await api.delete(`/documents/autorisations/${autorisationId}`);
};

// ============ HELPERS ============

export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} Go`;
};

export const getDocumentIcon = (typeDocument: string): string => {
  const icons: Record<string, string> = {
    pdf: '📄',
    image: '🖼️',
    excel: '📊',
    word: '📝',
    video: '🎬',
    autre: '📁',
  };
  return icons[typeDocument] || '📁';
};
