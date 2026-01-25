/**
 * Tests pour le service documents (GED)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as documentsService from './documents'
import api from './api'

vi.mock('./api')

describe('documentsService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ===== DOSSIERS =====

  describe('createDossier', () => {
    it('crée un nouveau dossier', async () => {
      const mockDossier = { id: 1, nom: 'Plans' }
      vi.mocked(api.post).mockResolvedValue({ data: mockDossier })

      const result = await documentsService.createDossier({
        nom: 'Plans',
        chantier_id: 1,
      })

      expect(api.post).toHaveBeenCalledWith('/api/documents/dossiers', {
        nom: 'Plans',
        chantier_id: 1,
      })
      expect(result).toEqual(mockDossier)
    })
  })

  describe('getDossier', () => {
    it('récupère un dossier par ID', async () => {
      const mockDossier = { id: 1, nom: 'Plans' }
      vi.mocked(api.get).mockResolvedValue({ data: mockDossier })

      const result = await documentsService.getDossier(1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/dossiers/1')
      expect(result).toEqual(mockDossier)
    })
  })

  describe('listDossiers', () => {
    it('liste les dossiers d\'un chantier', async () => {
      const mockDossiers = [{ id: 1, nom: 'Plans' }]
      vi.mocked(api.get).mockResolvedValue({ data: mockDossiers })

      const result = await documentsService.listDossiers(1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/chantiers/1/dossiers', { params: {} })
      expect(result).toEqual(mockDossiers)
    })

    it('liste les dossiers avec parent_id', async () => {
      const mockDossiers = [{ id: 2, nom: 'Sous-dossier', parent_id: 1 }]
      vi.mocked(api.get).mockResolvedValue({ data: mockDossiers })

      const result = await documentsService.listDossiers(1, 1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/chantiers/1/dossiers', {
        params: { parent_id: 1 },
      })
      expect(result).toEqual(mockDossiers)
    })

    it('liste les dossiers racine avec parent_id=null', async () => {
      const mockDossiers = [{ id: 1, nom: 'Plans' }]
      vi.mocked(api.get).mockResolvedValue({ data: mockDossiers })

      const result = await documentsService.listDossiers(1, null)

      expect(api.get).toHaveBeenCalledWith('/api/documents/chantiers/1/dossiers', {
        params: { parent_id: null },
      })
      expect(result).toEqual(mockDossiers)
    })
  })

  describe('getArborescence', () => {
    it('récupère l\'arborescence d\'un chantier', async () => {
      const mockArbo = { chantier_id: 1, dossiers: [] }
      vi.mocked(api.get).mockResolvedValue({ data: mockArbo })

      const result = await documentsService.getArborescence(1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/chantiers/1/arborescence')
      expect(result).toEqual(mockArbo)
    })
  })

  describe('updateDossier', () => {
    it('met à jour un dossier', async () => {
      const mockDossier = { id: 1, nom: 'Plans modifié' }
      vi.mocked(api.put).mockResolvedValue({ data: mockDossier })

      const result = await documentsService.updateDossier(1, { nom: 'Plans modifié' })

      expect(api.put).toHaveBeenCalledWith('/api/documents/dossiers/1', { nom: 'Plans modifié' })
      expect(result).toEqual(mockDossier)
    })
  })

  describe('deleteDossier', () => {
    it('supprime un dossier', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: {} })

      await documentsService.deleteDossier(1)

      expect(api.delete).toHaveBeenCalledWith('/api/documents/dossiers/1', { params: { force: false } })
    })

    it('supprime un dossier avec force=true', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: {} })

      await documentsService.deleteDossier(1, true)

      expect(api.delete).toHaveBeenCalledWith('/api/documents/dossiers/1', { params: { force: true } })
    })
  })

  describe('initArborescence', () => {
    it('initialise l\'arborescence d\'un chantier', async () => {
      const mockDossiers = [{ id: 1, nom: 'Plans' }, { id: 2, nom: 'Photos' }]
      vi.mocked(api.post).mockResolvedValue({ data: mockDossiers })

      const result = await documentsService.initArborescence(1)

      expect(api.post).toHaveBeenCalledWith('/api/documents/chantiers/1/init-arborescence')
      expect(result).toEqual(mockDossiers)
    })
  })

  // ===== DOCUMENTS =====

  describe('uploadDocument', () => {
    it('upload un document', async () => {
      const mockDocument = { id: 1, nom: 'plan.pdf' }
      vi.mocked(api.post).mockResolvedValue({ data: mockDocument })

      const file = new File(['content'], 'plan.pdf', { type: 'application/pdf' })
      const result = await documentsService.uploadDocument(1, 1, file)

      expect(api.post).toHaveBeenCalledWith(
        '/api/documents/dossiers/1/documents',
        expect.any(FormData),
        {
          params: { chantier_id: 1 },
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      )
      expect(result).toEqual(mockDocument)
    })

    it('upload un document avec description et niveau d\'accès', async () => {
      const mockDocument = { id: 1, nom: 'plan.pdf', description: 'Plan RDC' }
      vi.mocked(api.post).mockResolvedValue({ data: mockDocument })

      const file = new File(['content'], 'plan.pdf', { type: 'application/pdf' })
      const result = await documentsService.uploadDocument(1, 1, file, 'Plan RDC', 'conducteur')

      expect(api.post).toHaveBeenCalledWith(
        '/api/documents/dossiers/1/documents',
        expect.any(FormData),
        {
          params: { chantier_id: 1, description: 'Plan RDC', niveau_acces: 'conducteur' },
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      )
      expect(result).toEqual(mockDocument)
    })
  })

  describe('getDocument', () => {
    it('récupère un document par ID', async () => {
      const mockDocument = { id: 1, nom: 'plan.pdf' }
      vi.mocked(api.get).mockResolvedValue({ data: mockDocument })

      const result = await documentsService.getDocument(1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/documents/1')
      expect(result).toEqual(mockDocument)
    })
  })

  describe('listDocuments', () => {
    it('liste les documents d\'un dossier', async () => {
      const mockResponse = { documents: [], total: 0, skip: 0, limit: 100 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await documentsService.listDocuments(1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/dossiers/1/documents', {
        params: { skip: 0, limit: 100 },
      })
      expect(result).toEqual(mockResponse)
    })

    it('liste les documents avec pagination', async () => {
      const mockResponse = { documents: [], total: 50, skip: 10, limit: 20 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await documentsService.listDocuments(1, 10, 20)

      expect(api.get).toHaveBeenCalledWith('/api/documents/dossiers/1/documents', {
        params: { skip: 10, limit: 20 },
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('searchDocuments', () => {
    it('recherche des documents', async () => {
      const mockResponse = { documents: [], total: 0, skip: 0, limit: 100 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await documentsService.searchDocuments(1, 'plan')

      expect(api.get).toHaveBeenCalledWith('/api/documents/chantiers/1/documents/search', {
        params: { skip: 0, limit: 100, query: 'plan' },
      })
      expect(result).toEqual(mockResponse)
    })

    it('recherche des documents avec tous les filtres', async () => {
      const mockResponse = { documents: [], total: 0, skip: 0, limit: 50 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await documentsService.searchDocuments(1, 'plan', 'pdf', 2, 10, 50)

      expect(api.get).toHaveBeenCalledWith('/api/documents/chantiers/1/documents/search', {
        params: { skip: 10, limit: 50, query: 'plan', type_document: 'pdf', dossier_id: 2 },
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('updateDocument', () => {
    it('met à jour un document', async () => {
      const mockDocument = { id: 1, description: 'Nouvelle description' }
      vi.mocked(api.put).mockResolvedValue({ data: mockDocument })

      const result = await documentsService.updateDocument(1, { description: 'Nouvelle description' })

      expect(api.put).toHaveBeenCalledWith('/api/documents/documents/1', { description: 'Nouvelle description' })
      expect(result).toEqual(mockDocument)
    })
  })

  describe('deleteDocument', () => {
    it('supprime un document', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: {} })

      await documentsService.deleteDocument(1)

      expect(api.delete).toHaveBeenCalledWith('/api/documents/documents/1')
    })
  })

  describe('downloadDocument', () => {
    it('télécharge un document', async () => {
      const mockDownload = { url: 'https://...', filename: 'plan.pdf', mime_type: 'application/pdf' }
      vi.mocked(api.get).mockResolvedValue({ data: mockDownload })

      const result = await documentsService.downloadDocument(1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/documents/1/download')
      expect(result).toEqual(mockDownload)
    })
  })

  describe('downloadDocumentsZip', () => {
    it('télécharge plusieurs documents en ZIP', async () => {
      const mockBlob = new Blob(['zip content'], { type: 'application/zip' })
      vi.mocked(api.post).mockResolvedValue({ data: mockBlob })

      const result = await documentsService.downloadDocumentsZip([1, 2, 3])

      expect(api.post).toHaveBeenCalledWith(
        '/api/documents/documents/download-zip',
        { document_ids: [1, 2, 3] },
        { responseType: 'blob' }
      )
      expect(result).toBe(mockBlob)
    })
  })

  describe('getDocumentPreview', () => {
    it('récupère les informations de prévisualisation', async () => {
      const mockPreview = { id: 1, nom: 'plan.pdf', can_preview: true, preview_url: '/preview/1' }
      vi.mocked(api.get).mockResolvedValue({ data: mockPreview })

      const result = await documentsService.getDocumentPreview(1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/documents/1/preview')
      expect(result).toEqual(mockPreview)
    })
  })

  describe('getDocumentPreviewUrl', () => {
    it('retourne l\'URL de prévisualisation', () => {
      const url = documentsService.getDocumentPreviewUrl(123)
      expect(url).toBe('/api/documents/documents/123/preview/content')
    })
  })

  // ===== AUTORISATIONS =====

  describe('createAutorisation', () => {
    it('crée une autorisation', async () => {
      const mockAuth = { id: 1, utilisateur_id: 2, dossier_id: 1 }
      vi.mocked(api.post).mockResolvedValue({ data: mockAuth })

      const result = await documentsService.createAutorisation({
        user_id: 2,
        dossier_id: 1,
        type_autorisation: 'lecture',
      })

      expect(api.post).toHaveBeenCalledWith('/api/documents/autorisations', {
        user_id: 2,
        dossier_id: 1,
        type_autorisation: 'lecture',
      })
      expect(result).toEqual(mockAuth)
    })
  })

  describe('listAutorisationsByDossier', () => {
    it('liste les autorisations d\'un dossier', async () => {
      const mockResponse = { autorisations: [], total: 0 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await documentsService.listAutorisationsByDossier(1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/dossiers/1/autorisations')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('listAutorisationsByDocument', () => {
    it('liste les autorisations d\'un document', async () => {
      const mockResponse = { autorisations: [], total: 0 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await documentsService.listAutorisationsByDocument(1)

      expect(api.get).toHaveBeenCalledWith('/api/documents/documents/1/autorisations')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('revokeAutorisation', () => {
    it('révoque une autorisation', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: {} })

      await documentsService.revokeAutorisation(1)

      expect(api.delete).toHaveBeenCalledWith('/api/documents/autorisations/1')
    })
  })

  // ===== HELPERS =====

  describe('formatFileSize', () => {
    it('formate les octets', () => {
      expect(documentsService.formatFileSize(500)).toBe('500 o')
    })

    it('formate les Ko', () => {
      expect(documentsService.formatFileSize(1500)).toBe('1.5 Ko')
    })

    it('formate les Mo', () => {
      expect(documentsService.formatFileSize(1500000)).toBe('1.4 Mo')
    })

    it('formate les Go', () => {
      expect(documentsService.formatFileSize(1500000000)).toBe('1.40 Go')
    })
  })

  describe('getDocumentIcon', () => {
    it('retourne l\'icône PDF', () => {
      expect(documentsService.getDocumentIcon('pdf')).toBe('📄')
    })

    it('retourne l\'icône image', () => {
      expect(documentsService.getDocumentIcon('image')).toBe('🖼️')
    })

    it('retourne l\'icône Excel', () => {
      expect(documentsService.getDocumentIcon('excel')).toBe('📊')
    })

    it('retourne l\'icône Word', () => {
      expect(documentsService.getDocumentIcon('word')).toBe('📝')
    })

    it('retourne l\'icône vidéo', () => {
      expect(documentsService.getDocumentIcon('video')).toBe('🎬')
    })

    it('retourne l\'icône par défaut', () => {
      expect(documentsService.getDocumentIcon('inconnu')).toBe('📁')
    })
  })
})
