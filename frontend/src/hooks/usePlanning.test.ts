/**
 * Tests pour le hook usePlanning
 * Gestion du planning des affectations
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { usePlanning } from './usePlanning'

// Mock des services
vi.mock('../services/planning', () => ({
  planningService: {
    getAffectations: vi.fn(),
    getNonPlanifies: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    duplicate: vi.fn(),
    move: vi.fn(),
  },
}))

vi.mock('../services/users', () => ({
  usersService: {
    list: vi.fn(),
  },
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock useAuth avec différents rôles
let mockUserRole = 'admin'
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', role: mockUserRole },
  }),
}))

import { planningService } from '../services/planning'
import { usersService } from '../services/users'
import { chantiersService } from '../services/chantiers'

const mockAffectations: any[] = [
  {
    id: '1',
    utilisateur_id: 'u1',
    chantier_id: 'c1',
    date: '2024-01-15',
    type_journee: 'journee',
  },
  {
    id: '2',
    utilisateur_id: 'u2',
    chantier_id: 'c1',
    date: '2024-01-16',
    type_journee: 'matin',
  },
]

const mockUsers: any[] = [
  { id: 'u1', prenom: 'Jean', nom: 'Dupont', is_active: true, metier: 'macon' },
  { id: 'u2', prenom: 'Marie', nom: 'Martin', is_active: true, metier: 'electricien' },
  { id: 'u3', prenom: 'Inactif', nom: 'User', is_active: false, metier: 'macon' },
]

const mockChantiers: any[] = [
  { id: 'c1', nom: 'Chantier A', statut: 'en_cours' },
  { id: 'c2', nom: 'Chantier B', statut: 'en_cours' },
  { id: 'c3', nom: 'Chantier Fermé', statut: 'ferme' },
]

describe('usePlanning', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUserRole = 'admin'

    vi.mocked(planningService.getAffectations).mockResolvedValue(mockAffectations)
    vi.mocked(planningService.getNonPlanifies).mockResolvedValue({
      utilisateur_ids: ['u3'],
      date_debut: '2024-01-15',
      date_fin: '2024-01-21',
    } as any)
    vi.mocked(usersService.list).mockResolvedValue({
      items: mockUsers,
      total: 3,
      page: 1,
      size: 100,
      pages: 1,
    })
    vi.mocked(chantiersService.list).mockResolvedValue({
      items: mockChantiers,
      total: 3,
      page: 1,
      size: 100,
      pages: 1,
    })

    // Mock window.confirm
    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })

  describe('état initial', () => {
    it('initialise avec les valeurs par défaut', async () => {
      const { result } = renderHook(() => usePlanning())

      expect(result.current.viewMode).toBe('semaine')
      expect(result.current.viewTab).toBe('utilisateurs')
      expect(result.current.loading).toBe(true)
      expect(result.current.error).toBe('')
      expect(result.current.modalOpen).toBe(false)

      // Attendre la fin du chargement pour éviter les warnings act()
      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })
    })

    it('canEdit est true pour admin', async () => {
      mockUserRole = 'admin'
      const { result } = renderHook(() => usePlanning())
      expect(result.current.canEdit).toBe(true)

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })
    })

    it('canEdit est true pour conducteur', async () => {
      mockUserRole = 'conducteur'
      const { result } = renderHook(() => usePlanning())
      expect(result.current.canEdit).toBe(true)

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })
    })

    it('canEdit est false pour compagnon', async () => {
      mockUserRole = 'compagnon'
      const { result } = renderHook(() => usePlanning())
      expect(result.current.canEdit).toBe(false)

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })
    })
  })

  describe('chargement des données', () => {
    it('charge les données au montage', async () => {
      renderHook(() => usePlanning())

      await waitFor(() => {
        expect(planningService.getAffectations).toHaveBeenCalled()
        expect(usersService.list).toHaveBeenCalledWith({ size: 100 })
        expect(chantiersService.list).toHaveBeenCalledWith({ size: 100 })
        expect(planningService.getNonPlanifies).toHaveBeenCalled()
      })
    })

    it('filtre les utilisateurs inactifs', async () => {
      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Ne devrait contenir que les utilisateurs actifs
      expect(result.current.utilisateurs).toHaveLength(2)
      expect(result.current.utilisateurs.find(u => u.id === 'u3')).toBeUndefined()
    })

    it('filtre les chantiers fermés', async () => {
      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Ne devrait contenir que les chantiers non fermés
      expect(result.current.chantiers).toHaveLength(2)
      expect(result.current.chantiers.find(c => c.id === 'c3')).toBeUndefined()
    })

    it('gère les erreurs de chargement', async () => {
      vi.mocked(planningService.getAffectations).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.error).toBe('Erreur lors du chargement du planning')
      })
    })
  })

  describe('viewMode', () => {
    it('permet de changer le mode de vue', async () => {
      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setViewMode('mois')
      })

      expect(result.current.viewMode).toBe('mois')
    })
  })

  describe('viewTab', () => {
    it('permet de changer l\'onglet', async () => {
      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setViewTab('chantiers')
      })

      expect(result.current.viewTab).toBe('chantiers')
    })
  })

  describe('filtres', () => {
    it('filtre les affectations par chantier', async () => {
      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setFilterChantier('c1')
      })

      // Toutes les affectations mock sont sur c1
      expect(result.current.filteredAffectations).toHaveLength(2)
    })

    it('toggle les filtres par métier', async () => {
      const { result } = renderHook(() => usePlanning())

      act(() => {
        result.current.toggleFilterMetier('macon')
      })

      expect(result.current.filterMetiers).toContain('macon')

      act(() => {
        result.current.toggleFilterMetier('macon')
      })

      expect(result.current.filterMetiers).not.toContain('macon')
    })

    it('efface tous les filtres métier', async () => {
      const { result } = renderHook(() => usePlanning())

      act(() => {
        result.current.toggleFilterMetier('macon')
        result.current.toggleFilterMetier('electricien')
      })

      expect(result.current.filterMetiers).toHaveLength(2)

      act(() => {
        result.current.clearFilterMetiers()
      })

      expect(result.current.filterMetiers).toHaveLength(0)
    })

    it('toggle showFilters', async () => {
      const { result } = renderHook(() => usePlanning())

      expect(result.current.showFilters).toBe(false)

      act(() => {
        result.current.setShowFilters(true)
      })

      expect(result.current.showFilters).toBe(true)
    })
  })

  describe('modal', () => {
    it('ouvre la modal de création', async () => {
      const { result } = renderHook(() => usePlanning())

      act(() => {
        result.current.openCreateModal()
      })

      expect(result.current.modalOpen).toBe(true)
      expect(result.current.editingAffectation).toBeNull()
    })

    it('ferme la modal', async () => {
      const { result } = renderHook(() => usePlanning())

      act(() => {
        result.current.openCreateModal()
      })

      expect(result.current.modalOpen).toBe(true)

      act(() => {
        result.current.closeModal()
      })

      expect(result.current.modalOpen).toBe(false)
    })

    it('handleCellClick ouvre la modal avec userId et date', async () => {
      const { result } = renderHook(() => usePlanning())
      const testDate = new Date('2024-01-15')

      act(() => {
        result.current.handleCellClick('u1', testDate)
      })

      expect(result.current.modalOpen).toBe(true)
      expect(result.current.selectedUserId).toBe('u1')
      expect(result.current.selectedDate).toEqual(testDate)
      expect(result.current.editingAffectation).toBeNull()
    })

    it('handleCellClick ne fait rien si canEdit est false', async () => {
      mockUserRole = 'compagnon'
      const { result } = renderHook(() => usePlanning())

      act(() => {
        result.current.handleCellClick('u1', new Date())
      })

      expect(result.current.modalOpen).toBe(false)
    })

    it('handleAffectationClick ouvre la modal en mode édition', async () => {
      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.handleAffectationClick(mockAffectations[0])
      })

      expect(result.current.modalOpen).toBe(true)
      expect(result.current.editingAffectation).toEqual(mockAffectations[0])
    })

    it('handleChantierCellClick ouvre la modal avec chantierId', async () => {
      const { result } = renderHook(() => usePlanning())
      const testDate = new Date('2024-01-15')

      act(() => {
        result.current.handleChantierCellClick('c1', testDate)
      })

      expect(result.current.modalOpen).toBe(true)
      expect(result.current.selectedChantierId).toBe('c1')
      expect(result.current.selectedDate).toEqual(testDate)
    })
  })

  describe('handleToggleMetier', () => {
    it('toggle l\'expansion d\'un métier', async () => {
      const { result } = renderHook(() => usePlanning())

      // Par défaut tous les métiers sont expanded (initialisés avec PLANNING_CATEGORIES)
      // Les catégories sont: conducteur, chef_chantier, compagnon, interimaire, sous_traitant
      expect(result.current.expandedMetiers).toContain('compagnon')

      act(() => {
        result.current.handleToggleMetier('compagnon')
      })

      // Après toggle, compagnon devrait être collapsed (retiré)
      expect(result.current.expandedMetiers).not.toContain('compagnon')

      act(() => {
        result.current.handleToggleMetier('compagnon')
      })

      // Après second toggle, compagnon devrait être expanded (ajouté)
      expect(result.current.expandedMetiers).toContain('compagnon')
    })
  })

  describe('CRUD affectations', () => {
    it('handleSaveAffectation crée une nouvelle affectation', async () => {
      vi.mocked(planningService.create).mockResolvedValue({ id: '3' } as any)

      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      const newAffectation = {
        utilisateur_id: 'u1',
        chantier_id: 'c1',
        date: '2024-01-17',
        type_journee: 'journee',
      }

      await act(async () => {
        await result.current.handleSaveAffectation(newAffectation)
      })

      expect(planningService.create).toHaveBeenCalledWith(newAffectation)
    })

    it('handleSaveAffectation met à jour une affectation existante', async () => {
      vi.mocked(planningService.update).mockResolvedValue({ id: '1' } as any)

      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // D'abord ouvrir en mode édition
      act(() => {
        result.current.handleAffectationClick(mockAffectations[0])
      })

      const updateData: any = {
        type_journee: 'matin',
      }

      await act(async () => {
        await result.current.handleSaveAffectation(updateData)
      })

      expect(planningService.update).toHaveBeenCalledWith('1', updateData)
    })

    it('handleAffectationDelete supprime une affectation', async () => {
      vi.mocked(planningService.delete).mockResolvedValue(undefined)

      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleAffectationDelete(mockAffectations[0])
      })

      expect(planningService.delete).toHaveBeenCalledWith('1')
    })

    it('handleAffectationDelete ne fait rien si annulé', async () => {
      vi.spyOn(window, 'confirm').mockReturnValue(false)

      const { result } = renderHook(() => usePlanning())

      await act(async () => {
        await result.current.handleAffectationDelete(mockAffectations[0])
      })

      expect(planningService.delete).not.toHaveBeenCalled()
    })

    it('handleAffectationMove déplace une affectation', async () => {
      vi.mocked(planningService.move).mockResolvedValue(mockAffectations[0])

      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleAffectationMove('1', '2024-01-20', 'u2')
      })

      expect(planningService.move).toHaveBeenCalledWith('1', '2024-01-20', 'u2')
    })
  })

  describe('duplication', () => {
    it('handleDuplicate duplique les affectations d\'un utilisateur', async () => {
      vi.mocked(planningService.duplicate).mockResolvedValue(mockAffectations)

      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleDuplicate('u1')
      })

      expect(planningService.duplicate).toHaveBeenCalled()
    })

    it('handleDuplicateChantier duplique les affectations d\'un chantier', async () => {
      vi.mocked(planningService.duplicate).mockResolvedValue(mockAffectations)

      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleDuplicateChantier('c1')
      })

      // Devrait appeler duplicate pour chaque utilisateur sur ce chantier
      expect(planningService.duplicate).toHaveBeenCalled()
    })

    it('handleDuplicateChantier affiche erreur si aucune affectation', async () => {
      vi.mocked(planningService.getAffectations).mockResolvedValue([])

      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleDuplicateChantier('c2')
      })

      expect(result.current.error).toBe('Aucune affectation à dupliquer pour ce chantier')
      expect(planningService.duplicate).not.toHaveBeenCalled()
    })
  })

  describe('weekend toggle', () => {
    it('permet de toggle showWeekend', async () => {
      const { result } = renderHook(() => usePlanning())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      const initial = result.current.showWeekend

      act(() => {
        result.current.setShowWeekend(!initial)
      })

      expect(result.current.showWeekend).toBe(!initial)
    })
  })
})
