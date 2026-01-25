/**
 * Tests pour le service formulaires
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { formulairesService } from './formulaires'
import api from './api'

vi.mock('./api')

describe('formulairesService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ===== TEMPLATES =====

  describe('listTemplates', () => {
    it('liste les templates sans filtres', async () => {
      const mockResponse = { templates: [], total: 0, skip: 0, limit: 20 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await formulairesService.listTemplates()

      expect(api.get).toHaveBeenCalledWith('/api/templates-formulaires?')
      expect(result).toEqual(mockResponse)
    })

    it('liste les templates avec filtres', async () => {
      const mockResponse = { templates: [{ id: 1 }], total: 1, skip: 0, limit: 10 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await formulairesService.listTemplates({
        query: 'test',
        categorie: 'securite',
        active_only: true,
        skip: 0,
        limit: 10,
      })

      expect(api.get).toHaveBeenCalledWith(
        '/api/templates-formulaires?query=test&categorie=securite&active_only=true&skip=0&limit=10'
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getTemplate', () => {
    it('récupère un template par ID', async () => {
      const mockTemplate = { id: 1, nom: 'Template test' }
      vi.mocked(api.get).mockResolvedValue({ data: mockTemplate })

      const result = await formulairesService.getTemplate(1)

      expect(api.get).toHaveBeenCalledWith('/api/templates-formulaires/1')
      expect(result).toEqual(mockTemplate)
    })
  })

  describe('createTemplate', () => {
    it('crée un nouveau template', async () => {
      const mockTemplate = { id: 1, nom: 'Nouveau template' }
      vi.mocked(api.post).mockResolvedValue({ data: mockTemplate })

      const data = { nom: 'Nouveau template', categorie: 'securite' as const, champs: [] }
      const result = await formulairesService.createTemplate(data)

      expect(api.post).toHaveBeenCalledWith('/api/templates-formulaires', data)
      expect(result).toEqual(mockTemplate)
    })
  })

  describe('updateTemplate', () => {
    it('met à jour un template', async () => {
      const mockTemplate = { id: 1, nom: 'Template modifié' }
      vi.mocked(api.put).mockResolvedValue({ data: mockTemplate })

      const result = await formulairesService.updateTemplate(1, { nom: 'Template modifié' })

      expect(api.put).toHaveBeenCalledWith('/api/templates-formulaires/1', { nom: 'Template modifié' })
      expect(result).toEqual(mockTemplate)
    })
  })

  describe('deleteTemplate', () => {
    it('supprime un template', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: {} })

      await formulairesService.deleteTemplate(1)

      expect(api.delete).toHaveBeenCalledWith('/api/templates-formulaires/1')
    })
  })

  // ===== FORMULAIRES REMPLIS =====

  describe('listFormulaires', () => {
    it('liste les formulaires sans filtres', async () => {
      const mockResponse = { formulaires: [], total: 0, skip: 0, limit: 100 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await formulairesService.listFormulaires()

      expect(api.get).toHaveBeenCalledWith('/api/formulaires?')
      expect(result).toEqual(mockResponse)
    })

    it('liste les formulaires avec tous les filtres', async () => {
      const mockResponse = { formulaires: [{ id: 1 }], total: 1, skip: 0, limit: 10 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await formulairesService.listFormulaires({
        chantier_id: 1,
        template_id: 2,
        user_id: 3,
        statut: 'soumis',
        date_debut: '2026-01-01',
        date_fin: '2026-01-31',
        skip: 0,
        limit: 10,
      })

      expect(api.get).toHaveBeenCalledWith(
        '/api/formulaires?chantier_id=1&template_id=2&user_id=3&statut=soumis&date_debut=2026-01-01&date_fin=2026-01-31&skip=0&limit=10'
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('listByChantier', () => {
    it('liste les formulaires d\'un chantier', async () => {
      const mockResponse = { formulaires: [], total: 0, skip: 0, limit: 100 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await formulairesService.listByChantier(1)

      expect(api.get).toHaveBeenCalledWith('/api/formulaires/chantier/1?skip=0&limit=100')
      expect(result).toEqual(mockResponse)
    })

    it('liste les formulaires avec pagination', async () => {
      const mockResponse = { formulaires: [], total: 50, skip: 10, limit: 20 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await formulairesService.listByChantier(1, 10, 20)

      expect(api.get).toHaveBeenCalledWith('/api/formulaires/chantier/1?skip=10&limit=20')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getFormulaire', () => {
    it('récupère un formulaire par ID', async () => {
      const mockFormulaire = { id: 1, template_id: 1, chantier_id: 1 }
      vi.mocked(api.get).mockResolvedValue({ data: mockFormulaire })

      const result = await formulairesService.getFormulaire(1)

      expect(api.get).toHaveBeenCalledWith('/api/formulaires/1')
      expect(result).toEqual(mockFormulaire)
    })
  })

  describe('createFormulaire', () => {
    it('crée un nouveau formulaire', async () => {
      const mockFormulaire = { id: 1, template_id: 1, chantier_id: 1 }
      vi.mocked(api.post).mockResolvedValue({ data: mockFormulaire })

      const data = { template_id: 1, chantier_id: 1 }
      const result = await formulairesService.createFormulaire(data)

      expect(api.post).toHaveBeenCalledWith('/api/formulaires', data)
      expect(result).toEqual(mockFormulaire)
    })
  })

  describe('updateFormulaire', () => {
    it('met à jour un formulaire', async () => {
      const mockFormulaire = { id: 1, champs: [{ nom: 'field1', valeur: 'value1', type_champ: 'text' }] }
      vi.mocked(api.put).mockResolvedValue({ data: mockFormulaire })

      const updateData = {
        champs: [{ nom: 'field1', valeur: 'value1', type_champ: 'text' as const }],
      }
      const result = await formulairesService.updateFormulaire(1, updateData)

      expect(api.put).toHaveBeenCalledWith('/api/formulaires/1', updateData)
      expect(result).toEqual(mockFormulaire)
    })
  })

  // ===== PHOTOS =====

  describe('addPhoto', () => {
    it('ajoute une photo sans coordonnées', async () => {
      const mockFormulaire = { id: 1, photos: [{ url: 'photo.jpg' }] }
      vi.mocked(api.post).mockResolvedValue({ data: mockFormulaire })

      const result = await formulairesService.addPhoto(1, 'photo.jpg', 'photo.jpg', 'photo_field')

      expect(api.post).toHaveBeenCalledWith('/api/formulaires/1/photos', {
        url: 'photo.jpg',
        nom_fichier: 'photo.jpg',
        champ_nom: 'photo_field',
        latitude: undefined,
        longitude: undefined,
      })
      expect(result).toEqual(mockFormulaire)
    })

    it('ajoute une photo avec coordonnées GPS', async () => {
      const mockFormulaire = { id: 1, photos: [] }
      vi.mocked(api.post).mockResolvedValue({ data: mockFormulaire })

      const result = await formulairesService.addPhoto(1, 'photo.jpg', 'photo.jpg', 'photo_field', 48.8566, 2.3522)

      expect(api.post).toHaveBeenCalledWith('/api/formulaires/1/photos', {
        url: 'photo.jpg',
        nom_fichier: 'photo.jpg',
        champ_nom: 'photo_field',
        latitude: 48.8566,
        longitude: 2.3522,
      })
      expect(result).toEqual(mockFormulaire)
    })
  })

  // ===== SIGNATURE =====

  describe('addSignature', () => {
    it('ajoute une signature', async () => {
      const mockFormulaire = { id: 1, signature_url: 'sig.png' }
      vi.mocked(api.post).mockResolvedValue({ data: mockFormulaire })

      const result = await formulairesService.addSignature(1, 'sig.png', 'John Doe')

      expect(api.post).toHaveBeenCalledWith('/api/formulaires/1/signature', {
        signature_url: 'sig.png',
        signature_nom: 'John Doe',
      })
      expect(result).toEqual(mockFormulaire)
    })
  })

  // ===== SOUMISSION ET VALIDATION =====

  describe('submitFormulaire', () => {
    it('soumet un formulaire sans signature', async () => {
      const mockFormulaire = { id: 1, statut: 'soumis' }
      vi.mocked(api.post).mockResolvedValue({ data: mockFormulaire })

      const result = await formulairesService.submitFormulaire(1)

      expect(api.post).toHaveBeenCalledWith('/api/formulaires/1/submit', {
        signature_url: undefined,
        signature_nom: undefined,
      })
      expect(result).toEqual(mockFormulaire)
    })

    it('soumet un formulaire avec signature', async () => {
      const mockFormulaire = { id: 1, statut: 'soumis' }
      vi.mocked(api.post).mockResolvedValue({ data: mockFormulaire })

      const result = await formulairesService.submitFormulaire(1, 'sig.png', 'John Doe')

      expect(api.post).toHaveBeenCalledWith('/api/formulaires/1/submit', {
        signature_url: 'sig.png',
        signature_nom: 'John Doe',
      })
      expect(result).toEqual(mockFormulaire)
    })
  })

  describe('validateFormulaire', () => {
    it('valide un formulaire', async () => {
      const mockFormulaire = { id: 1, statut: 'valide' }
      vi.mocked(api.post).mockResolvedValue({ data: mockFormulaire })

      const result = await formulairesService.validateFormulaire(1)

      expect(api.post).toHaveBeenCalledWith('/api/formulaires/1/validate')
      expect(result).toEqual(mockFormulaire)
    })
  })

  // ===== HISTORIQUE =====

  describe('getHistory', () => {
    it('récupère l\'historique des versions', async () => {
      const mockHistory = { formulaire_id: 1, versions: [{ version: 1 }] }
      vi.mocked(api.get).mockResolvedValue({ data: mockHistory })

      const result = await formulairesService.getHistory(1)

      expect(api.get).toHaveBeenCalledWith('/api/formulaires/1/history')
      expect(result).toEqual(mockHistory)
    })
  })

  // ===== EXPORT PDF =====

  describe('exportPDF', () => {
    it('exporte un formulaire en PDF', async () => {
      const mockExport = { formulaire_id: 1, filename: 'form.pdf', content_type: 'application/pdf', content_base64: 'base64...' }
      vi.mocked(api.get).mockResolvedValue({ data: mockExport })

      const result = await formulairesService.exportPDF(1)

      expect(api.get).toHaveBeenCalledWith('/api/formulaires/1/export')
      expect(result).toEqual(mockExport)
    })
  })
})
