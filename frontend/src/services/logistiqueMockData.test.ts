/**
 * Tests unitaires pour le service logistiqueMockData
 * Couvre: initializeMockData, getMockRessources, getMockReservations,
 * getReservationsByChantier, getActiveReservationsByChantier,
 * getTodayReservationsByChantier, getUpcomingReservationsByChantier,
 * listMockRessources, listMockReservationsByChantier,
 * resetMockData, addMockReservation, updateMockReservationStatus
 */

import { describe, it, expect, beforeEach } from 'vitest'
import {
  initializeMockData,
  getMockRessources,
  getMockReservations,
  getReservationsByChantier,
  getActiveReservationsByChantier,
  getTodayReservationsByChantier,
  getUpcomingReservationsByChantier,
  listMockRessources,
  listMockReservationsByChantier,
  resetMockData,
  addMockReservation,
  updateMockReservationStatus,
} from './logistiqueMockData'
import type { Reservation } from '../types/logistique'

describe('logistiqueMockData', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  describe('initializeMockData', () => {
    it('initialise les donnees en sessionStorage', () => {
      initializeMockData()

      expect(sessionStorage.getItem('logistique_mock_initialized')).toBe('true')
      expect(sessionStorage.getItem('logistique_mock_ressources')).toBeTruthy()
      expect(sessionStorage.getItem('logistique_mock_reservations')).toBeTruthy()
    })

    it('ne reinitialise pas si deja initialise', () => {
      initializeMockData()
      const firstRessources = sessionStorage.getItem('logistique_mock_ressources')

      // Call again
      initializeMockData()
      const secondRessources = sessionStorage.getItem('logistique_mock_ressources')

      // Should be the same data (not regenerated)
      expect(firstRessources).toBe(secondRessources)
    })

    it('cree des ressources avec categories variees', () => {
      initializeMockData()
      const ressources = JSON.parse(sessionStorage.getItem('logistique_mock_ressources')!)
      expect(ressources.length).toBeGreaterThan(0)

      // Should have at least one per category (5) + 3 extras = 8
      expect(ressources.length).toBe(8)
    })

    it('cree des reservations avec noms enrichis', () => {
      initializeMockData()
      const reservations = JSON.parse(sessionStorage.getItem('logistique_mock_reservations')!)
      expect(reservations.length).toBeGreaterThan(0)

      // Check enrichment
      const withRessourceNom = reservations.filter((r: Reservation) => r.ressource_nom)
      expect(withRessourceNom.length).toBeGreaterThan(0)

      const withChantierNom = reservations.filter((r: Reservation) => r.chantier_nom)
      expect(withChantierNom.length).toBeGreaterThan(0)

      const withDemandeurNom = reservations.filter((r: Reservation) => r.demandeur_nom)
      expect(withDemandeurNom.length).toBeGreaterThan(0)
    })
  })

  describe('getMockRessources', () => {
    it('retourne les ressources (initialise si besoin)', () => {
      const ressources = getMockRessources()
      expect(ressources.length).toBeGreaterThan(0)
      expect(ressources[0]).toHaveProperty('id')
      expect(ressources[0]).toHaveProperty('nom')
      expect(ressources[0]).toHaveProperty('categorie')
    })

    it('retourne un tableau vide si sessionStorage est vide et initialized flag set', () => {
      sessionStorage.setItem('logistique_mock_initialized', 'true')
      // No ressources key set
      sessionStorage.removeItem('logistique_mock_ressources')
      const ressources = getMockRessources()
      expect(ressources).toEqual([])
    })
  })

  describe('getMockReservations', () => {
    it('retourne les reservations (initialise si besoin)', () => {
      const reservations = getMockReservations()
      expect(reservations.length).toBeGreaterThan(0)
      expect(reservations[0]).toHaveProperty('id')
      expect(reservations[0]).toHaveProperty('statut')
    })

    it('retourne un tableau vide si sessionStorage est vide et initialized flag set', () => {
      sessionStorage.setItem('logistique_mock_initialized', 'true')
      sessionStorage.removeItem('logistique_mock_reservations')
      const reservations = getMockReservations()
      expect(reservations).toEqual([])
    })
  })

  describe('getReservationsByChantier', () => {
    it('filtre les reservations par chantier_id', () => {
      initializeMockData()
      const allReservations = getMockReservations()
      // Pick a chantier_id that exists
      const targetId = allReservations[0]?.chantier_id
      if (targetId !== undefined) {
        const filtered = getReservationsByChantier(targetId)
        expect(filtered.every((r) => r.chantier_id === targetId)).toBe(true)
      }
    })

    it('retourne un tableau vide pour un chantier inexistant', () => {
      initializeMockData()
      const result = getReservationsByChantier(99999)
      expect(result).toEqual([])
    })
  })

  describe('getActiveReservationsByChantier', () => {
    it('filtre les reservations actives (validee ou en_attente)', () => {
      initializeMockData()
      const allReservations = getMockReservations()
      const targetId = allReservations[0]?.chantier_id
      if (targetId !== undefined) {
        const active = getActiveReservationsByChantier(targetId)
        expect(active.every((r) => r.statut === 'validee' || r.statut === 'en_attente')).toBe(true)
      }
    })
  })

  describe('getTodayReservationsByChantier', () => {
    it('filtre les reservations pour aujourd hui', () => {
      initializeMockData()
      // Add a reservation for today
      const today = new Date().toISOString().split('T')[0]
      const todayReservation: Reservation = {
        id: 9999,
        ressource_id: 1,
        chantier_id: 42,
        demandeur_id: 1,
        date_reservation: today,
        heure_debut: '08:00',
        heure_fin: '17:00',
        statut: 'validee',
        statut_label: 'Validee',
        statut_couleur: '#4CAF50',
      }
      addMockReservation(todayReservation)

      const result = getTodayReservationsByChantier(42)
      expect(result.length).toBeGreaterThanOrEqual(1)
      expect(result.some((r) => r.id === 9999)).toBe(true)
    })

    it('exclut les reservations annulees ou refusees', () => {
      initializeMockData()
      const today = new Date().toISOString().split('T')[0]
      addMockReservation({
        id: 9998,
        ressource_id: 1,
        chantier_id: 43,
        demandeur_id: 1,
        date_reservation: today,
        heure_debut: '08:00',
        heure_fin: '17:00',
        statut: 'annulee',
        statut_label: 'Annulee',
        statut_couleur: '#9E9E9E',
      })

      const result = getTodayReservationsByChantier(43)
      expect(result.some((r) => r.id === 9998)).toBe(false)
    })
  })

  describe('getUpcomingReservationsByChantier', () => {
    it('retourne les reservations des 7 prochains jours', () => {
      initializeMockData()
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      const tomorrowStr = tomorrow.toISOString().split('T')[0]

      addMockReservation({
        id: 9997,
        ressource_id: 1,
        chantier_id: 44,
        demandeur_id: 1,
        date_reservation: tomorrowStr,
        heure_debut: '08:00',
        heure_fin: '17:00',
        statut: 'en_attente',
        statut_label: 'En attente',
        statut_couleur: '#FFC107',
      })

      const result = getUpcomingReservationsByChantier(44)
      expect(result.some((r) => r.id === 9997)).toBe(true)
    })

    it('exclut les reservations trop loin dans le futur', () => {
      initializeMockData()
      const farFuture = new Date()
      farFuture.setDate(farFuture.getDate() + 30)
      const farFutureStr = farFuture.toISOString().split('T')[0]

      addMockReservation({
        id: 9996,
        ressource_id: 1,
        chantier_id: 45,
        demandeur_id: 1,
        date_reservation: farFutureStr,
        heure_debut: '08:00',
        heure_fin: '17:00',
        statut: 'validee',
        statut_label: 'Validee',
        statut_couleur: '#4CAF50',
      })

      const result = getUpcomingReservationsByChantier(45)
      expect(result.some((r) => r.id === 9996)).toBe(false)
    })
  })

  describe('listMockRessources', () => {
    it('retourne une liste paginee de toutes les ressources actives par defaut', () => {
      initializeMockData()
      const result = listMockRessources()

      expect(result).toHaveProperty('items')
      expect(result).toHaveProperty('total')
      expect(result).toHaveProperty('limit')
      expect(result).toHaveProperty('offset')
      expect(result).toHaveProperty('has_more')
      expect(result.items.length).toBeGreaterThan(0)
      expect(result.items.every((r) => r.actif)).toBe(true)
    })

    it('filtre par categorie', () => {
      initializeMockData()
      const result = listMockRessources('vehicule')
      expect(result.items.every((r) => r.categorie === 'vehicule')).toBe(true)
    })

    it('inclut les ressources inactives si actifSeulement=false', () => {
      initializeMockData()
      const result = listMockRessources(undefined, false)
      expect(result.total).toBeGreaterThan(0)
    })

    it('respecte limit et offset', () => {
      initializeMockData()
      const result = listMockRessources(undefined, true, 2, 0)
      expect(result.items.length).toBeLessThanOrEqual(2)
      expect(result.limit).toBe(2)
      expect(result.offset).toBe(0)
    })

    it('calcule has_more correctement', () => {
      initializeMockData()
      const smallPage = listMockRessources(undefined, true, 1, 0)
      if (smallPage.total > 1) {
        expect(smallPage.has_more).toBe(true)
      }

      const bigPage = listMockRessources(undefined, true, 1000, 0)
      expect(bigPage.has_more).toBe(false)
    })
  })

  describe('listMockReservationsByChantier', () => {
    it('retourne une liste paginee', () => {
      initializeMockData()
      const allReservations = getMockReservations()
      const chantierId = allReservations[0]?.chantier_id
      if (chantierId !== undefined) {
        const result = listMockReservationsByChantier(chantierId)
        expect(result).toHaveProperty('items')
        expect(result).toHaveProperty('total')
        expect(result.items.every((r) => r.chantier_id === chantierId)).toBe(true)
      }
    })

    it('respecte limit et offset', () => {
      initializeMockData()
      const allReservations = getMockReservations()
      const chantierId = allReservations[0]?.chantier_id
      if (chantierId !== undefined) {
        const result = listMockReservationsByChantier(chantierId, 1, 0)
        expect(result.items.length).toBeLessThanOrEqual(1)
        expect(result.limit).toBe(1)
      }
    })
  })

  describe('resetMockData', () => {
    it('supprime toutes les donnees mock du sessionStorage', () => {
      initializeMockData()
      expect(sessionStorage.getItem('logistique_mock_initialized')).toBe('true')

      resetMockData()

      expect(sessionStorage.getItem('logistique_mock_initialized')).toBeNull()
      expect(sessionStorage.getItem('logistique_mock_ressources')).toBeNull()
      expect(sessionStorage.getItem('logistique_mock_reservations')).toBeNull()
    })
  })

  describe('addMockReservation', () => {
    it('ajoute une reservation au sessionStorage', () => {
      initializeMockData()
      const countBefore = getMockReservations().length

      addMockReservation({
        id: 8888,
        ressource_id: 1,
        chantier_id: 1,
        demandeur_id: 1,
        date_reservation: '2026-02-01',
        heure_debut: '08:00',
        heure_fin: '17:00',
        statut: 'en_attente',
        statut_label: 'En attente',
        statut_couleur: '#FFC107',
      })

      const countAfter = getMockReservations().length
      expect(countAfter).toBe(countBefore + 1)
    })
  })

  describe('updateMockReservationStatus', () => {
    it('met a jour le statut d une reservation existante', () => {
      initializeMockData()
      const reservations = getMockReservations()
      const target = reservations.find((r) => r.statut === 'en_attente')
      if (target) {
        const result = updateMockReservationStatus(target.id, 'validee', 5)
        expect(result).not.toBeNull()
        expect(result!.statut).toBe('validee')
        expect(result!.valideur_id).toBe(5)
        expect(result!.validated_at).toBeTruthy()
      }
    })

    it('retourne null pour une reservation inexistante', () => {
      initializeMockData()
      const result = updateMockReservationStatus(99999, 'validee')
      expect(result).toBeNull()
    })

    it('met a jour le motif_refus pour un refus', () => {
      initializeMockData()
      const reservations = getMockReservations()
      const target = reservations.find((r) => r.statut === 'en_attente')
      if (target) {
        const result = updateMockReservationStatus(target.id, 'refusee', 5, 'Pas disponible')
        expect(result).not.toBeNull()
        expect(result!.statut).toBe('refusee')
        expect(result!.motif_refus).toBe('Pas disponible')
      }
    })

    it('met a jour le statut_label et statut_couleur', () => {
      initializeMockData()
      const reservations = getMockReservations()
      const target = reservations.find((r) => r.statut === 'en_attente')
      if (target) {
        const result = updateMockReservationStatus(target.id, 'annulee')
        expect(result).not.toBeNull()
        expect(result!.statut_label).toBe('Annulée')
        expect(result!.statut_couleur).toBe('#9E9E9E')
      }
    })

    it('persiste les modifications en sessionStorage', () => {
      initializeMockData()
      const reservations = getMockReservations()
      const target = reservations.find((r) => r.statut === 'en_attente')
      if (target) {
        updateMockReservationStatus(target.id, 'validee', 3)
        // Re-fetch from storage
        const updated = getMockReservations().find((r) => r.id === target.id)
        expect(updated?.statut).toBe('validee')
      }
    })
  })
})
