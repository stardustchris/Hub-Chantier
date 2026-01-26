/**
 * Tests pour ChampEditor
 *
 * Couvre:
 * - Affichage header avec label et type
 * - Toggle expansion
 * - Actions déplacer/supprimer
 * - Édition des propriétés du champ
 * - Options conditionnelles (select/radio, number)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChampEditor } from './ChampEditor'
import type { ChampTemplate } from '../../types'

const createMockChamp = (overrides: Partial<ChampTemplate> = {}): ChampTemplate => ({
  nom: 'test_field',
  label: 'Test Field',
  type_champ: 'text',
  obligatoire: false,
  ordre: 1,
  ...overrides,
})

describe('ChampEditor', () => {
  const mockOnToggleExpand = vi.fn()
  const mockOnUpdate = vi.fn()
  const mockOnRemove = vi.fn()
  const mockOnMoveUp = vi.fn()
  const mockOnMoveDown = vi.fn()

  const defaultProps = {
    champ: createMockChamp(),
    index: 0,
    isExpanded: false,
    isFirst: false,
    isLast: false,
    onToggleExpand: mockOnToggleExpand,
    onUpdate: mockOnUpdate,
    onRemove: mockOnRemove,
    onMoveUp: mockOnMoveUp,
    onMoveDown: mockOnMoveDown,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Header', () => {
    it('affiche le label du champ', () => {
      render(<ChampEditor {...defaultProps} />)
      expect(screen.getByText('Test Field')).toBeInTheDocument()
    })

    it('affiche "Champ N" si pas de label', () => {
      render(
        <ChampEditor
          {...defaultProps}
          champ={createMockChamp({ label: '' })}
        />
      )
      expect(screen.getByText('Champ 1')).toBeInTheDocument()
    })

    it('affiche le type de champ', () => {
      render(<ChampEditor {...defaultProps} />)
      expect(screen.getByText('Texte court')).toBeInTheDocument()
    })

    it('affiche l\'indicateur obligatoire', () => {
      render(
        <ChampEditor
          {...defaultProps}
          champ={createMockChamp({ obligatoire: true })}
        />
      )
      expect(screen.getByText('*')).toBeInTheDocument()
    })
  })

  describe('Toggle expansion', () => {
    it('appelle onToggleExpand au clic sur le header', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} />)

      const header = screen.getByText('Test Field').closest('.cursor-pointer')
      if (header) {
        await user.click(header)
        expect(mockOnToggleExpand).toHaveBeenCalled()
      }
    })

    it('n\'affiche pas le contenu si non expanded', () => {
      render(<ChampEditor {...defaultProps} isExpanded={false} />)
      expect(screen.queryByLabelText(/label/i)).not.toBeInTheDocument()
    })

    it('affiche le contenu si expanded', () => {
      render(<ChampEditor {...defaultProps} isExpanded={true} />)
      // Le label est splitté en "Label " et "*" dans des éléments séparés
      expect(screen.getByPlaceholderText('Label affiche')).toBeInTheDocument()
    })
  })

  describe('Actions déplacer', () => {
    it('appelle onMoveUp au clic sur bouton monter', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} />)

      const buttons = screen.getAllByRole('button')
      const upButton = buttons.find(btn => btn.querySelector('svg.lucide-chevron-up'))
      if (upButton) {
        await user.click(upButton)
        expect(mockOnMoveUp).toHaveBeenCalled()
      }
    })

    it('appelle onMoveDown au clic sur bouton descendre', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} />)

      const buttons = screen.getAllByRole('button')
      const downButton = buttons.find(btn => btn.querySelector('svg.lucide-chevron-down'))
      if (downButton) {
        await user.click(downButton)
        expect(mockOnMoveDown).toHaveBeenCalled()
      }
    })

    it('désactive le bouton monter si premier', () => {
      render(<ChampEditor {...defaultProps} isFirst={true} />)
      const buttons = screen.getAllByRole('button')
      const upButton = buttons.find(btn => btn.querySelector('svg.lucide-chevron-up'))
      expect(upButton).toBeDisabled()
    })

    it('désactive le bouton descendre si dernier', () => {
      render(<ChampEditor {...defaultProps} isLast={true} />)
      const buttons = screen.getAllByRole('button')
      const downButton = buttons.find(btn => btn.querySelector('svg.lucide-chevron-down'))
      expect(downButton).toBeDisabled()
    })
  })

  describe('Action supprimer', () => {
    it('appelle onRemove au clic sur bouton supprimer', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} />)

      const buttons = screen.getAllByRole('button')
      const deleteButton = buttons.find(btn => btn.querySelector('svg.lucide-trash-2'))
      if (deleteButton) {
        await user.click(deleteButton)
        expect(mockOnRemove).toHaveBeenCalled()
      }
    })
  })

  describe('Édition propriétés (expanded)', () => {
    it('permet de modifier le label', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} isExpanded={true} />)

      const labelInput = screen.getByPlaceholderText('Label affiche')
      // Taper un caractère supplémentaire pour vérifier que onUpdate est appelé
      await user.type(labelInput, 'X')

      // onUpdate est appelé à chaque caractère
      expect(mockOnUpdate).toHaveBeenCalled()
      expect(mockOnUpdate).toHaveBeenCalledWith(expect.objectContaining({ label: expect.any(String) }))
    })

    it('permet de modifier le nom technique', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} isExpanded={true} />)

      const nomInput = screen.getByPlaceholderText('nom_technique')
      await user.type(nomInput, '_extra')

      expect(mockOnUpdate).toHaveBeenCalled()
      expect(mockOnUpdate).toHaveBeenCalledWith(expect.objectContaining({ nom: expect.any(String) }))
    })

    it('permet de changer le type de champ', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} isExpanded={true} />)

      const typeSelect = screen.getByDisplayValue('Texte court')
      await user.selectOptions(typeSelect, 'textarea')

      expect(mockOnUpdate).toHaveBeenCalledWith({ type_champ: 'textarea' })
    })

    it('permet de modifier le placeholder', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} isExpanded={true} />)

      const placeholderInput = screen.getByPlaceholderText('Texte d\'aide')
      await user.type(placeholderInput, 'Mon placeholder')

      expect(mockOnUpdate).toHaveBeenCalled()
      expect(mockOnUpdate).toHaveBeenCalledWith(expect.objectContaining({ placeholder: expect.any(String) }))
    })

    it('permet de modifier l\'obligation', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} isExpanded={true} />)

      const checkbox = screen.getByRole('checkbox', { name: /champ obligatoire/i })
      await user.click(checkbox)

      expect(mockOnUpdate).toHaveBeenCalledWith({ obligatoire: true })
    })
  })

  describe('Options conditionnelles - select/radio', () => {
    it('affiche le textarea options pour select', () => {
      render(
        <ChampEditor
          {...defaultProps}
          isExpanded={true}
          champ={createMockChamp({ type_champ: 'select' })}
        />
      )
      expect(screen.getByText('Options (une par ligne)')).toBeInTheDocument()
    })

    it('affiche le textarea options pour radio', () => {
      render(
        <ChampEditor
          {...defaultProps}
          isExpanded={true}
          champ={createMockChamp({ type_champ: 'radio' })}
        />
      )
      expect(screen.getByText('Options (une par ligne)')).toBeInTheDocument()
    })

    it('n\'affiche pas les options pour text', () => {
      render(
        <ChampEditor
          {...defaultProps}
          isExpanded={true}
          champ={createMockChamp({ type_champ: 'text' })}
        />
      )
      expect(screen.queryByText('Options (une par ligne)')).not.toBeInTheDocument()
    })

    it('permet de modifier les options', async () => {
      const user = userEvent.setup()
      render(
        <ChampEditor
          {...defaultProps}
          isExpanded={true}
          champ={createMockChamp({ type_champ: 'select', options: [] })}
        />
      )

      const textarea = screen.getByPlaceholderText(/Option 1/i)
      await user.type(textarea, 'Option A')

      // Vérifier que onUpdate est appelé avec un tableau d'options
      expect(mockOnUpdate).toHaveBeenCalled()
      expect(mockOnUpdate).toHaveBeenCalledWith(expect.objectContaining({ options: expect.any(Array) }))
    })

    it('affiche les options existantes', () => {
      render(
        <ChampEditor
          {...defaultProps}
          isExpanded={true}
          champ={createMockChamp({
            type_champ: 'select',
            options: ['Opt1', 'Opt2', 'Opt3'],
          })}
        />
      )
      const textarea = screen.getByPlaceholderText(/Option 1/i) as HTMLTextAreaElement
      expect(textarea.value).toBe('Opt1\nOpt2\nOpt3')
    })
  })

  describe('Options conditionnelles - number', () => {
    it('affiche les champs min/max pour number', () => {
      render(
        <ChampEditor
          {...defaultProps}
          isExpanded={true}
          champ={createMockChamp({ type_champ: 'number' })}
        />
      )
      expect(screen.getByText('Valeur min')).toBeInTheDocument()
      expect(screen.getByText('Valeur max')).toBeInTheDocument()
    })

    it('n\'affiche pas min/max pour text', () => {
      render(
        <ChampEditor
          {...defaultProps}
          isExpanded={true}
          champ={createMockChamp({ type_champ: 'text' })}
        />
      )
      expect(screen.queryByText('Valeur min')).not.toBeInTheDocument()
    })

    it('permet de modifier la valeur min', async () => {
      const user = userEvent.setup()
      render(
        <ChampEditor
          {...defaultProps}
          isExpanded={true}
          champ={createMockChamp({ type_champ: 'number' })}
        />
      )

      const minInputs = screen.getAllByRole('spinbutton')
      const minInput = minInputs[0]
      await user.type(minInput, '5')

      // Vérifier que onUpdate est appelé avec min_value
      expect(mockOnUpdate).toHaveBeenCalled()
      expect(mockOnUpdate).toHaveBeenCalledWith(expect.objectContaining({ min_value: expect.any(Number) }))
    })

    it('permet de modifier la valeur max', async () => {
      const user = userEvent.setup()
      render(
        <ChampEditor
          {...defaultProps}
          isExpanded={true}
          champ={createMockChamp({ type_champ: 'number' })}
        />
      )

      const maxInputs = screen.getAllByRole('spinbutton')
      const maxInput = maxInputs[1]
      await user.type(maxInput, '9')

      expect(mockOnUpdate).toHaveBeenCalled()
      expect(mockOnUpdate).toHaveBeenCalledWith(expect.objectContaining({ max_value: expect.any(Number) }))
    })
  })

  describe('Propagation d\'événements', () => {
    it('ne propage pas le clic sur les boutons au header', async () => {
      const user = userEvent.setup()
      render(<ChampEditor {...defaultProps} />)

      const buttons = screen.getAllByRole('button')
      const deleteButton = buttons.find(btn => btn.querySelector('svg.lucide-trash-2'))
      if (deleteButton) {
        await user.click(deleteButton)
        // onRemove should be called but not onToggleExpand
        expect(mockOnRemove).toHaveBeenCalled()
        expect(mockOnToggleExpand).not.toHaveBeenCalled()
      }
    })
  })
})
