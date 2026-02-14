// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'

// Mock dependencies before importing hook
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
    rejectFormulaire: vi.fn(),
    downloadPDF: vi.fn(),
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
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

import { useFormulairesData } from './useFormulairesData'
import { formulairesService } from '../services/formulaires'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'

const mockTemplates = [
  {
    id: 1,
    nom: 'Template A',
    categorie: 'securite',
    description: 'Desc A',
    champs: [],
    is_active: true,
    created_at: '2026-01-01',
    updated_at: '2026-01-01',
  },
]

const mockFormulaires = [
  {
    id: 10,
    template_id: 1,
    chantier_id: 1,
    statut: 'brouillon',
    valeurs: {},
    created_at: '2026-01-01',
    updated_at: '2026-01-01',
  },
]

const mockChantiers = [
  { id: 1, nom: 'Chantier 1' },
]

function setupDefaultMocks() {
  vi.mocked(formulairesService.listTemplates).mockResolvedValue({
    templates: mockTemplates as any,
    total: 1,
    skip: 0,
    limit: 50,
  })
  vi.mocked(formulairesService.listFormulaires).mockResolvedValue({
    formulaires: mockFormulaires as any,
    total: 1,
    skip: 0,
    limit: 50,
  })
  vi.mocked(chantiersService.list).mockResolvedValue({
    items: mockChantiers as any,
    total: 1,
    page: 1,
    size: 100,
    pages: 1,
  })
}

describe('useFormulairesData', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have correct initial state', () => {
      // Don't set up mocks so loading stays in progress
      vi.mocked(formulairesService.listTemplates).mockReturnValue(new Promise(() => {}))
      vi.mocked(formulairesService.listFormulaires).mockReturnValue(new Promise(() => {}))
      vi.mocked(chantiersService.list).mockReturnValue(new Promise(() => {}))

      const { result } = renderHook(() => useFormulairesData())

      expect(result.current.loading).toBe(true)
      expect(result.current.error).toBe('')
      expect(result.current.templates).toEqual([])
      expect(result.current.formulaires).toEqual([])
      expect(result.current.chantiers).toEqual([])
    })
  })

  describe('loadData', () => {
    it('should load templates, formulaires, and chantiers', async () => {
      setupDefaultMocks()

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.loadData()
      })

      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBe('')
      expect(result.current.templates).toEqual(mockTemplates)
      expect(result.current.formulaires).toEqual(mockFormulaires)
      expect(result.current.chantiers).toEqual(mockChantiers)
    })

    it('should pass filter params for templates tab', async () => {
      setupDefaultMocks()

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.loadData({
          activeTab: 'templates',
          searchQuery: 'test',
          filterCategorie: 'securite' as any,
        })
      })

      expect(formulairesService.listTemplates).toHaveBeenCalledWith({
        query: 'test',
        categorie: 'securite',
        active_only: false,
      })
    })

    it('should set active_only when activeTab is formulaires', async () => {
      setupDefaultMocks()

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.loadData({ activeTab: 'formulaires' })
      })

      expect(formulairesService.listTemplates).toHaveBeenCalledWith(
        expect.objectContaining({ active_only: true })
      )
    })

    it('should pass chantier_id filter', async () => {
      setupDefaultMocks()

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.loadData({ filterChantierId: 5 })
      })

      expect(formulairesService.listFormulaires).toHaveBeenCalledWith({
        chantier_id: 5,
        template_id: undefined,
      })
    })

    it('should use empty arrays as fallback when API returns empty', async () => {
      vi.mocked(formulairesService.listTemplates).mockResolvedValue({
        templates: [],
        total: 0,
        skip: 0,
        limit: 50,
      })
      vi.mocked(formulairesService.listFormulaires).mockResolvedValue({
        formulaires: [],
        total: 0,
        skip: 0,
        limit: 50,
      })
      vi.mocked(chantiersService.list).mockResolvedValue({
        items: [],
        total: 0,
        page: 1,
        size: 100,
        pages: 1,
      })

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.loadData()
      })

      // Falls back to MOCK_ constants when API returns empty
      expect(result.current.templates.length).toBeGreaterThan(0)
      expect(result.current.formulaires.length).toBeGreaterThan(0)
      expect(result.current.chantiers).toEqual([])
    })

    it('should handle errors and use mock data', async () => {
      vi.mocked(formulairesService.listTemplates).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.loadData()
      })

      expect(result.current.loading).toBe(false)
      expect(logger.error).toHaveBeenCalledWith(
        'Error loading data, using mocks',
        expect.any(Error),
        { context: 'useFormulairesData' }
      )
      // Fallback to MOCK_ data on error
      expect(result.current.templates.length).toBeGreaterThan(0)
      expect(result.current.formulaires.length).toBeGreaterThan(0)
      expect(result.current.chantiers).toEqual([])
    })
  })

  describe('setError', () => {
    it('should allow setting error manually', async () => {
      setupDefaultMocks()
      const { result } = renderHook(() => useFormulairesData())

      act(() => {
        result.current.setError('Custom error')
      })

      expect(result.current.error).toBe('Custom error')
    })
  })

  describe('template CRUD', () => {
    it('createTemplate should call service and reload data', async () => {
      setupDefaultMocks()
      vi.mocked(formulairesService.createTemplate).mockResolvedValue({} as any)

      const { result } = renderHook(() => useFormulairesData())

      const newTemplate = {
        nom: 'New Template',
        categorie: 'securite' as any,
        description: 'desc',
        champs: [],
      }

      await act(async () => {
        await result.current.createTemplate(newTemplate)
      })

      expect(formulairesService.createTemplate).toHaveBeenCalledWith(newTemplate)
      // loadData is called after create
      expect(formulairesService.listTemplates).toHaveBeenCalled()
    })

    it('updateTemplate should call service and reload data', async () => {
      setupDefaultMocks()
      vi.mocked(formulairesService.updateTemplate).mockResolvedValue({} as any)

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.updateTemplate(1, { nom: 'Updated' })
      })

      expect(formulairesService.updateTemplate).toHaveBeenCalledWith(1, { nom: 'Updated' })
    })

    it('deleteTemplate should call service and reload data', async () => {
      setupDefaultMocks()
      vi.mocked(formulairesService.deleteTemplate).mockResolvedValue(undefined as any)

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.deleteTemplate(1)
      })

      expect(formulairesService.deleteTemplate).toHaveBeenCalledWith(1)
    })

    it('duplicateTemplate should create with "(copie)" suffix', async () => {
      setupDefaultMocks()
      vi.mocked(formulairesService.createTemplate).mockResolvedValue({} as any)

      const { result } = renderHook(() => useFormulairesData())

      const template = {
        id: 1,
        nom: 'Original',
        categorie: 'securite' as any,
        description: 'desc',
        champs: [],
        is_active: true,
        created_at: '2026-01-01',
        updated_at: '2026-01-01',
      }

      await act(async () => {
        await result.current.duplicateTemplate(template as any)
      })

      expect(formulairesService.createTemplate).toHaveBeenCalledWith({
        nom: 'Original (copie)',
        categorie: 'securite',
        description: 'desc',
        champs: [],
      })
    })

    it('toggleTemplateActive should toggle is_active', async () => {
      setupDefaultMocks()
      vi.mocked(formulairesService.updateTemplate).mockResolvedValue({} as any)

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.toggleTemplateActive(1, true)
      })

      expect(formulairesService.updateTemplate).toHaveBeenCalledWith(1, { is_active: false })
    })

    it('getTemplate should return template from service', async () => {
      const template = { id: 1, nom: 'Test' } as any
      vi.mocked(formulairesService.getTemplate).mockResolvedValue(template)

      const { result } = renderHook(() => useFormulairesData())

      let returnedTemplate: any
      await act(async () => {
        returnedTemplate = await result.current.getTemplate(1)
      })

      expect(formulairesService.getTemplate).toHaveBeenCalledWith(1)
      expect(returnedTemplate).toEqual(template)
    })
  })

  describe('formulaire CRUD', () => {
    it('createFormulaire should call service with template and chantier ids', async () => {
      const created = { id: 10, template_id: 1, chantier_id: 2 } as any
      vi.mocked(formulairesService.createFormulaire).mockResolvedValue(created)

      const { result } = renderHook(() => useFormulairesData())

      let returnedFormulaire: any
      await act(async () => {
        returnedFormulaire = await result.current.createFormulaire(1, 2)
      })

      expect(formulairesService.createFormulaire).toHaveBeenCalledWith({
        template_id: 1,
        chantier_id: 2,
      })
      expect(returnedFormulaire).toEqual(created)
    })

    it('getFormulaire should return formulaire from service', async () => {
      const formulaire = { id: 10 } as any
      vi.mocked(formulairesService.getFormulaire).mockResolvedValue(formulaire)

      const { result } = renderHook(() => useFormulairesData())

      let returned: any
      await act(async () => {
        returned = await result.current.getFormulaire(10)
      })

      expect(returned).toEqual(formulaire)
    })

    it('updateFormulaire should call service and reload data', async () => {
      setupDefaultMocks()
      const updated = { id: 10, valeurs: { field: 'value' } } as any
      vi.mocked(formulairesService.updateFormulaire).mockResolvedValue(updated)

      const { result } = renderHook(() => useFormulairesData())

      let returned: any
      await act(async () => {
        returned = await result.current.updateFormulaire(10, { valeurs: { field: 'value' } } as any)
      })

      expect(returned).toEqual(updated)
    })

    it('submitFormulaire should call service with optional signature', async () => {
      setupDefaultMocks()
      vi.mocked(formulairesService.submitFormulaire).mockResolvedValue(undefined as any)

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.submitFormulaire(10, 'http://sig.png', 'John')
      })

      expect(formulairesService.submitFormulaire).toHaveBeenCalledWith(10, 'http://sig.png', 'John')
    })

    it('validateFormulaire should call service and reload data', async () => {
      setupDefaultMocks()
      vi.mocked(formulairesService.validateFormulaire).mockResolvedValue(undefined as any)

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.validateFormulaire(10)
      })

      expect(formulairesService.validateFormulaire).toHaveBeenCalledWith(10)
    })

    it('rejectFormulaire should call service and reload data', async () => {
      setupDefaultMocks()
      vi.mocked(formulairesService.rejectFormulaire).mockResolvedValue(undefined as any)

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.rejectFormulaire(10)
      })

      expect(formulairesService.rejectFormulaire).toHaveBeenCalledWith(10)
    })

    it('exportPDF should call downloadPDF service', async () => {
      vi.mocked(formulairesService.downloadPDF).mockResolvedValue(undefined as any)

      const { result } = renderHook(() => useFormulairesData())

      await act(async () => {
        await result.current.exportPDF(10)
      })

      expect(formulairesService.downloadPDF).toHaveBeenCalledWith(10)
    })
  })
})
