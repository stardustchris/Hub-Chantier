/**
 * Tests pour le service signalements
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as signalementsService from './signalements'
import api from './api'

vi.mock('./api')

describe('signalementsService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('createSignalement', () => {
    it('crée un signalement', async () => {
      const mockSignalement = { id: 1, titre: 'Test' }
      vi.mocked(api.post).mockResolvedValue({ data: mockSignalement })

      const result = await signalementsService.createSignalement({
        chantier_id: 1,
        titre: 'Test',
        description: 'Description',
        priorite: 'haute',
        localisation: 'Zone A',
      })

      expect(api.post).toHaveBeenCalledWith('/api/signalements', {
        chantier_id: 1,
        titre: 'Test',
        description: 'Description',
        priorite: 'haute',
        localisation: 'Zone A',
      })
      expect(result).toEqual(mockSignalement)
    })
  })

  describe('getSignalement', () => {
    it('récupère un signalement par ID', async () => {
      const mockSignalement = { id: 1, titre: 'Test' }
      vi.mocked(api.get).mockResolvedValue({ data: mockSignalement })

      const result = await signalementsService.getSignalement(1)

      expect(api.get).toHaveBeenCalledWith('/api/signalements/1')
      expect(result).toEqual(mockSignalement)
    })
  })

  describe('listSignalementsByChantier', () => {
    it('liste les signalements d\'un chantier', async () => {
      const mockResponse = { items: [], total: 0 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await signalementsService.listSignalementsByChantier(1)

      expect(api.get).toHaveBeenCalledWith('/api/signalements/chantier/1', {
        params: { skip: 0, limit: 100 },
      })
      expect(result).toEqual(mockResponse)
    })

    it('liste les signalements avec filtres', async () => {
      const mockResponse = { items: [{ id: 1 }], total: 1 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      await signalementsService.listSignalementsByChantier(1, 10, 50, 'ouvert', 'haute')

      expect(api.get).toHaveBeenCalledWith('/api/signalements/chantier/1', {
        params: { skip: 10, limit: 50, statut: 'ouvert', priorite: 'haute' },
      })
    })
  })

  describe('searchSignalements', () => {
    it('recherche des signalements', async () => {
      const mockResponse = { items: [], total: 0 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      await signalementsService.searchSignalements({
        query: 'fuite',
        chantier_id: 1,
        statut: 'ouvert',
        priorite: 'critique',
      })

      expect(api.get).toHaveBeenCalledWith('/api/signalements', {
        params: expect.objectContaining({
          query: 'fuite',
          chantier_id: 1,
          statut: 'ouvert',
          priorite: 'critique',
        }),
      })
    })
  })

  describe('updateSignalement', () => {
    it('met à jour un signalement', async () => {
      const mockSignalement = { id: 1, titre: 'Updated' }
      vi.mocked(api.put).mockResolvedValue({ data: mockSignalement })

      const result = await signalementsService.updateSignalement(1, {
        titre: 'Updated',
        priorite: 'moyenne',
      })

      expect(api.put).toHaveBeenCalledWith('/api/signalements/1', {
        titre: 'Updated',
        priorite: 'moyenne',
      })
      expect(result).toEqual(mockSignalement)
    })
  })

  describe('deleteSignalement', () => {
    it('supprime un signalement', async () => {
      vi.mocked(api.delete).mockResolvedValue({})

      await signalementsService.deleteSignalement(1)

      expect(api.delete).toHaveBeenCalledWith('/api/signalements/1')
    })
  })

  describe('assignerSignalement', () => {
    it('assigne un signalement à un utilisateur', async () => {
      const mockSignalement = { id: 1, assigne_a: 2 }
      vi.mocked(api.post).mockResolvedValue({ data: mockSignalement })

      const result = await signalementsService.assignerSignalement(1, 2)

      expect(api.post).toHaveBeenCalledWith('/api/signalements/1/assigner', null, {
        params: { assigne_a: 2 },
      })
      expect(result).toEqual(mockSignalement)
    })
  })

  describe('marquerTraite', () => {
    it('marque un signalement comme traité', async () => {
      const mockSignalement = { id: 1, statut: 'traite' }
      vi.mocked(api.post).mockResolvedValue({ data: mockSignalement })

      const result = await signalementsService.marquerTraite(1, 'Problème résolu')

      expect(api.post).toHaveBeenCalledWith('/api/signalements/1/traiter', {
        commentaire: 'Problème résolu',
      })
      expect(result).toEqual(mockSignalement)
    })
  })

  describe('cloturerSignalement', () => {
    it('clôture un signalement', async () => {
      const mockSignalement = { id: 1, statut: 'cloture' }
      vi.mocked(api.post).mockResolvedValue({ data: mockSignalement })

      const result = await signalementsService.cloturerSignalement(1)

      expect(api.post).toHaveBeenCalledWith('/api/signalements/1/cloturer')
      expect(result).toEqual(mockSignalement)
    })
  })

  describe('reouvrirSignalement', () => {
    it('réouvre un signalement', async () => {
      const mockSignalement = { id: 1, statut: 'ouvert' }
      vi.mocked(api.post).mockResolvedValue({ data: mockSignalement })

      const result = await signalementsService.reouvrirSignalement(1)

      expect(api.post).toHaveBeenCalledWith('/api/signalements/1/reouvrir')
      expect(result).toEqual(mockSignalement)
    })
  })

  describe('getStatistiques', () => {
    it('récupère les statistiques des signalements', async () => {
      const mockStats = { total: 10, ouverts: 5 }
      vi.mocked(api.get).mockResolvedValue({ data: mockStats })

      const result = await signalementsService.getStatistiques(1, '2026-01-01', '2026-01-31')

      expect(api.get).toHaveBeenCalledWith('/api/signalements/stats/global', {
        params: { chantier_id: 1, date_debut: '2026-01-01', date_fin: '2026-01-31' },
      })
      expect(result).toEqual(mockStats)
    })
  })

  describe('getSignalementsEnRetard', () => {
    it('récupère les signalements en retard', async () => {
      const mockResponse = { items: [{ id: 1, est_en_retard: true }], total: 1 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await signalementsService.getSignalementsEnRetard(1)

      expect(api.get).toHaveBeenCalledWith('/api/signalements/alertes/en-retard', {
        params: { skip: 0, limit: 100, chantier_id: 1 },
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('createReponse', () => {
    it('ajoute une réponse à un signalement', async () => {
      const mockReponse = { id: 1, contenu: 'Réponse test' }
      vi.mocked(api.post).mockResolvedValue({ data: mockReponse })

      const result = await signalementsService.createReponse(1, {
        contenu: 'Réponse test',
      })

      expect(api.post).toHaveBeenCalledWith('/api/signalements/1/reponses', {
        contenu: 'Réponse test',
      })
      expect(result).toEqual(mockReponse)
    })
  })

  describe('listReponses', () => {
    it('liste les réponses d\'un signalement', async () => {
      const mockResponse = { items: [], total: 0 }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await signalementsService.listReponses(1)

      expect(api.get).toHaveBeenCalledWith('/api/signalements/1/reponses', {
        params: { skip: 0, limit: 100 },
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('updateReponse', () => {
    it('met à jour une réponse', async () => {
      const mockReponse = { id: 1, contenu: 'Updated' }
      vi.mocked(api.put).mockResolvedValue({ data: mockReponse })

      const result = await signalementsService.updateReponse(1, {
        contenu: 'Updated',
      })

      expect(api.put).toHaveBeenCalledWith('/api/signalements/reponses/1', {
        contenu: 'Updated',
      })
      expect(result).toEqual(mockReponse)
    })
  })

  describe('deleteReponse', () => {
    it('supprime une réponse', async () => {
      vi.mocked(api.delete).mockResolvedValue({})

      await signalementsService.deleteReponse(1)

      expect(api.delete).toHaveBeenCalledWith('/api/signalements/reponses/1')
    })
  })

  // Tests des helpers
  describe('getPrioriteIcon', () => {
    it('retourne l\'icône correcte pour chaque priorité', () => {
      expect(signalementsService.getPrioriteIcon('critique')).toBe('🔴')
      expect(signalementsService.getPrioriteIcon('haute')).toBe('🟠')
      expect(signalementsService.getPrioriteIcon('moyenne')).toBe('🟡')
      expect(signalementsService.getPrioriteIcon('basse')).toBe('🟢')
    })
  })

  describe('getStatutIcon', () => {
    it('retourne l\'icône correcte pour chaque statut', () => {
      expect(signalementsService.getStatutIcon('ouvert')).toBe('⚠️')
      expect(signalementsService.getStatutIcon('en_cours')).toBe('🔄')
      expect(signalementsService.getStatutIcon('traite')).toBe('✅')
      expect(signalementsService.getStatutIcon('cloture')).toBe('✔️')
    })
  })

  describe('formatTempsRestant', () => {
    it('formate le temps restant', () => {
      expect(signalementsService.formatTempsRestant('2h 30m')).toBe('2h 30m')
      expect(signalementsService.formatTempsRestant(null)).toBe('-')
    })
  })

  describe('isSignalementEnAlerte', () => {
    it('détecte les signalements en alerte', () => {
      expect(
        signalementsService.isSignalementEnAlerte({
          est_en_retard: true,
          pourcentage_temps: 30,
        } as signalementsService.Signalement)
      ).toBe(true)

      expect(
        signalementsService.isSignalementEnAlerte({
          est_en_retard: false,
          pourcentage_temps: 60,
        } as signalementsService.Signalement)
      ).toBe(true)

      expect(
        signalementsService.isSignalementEnAlerte({
          est_en_retard: false,
          pourcentage_temps: 40,
        } as signalementsService.Signalement)
      ).toBe(false)
    })
  })
})
