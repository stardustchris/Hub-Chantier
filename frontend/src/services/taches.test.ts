/**
 * Tests pour le service taches
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { tachesService } from './taches'
import api from './api'

vi.mock('./api')

describe('tachesService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('listByChantier', () => {
    it('récupère les taches d\'un chantier avec les paramètres par défaut', async () => {
      const mockResponse = {
        data: {
          items: [{ id: 1, titre: 'Tache 1' }],
          page: 1,
          pages: 1,
          total: 1,
        },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await tachesService.listByChantier(1)

      expect(api.get).toHaveBeenCalledWith('/api/taches/chantier/1', {
        params: {
          page: 1,
          size: 50,
          query: undefined,
          statut: undefined,
          include_sous_taches: true,
        },
      })
      expect(result).toEqual(mockResponse.data)
    })

    it('récupère les taches avec des paramètres personnalisés', async () => {
      const mockResponse = { data: { items: [], page: 2, pages: 3, total: 100 } }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await tachesService.listByChantier(1, {
        page: 2,
        size: 20,
        query: 'fondation',
        statut: 'en_cours',
        include_sous_taches: false,
      })

      expect(api.get).toHaveBeenCalledWith('/api/taches/chantier/1', {
        params: {
          page: 2,
          size: 20,
          query: 'fondation',
          statut: 'en_cours',
          include_sous_taches: false,
        },
      })
    })
  })

  describe('getById', () => {
    it('récupère une tache par ID', async () => {
      const mockTache = { id: 1, titre: 'Tache test' }
      vi.mocked(api.get).mockResolvedValue({ data: mockTache })

      const result = await tachesService.getById(1)

      expect(api.get).toHaveBeenCalledWith('/api/taches/1', {
        params: { include_sous_taches: true },
      })
      expect(result).toEqual(mockTache)
    })

    it('récupère une tache sans sous-taches', async () => {
      const mockTache = { id: 1, titre: 'Tache test' }
      vi.mocked(api.get).mockResolvedValue({ data: mockTache })

      await tachesService.getById(1, false)

      expect(api.get).toHaveBeenCalledWith('/api/taches/1', {
        params: { include_sous_taches: false },
      })
    })
  })

  describe('create', () => {
    it('crée une nouvelle tache', async () => {
      const newTache = {
        titre: 'Nouvelle tache',
        chantier_id: 1,
        description: 'Description',
      }
      const mockResponse = { id: 1, ...newTache }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const result = await tachesService.create(newTache)

      expect(api.post).toHaveBeenCalledWith('/api/taches', newTache)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('update', () => {
    it('met à jour une tache existante', async () => {
      const updates = { titre: 'Tache modifiée' }
      const mockResponse = { id: 1, ...updates }
      vi.mocked(api.put).mockResolvedValue({ data: mockResponse })

      const result = await tachesService.update(1, updates)

      expect(api.put).toHaveBeenCalledWith('/api/taches/1', updates)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('delete', () => {
    it('supprime une tache', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: null })

      await tachesService.delete(1)

      expect(api.delete).toHaveBeenCalledWith('/api/taches/1')
    })
  })

  describe('complete', () => {
    it('marque une tache comme terminée', async () => {
      const mockTache = { id: 1, statut: 'termine' }
      vi.mocked(api.post).mockResolvedValue({ data: mockTache })

      const result = await tachesService.complete(1, true)

      expect(api.post).toHaveBeenCalledWith('/api/taches/1/complete', { terminer: true })
      expect(result).toEqual(mockTache)
    })

    it('rouvre une tache terminée', async () => {
      const mockTache = { id: 1, statut: 'en_cours' }
      vi.mocked(api.post).mockResolvedValue({ data: mockTache })

      const result = await tachesService.complete(1, false)

      expect(api.post).toHaveBeenCalledWith('/api/taches/1/complete', { terminer: false })
      expect(result).toEqual(mockTache)
    })
  })

  describe('getStats', () => {
    it('récupère les statistiques d\'un chantier', async () => {
      const mockStats = { total: 10, terminees: 5, en_cours: 3, a_faire: 2 }
      vi.mocked(api.get).mockResolvedValue({ data: mockStats })

      const result = await tachesService.getStats(1)

      expect(api.get).toHaveBeenCalledWith('/api/taches/chantier/1/stats')
      expect(result).toEqual(mockStats)
    })
  })

  describe('reorder', () => {
    it('réordonne les taches', async () => {
      const ordres = [
        { tache_id: 3, ordre: 0 },
        { tache_id: 1, ordre: 1 },
        { tache_id: 2, ordre: 2 },
      ]
      const mockTaches = [{ id: 3 }, { id: 1 }, { id: 2 }]
      vi.mocked(api.post).mockResolvedValue({ data: mockTaches })

      const result = await tachesService.reorder(ordres)

      expect(api.post).toHaveBeenCalledWith('/api/taches/reorder', ordres)
      expect(result).toEqual(mockTaches)
    })
  })

  describe('listTemplates', () => {
    it('récupère les templates de taches', async () => {
      const mockResponse = {
        data: {
          items: [{ id: 1, nom: 'Template fondations' }],
          page: 1,
          pages: 1,
          total: 1,
          categories: ['gros_oeuvre'],
        },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await tachesService.listTemplates()

      expect(api.get).toHaveBeenCalledWith('/api/templates-taches', {
        params: {
          page: 1,
          size: 50,
          query: undefined,
          categorie: undefined,
          active_only: true,
        },
      })
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('createTemplate', () => {
    it('crée un nouveau template', async () => {
      const newTemplate = {
        nom: 'Nouveau template',
        taches: [{ titre: 'Tache 1' }],
      }
      const mockResponse = { id: 1, ...newTemplate }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const result = await tachesService.createTemplate(newTemplate)

      expect(api.post).toHaveBeenCalledWith('/api/templates-taches', newTemplate)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('importTemplate', () => {
    it('importe un template dans un chantier', async () => {
      const mockTaches = [{ id: 1, titre: 'Tache importée' }]
      vi.mocked(api.post).mockResolvedValue({ data: mockTaches })

      const result = await tachesService.importTemplate(5, 3)

      expect(api.post).toHaveBeenCalledWith('/api/templates-taches/import', {
        template_id: 5,
        chantier_id: 3,
      })
      expect(result).toEqual(mockTaches)
    })
  })

  describe('listFeuillesByTache', () => {
    it('récupère les feuilles d\'une tache', async () => {
      const mockResponse = {
        data: {
          items: [{ id: 1, tache_id: 1, heures: 8 }],
          page: 1,
          pages: 1,
          total: 1,
          total_heures: 8,
          total_quantite: 1,
        },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await tachesService.listFeuillesByTache(1)

      expect(api.get).toHaveBeenCalledWith('/api/feuilles-taches/tache/1', {
        params: { page: 1, size: 50 },
      })
      expect(result).toEqual(mockResponse.data)
    })

    it('récupère les feuilles avec pagination', async () => {
      const mockResponse = { data: { items: [], page: 2, pages: 3, total: 100 } }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await tachesService.listFeuillesByTache(1, { page: 2, size: 20 })

      expect(api.get).toHaveBeenCalledWith('/api/feuilles-taches/tache/1', {
        params: { page: 2, size: 20 },
      })
    })
  })

  describe('listFeuillesEnAttente', () => {
    it('récupère les feuilles en attente de validation', async () => {
      const mockResponse = {
        data: {
          items: [{ id: 1, statut: 'en_attente' }],
          page: 1,
          pages: 1,
          total: 1,
          total_heures: 8,
          total_quantite: 1,
        },
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await tachesService.listFeuillesEnAttente()

      expect(api.get).toHaveBeenCalledWith('/api/feuilles-taches/en-attente', {
        params: { chantier_id: undefined, page: 1, size: 50 },
      })
      expect(result).toEqual(mockResponse.data)
    })

    it('récupère les feuilles en attente d\'un chantier spécifique', async () => {
      const mockResponse = { data: { items: [], page: 1, pages: 1, total: 0 } }
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      await tachesService.listFeuillesEnAttente(5, { page: 2, size: 10 })

      expect(api.get).toHaveBeenCalledWith('/api/feuilles-taches/en-attente', {
        params: { chantier_id: 5, page: 2, size: 10 },
      })
    })
  })

  describe('createFeuille', () => {
    it('crée une feuille de tache', async () => {
      const newFeuille = {
        tache_id: 1,
        utilisateur_id: 1,
        date: '2024-01-15',
        heures: 8,
      }
      const mockResponse = { id: 1, ...newFeuille }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const result = await tachesService.createFeuille(newFeuille as any)

      expect(api.post).toHaveBeenCalledWith('/api/feuilles-taches', newFeuille)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('validateFeuille', () => {
    it('valide une feuille de tache', async () => {
      const mockFeuille = { id: 1, statut: 'validee' }
      vi.mocked(api.post).mockResolvedValue({ data: mockFeuille })

      const result = await tachesService.validateFeuille(1, true)

      expect(api.post).toHaveBeenCalledWith('/api/feuilles-taches/1/validate', {
        valider: true,
        motif_rejet: undefined,
      })
      expect(result).toEqual(mockFeuille)
    })

    it('rejette une feuille avec motif', async () => {
      const mockFeuille = { id: 1, statut: 'rejetee' }
      vi.mocked(api.post).mockResolvedValue({ data: mockFeuille })

      const result = await tachesService.validateFeuille(1, false, 'Heures incorrectes')

      expect(api.post).toHaveBeenCalledWith('/api/feuilles-taches/1/validate', {
        valider: false,
        motif_rejet: 'Heures incorrectes',
      })
      expect(result).toEqual(mockFeuille)
    })
  })

  describe('exportPDF', () => {
    it('génère un export PDF', async () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' })
      vi.mocked(api.get).mockResolvedValue({ data: mockBlob })

      const result = await tachesService.exportPDF(1)

      expect(api.get).toHaveBeenCalledWith('/api/taches/chantier/1/export-pdf', {
        responseType: 'blob',
      })
      expect(result).toEqual(mockBlob)
    })
  })

  describe('downloadPDF', () => {
    it('télécharge le PDF', () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' })
      const mockCreateObjectURL = vi.fn().mockReturnValue('blob:url')
      const mockRevokeObjectURL = vi.fn()
      global.URL.createObjectURL = mockCreateObjectURL
      global.URL.revokeObjectURL = mockRevokeObjectURL

      const mockLink = {
        href: '',
        setAttribute: vi.fn(),
        click: vi.fn(),
        remove: vi.fn(),
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)

      tachesService.downloadPDF(mockBlob, 'taches-chantier-1.pdf')

      expect(mockCreateObjectURL).toHaveBeenCalledWith(mockBlob)
      expect(mockLink.setAttribute).toHaveBeenCalledWith('download', 'taches-chantier-1.pdf')
      expect(mockLink.click).toHaveBeenCalled()
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('blob:url')
    })
  })
})
