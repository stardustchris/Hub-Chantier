/**
 * Tests pour le hook useFeuillesHeures
 * Gestion des feuilles d'heures et pointages
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useFeuillesHeures } from './useFeuillesHeures'

// Mocks
vi.mock('../contexts/AuthContext', () => {
  let mockRole = 'admin'
  return {
    useAuth: () => ({
      user: { id: '1', role: mockRole },
    }),
    __setMockRole: (role: string) => {
      mockRole = role
    },
  }
})

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

vi.mock('../services/pointages', () => ({
  pointagesService: {
    getVueCompagnons: vi.fn(),
    getVueChantiers: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    sign: vi.fn(),
    submit: vi.fn(),
    validate: vi.fn(),
    reject: vi.fn(),
    export: vi.fn(),
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

import { pointagesService } from '../services/pointages'
import { usersService } from '../services/users'
import { chantiersService } from '../services/chantiers'

const mockUsers: any[] = [
  { id: '1', prenom: 'Jean', nom: 'Dupont', is_active: true },
  { id: '2', prenom: 'Marie', nom: 'Martin', is_active: true },
  { id: '3', prenom: 'Inactif', nom: 'User', is_active: false },
]

const mockChantiers: any[] = [
  { id: '1', nom: 'Chantier A', statut: 'en_cours' },
  { id: '2', nom: 'Chantier B', statut: 'en_cours' },
  { id: '3', nom: 'Chantier Ferme', statut: 'ferme' },
]

const mockVueCompagnons: any[] = [
  {
    utilisateur_id: 1,
    utilisateur_nom: 'Jean Dupont',
    jours: [],
    total_heures: 40,
  },
]

const mockVueChantiers: any[] = [
  {
    chantier_id: 1,
    chantier_nom: 'Chantier A',
    jours: [],
    total_heures: 80,
  },
]

const mockPointage: any = {
  id: 1,
  utilisateur_id: 1,
  chantier_id: 1,
  date: '2024-01-15',
  heures: 8,
  statut: 'brouillon',
}

describe('useFeuillesHeures', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()

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
    vi.mocked(pointagesService.getVueCompagnons).mockResolvedValue(mockVueCompagnons)
    vi.mocked(pointagesService.getVueChantiers).mockResolvedValue(mockVueChantiers)
  })

  afterEach(() => {
    localStorage.clear()
  })

  describe('etat initial', () => {
    it('initialise avec les valeurs par defaut', () => {
      const { result } = renderHook(() => useFeuillesHeures())

      expect(result.current.viewTab).toBe('compagnons')
      expect(result.current.loading).toBe(true)
      expect(result.current.error).toBe('')
      expect(result.current.modalOpen).toBe(false)
      expect(result.current.showFilters).toBe(false)
      expect(result.current.filterUtilisateurs).toEqual([])
      expect(result.current.filterChantiers).toEqual([])
    })

    it('canEdit est true pour admin', () => {
      const { result } = renderHook(() => useFeuillesHeures())
      expect(result.current.canEdit).toBe(true)
    })

    it('isValidateur est true pour admin', () => {
      const { result } = renderHook(() => useFeuillesHeures())
      expect(result.current.isValidateur).toBe(true)
    })
  })

  describe('chargement des donnees', () => {
    it('charge les utilisateurs et chantiers au montage', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(usersService.list).toHaveBeenCalledWith({ size: 100 })
      expect(chantiersService.list).toHaveBeenCalledWith({ size: 100 })
    })

    it('filtre les utilisateurs inactifs', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Ne devrait contenir que les utilisateurs actifs (2)
      expect(result.current.utilisateurs).toHaveLength(2)
      expect(result.current.utilisateurs.find(u => u.id === '3')).toBeUndefined()
    })

    it('filtre les chantiers fermes', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Ne devrait contenir que les chantiers non fermes (2)
      expect(result.current.chantiers).toHaveLength(2)
      expect(result.current.chantiers.find(c => c.id === '3')).toBeUndefined()
    })

    it('charge la vue compagnons par defaut', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(pointagesService.getVueCompagnons).toHaveBeenCalled()
      expect(result.current.vueCompagnons).toEqual(mockVueCompagnons)
    })

    it('gere les erreurs de chargement', async () => {
      vi.mocked(usersService.list).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.error).toBe('Erreur lors du chargement des donnees')
      })
    })
  })

  describe('viewTab', () => {
    it('permet de changer l\'onglet', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setViewTab('chantiers')
      })

      expect(result.current.viewTab).toBe('chantiers')
    })

    it('charge la vue chantiers quand initialise avec tab chantiers', async () => {
      // Simuler le paramètre URL tab=chantiers
      Object.defineProperty(window, 'location', {
        value: { ...window.location, search: '?tab=chantiers' },
        writable: true,
      })

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // getVueChantiers est appelé car le tab initial est 'chantiers'
      expect(pointagesService.getVueChantiers).toHaveBeenCalled()
      expect(result.current.viewTab).toBe('chantiers')
    })
  })

  describe('navigation date', () => {
    it('permet de changer la date', async () => {
      const { result } = renderHook(() => useFeuillesHeures())
      const newDate = new Date('2024-02-01')

      act(() => {
        result.current.setCurrentDate(newDate)
      })

      expect(result.current.currentDate).toEqual(newDate)
    })
  })

  describe('filtres', () => {
    it('toggle un filtre utilisateur', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      act(() => {
        result.current.handleFilterUtilisateur(1)
      })

      expect(result.current.filterUtilisateurs).toContain(1)

      act(() => {
        result.current.handleFilterUtilisateur(1)
      })

      expect(result.current.filterUtilisateurs).not.toContain(1)
    })

    it('toggle un filtre chantier', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      act(() => {
        result.current.handleFilterChantier(1)
      })

      expect(result.current.filterChantiers).toContain(1)

      act(() => {
        result.current.handleFilterChantier(1)
      })

      expect(result.current.filterChantiers).not.toContain(1)
    })

    it('efface tous les filtres utilisateurs', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      act(() => {
        result.current.handleFilterUtilisateur(1)
        result.current.handleFilterUtilisateur(2)
      })

      expect(result.current.filterUtilisateurs).toHaveLength(2)

      act(() => {
        result.current.clearFilterUtilisateurs()
      })

      expect(result.current.filterUtilisateurs).toHaveLength(0)
    })

    it('efface tous les filtres chantiers', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      act(() => {
        result.current.handleFilterChantier(1)
        result.current.handleFilterChantier(2)
      })

      expect(result.current.filterChantiers).toHaveLength(2)

      act(() => {
        result.current.clearFilterChantiers()
      })

      expect(result.current.filterChantiers).toHaveLength(0)
    })

    it('toggle showFilters', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      expect(result.current.showFilters).toBe(false)

      act(() => {
        result.current.setShowFilters(true)
      })

      expect(result.current.showFilters).toBe(true)
    })
  })

  describe('modal', () => {
    it('handleCellClick ouvre la modal avec les bons parametres', async () => {
      const { result } = renderHook(() => useFeuillesHeures())
      const testDate = new Date('2024-01-15')

      act(() => {
        result.current.handleCellClick(1, 2, testDate)
      })

      expect(result.current.modalOpen).toBe(true)
      expect(result.current.selectedUserId).toBe(1)
      expect(result.current.selectedChantierId).toBe(2)
      expect(result.current.selectedDate).toEqual(testDate)
      expect(result.current.editingPointage).toBeNull()
    })

    it('handleChantierCellClick ouvre la modal pour chantier', async () => {
      const { result } = renderHook(() => useFeuillesHeures())
      const testDate = new Date('2024-01-15')

      act(() => {
        result.current.handleChantierCellClick(1, testDate)
      })

      expect(result.current.modalOpen).toBe(true)
      expect(result.current.selectedChantierId).toBe(1)
      expect(result.current.selectedDate).toEqual(testDate)
      expect(result.current.selectedUserId).toBeUndefined()
    })

    it('handlePointageClick ouvre la modal en mode edition', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      act(() => {
        result.current.handlePointageClick(mockPointage)
      })

      expect(result.current.modalOpen).toBe(true)
      expect(result.current.editingPointage).toEqual(mockPointage)
    })

    it('closeModal ferme la modal', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      act(() => {
        result.current.handleCellClick(1, 2, new Date())
      })

      expect(result.current.modalOpen).toBe(true)

      act(() => {
        result.current.closeModal()
      })

      expect(result.current.modalOpen).toBe(false)
    })
  })

  describe('CRUD pointages', () => {
    it('handleSavePointage cree un nouveau pointage', async () => {
      vi.mocked(pointagesService.create).mockResolvedValue(mockPointage)

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      const newPointage: any = {
        utilisateur_id: 1,
        chantier_id: 1,
        date_pointage: '2024-01-17',
        heures_normales: '08:00',
      }

      await act(async () => {
        await result.current.handleSavePointage(newPointage)
      })

      expect(pointagesService.create).toHaveBeenCalledWith(newPointage, 1)
    })

    it('handleSavePointage met a jour un pointage existant', async () => {
      vi.mocked(pointagesService.update).mockResolvedValue(mockPointage)

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // D'abord ouvrir en mode edition
      act(() => {
        result.current.handlePointageClick(mockPointage)
      })

      const updateData: any = { heures_normales: '10:00' }

      await act(async () => {
        await result.current.handleSavePointage(updateData)
      })

      expect(pointagesService.update).toHaveBeenCalledWith(mockPointage.id, updateData, 1)
    })

    it('handleDeletePointage supprime le pointage', async () => {
      vi.mocked(pointagesService.delete).mockResolvedValue(undefined)

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.handlePointageClick(mockPointage)
      })

      await act(async () => {
        await result.current.handleDeletePointage()
      })

      expect(pointagesService.delete).toHaveBeenCalledWith(mockPointage.id, 1)
    })

    it('handleDeletePointage ne fait rien sans pointage', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      await act(async () => {
        await result.current.handleDeletePointage()
      })

      expect(pointagesService.delete).not.toHaveBeenCalled()
    })
  })

  describe('workflow pointages', () => {
    it('handleSignPointage signe le pointage', async () => {
      vi.mocked(pointagesService.sign).mockResolvedValue(mockPointage)

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.handlePointageClick(mockPointage)
      })

      await act(async () => {
        await result.current.handleSignPointage('signature-data')
      })

      expect(pointagesService.sign).toHaveBeenCalledWith(mockPointage.id, 'signature-data')
    })

    it('handleSubmitPointage soumet le pointage', async () => {
      vi.mocked(pointagesService.submit).mockResolvedValue(mockPointage)

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.handlePointageClick(mockPointage)
      })

      await act(async () => {
        await result.current.handleSubmitPointage()
      })

      expect(pointagesService.submit).toHaveBeenCalledWith(mockPointage.id)
    })

    it('handleValidatePointage valide le pointage', async () => {
      vi.mocked(pointagesService.validate).mockResolvedValue(mockPointage)

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.handlePointageClick(mockPointage)
      })

      await act(async () => {
        await result.current.handleValidatePointage()
      })

      expect(pointagesService.validate).toHaveBeenCalledWith(mockPointage.id, 1)
    })

    it('handleRejectPointage rejette le pointage', async () => {
      vi.mocked(pointagesService.reject).mockResolvedValue(mockPointage)

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.handlePointageClick(mockPointage)
      })

      await act(async () => {
        await result.current.handleRejectPointage('Heures incorrectes')
      })

      expect(pointagesService.reject).toHaveBeenCalledWith(mockPointage.id, 'Heures incorrectes', 1)
    })
  })

  describe('export', () => {
    it('handleExport telecharge le fichier excel', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      vi.mocked(pointagesService.export).mockResolvedValue(mockBlob)

      const mockCreateObjectURL = vi.fn().mockReturnValue('blob:url')
      const mockRevokeObjectURL = vi.fn()
      global.URL.createObjectURL = mockCreateObjectURL
      global.URL.revokeObjectURL = mockRevokeObjectURL

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleExport()
      })

      expect(pointagesService.export).toHaveBeenCalled()
      expect(result.current.isExporting).toBe(false)
    })

    it('handleExport gere les erreurs', async () => {
      vi.mocked(pointagesService.export).mockRejectedValue(new Error('Export error'))

      const { result } = renderHook(() => useFeuillesHeures())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleExport()
      })

      expect(result.current.error).toBe('Erreur lors de l\'export')
      expect(result.current.isExporting).toBe(false)
    })
  })

  describe('weekend toggle', () => {
    it('permet de toggle showWeekend', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      const initial = result.current.showWeekend

      act(() => {
        result.current.setShowWeekend(!initial)
      })

      expect(result.current.showWeekend).toBe(!initial)
    })

    it('showWeekend change de valeur', async () => {
      const { result } = renderHook(() => useFeuillesHeures())

      act(() => {
        result.current.setShowWeekend(true)
      })

      expect(result.current.showWeekend).toBe(true)

      act(() => {
        result.current.setShowWeekend(false)
      })

      expect(result.current.showWeekend).toBe(false)
    })
  })
})
