/**
 * Tests unitaires pour useTemplateForm
 * Hook de gestion du formulaire de template
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTemplateForm } from './useTemplateForm'

const mockTemplate: any = {
  id: 1,
  nom: 'Rapport journalier',
  categorie: 'rapport_journalier',
  description: 'Description',
  champs: [
    { nom: 'champ1', label: 'Champ 1', type_champ: 'texte', obligatoire: false, ordre: 0, placeholder: '', options: [] },
  ],
  is_active: true,
  created_at: '2024-01-01',
}

describe('useTemplateForm', () => {
  const defaultProps = {
    template: null as any,
    isOpen: true,
    onSave: vi.fn().mockResolvedValue(undefined),
    onClose: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initialise un formulaire vide en mode creation', () => {
    // Arrange & Act
    const { result } = renderHook(() => useTemplateForm(defaultProps))

    // Assert
    expect(result.current.isEditing).toBe(false)
    expect(result.current.formData.nom).toBe('')
    expect(result.current.formData.categorie).toBe('autre')
    expect(result.current.formData.description).toBe('')
    expect(result.current.formData.champs).toEqual([])
  })

  it('initialise avec les donnees du template en mode edition', () => {
    // Arrange & Act
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, template: mockTemplate })
    )

    // Assert
    expect(result.current.isEditing).toBe(true)
    expect(result.current.formData.nom).toBe('Rapport journalier')
    expect(result.current.formData.categorie).toBe('rapport_journalier')
    expect(result.current.formData.description).toBe('Description')
    expect(result.current.formData.champs).toHaveLength(1)
  })

  it('addChamp ajoute un champ vide', () => {
    // Arrange
    const { result } = renderHook(() => useTemplateForm(defaultProps))

    // Act
    act(() => {
      result.current.addChamp()
    })

    // Assert
    expect(result.current.formData.champs).toHaveLength(1)
    expect(result.current.formData.champs![0].nom).toBe('')
    expect(result.current.formData.champs![0].label).toBe('')
    expect(result.current.formData.champs![0].type_champ).toBe('texte')
  })

  it('updateChamp met a jour un champ existant', () => {
    // Arrange
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, template: mockTemplate })
    )

    // Act
    act(() => {
      result.current.updateChamp(0, { label: 'Nouveau Label' })
    })

    // Assert
    expect(result.current.formData.champs![0].label).toBe('Nouveau Label')
  })

  it('removeChamp supprime un champ', () => {
    // Arrange
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, template: mockTemplate })
    )
    expect(result.current.formData.champs).toHaveLength(1)

    // Act
    act(() => {
      result.current.removeChamp(0)
    })

    // Assert
    expect(result.current.formData.champs).toHaveLength(0)
  })

  it('moveChamp deplace un champ vers le haut', () => {
    // Arrange
    const templateWithChamps: any = {
      ...mockTemplate,
      champs: [
        { nom: 'a', label: 'A', type_champ: 'texte', obligatoire: false, ordre: 0, placeholder: '', options: [] },
        { nom: 'b', label: 'B', type_champ: 'texte', obligatoire: false, ordre: 1, placeholder: '', options: [] },
      ],
    }
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, template: templateWithChamps })
    )

    // Act
    act(() => {
      result.current.moveChamp(1, 'up')
    })

    // Assert
    expect(result.current.formData.champs![0].label).toBe('B')
    expect(result.current.formData.champs![1].label).toBe('A')
  })

  it('moveChamp deplace un champ vers le bas', () => {
    // Arrange
    const templateWithChamps: any = {
      ...mockTemplate,
      champs: [
        { nom: 'a', label: 'A', type_champ: 'texte', obligatoire: false, ordre: 0, placeholder: '', options: [] },
        { nom: 'b', label: 'B', type_champ: 'texte', obligatoire: false, ordre: 1, placeholder: '', options: [] },
      ],
    }
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, template: templateWithChamps })
    )

    // Act
    act(() => {
      result.current.moveChamp(0, 'down')
    })

    // Assert
    expect(result.current.formData.champs![0].label).toBe('B')
    expect(result.current.formData.champs![1].label).toBe('A')
  })

  it('moveChamp ne fait rien si l\'index est hors limites', () => {
    // Arrange
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, template: mockTemplate })
    )

    // Act
    act(() => {
      result.current.moveChamp(0, 'up') // deja en premiere position
    })

    // Assert
    expect(result.current.formData.champs![0].label).toBe('Champ 1')
  })

  it('updateFormField met a jour un champ du formulaire', () => {
    // Arrange
    const { result } = renderHook(() => useTemplateForm(defaultProps))

    // Act
    act(() => {
      result.current.updateFormField('nom', 'Nouveau nom')
    })

    // Assert
    expect(result.current.formData.nom).toBe('Nouveau nom')
  })

  it('handleSubmit valide le nom requis', async () => {
    // Arrange
    const { result } = renderHook(() => useTemplateForm(defaultProps))
    const mockEvent = { preventDefault: vi.fn() } as any

    // Act
    await act(async () => {
      await result.current.handleSubmit(mockEvent)
    })

    // Assert
    expect(mockEvent.preventDefault).toHaveBeenCalled()
    expect(result.current.error).toBe('Le nom du template est requis')
    expect(defaultProps.onSave).not.toHaveBeenCalled()
  })

  it('handleSubmit valide les champs avec nom et label', async () => {
    // Arrange
    const { result } = renderHook(() => useTemplateForm(defaultProps))
    const mockEvent = { preventDefault: vi.fn() } as any

    // D'abord mettre le nom, puis ajouter un champ vide
    act(() => {
      result.current.updateFormField('nom', 'Mon template')
    })
    act(() => {
      result.current.addChamp() // ajoute un champ vide (sans nom/label)
    })

    // Act
    await act(async () => {
      await result.current.handleSubmit(mockEvent)
    })

    // Assert
    expect(result.current.error).toContain('doit avoir un nom et un label')
  })

  it('handleSubmit valide les options pour select/radio/multi_select', async () => {
    // Arrange
    const templateSelect: any = {
      ...mockTemplate,
      champs: [
        { nom: 'select1', label: 'Select 1', type_champ: 'select', obligatoire: false, ordre: 0, placeholder: '', options: [] },
      ],
    }
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, template: templateSelect })
    )
    const mockEvent = { preventDefault: vi.fn() } as any

    // Act
    await act(async () => {
      await result.current.handleSubmit(mockEvent)
    })

    // Assert
    expect(result.current.error).toContain('doit avoir au moins une option')
  })

  it('handleSubmit appelle onSave avec les donnees formatees', async () => {
    // Arrange
    const onSave = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, onSave, template: mockTemplate })
    )
    const mockEvent = { preventDefault: vi.fn() } as any

    // Act
    await act(async () => {
      await result.current.handleSubmit(mockEvent)
    })

    // Assert
    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({
        nom: 'Rapport journalier',
        categorie: 'rapport_journalier',
      })
    )
  })

  it('handleSubmit appelle onClose apres succes', async () => {
    // Arrange
    const onClose = vi.fn()
    const onSave = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, onSave, onClose, template: mockTemplate })
    )
    const mockEvent = { preventDefault: vi.fn() } as any

    // Act
    await act(async () => {
      await result.current.handleSubmit(mockEvent)
    })

    // Assert
    expect(onClose).toHaveBeenCalled()
  })

  it('handleSubmit gere les erreurs', async () => {
    // Arrange
    const onSave = vi.fn().mockRejectedValue(new Error('Erreur serveur'))
    const { result } = renderHook(() =>
      useTemplateForm({ ...defaultProps, onSave, template: mockTemplate })
    )
    const mockEvent = { preventDefault: vi.fn() } as any

    // Act
    await act(async () => {
      await result.current.handleSubmit(mockEvent)
    })

    // Assert
    expect(result.current.error).toBe('Erreur serveur')
  })
})
