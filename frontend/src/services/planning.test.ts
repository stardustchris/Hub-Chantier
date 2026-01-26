/**
 * Tests pour le service planning
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { planningService } from './planning'
import api from './api'

vi.mock('./api')

describe('planningService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAffectations', () => {
    it('récupère les affectations avec filtres de base', async () => {
      const mockAffectations = [{ id: '1', chantier_id: '1', utilisateur_id: '1' }]
      vi.mocked(api.get).mockResolvedValue({ data: mockAffectations })

      const result = await planningService.getAffectations({
        date_debut: '2026-01-20',
        date_fin: '2026-01-26',
      })

      expect(api.get).toHaveBeenCalledWith('/api/planning/affectations', {
        params: expect.any(URLSearchParams),
      })
      expect(result).toEqual(mockAffectations)
    })

    it('récupère les affectations avec tous les filtres', async () => {
      const mockAffectations = [{ id: '1' }]
      vi.mocked(api.get).mockResolvedValue({ data: mockAffectations })

      const result = await planningService.getAffectations({
        date_debut: '2026-01-20',
        date_fin: '2026-01-26',
        utilisateur_ids: ['1', '2'],
        chantier_ids: ['3', '4'],
        metiers: ['macon', 'electricien'],
      })

      expect(api.get).toHaveBeenCalled()
      expect(result).toEqual(mockAffectations)
    })
  })

  describe('getById', () => {
    it('récupère une affectation par ID', async () => {
      const mockAffectation = { id: '1', chantier_id: '1' }
      vi.mocked(api.get).mockResolvedValue({ data: mockAffectation })

      const result = await planningService.getById('1')

      expect(api.get).toHaveBeenCalledWith('/api/planning/affectations/1')
      expect(result).toEqual(mockAffectation)
    })
  })

  describe('create', () => {
    it('crée une nouvelle affectation', async () => {
      const mockAffectations = [{ id: '1', chantier_id: '1' }]
      vi.mocked(api.post).mockResolvedValue({ data: mockAffectations })

      const data = {
        utilisateur_id: '1',
        chantier_id: '1',
        date: '2026-01-20',
      }
      const result = await planningService.create(data)

      expect(api.post).toHaveBeenCalledWith('/api/planning/affectations', data)
      expect(result).toEqual(mockAffectations)
    })
  })

  describe('update', () => {
    it('met à jour une affectation', async () => {
      const mockAffectation = { id: '1', heure_debut: '08:00' }
      vi.mocked(api.put).mockResolvedValue({ data: mockAffectation })

      const result = await planningService.update('1', { heure_debut: '08:00' })

      expect(api.put).toHaveBeenCalledWith('/api/planning/affectations/1', { heure_debut: '08:00' })
      expect(result).toEqual(mockAffectation)
    })
  })

  describe('delete', () => {
    it('supprime une affectation', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: {} })

      await planningService.delete('1')

      expect(api.delete).toHaveBeenCalledWith('/api/planning/affectations/1')
    })
  })

  describe('move', () => {
    it('déplace une affectation vers une nouvelle date', async () => {
      const mockAffectation = { id: '1', date: '2026-01-21' }
      vi.mocked(api.put).mockResolvedValue({ data: mockAffectation })

      const result = await planningService.move('1', '2026-01-21')

      expect(api.put).toHaveBeenCalledWith('/api/planning/affectations/1', { date: '2026-01-21' })
      expect(result).toEqual(mockAffectation)
    })

    it('déplace une affectation vers un nouvel utilisateur', async () => {
      const mockAffectation = { id: '1', date: '2026-01-21', utilisateur_id: 2 }
      vi.mocked(api.put).mockResolvedValue({ data: mockAffectation })

      const result = await planningService.move('1', '2026-01-21', '2')

      // Le service convertit l'utilisateur_id en number pour le backend
      expect(api.put).toHaveBeenCalledWith('/api/planning/affectations/1', {
        date: '2026-01-21',
        utilisateur_id: 2,
      })
      expect(result).toEqual(mockAffectation)
    })
  })

  describe('duplicate', () => {
    it('duplique les affectations d\'une période', async () => {
      const mockAffectations = [{ id: '2' }, { id: '3' }]
      vi.mocked(api.post).mockResolvedValue({ data: mockAffectations })

      const data = {
        utilisateur_id: '1',
        source_date_debut: '2026-01-20',
        source_date_fin: '2026-01-24',
        target_date_debut: '2026-01-27',
      }
      const result = await planningService.duplicate(data)

      expect(api.post).toHaveBeenCalledWith('/api/planning/affectations/duplicate', data)
      expect(result).toEqual(mockAffectations)
    })
  })

  describe('getNonPlanifies', () => {
    it('récupère les utilisateurs non planifiés', async () => {
      const mockResponse = {
        utilisateur_ids: ['1', '2'],
        date_debut: '2026-01-20',
        date_fin: '2026-01-26',
        count: 2,
      }
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse })

      const result = await planningService.getNonPlanifies('2026-01-20', '2026-01-26')

      expect(api.get).toHaveBeenCalledWith('/api/planning/non-planifies', {
        params: { date_debut: '2026-01-20', date_fin: '2026-01-26' },
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getByChantier', () => {
    it('récupère les affectations d\'un chantier', async () => {
      const mockAffectations = [{ id: '1', chantier_id: '1' }]
      vi.mocked(api.get).mockResolvedValue({ data: mockAffectations })

      const result = await planningService.getByChantier('1', '2026-01-20', '2026-01-26')

      expect(api.get).toHaveBeenCalledWith('/api/planning/chantiers/1/affectations', {
        params: { date_debut: '2026-01-20', date_fin: '2026-01-26' },
      })
      expect(result).toEqual(mockAffectations)
    })
  })

  describe('getByUtilisateur', () => {
    it('récupère les affectations d\'un utilisateur', async () => {
      const mockAffectations = [{ id: '1', utilisateur_id: '1' }]
      vi.mocked(api.get).mockResolvedValue({ data: mockAffectations })

      const result = await planningService.getByUtilisateur('1', '2026-01-20', '2026-01-26')

      expect(api.get).toHaveBeenCalledWith('/api/planning/utilisateurs/1/affectations', {
        params: { date_debut: '2026-01-20', date_fin: '2026-01-26' },
      })
      expect(result).toEqual(mockAffectations)
    })
  })
})
