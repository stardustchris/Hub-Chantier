/**
 * Tests unitaires pour usePointageForm hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { usePointageForm } from './usePointageForm'
import type { Pointage } from '../../types'

// Mock logger
vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

// Mock confirm
vi.stubGlobal('confirm', vi.fn(() => true))

const mockOnSave = vi.fn()
const mockOnDelete = vi.fn()
const mockOnSign = vi.fn()
const mockOnSubmit = vi.fn()
const mockOnValidate = vi.fn()
const mockOnReject = vi.fn()
const mockOnClose = vi.fn()

const defaultProps = {
  isOpen: true,
  pointage: null,
  selectedDate: new Date('2026-01-25'),
  selectedUserId: 1,
  selectedChantierId: 1,
  onSave: mockOnSave,
  onDelete: mockOnDelete,
  onSign: mockOnSign,
  onSubmit: mockOnSubmit,
  onValidate: mockOnValidate,
  onReject: mockOnReject,
  onClose: mockOnClose,
}

const mockPointage: Pointage = {
  id: 1,
  utilisateur_id: 1,
  chantier_id: 2,
  date_pointage: '2026-01-25',
  heures_normales: '08:00',
  heures_supplementaires: '02:00',
  commentaire: 'Test commentaire',
  statut: 'brouillon',
}

describe('usePointageForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('initialise avec valeurs par defaut sans pointage', () => {
      const { result } = renderHook(() => usePointageForm(defaultProps))

      expect(result.current.chantierId).toBe(1)
      expect(result.current.heuresNormales).toBe('07:00')
      expect(result.current.heuresSupplementaires).toBe('00:00')
      expect(result.current.commentaire).toBe('')
      expect(result.current.isEditing).toBe(false)
      expect(result.current.isEditable).toBe(true)
    })

    it('initialise avec valeurs du pointage existant', () => {
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      expect(result.current.chantierId).toBe(2)
      expect(result.current.heuresNormales).toBe('08:00')
      expect(result.current.heuresSupplementaires).toBe('02:00')
      expect(result.current.commentaire).toBe('Test commentaire')
      expect(result.current.isEditing).toBe(true)
    })

    it('reset quand modal ferme et rouvre', () => {
      const { result, rerender } = renderHook(
        ({ isOpen }) => usePointageForm({ ...defaultProps, isOpen }),
        { initialProps: { isOpen: true } }
      )

      act(() => {
        result.current.setCommentaire('Modified')
      })

      rerender({ isOpen: false })
      rerender({ isOpen: true })

      expect(result.current.commentaire).toBe('')
    })
  })

  describe('isEditable', () => {
    it('true pour nouveau pointage', () => {
      const { result } = renderHook(() => usePointageForm(defaultProps))
      expect(result.current.isEditable).toBe(true)
    })

    it('true pour pointage brouillon', () => {
      const { result } = renderHook(() =>
        usePointageForm({
          ...defaultProps,
          pointage: { ...mockPointage, statut: 'brouillon' },
        })
      )
      expect(result.current.isEditable).toBe(true)
    })

    it('true pour pointage rejete', () => {
      const { result } = renderHook(() =>
        usePointageForm({
          ...defaultProps,
          pointage: { ...mockPointage, statut: 'rejete' },
        })
      )
      expect(result.current.isEditable).toBe(true)
    })

    it('false pour pointage soumis', () => {
      const { result } = renderHook(() =>
        usePointageForm({
          ...defaultProps,
          pointage: { ...mockPointage, statut: 'soumis' },
        })
      )
      expect(result.current.isEditable).toBe(false)
    })

    it('false pour pointage valide', () => {
      const { result } = renderHook(() =>
        usePointageForm({
          ...defaultProps,
          pointage: { ...mockPointage, statut: 'valide' },
        })
      )
      expect(result.current.isEditable).toBe(false)
    })
  })

  describe('state setters', () => {
    it('met a jour chantierId', () => {
      const { result } = renderHook(() => usePointageForm(defaultProps))

      act(() => {
        result.current.setChantierId(5)
      })

      expect(result.current.chantierId).toBe(5)
    })

    it('met a jour heuresNormales', () => {
      const { result } = renderHook(() => usePointageForm(defaultProps))

      act(() => {
        result.current.setHeuresNormales('09:00')
      })

      expect(result.current.heuresNormales).toBe('09:00')
    })

    it('met a jour heuresSupplementaires', () => {
      const { result } = renderHook(() => usePointageForm(defaultProps))

      act(() => {
        result.current.setHeuresSupplementaires('03:00')
      })

      expect(result.current.heuresSupplementaires).toBe('03:00')
    })

    it('met a jour commentaire', () => {
      const { result } = renderHook(() => usePointageForm(defaultProps))

      act(() => {
        result.current.setCommentaire('Mon commentaire')
      })

      expect(result.current.commentaire).toBe('Mon commentaire')
    })

    it('met a jour signature', () => {
      const { result } = renderHook(() => usePointageForm(defaultProps))

      act(() => {
        result.current.setSignature('Ma Signature')
      })

      expect(result.current.signature).toBe('Ma Signature')
    })

    it('met a jour motifRejet', () => {
      const { result } = renderHook(() => usePointageForm(defaultProps))

      act(() => {
        result.current.setMotifRejet('Heures incorrectes')
      })

      expect(result.current.motifRejet).toBe('Heures incorrectes')
    })

    it('toggle showRejectForm', () => {
      const { result } = renderHook(() => usePointageForm(defaultProps))

      act(() => {
        result.current.setShowRejectForm(true)
      })

      expect(result.current.showRejectForm).toBe(true)
    })
  })

  describe('handleSubmit', () => {
    it('affiche erreur si pas de chantier', async () => {
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, selectedChantierId: undefined })
      )

      const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

      await act(async () => {
        await result.current.handleSubmit(mockEvent)
      })

      expect(result.current.error).toBe('Veuillez selectionner un chantier')
      expect(mockOnSave).not.toHaveBeenCalled()
    })

    it('cree un nouveau pointage', async () => {
      mockOnSave.mockResolvedValue(undefined)
      const { result } = renderHook(() => usePointageForm(defaultProps))

      const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

      await act(async () => {
        await result.current.handleSubmit(mockEvent)
      })

      expect(mockOnSave).toHaveBeenCalledWith(
        expect.objectContaining({
          utilisateur_id: 1,
          chantier_id: 1,
          date_pointage: '2026-01-25',
          heures_normales: '07:00',
          heures_supplementaires: '00:00',
        })
      )
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('met a jour un pointage existant', async () => {
      mockOnSave.mockResolvedValue(undefined)
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

      await act(async () => {
        await result.current.handleSubmit(mockEvent)
      })

      expect(mockOnSave).toHaveBeenCalledWith(
        expect.objectContaining({
          heures_normales: '08:00',
          heures_supplementaires: '02:00',
        })
      )
    })

    it('gere les erreurs de sauvegarde', async () => {
      mockOnSave.mockRejectedValue(new Error('Save failed'))
      const { result } = renderHook(() => usePointageForm(defaultProps))

      const mockEvent = { preventDefault: vi.fn() } as unknown as React.FormEvent

      await act(async () => {
        await result.current.handleSubmit(mockEvent)
      })

      expect(result.current.error).toBe("Erreur lors de l'enregistrement")
      expect(result.current.saving).toBe(false)
    })
  })

  describe('handleDelete', () => {
    it('supprime le pointage apres confirmation', async () => {
      mockOnDelete.mockResolvedValue(undefined)
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      await act(async () => {
        await result.current.handleDelete()
      })

      expect(mockOnDelete).toHaveBeenCalled()
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('ne supprime pas si annule', async () => {
      vi.mocked(confirm).mockReturnValueOnce(false)
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      await act(async () => {
        await result.current.handleDelete()
      })

      expect(mockOnDelete).not.toHaveBeenCalled()
    })
  })

  describe('handleSign', () => {
    it('signe avec signature valide', async () => {
      mockOnSign.mockResolvedValue(undefined)
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      act(() => {
        result.current.setSignature('John Doe')
      })

      await act(async () => {
        await result.current.handleSign()
      })

      expect(mockOnSign).toHaveBeenCalledWith('John Doe')
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('affiche erreur si signature vide', async () => {
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      await act(async () => {
        await result.current.handleSign()
      })

      expect(result.current.error).toBe('Veuillez saisir votre signature')
      expect(mockOnSign).not.toHaveBeenCalled()
    })
  })

  describe('handleSubmitForValidation', () => {
    it('soumet pour validation', async () => {
      mockOnSubmit.mockResolvedValue(undefined)
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      await act(async () => {
        await result.current.handleSubmitForValidation()
      })

      expect(mockOnSubmit).toHaveBeenCalled()
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('handleValidate', () => {
    it('valide le pointage', async () => {
      mockOnValidate.mockResolvedValue(undefined)
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      await act(async () => {
        await result.current.handleValidate()
      })

      expect(mockOnValidate).toHaveBeenCalled()
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('handleReject', () => {
    it('rejette avec motif valide', async () => {
      mockOnReject.mockResolvedValue(undefined)
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      act(() => {
        result.current.setMotifRejet('Heures incorrectes')
      })

      await act(async () => {
        await result.current.handleReject()
      })

      expect(mockOnReject).toHaveBeenCalledWith('Heures incorrectes')
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('affiche erreur si motif vide', async () => {
      const { result } = renderHook(() =>
        usePointageForm({ ...defaultProps, pointage: mockPointage })
      )

      await act(async () => {
        await result.current.handleReject()
      })

      expect(result.current.error).toBe('Veuillez saisir un motif de rejet')
      expect(mockOnReject).not.toHaveBeenCalled()
    })
  })
})
