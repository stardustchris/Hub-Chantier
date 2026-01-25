/**
 * Tests pour le service pointages
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { pointagesService } from './pointages'
import api from './api'

vi.mock('./api')

describe('pointagesService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('create', () => {
    it('crée un pointage', async () => {
      const mockPointage = { id: 1, heures: 8 }
      vi.mocked(api.post).mockResolvedValue({ data: mockPointage })

      const result = await pointagesService.create(
        { utilisateur_id: 1, chantier_id: 1, date_pointage: '2026-01-25', heures_normales: '8' },
        123
      )

      expect(api.post).toHaveBeenCalledWith(
        '/api/pointages',
        { utilisateur_id: 1, chantier_id: 1, date_pointage: '2026-01-25', heures_normales: '8' },
        { params: { current_user_id: 123 } }
      )
      expect(result).toEqual(mockPointage)
    })
  })

  describe('list', () => {
    it('liste les pointages sans filtres', async () => {
      const mockResponse = { items: [], page: 1, pages: 1, total: 0, size: 20 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await pointagesService.list()

      expect(api.get).toHaveBeenCalledWith('/api/pointages', { params: expect.any(URLSearchParams) })
      expect(result).toEqual(mockResponse)
    })

    it('liste les pointages avec filtres', async () => {
      const mockResponse = { items: [{ id: 1 }], page: 1, pages: 1, total: 1, size: 20 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      await pointagesService.list({
        utilisateur_id: 1,
        chantier_id: 2,
        date_debut: '2026-01-01',
        date_fin: '2026-01-31',
        statut: 'brouillon',
      })

      expect(api.get).toHaveBeenCalled()
    })
  })

  describe('getById', () => {
    it('récupère un pointage par ID', async () => {
      const mockPointage = { id: 1, heures: 8 }
      vi.mocked(api.get).mockResolvedValue({ data: mockPointage })

      const result = await pointagesService.getById(1)

      expect(api.get).toHaveBeenCalledWith('/api/pointages/1')
      expect(result).toEqual(mockPointage)
    })
  })

  describe('update', () => {
    it('met à jour un pointage', async () => {
      const mockPointage = { id: 1, heures: 9 }
      vi.mocked(api.put).mockResolvedValue({ data: mockPointage })

      const result = await pointagesService.update(1, { heures_normales: '9' }, 123)

      expect(api.put).toHaveBeenCalledWith(
        '/api/pointages/1',
        { heures_normales: '9' },
        { params: { current_user_id: 123 } }
      )
      expect(result).toEqual(mockPointage)
    })
  })

  describe('delete', () => {
    it('supprime un pointage', async () => {
      vi.mocked(api.delete).mockResolvedValue({})

      await pointagesService.delete(1, 123)

      expect(api.delete).toHaveBeenCalledWith('/api/pointages/1', {
        params: { current_user_id: 123 },
      })
    })
  })

  describe('sign', () => {
    it('signe un pointage', async () => {
      const mockPointage = { id: 1, signature: 'data:...' }
      vi.mocked(api.post).mockResolvedValue({ data: mockPointage })

      const result = await pointagesService.sign(1, 'data:image/png;base64,abc')

      expect(api.post).toHaveBeenCalledWith('/api/pointages/1/sign', {
        signature: 'data:image/png;base64,abc',
      })
      expect(result).toEqual(mockPointage)
    })
  })

  describe('submit', () => {
    it('soumet un pointage', async () => {
      const mockPointage = { id: 1, statut: 'soumis' }
      vi.mocked(api.post).mockResolvedValue({ data: mockPointage })

      const result = await pointagesService.submit(1)

      expect(api.post).toHaveBeenCalledWith('/api/pointages/1/submit')
      expect(result).toEqual(mockPointage)
    })
  })

  describe('validate', () => {
    it('valide un pointage', async () => {
      const mockPointage = { id: 1, statut: 'valide' }
      vi.mocked(api.post).mockResolvedValue({ data: mockPointage })

      const result = await pointagesService.validate(1, 456)

      expect(api.post).toHaveBeenCalledWith('/api/pointages/1/validate', null, {
        params: { validateur_id: 456 },
      })
      expect(result).toEqual(mockPointage)
    })
  })

  describe('reject', () => {
    it('rejette un pointage avec motif', async () => {
      const mockPointage = { id: 1, statut: 'rejete' }
      vi.mocked(api.post).mockResolvedValue({ data: mockPointage })

      const result = await pointagesService.reject(1, 'Heures incorrectes', 456)

      expect(api.post).toHaveBeenCalledWith(
        '/api/pointages/1/reject',
        { motif: 'Heures incorrectes' },
        { params: { validateur_id: 456 } }
      )
      expect(result).toEqual(mockPointage)
    })
  })

  describe('listFeuilles', () => {
    it('liste les feuilles d\'heures', async () => {
      const mockResponse = { items: [], page: 1, pages: 1, total: 0, size: 20 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      await pointagesService.listFeuilles({ utilisateur_id: 1, annee: 2026 })

      expect(api.get).toHaveBeenCalledWith('/api/pointages/feuilles', {
        params: expect.any(URLSearchParams),
      })
    })
  })

  describe('getFeuilleById', () => {
    it('récupère une feuille par ID', async () => {
      const mockFeuille = { id: 1, utilisateur_id: 1 }
      vi.mocked(api.get).mockResolvedValue({ data: mockFeuille })

      const result = await pointagesService.getFeuilleById(1)

      expect(api.get).toHaveBeenCalledWith('/api/pointages/feuilles/1')
      expect(result).toEqual(mockFeuille)
    })
  })

  describe('getFeuilleUtilisateurSemaine', () => {
    it('récupère la feuille d\'un utilisateur pour une semaine', async () => {
      const mockFeuille = { id: 1, utilisateur_id: 1 }
      vi.mocked(api.get).mockResolvedValue({ data: mockFeuille })

      const result = await pointagesService.getFeuilleUtilisateurSemaine(1, '2026-01-20')

      expect(api.get).toHaveBeenCalledWith('/api/pointages/feuilles/utilisateur/1/semaine', {
        params: { semaine_debut: '2026-01-20' },
      })
      expect(result).toEqual(mockFeuille)
    })
  })

  describe('getNavigation', () => {
    it('récupère la navigation par semaine', async () => {
      const mockNav = { prev: '2026-01-13', next: '2026-01-27' }
      vi.mocked(api.get).mockResolvedValue({ data: mockNav })

      const result = await pointagesService.getNavigation('2026-01-20')

      expect(api.get).toHaveBeenCalledWith('/api/pointages/navigation', {
        params: { semaine_debut: '2026-01-20' },
      })
      expect(result).toEqual(mockNav)
    })
  })

  describe('getVueChantiers', () => {
    it('récupère la vue par chantiers', async () => {
      const mockVue = [{ chantier_id: 1, heures: 40 }]
      vi.mocked(api.get).mockResolvedValue({ data: mockVue })

      const result = await pointagesService.getVueChantiers('2026-01-20', [1, 2])

      expect(api.get).toHaveBeenCalledWith('/api/pointages/vues/chantiers', {
        params: expect.any(URLSearchParams),
      })
      expect(result).toEqual(mockVue)
    })
  })

  describe('getVueCompagnons', () => {
    it('récupère la vue par compagnons', async () => {
      const mockVue = [{ utilisateur_id: 1, heures: 35 }]
      vi.mocked(api.get).mockResolvedValue({ data: mockVue })

      const result = await pointagesService.getVueCompagnons('2026-01-20')

      expect(api.get).toHaveBeenCalledWith('/api/pointages/vues/compagnons', {
        params: expect.any(URLSearchParams),
      })
      expect(result).toEqual(mockVue)
    })
  })

  describe('getJaugeAvancement', () => {
    it('récupère la jauge d\'avancement', async () => {
      const mockJauge = { pourcentage: 80, heures_faites: 28 }
      vi.mocked(api.get).mockResolvedValue({ data: mockJauge })

      const result = await pointagesService.getJaugeAvancement(1, '2026-01-20', 35)

      expect(api.get).toHaveBeenCalledWith('/api/pointages/stats/jauge-avancement/1', {
        params: { semaine_debut: '2026-01-20', heures_planifiees: 35 },
      })
      expect(result).toEqual(mockJauge)
    })
  })

  describe('export', () => {
    it('exporte les feuilles d\'heures', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/pdf' })
      vi.mocked(api.post).mockResolvedValue({ data: mockBlob })

      const exportData = {
        format_export: 'pdf' as const,
        date_debut: '2026-01-20',
        date_fin: '2026-01-26',
        utilisateur_ids: [1],
      }
      const result = await pointagesService.export(exportData, 123)

      expect(api.post).toHaveBeenCalledWith(
        '/api/pointages/export',
        exportData,
        { params: { current_user_id: 123 }, responseType: 'blob' }
      )
      expect(result).toBe(mockBlob)
    })
  })

  describe('bulkCreateFromPlanning', () => {
    it('crée des pointages en masse depuis le planning', async () => {
      const mockPointages = [{ id: 1 }, { id: 2 }]
      vi.mocked(api.post).mockResolvedValue({ data: mockPointages })

      const data = {
        utilisateur_id: 1,
        semaine_debut: '2026-01-20',
        affectations: [
          { affectation_id: 1, chantier_id: 1, date_affectation: '2026-01-20', heures_prevues: '8' },
        ],
      }

      const result = await pointagesService.bulkCreateFromPlanning(data, 123)

      expect(api.post).toHaveBeenCalledWith('/api/pointages/bulk-from-planning', data, {
        params: { current_user_id: 123 },
      })
      expect(result).toEqual(mockPointages)
    })
  })
})
