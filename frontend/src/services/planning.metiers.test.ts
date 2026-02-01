/**
 * Tests pour le filtrage planning avec metiers array
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import type { Affectation, Metier } from '../types'

// Mock des données de test
const createMockAffectation = (overrides: Partial<Affectation> = {}): Affectation => ({
  id: 'aff-1',
  utilisateur_id: 'user-1',
  chantier_id: 'chantier-1',
  date: '2026-02-03',
  heure_debut: '08:00',
  heure_fin: '17:00',
  utilisateur_nom: 'Jean Dupont',
  utilisateur_couleur: '#3498DB',
  utilisateur_metiers: ['macon'],
  chantier_nom: 'Chantier A',
  chantier_couleur: '#2ECC71',
  ...overrides,
})

describe('Planning - Filtrage par métiers', () => {
  let affectations: Affectation[]

  beforeEach(() => {
    affectations = [
      createMockAffectation({
        id: 'aff-1',
        utilisateur_id: 'user-1',
        utilisateur_nom: 'Jean Macon',
        utilisateur_metiers: ['macon', 'coffreur'],
      }),
      createMockAffectation({
        id: 'aff-2',
        utilisateur_id: 'user-2',
        utilisateur_nom: 'Pierre Electricien',
        utilisateur_metiers: ['electricien'],
      }),
      createMockAffectation({
        id: 'aff-3',
        utilisateur_id: 'user-3',
        utilisateur_nom: 'Marie Plombier',
        utilisateur_metiers: ['plombier'],
      }),
      createMockAffectation({
        id: 'aff-4',
        utilisateur_id: 'user-4',
        utilisateur_nom: 'Paul Polyvalent',
        utilisateur_metiers: ['macon', 'electricien', 'plombier'],
      }),
      createMockAffectation({
        id: 'aff-5',
        utilisateur_id: 'user-5',
        utilisateur_nom: 'Sophie Sans',
        utilisateur_metiers: undefined,
      }),
    ]
  })

  describe('Filtrage par un seul métier', () => {
    it('filtre les affectations par métier "macon"', () => {
      const metierFilter: Metier[] = ['macon']

      const filtered = affectations.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered).toHaveLength(2)
      expect(filtered.map(a => a.utilisateur_nom)).toEqual([
        'Jean Macon',
        'Paul Polyvalent',
      ])
    })

    it('filtre les affectations par métier "electricien"', () => {
      const metierFilter: Metier[] = ['electricien']

      const filtered = affectations.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered).toHaveLength(2)
      expect(filtered.map(a => a.utilisateur_nom)).toEqual([
        'Pierre Electricien',
        'Paul Polyvalent',
      ])
    })

    it('filtre les affectations par métier "plombier"', () => {
      const metierFilter: Metier[] = ['plombier']

      const filtered = affectations.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered).toHaveLength(2)
      expect(filtered.map(a => a.utilisateur_nom)).toEqual([
        'Marie Plombier',
        'Paul Polyvalent',
      ])
    })
  })

  describe('Filtrage par plusieurs métiers (union)', () => {
    it('filtre par "macon" OU "electricien"', () => {
      const metierFilter: Metier[] = ['macon', 'electricien']

      const filtered = affectations.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered).toHaveLength(3)
      expect(filtered.map(a => a.utilisateur_nom)).toEqual([
        'Jean Macon',
        'Pierre Electricien',
        'Paul Polyvalent',
      ])
    })

    it('filtre par "coffreur" OU "plombier"', () => {
      const metierFilter: Metier[] = ['coffreur', 'plombier']

      const filtered = affectations.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered).toHaveLength(3)
      expect(filtered.map(a => a.utilisateur_nom)).toEqual([
        'Jean Macon', // a coffreur
        'Marie Plombier',
        'Paul Polyvalent',
      ])
    })
  })

  describe('Cas limites', () => {
    it('exclut les utilisateurs sans métiers (undefined)', () => {
      const metierFilter: Metier[] = ['macon']

      const filtered = affectations.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered.every(a => a.utilisateur_nom !== 'Sophie Sans')).toBe(true)
    })

    it('exclut les utilisateurs avec métiers vides', () => {
      const affWithEmpty = [
        ...affectations,
        createMockAffectation({
          id: 'aff-6',
          utilisateur_id: 'user-6',
          utilisateur_nom: 'Empty User',
          utilisateur_metiers: [],
        }),
      ]

      const metierFilter: Metier[] = ['macon']

      const filtered = affWithEmpty.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered.every(a => a.utilisateur_nom !== 'Empty User')).toBe(true)
    })

    it('retourne vide si aucun utilisateur ne correspond', () => {
      const metierFilter: Metier[] = ['grutier']

      const filtered = affectations.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered).toHaveLength(0)
    })

    it('retourne tout si le filtre est vide', () => {
      const metierFilter: Metier[] = []

      const filtered = affectations.filter(aff => {
        if (metierFilter.length === 0) return true
        return aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      })

      expect(filtered).toHaveLength(affectations.length)
    })
  })

  describe('Intersection avec user.metiers', () => {
    it('trouve les utilisateurs ayant AU MOINS UN métier du filtre', () => {
      const metierFilter: Metier[] = ['coffreur', 'grutier']

      const filtered = affectations.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      // Jean Macon a "coffreur" -> inclus
      // Autres n'ont ni coffreur ni grutier -> exclus
      expect(filtered).toHaveLength(1)
      expect(filtered[0].utilisateur_nom).toBe('Jean Macon')
    })

    it('vérifie l\'intersection correctement', () => {
      const user1Metiers: Metier[] = ['macon', 'coffreur']
      const filterMetiers: Metier[] = ['coffreur', 'plombier']

      const hasIntersection = user1Metiers.some(m => filterMetiers.includes(m))

      expect(hasIntersection).toBe(true) // coffreur est commun
    })

    it('vérifie l\'absence d\'intersection', () => {
      const user2Metiers: Metier[] = ['electricien']
      const filterMetiers: Metier[] = ['macon', 'plombier']

      const hasIntersection = user2Metiers.some(m => filterMetiers.includes(m))

      expect(hasIntersection).toBe(false)
    })
  })

  describe('Performance et optimisation', () => {
    it('gère une grande liste d\'affectations', () => {
      const largeList: Affectation[] = Array.from({ length: 1000 }, (_, i) =>
        createMockAffectation({
          id: `aff-${i}`,
          utilisateur_id: `user-${i}`,
          utilisateur_metiers: i % 2 === 0 ? ['macon'] : ['electricien'],
        })
      )

      const metierFilter: Metier[] = ['macon']

      const start = performance.now()
      const filtered = largeList.filter(aff =>
        aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )
      const end = performance.now()

      expect(filtered).toHaveLength(500)
      expect(end - start).toBeLessThan(100) // Devrait être très rapide
    })

    it('gère les utilisateurs avec beaucoup de métiers', () => {
      const manyMetiers = createMockAffectation({
        utilisateur_metiers: [
          'macon',
          'coffreur',
          'ferrailleur',
          'electricien',
          'plombier',
        ] as Metier[],
      })

      const metierFilter: Metier[] = ['electricien']

      const hasMatch = manyMetiers.utilisateur_metiers?.some(m =>
        metierFilter.includes(m as Metier)
      )

      expect(hasMatch).toBe(true)
    })
  })

  describe('Combinaison avec autres filtres', () => {
    it('combine filtre métier avec filtre chantier', () => {
      const metierFilter: Metier[] = ['macon']
      const chantierIds = ['chantier-1']

      const filtered = affectations.filter(
        aff =>
          chantierIds.includes(aff.chantier_id) &&
          aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered.every(a => a.chantier_id === 'chantier-1')).toBe(true)
      expect(
        filtered.every(a => a.utilisateur_metiers?.includes('macon'))
      ).toBe(true)
    })

    it('combine filtre métier avec filtre utilisateur', () => {
      const metierFilter: Metier[] = ['macon']
      const userIds = ['user-1', 'user-4']

      const filtered = affectations.filter(
        aff =>
          userIds.includes(aff.utilisateur_id) &&
          aff.utilisateur_metiers?.some(m => metierFilter.includes(m as Metier))
      )

      expect(filtered).toHaveLength(2)
      expect(filtered.map(a => a.utilisateur_id)).toEqual(['user-1', 'user-4'])
    })
  })
})
