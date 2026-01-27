/**
 * Tests pour FieldRenderer
 *
 * Couvre:
 * - Rendu des différents types de champs (text, textarea, number, email, date, time, select, checkbox, radio)
 * - Affichage label avec indicateur obligatoire
 * - Gestion des erreurs de validation
 * - Mode lecture seule
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FieldRenderer from './FieldRenderer'
import type { ChampTemplate } from '../../types'

// Mock PhotoCapture et SignaturePad
vi.mock('./PhotoCapture', () => ({
  default: ({ value, onChange, readOnly, label }: {
    value: string
    onChange: (v: string) => void
    readOnly: boolean
    label: string
  }) => (
    <div data-testid="photo-capture">
      <span>{label}</span>
      <input
        type="text"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        disabled={readOnly}
      />
    </div>
  ),
}))

vi.mock('./SignaturePad', () => ({
  default: ({ value, onChange, readOnly }: {
    value: string
    onChange: (v: string) => void
    readOnly: boolean
  }) => (
    <div data-testid="signature-pad">
      <input
        type="text"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        disabled={readOnly}
      />
    </div>
  ),
}))

const createMockChamp = (overrides: Partial<ChampTemplate> = {}): ChampTemplate => ({
  nom: 'test_field',
  label: 'Test Field',
  type_champ: 'texte',
  obligatoire: false,
  ordre: 1,
  ...overrides,
})

describe('FieldRenderer', () => {
  const mockOnChange = vi.fn()

  const defaultProps = {
    champ: createMockChamp(),
    onChange: mockOnChange,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Label et indicateur obligatoire', () => {
    it('affiche le label du champ', () => {
      render(<FieldRenderer {...defaultProps} />)
      expect(screen.getByText('Test Field')).toBeInTheDocument()
    })

    it('affiche l\'indicateur obligatoire si champ requis', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ obligatoire: true })}
        />
      )
      expect(screen.getByText('*')).toBeInTheDocument()
    })

    it('n\'affiche pas l\'indicateur si champ non obligatoire', () => {
      render(<FieldRenderer {...defaultProps} />)
      expect(screen.queryByText('*')).not.toBeInTheDocument()
    })
  })

  describe('Erreur de validation', () => {
    it('affiche le message d\'erreur', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          error="Ce champ est requis"
        />
      )
      expect(screen.getByText('Ce champ est requis')).toBeInTheDocument()
    })

    it('applique le style d\'erreur au champ', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          error="Ce champ est requis"
        />
      )
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('border-red-500')
    })
  })

  describe('Champ text', () => {
    it('rend un input text', () => {
      render(<FieldRenderer {...defaultProps} />)
      expect(screen.getByRole('textbox')).toBeInTheDocument()
    })

    it('affiche le placeholder', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ placeholder: 'Entrez du texte' })}
        />
      )
      expect(screen.getByPlaceholderText('Entrez du texte')).toBeInTheDocument()
    })

    it('appelle onChange lors de la saisie', async () => {
      const user = userEvent.setup()
      render(<FieldRenderer {...defaultProps} />)

      await user.type(screen.getByRole('textbox'), 'test')
      expect(mockOnChange).toHaveBeenCalled()
    })

    it('affiche la valeur initiale', () => {
      render(<FieldRenderer {...defaultProps} value="Valeur initiale" />)
      expect(screen.getByRole('textbox')).toHaveValue('Valeur initiale')
    })
  })

  describe('Champ textarea', () => {
    it('rend un textarea', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'texte_long' })}
        />
      )
      expect(screen.getByRole('textbox')).toHaveClass('min-h-[100px]')
    })
  })

  describe('Champ number', () => {
    it('rend un input number', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'nombre' })}
        />
      )
      expect(screen.getByRole('spinbutton')).toBeInTheDocument()
    })

    it('applique les contraintes min/max', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({
            type_champ: 'nombre',
            min_value: 0,
            max_value: 100,
          })}
        />
      )
      const input = screen.getByRole('spinbutton')
      expect(input).toHaveAttribute('min', '0')
      expect(input).toHaveAttribute('max', '100')
    })
  })

  describe('Champ email', () => {
    it('rend un input email', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'texte' })}
        />
      )
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('type', 'email')
    })

    it('utilise le placeholder par défaut', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'texte' })}
        />
      )
      expect(screen.getByPlaceholderText('exemple@email.com')).toBeInTheDocument()
    })
  })

  describe('Champ date', () => {
    it('rend un input date', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'date' })}
        />
      )
      const input = document.querySelector('input[type="date"]')
      expect(input).toBeInTheDocument()
    })
  })

  describe('Champ time', () => {
    it('rend un input time', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'heure' })}
        />
      )
      const input = document.querySelector('input[type="time"]')
      expect(input).toBeInTheDocument()
    })
  })

  describe('Champ select', () => {
    it('rend un select avec options', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({
            type_champ: 'select',
            options: ['Option 1', 'Option 2', 'Option 3'],
          })}
        />
      )
      expect(screen.getByRole('combobox')).toBeInTheDocument()
      expect(screen.getByText('Option 1')).toBeInTheDocument()
      expect(screen.getByText('Option 2')).toBeInTheDocument()
      expect(screen.getByText('Option 3')).toBeInTheDocument()
    })

    it('affiche l\'option par défaut', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({
            type_champ: 'select',
            options: ['Option 1'],
          })}
        />
      )
      expect(screen.getByText('Selectionnez...')).toBeInTheDocument()
    })
  })

  describe('Champ checkbox', () => {
    it('rend une checkbox', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'checkbox' })}
        />
      )
      expect(screen.getByRole('checkbox')).toBeInTheDocument()
    })

    it('affiche le placeholder comme label', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({
            type_champ: 'checkbox',
            placeholder: 'J\'accepte les conditions',
          })}
        />
      )
      expect(screen.getByText('J\'accepte les conditions')).toBeInTheDocument()
    })

    it('utilise "Oui" par défaut si pas de placeholder', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'checkbox' })}
        />
      )
      expect(screen.getByText('Oui')).toBeInTheDocument()
    })

    it('appelle onChange avec true/false', async () => {
      const user = userEvent.setup()
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'checkbox' })}
        />
      )

      await user.click(screen.getByRole('checkbox'))
      expect(mockOnChange).toHaveBeenCalledWith(true)
    })
  })

  describe('Champ radio', () => {
    it('rend des boutons radio', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({
            type_champ: 'radio',
            options: ['Option A', 'Option B'],
          })}
        />
      )
      expect(screen.getAllByRole('radio')).toHaveLength(2)
      expect(screen.getByText('Option A')).toBeInTheDocument()
      expect(screen.getByText('Option B')).toBeInTheDocument()
    })

    it('appelle onChange avec la valeur sélectionnée', async () => {
      const user = userEvent.setup()
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({
            type_champ: 'radio',
            options: ['Option A', 'Option B'],
          })}
        />
      )

      await user.click(screen.getByText('Option B'))
      expect(mockOnChange).toHaveBeenCalledWith('Option B')
    })

    it('sélectionne l\'option correspondant à la valeur', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          value="Option A"
          champ={createMockChamp({
            type_champ: 'radio',
            options: ['Option A', 'Option B'],
          })}
        />
      )
      const radios = screen.getAllByRole('radio')
      expect(radios[0]).toBeChecked()
      expect(radios[1]).not.toBeChecked()
    })
  })

  describe('Champ photo', () => {
    it('rend le composant PhotoCapture', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'photo' })}
        />
      )
      expect(screen.getByTestId('photo-capture')).toBeInTheDocument()
    })
  })

  describe('Champ signature', () => {
    it('rend le composant SignaturePad', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ type_champ: 'signature' })}
        />
      )
      expect(screen.getByTestId('signature-pad')).toBeInTheDocument()
    })
  })

  describe('Mode lecture seule', () => {
    it('désactive l\'input en mode lecture seule', () => {
      render(<FieldRenderer {...defaultProps} readOnly />)
      expect(screen.getByRole('textbox')).toBeDisabled()
    })

    it('applique le style lecture seule', () => {
      render(<FieldRenderer {...defaultProps} readOnly />)
      expect(screen.getByRole('textbox')).toHaveClass('bg-gray-100')
    })

    it('désactive le select en mode lecture seule', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          readOnly
          champ={createMockChamp({
            type_champ: 'select',
            options: ['Option 1'],
          })}
        />
      )
      expect(screen.getByRole('combobox')).toBeDisabled()
    })

    it('désactive la checkbox en mode lecture seule', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          readOnly
          champ={createMockChamp({ type_champ: 'checkbox' })}
        />
      )
      expect(screen.getByRole('checkbox')).toBeDisabled()
    })
  })

  describe('Valeur par défaut', () => {
    it('utilise la valeur par défaut du champ si pas de value', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          champ={createMockChamp({ valeur_defaut: 'Défaut' })}
        />
      )
      expect(screen.getByRole('textbox')).toHaveValue('Défaut')
    })

    it('privilégie la value prop sur la valeur par défaut', () => {
      render(
        <FieldRenderer
          {...defaultProps}
          value="Ma valeur"
          champ={createMockChamp({ valeur_defaut: 'Défaut' })}
        />
      )
      expect(screen.getByRole('textbox')).toHaveValue('Ma valeur')
    })
  })
})
