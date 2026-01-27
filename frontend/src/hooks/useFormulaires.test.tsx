/**
 * Tests unitaires pour useFormulaires hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { useFormulaires } from './useFormulaires'
import { formulairesService } from '../services/formulaires'
import { chantiersService } from '../services/chantiers'
import { consentService } from '../services/consent'
import type { ReactNode } from 'react'

// Mocks
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', role: 'admin', email: 'admin@test.com' },
  }),
}))

vi.mock('../services/formulaires', () => ({
  formulairesService: {
    listTemplates: vi.fn(),
    listFormulaires: vi.fn(),
    createTemplate: vi.fn(),
    updateTemplate: vi.fn(),
    deleteTemplate: vi.fn(),
    getTemplate: vi.fn(),
    createFormulaire: vi.fn(),
    getFormulaire: vi.fn(),
    updateFormulaire: vi.fn(),
    submitFormulaire: vi.fn(),
    validateFormulaire: vi.fn(),
    downloadPDF: vi.fn(),
  },
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(),
  },
}))

vi.mock('../services/consent', () => ({
  consentService: {
    wasAsked: vi.fn(),
    hasConsent: vi.fn(),
    setConsent: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

const mockTemplates = [
  {
    id: 1,
    nom: 'Template 1',
    categorie: 'securite',
    description: 'Test template',
    champs: [],
    is_active: true,
  },
  {
    id: 2,
    nom: 'Template 2',
    categorie: 'securite',
    description: 'Test template 2',
    champs: [],
    is_active: true,
  },
]

const mockFormulaires = [
  {
    id: 1,
    template_id: 1,
    chantier_id: 1,
    statut: 'brouillon',
    reponses: {},
  },
]

const mockChantiers = [
  { id: 1, nom: 'Chantier 1', code: 'CH1' },
  { id: 2, nom: 'Chantier 2', code: 'CH2' },
]

const wrapper = ({ children }: { children: ReactNode }) => (
  <MemoryRouter>{children}</MemoryRouter>
)

describe('useFormulaires', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(formulairesService.listTemplates).mockResolvedValue({ templates: mockTemplates })
    vi.mocked(formulairesService.listFormulaires).mockResolvedValue({ formulaires: mockFormulaires })
    vi.mocked(chantiersService.list).mockResolvedValue({ items: mockChantiers })
  })

  describe('initial state', () => {
    it('demarre en mode loading', () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })
      expect(result.current.loading).toBe(true)
    })

    it('charge les donnees au demarrage', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.templates).toHaveLength(2)
      expect(result.current.chantiers).toHaveLength(2)
    })

    it('a un onglet formulaires par defaut', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.activeTab).toBe('formulaires')
    })
  })

  describe('permissions', () => {
    it('admin peut gerer les templates', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.canManageTemplates).toBe(true)
    })
  })

  describe('tab management', () => {
    it('change onglet avec handleTabChange', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.handleTabChange('templates')
      })

      expect(result.current.activeTab).toBe('templates')
    })
  })

  describe('filter templates', () => {
    it('filtre par searchQuery', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setSearchQuery('Template 1')
      })

      expect(result.current.filteredTemplates).toHaveLength(1)
      expect(result.current.filteredTemplates[0].nom).toBe('Template 1')
    })

    it('filtre case-insensitive', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setSearchQuery('template 1')
      })

      expect(result.current.filteredTemplates).toHaveLength(1)
    })
  })

  describe('template modals', () => {
    it('ouvre le modal nouveau template', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.openNewTemplateModal()
      })

      expect(result.current.templateModalOpen).toBe(true)
      expect(result.current.selectedTemplate).toBeNull()
    })

    it('ferme le modal template', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.openNewTemplateModal()
      })

      act(() => {
        result.current.closeTemplateModal()
      })

      expect(result.current.templateModalOpen).toBe(false)
    })

    it('ouvre le modal en mode edition', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.handleEditTemplate(mockTemplates[0] as never)
      })

      expect(result.current.templateModalOpen).toBe(true)
      expect(result.current.selectedTemplate).toEqual(mockTemplates[0])
    })
  })

  describe('template actions', () => {
    it('cree un nouveau template', async () => {
      vi.mocked(formulairesService.createTemplate).mockResolvedValue(mockTemplates[0] as never)
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleSaveTemplate({
          nom: 'New Template',
          categorie: 'securite',
          champs: [],
        })
      })

      expect(formulairesService.createTemplate).toHaveBeenCalled()
    })

    it('met a jour un template existant', async () => {
      vi.mocked(formulairesService.updateTemplate).mockResolvedValue(mockTemplates[0] as never)
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.handleEditTemplate(mockTemplates[0] as never)
      })

      await act(async () => {
        await result.current.handleSaveTemplate({ nom: 'Updated' })
      })

      expect(formulairesService.updateTemplate).toHaveBeenCalledWith(1, { nom: 'Updated' })
    })

    it('duplique un template', async () => {
      vi.mocked(formulairesService.createTemplate).mockResolvedValue(mockTemplates[0] as never)
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleDuplicateTemplate(mockTemplates[0] as never)
      })

      expect(formulairesService.createTemplate).toHaveBeenCalledWith(
        expect.objectContaining({
          nom: 'Template 1 (copie)',
        })
      )
    })

    it('toggle active state du template', async () => {
      vi.mocked(formulairesService.updateTemplate).mockResolvedValue(mockTemplates[0] as never)
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleToggleTemplateActive(mockTemplates[0] as never)
      })

      expect(formulairesService.updateTemplate).toHaveBeenCalledWith(1, { is_active: false })
    })
  })

  describe('formulaire modals', () => {
    it('ouvre le modal nouveau formulaire', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.openNewFormulaireModal()
      })

      expect(result.current.newFormulaireModalOpen).toBe(true)
    })

    it('ferme le modal nouveau formulaire', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.openNewFormulaireModal()
      })

      act(() => {
        result.current.closeNewFormulaireModal()
      })

      expect(result.current.newFormulaireModalOpen).toBe(false)
    })
  })

  describe('geolocation consent', () => {
    it('demande le consentement si pas encore demande', async () => {
      vi.mocked(consentService.wasAsked).mockReturnValue(false)
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setSelectedChantierId('1')
      })

      await act(async () => {
        await result.current.handleCreateFormulaire(1)
      })

      expect(result.current.geoConsentModalOpen).toBe(true)
    })

    it('accepte le consentement geoloc', async () => {
      vi.mocked(consentService.wasAsked).mockReturnValue(false)
      vi.mocked(formulairesService.createFormulaire).mockResolvedValue(mockFormulaires[0] as never)
      vi.mocked(formulairesService.getTemplate).mockResolvedValue(mockTemplates[0] as never)

      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setSelectedChantierId('1')
      })

      await act(async () => {
        await result.current.handleCreateFormulaire(1)
      })

      await act(async () => {
        await result.current.handleGeoConsentAccept()
      })

      expect(consentService.setConsent).toHaveBeenCalledWith('geolocation', true)
      expect(result.current.geoConsentModalOpen).toBe(false)
    })

    it('decline le consentement geoloc', async () => {
      vi.mocked(consentService.wasAsked).mockReturnValue(false)
      vi.mocked(formulairesService.createFormulaire).mockResolvedValue(mockFormulaires[0] as never)
      vi.mocked(formulairesService.getTemplate).mockResolvedValue(mockTemplates[0] as never)

      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setSelectedChantierId('1')
      })

      await act(async () => {
        await result.current.handleCreateFormulaire(1)
      })

      await act(async () => {
        await result.current.handleGeoConsentDecline()
      })

      expect(consentService.setConsent).toHaveBeenCalledWith('geolocation', false)
    })

    it('ferme le modal consentement', async () => {
      vi.mocked(consentService.wasAsked).mockReturnValue(false)
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.setSelectedChantierId('1')
      })

      await act(async () => {
        await result.current.handleCreateFormulaire(1)
      })

      act(() => {
        result.current.handleGeoConsentClose()
      })

      expect(result.current.geoConsentModalOpen).toBe(false)
    })
  })

  describe('formulaire actions', () => {
    it('affiche erreur si pas de chantier selectionne', async () => {
      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleCreateFormulaire(1)
      })

      expect(result.current.error).toBe('Veuillez selectionner un chantier')
    })

    it('view formulaire ouvre en mode lecture', async () => {
      vi.mocked(formulairesService.getFormulaire).mockResolvedValue(mockFormulaires[0] as never)
      vi.mocked(formulairesService.getTemplate).mockResolvedValue(mockTemplates[0] as never)

      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleViewFormulaire(mockFormulaires[0] as never)
      })

      expect(result.current.formulaireModalOpen).toBe(true)
      expect(result.current.formulaireReadOnly).toBe(true)
    })

    it('edit formulaire ouvre en mode edition', async () => {
      vi.mocked(formulairesService.getFormulaire).mockResolvedValue(mockFormulaires[0] as never)
      vi.mocked(formulairesService.getTemplate).mockResolvedValue(mockTemplates[0] as never)

      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      await act(async () => {
        await result.current.handleEditFormulaire(mockFormulaires[0] as never)
      })

      expect(result.current.formulaireModalOpen).toBe(true)
      expect(result.current.formulaireReadOnly).toBe(false)
    })
  })

  describe('error handling', () => {
    it('gere les erreurs de chargement', async () => {
      vi.mocked(formulairesService.listTemplates).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useFormulaires(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Utilise les mocks vides en cas d'erreur
      expect(result.current.templates).toEqual([])
    })
  })
})
