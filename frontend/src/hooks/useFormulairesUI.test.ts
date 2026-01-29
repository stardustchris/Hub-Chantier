// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import { useFormulairesUI } from './useFormulairesUI'
import type { TemplateFormulaire, FormulaireRempli } from '../types'

const mockTemplate: Partial<TemplateFormulaire> = {
  id: 1,
  nom: 'Template Test',
  categorie: 'securite' as any,
  description: 'desc',
  champs: [],
  is_active: true,
}

const mockFormulaire: Partial<FormulaireRempli> = {
  id: 10,
  template_id: 1,
  chantier_id: 1,
  statut: 'brouillon' as any,
  champs: [],
}

function wrapper({ children }: { children: React.ReactNode }) {
  return React.createElement(MemoryRouter, null, children)
}

describe('useFormulairesUI', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have correct default values', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      expect(result.current.activeTab).toBe('formulaires')
      expect(result.current.selectedTemplate).toBeNull()
      expect(result.current.selectedFormulaire).toBeNull()
      expect(result.current.selectedChantierId).toBeNull()
      expect(result.current.templateModalOpen).toBe(false)
      expect(result.current.formulaireModalOpen).toBe(false)
      expect(result.current.newFormulaireModalOpen).toBe(false)
      expect(result.current.formulaireReadOnly).toBe(false)
    })
  })

  describe('tab management', () => {
    it('should change active tab', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.handleTabChange('templates')
      })

      expect(result.current.activeTab).toBe('templates')
    })

    it('should switch back to formulaires tab', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.handleTabChange('templates')
      })
      act(() => {
        result.current.handleTabChange('formulaires')
      })

      expect(result.current.activeTab).toBe('formulaires')
    })

    it('should sync tab from URL search params', () => {
      function wrapperWithParams({ children }: { children: React.ReactNode }) {
        return React.createElement(
          MemoryRouter,
          { initialEntries: ['/?tab=templates'] },
          children
        )
      }

      const { result } = renderHook(() => useFormulairesUI(), {
        wrapper: wrapperWithParams,
      })

      expect(result.current.activeTab).toBe('templates')
    })
  })

  describe('selection state', () => {
    it('should set selected template', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.setSelectedTemplate(mockTemplate as TemplateFormulaire)
      })

      expect(result.current.selectedTemplate).toEqual(mockTemplate)
    })

    it('should set selected formulaire', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.setSelectedFormulaire(mockFormulaire as FormulaireRempli)
      })

      expect(result.current.selectedFormulaire).toEqual(mockFormulaire)
    })

    it('should set selected chantier id', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.setSelectedChantierId('5')
      })

      expect(result.current.selectedChantierId).toBe('5')
    })
  })

  describe('template modal actions', () => {
    it('openNewTemplateModal should clear selected and open modal', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.openNewTemplateModal()
      })

      expect(result.current.templateModalOpen).toBe(true)
      expect(result.current.selectedTemplate).toBeNull()
    })

    it('openEditTemplateModal should set template and open modal', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.openEditTemplateModal(mockTemplate as TemplateFormulaire)
      })

      expect(result.current.templateModalOpen).toBe(true)
      expect(result.current.selectedTemplate).toEqual(mockTemplate)
    })

    it('openPreviewTemplateModal should set template, readOnly and open formulaire modal', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.openPreviewTemplateModal(mockTemplate as TemplateFormulaire)
      })

      expect(result.current.formulaireModalOpen).toBe(true)
      expect(result.current.selectedTemplate).toEqual(mockTemplate)
      expect(result.current.selectedFormulaire).toBeNull()
      expect(result.current.formulaireReadOnly).toBe(true)
    })

    it('closeTemplateModal should close modal and clear selected template', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.openEditTemplateModal(mockTemplate as TemplateFormulaire)
      })

      act(() => {
        result.current.closeTemplateModal()
      })

      expect(result.current.templateModalOpen).toBe(false)
      expect(result.current.selectedTemplate).toBeNull()
    })
  })

  describe('formulaire modal actions', () => {
    it('openNewFormulaireModal should open new formulaire modal', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.openNewFormulaireModal()
      })

      expect(result.current.newFormulaireModalOpen).toBe(true)
    })

    it('openViewFormulaireModal should set readOnly to true', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.openViewFormulaireModal(
          mockFormulaire as FormulaireRempli,
          mockTemplate as TemplateFormulaire
        )
      })

      expect(result.current.formulaireModalOpen).toBe(true)
      expect(result.current.formulaireReadOnly).toBe(true)
      expect(result.current.selectedTemplate).toEqual(mockTemplate)
      expect(result.current.selectedFormulaire).toEqual(mockFormulaire)
    })

    it('openEditFormulaireModal should set readOnly to false', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.openEditFormulaireModal(
          mockFormulaire as FormulaireRempli,
          mockTemplate as TemplateFormulaire
        )
      })

      expect(result.current.formulaireModalOpen).toBe(true)
      expect(result.current.formulaireReadOnly).toBe(false)
      expect(result.current.selectedTemplate).toEqual(mockTemplate)
      expect(result.current.selectedFormulaire).toEqual(mockFormulaire)
    })

    it('openCreatedFormulaireModal should open formulaire modal and close new formulaire modal', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      // First open the new formulaire modal
      act(() => {
        result.current.openNewFormulaireModal()
      })
      expect(result.current.newFormulaireModalOpen).toBe(true)

      // Then open the created formulaire modal
      act(() => {
        result.current.openCreatedFormulaireModal(
          mockFormulaire as FormulaireRempli,
          mockTemplate as TemplateFormulaire
        )
      })

      expect(result.current.formulaireModalOpen).toBe(true)
      expect(result.current.newFormulaireModalOpen).toBe(false)
      expect(result.current.formulaireReadOnly).toBe(false)
      expect(result.current.selectedTemplate).toEqual(mockTemplate)
      expect(result.current.selectedFormulaire).toEqual(mockFormulaire)
    })

    it('closeNewFormulaireModal should close new formulaire modal', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.openNewFormulaireModal()
      })

      act(() => {
        result.current.closeNewFormulaireModal()
      })

      expect(result.current.newFormulaireModalOpen).toBe(false)
    })

    it('closeFormulaireModal should close modal and clear selections', () => {
      const { result } = renderHook(() => useFormulairesUI(), { wrapper })

      act(() => {
        result.current.openEditFormulaireModal(
          mockFormulaire as FormulaireRempli,
          mockTemplate as TemplateFormulaire
        )
      })

      act(() => {
        result.current.closeFormulaireModal()
      })

      expect(result.current.formulaireModalOpen).toBe(false)
      expect(result.current.selectedFormulaire).toBeNull()
      expect(result.current.selectedTemplate).toBeNull()
    })
  })
})
