/**
 * Tests pour l'API Logistique
 * Gestion du materiel et reservations
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  createRessource,
  listRessources,
  getRessource,
  updateRessource,
  deleteRessource,
  getPlanningRessource,
  getHistoriqueRessource,
  createReservation,
  getReservation,
  updateReservation,
  listReservationsEnAttente,
  validerReservation,
  refuserReservation,
  annulerReservation,
  formatPlageHoraire,
  getLundiSemaine,
  getJoursSemaine,
  formatDateISO,
  plagesHorairesSeChevauchent,
} from './logistique'
import type { CategorieRessource } from '../types/logistique'

// Mock de l'API
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

import api from '../services/api'

const mockRessource = {
  id: 1,
  nom: 'Camion Benne',
  type_ressource: 'vehicule',
  description: 'Camion pour transport',
  disponible: true,
  heure_debut_defaut: '07:00:00',
  heure_fin_defaut: '17:00:00',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
}

const mockReservation = {
  id: 1,
  ressource_id: 1,
  chantier_id: 1,
  utilisateur_id: 1,
  date_reservation: '2024-01-15',
  heure_debut: '08:00',
  heure_fin: '12:00',
  statut: 'en_attente',
  commentaire: 'Test',
  created_at: '2024-01-10',
  updated_at: '2024-01-10',
}

describe('API Logistique', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Ressources', () => {
    it('createRessource appelle POST /logistique/ressources', async () => {
      vi.mocked(api.post).mockResolvedValue({ data: mockRessource })

      const data = { nom: 'Camion Benne', type_ressource: 'vehicule' }
      const result = await createRessource(data as any)

      expect(api.post).toHaveBeenCalledWith('/api/logistique/ressources', data)
      expect(result).toEqual(mockRessource)
    })

    it('listRessources appelle GET avec filtres', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { ressources: [mockRessource], total: 1 },
      })

      const filters = { categorie: 'vehicule' as CategorieRessource, actif_seulement: true, limit: 10, offset: 0 }
      await listRessources(filters)

      expect(api.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/logistique/ressources?')
      )
      expect(api.get).toHaveBeenCalledWith(
        expect.stringContaining('categorie=vehicule')
      )
      expect(api.get).toHaveBeenCalledWith(
        expect.stringContaining('actif_seulement=true')
      )
    })

    it('listRessources fonctionne sans filtres', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { ressources: [mockRessource], total: 1 },
      })

      await listRessources()

      expect(api.get).toHaveBeenCalledWith('/api/logistique/ressources?')
    })

    it('getRessource appelle GET /logistique/ressources/:id', async () => {
      vi.mocked(api.get).mockResolvedValue({ data: mockRessource })

      const result = await getRessource(1)

      expect(api.get).toHaveBeenCalledWith('/api/logistique/ressources/1')
      expect(result).toEqual(mockRessource)
    })

    it('updateRessource appelle PUT /logistique/ressources/:id', async () => {
      vi.mocked(api.put).mockResolvedValue({ data: mockRessource })

      const data = { nom: 'Camion Benne Modifie' }
      const result = await updateRessource(1, data)

      expect(api.put).toHaveBeenCalledWith('/api/logistique/ressources/1', data)
      expect(result).toEqual(mockRessource)
    })

    it('deleteRessource appelle DELETE /logistique/ressources/:id', async () => {
      vi.mocked(api.delete).mockResolvedValue({})

      await deleteRessource(1)

      expect(api.delete).toHaveBeenCalledWith('/api/logistique/ressources/1')
    })

    it('getPlanningRessource appelle GET avec dates', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { ressource_id: 1, jours: [] },
      })

      await getPlanningRessource(1, '2024-01-15', '2024-01-21')

      expect(api.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/logistique/ressources/1/planning?')
      )
      expect(api.get).toHaveBeenCalledWith(
        expect.stringContaining('date_debut=2024-01-15')
      )
      expect(api.get).toHaveBeenCalledWith(
        expect.stringContaining('date_fin=2024-01-21')
      )
    })

    it('getPlanningRessource fonctionne sans date_fin', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { ressource_id: 1, jours: [] },
      })

      await getPlanningRessource(1, '2024-01-15')

      expect(api.get).toHaveBeenCalledWith(
        '/api/logistique/ressources/1/planning?date_debut=2024-01-15'
      )
    })

    it('getHistoriqueRessource appelle GET avec pagination', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { reservations: [], total: 0 },
      })

      await getHistoriqueRessource(1, 50, 10)

      expect(api.get).toHaveBeenCalledWith(
        '/api/logistique/ressources/1/historique?limit=50&offset=10'
      )
    })
  })

  describe('Reservations', () => {
    it('createReservation appelle POST /logistique/reservations', async () => {
      vi.mocked(api.post).mockResolvedValue({ data: mockReservation })

      const data = {
        ressource_id: 1,
        chantier_id: 1,
        date_reservation: '2024-01-15',
        heure_debut: '08:00',
        heure_fin: '12:00',
      }
      const result = await createReservation(data as any)

      expect(api.post).toHaveBeenCalledWith('/api/logistique/reservations', data)
      expect(result).toEqual(mockReservation)
    })

    it('getReservation appelle GET /logistique/reservations/:id', async () => {
      vi.mocked(api.get).mockResolvedValue({ data: mockReservation })

      const result = await getReservation(1)

      expect(api.get).toHaveBeenCalledWith('/api/logistique/reservations/1')
      expect(result).toEqual(mockReservation)
    })

    it('updateReservation appelle PUT /logistique/reservations/:id', async () => {
      vi.mocked(api.put).mockResolvedValue({ data: mockReservation })

      const data = { commentaire: 'Mis a jour' }
      const result = await updateReservation(1, data)

      expect(api.put).toHaveBeenCalledWith('/api/logistique/reservations/1', data)
      expect(result).toEqual(mockReservation)
    })

    it('listReservationsEnAttente appelle GET avec pagination', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { items: [mockReservation], total: 1, limit: 50, offset: 10, has_more: false },
      })

      const result = await listReservationsEnAttente(50, 10)

      expect(api.get).toHaveBeenCalledWith(
        '/api/logistique/reservations/en-attente?limit=50&offset=10'
      )
      expect(result.items).toHaveLength(1)
    })

    it('validerReservation appelle POST /logistique/reservations/:id/valider', async () => {
      vi.mocked(api.post).mockResolvedValue({
        data: { ...mockReservation, statut: 'confirmee' },
      })

      const result = await validerReservation(1)

      expect(api.post).toHaveBeenCalledWith('/api/logistique/reservations/1/valider')
      expect(result.statut).toBe('confirmee')
    })

    it('refuserReservation appelle POST avec motif', async () => {
      vi.mocked(api.post).mockResolvedValue({
        data: { ...mockReservation, statut: 'refusee' },
      })

      const result = await refuserReservation(1, 'Vehicule indisponible')

      expect(api.post).toHaveBeenCalledWith('/api/logistique/reservations/1/refuser', {
        motif: 'Vehicule indisponible',
      })
      expect(result.statut).toBe('refusee')
    })

    it('refuserReservation fonctionne sans motif', async () => {
      vi.mocked(api.post).mockResolvedValue({
        data: { ...mockReservation, statut: 'refusee' },
      })

      await refuserReservation(1)

      expect(api.post).toHaveBeenCalledWith('/api/logistique/reservations/1/refuser', {
        motif: undefined,
      })
    })

    it('annulerReservation appelle POST /logistique/reservations/:id/annuler', async () => {
      vi.mocked(api.post).mockResolvedValue({
        data: { ...mockReservation, statut: 'annulee' },
      })

      const result = await annulerReservation(1)

      expect(api.post).toHaveBeenCalledWith('/api/logistique/reservations/1/annuler')
      expect(result.statut).toBe('annulee')
    })
  })

  describe('Utilitaires', () => {
    describe('formatPlageHoraire', () => {
      it('formate correctement une plage horaire', () => {
        expect(formatPlageHoraire('08:00:00', '12:00:00')).toBe('08:00 - 12:00')
        expect(formatPlageHoraire('07:30:00', '17:30:00')).toBe('07:30 - 17:30')
      })

      it('gere les heures courtes', () => {
        expect(formatPlageHoraire('08:00', '12:00')).toBe('08:00 - 12:00')
      })
    })

    describe('getLundiSemaine', () => {
      it('retourne le lundi de la semaine pour un mercredi', () => {
        const mercredi = new Date('2024-01-17') // Mercredi
        const lundi = getLundiSemaine(mercredi)
        expect(lundi.getDay()).toBe(1) // Lundi
        expect(lundi.getDate()).toBe(15)
      })

      it('retourne le meme jour pour un lundi', () => {
        const lundi = new Date('2024-01-15') // Lundi
        const result = getLundiSemaine(lundi)
        expect(result.getDate()).toBe(15)
      })

      it('retourne le lundi precedent pour un dimanche', () => {
        const dimanche = new Date('2024-01-21') // Dimanche
        const lundi = getLundiSemaine(dimanche)
        expect(lundi.getDay()).toBe(1)
        expect(lundi.getDate()).toBe(15)
      })
    })

    describe('getJoursSemaine', () => {
      it('genere 7 jours a partir du lundi', () => {
        const lundi = new Date('2024-01-15')
        const jours = getJoursSemaine(lundi)

        expect(jours).toHaveLength(7)
        expect(jours[0].getDate()).toBe(15) // Lundi
        expect(jours[6].getDate()).toBe(21) // Dimanche
      })

      it('chaque jour est consecutif', () => {
        const lundi = new Date('2024-01-15')
        const jours = getJoursSemaine(lundi)

        for (let i = 1; i < jours.length; i++) {
          const diff = jours[i].getDate() - jours[i - 1].getDate()
          expect(diff).toBe(1)
        }
      })
    })

    describe('formatDateISO', () => {
      it('formate une date au format ISO', () => {
        const date = new Date('2024-01-15T10:30:00')
        expect(formatDateISO(date)).toBe('2024-01-15')
      })

      it('gere les dates de fin de mois', () => {
        const date = new Date('2024-01-31T23:59:59')
        expect(formatDateISO(date)).toBe('2024-01-31')
      })
    })

    describe('plagesHorairesSeChevauchent', () => {
      it('detecte un chevauchement complet', () => {
        expect(plagesHorairesSeChevauchent('08:00', '12:00', '08:00', '12:00')).toBe(true)
      })

      it('detecte un chevauchement partiel debut', () => {
        expect(plagesHorairesSeChevauchent('08:00', '12:00', '10:00', '14:00')).toBe(true)
      })

      it('detecte un chevauchement partiel fin', () => {
        expect(plagesHorairesSeChevauchent('10:00', '14:00', '08:00', '12:00')).toBe(true)
      })

      it('detecte un chevauchement inclusion', () => {
        expect(plagesHorairesSeChevauchent('08:00', '17:00', '10:00', '12:00')).toBe(true)
        expect(plagesHorairesSeChevauchent('10:00', '12:00', '08:00', '17:00')).toBe(true)
      })

      it('retourne false pour plages disjointes', () => {
        expect(plagesHorairesSeChevauchent('08:00', '10:00', '12:00', '14:00')).toBe(false)
        expect(plagesHorairesSeChevauchent('12:00', '14:00', '08:00', '10:00')).toBe(false)
      })

      it('retourne false pour plages adjacentes', () => {
        expect(plagesHorairesSeChevauchent('08:00', '10:00', '10:00', '12:00')).toBe(false)
      })
    })
  })
})
