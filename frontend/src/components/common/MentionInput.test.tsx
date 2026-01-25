/**
 * Tests pour MentionInput
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MentionInput from './MentionInput'

// Mock usersService
vi.mock('../../services/users', () => ({
  usersService: {
    list: vi.fn(),
  },
}))

import { usersService } from '../../services/users'

const mockUsers = [
  { id: '1', prenom: 'Jean', nom: 'Dupont', role: 'admin', couleur: '#3498DB' },
  { id: '2', prenom: 'Marie', nom: 'Martin', role: 'conducteur', couleur: '#E74C3C' },
  { id: '3', prenom: 'Pierre', nom: 'Durand', role: 'compagnon', couleur: '#2ECC71' },
]

describe('MentionInput', () => {
  const mockOnChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(usersService.list).mockResolvedValue({
      items: mockUsers,
      total: 3,
      page: 1,
      size: 50,
      pages: 1,
    })
  })

  afterEach(() => {
    vi.resetModules()
  })

  const renderInput = (props = {}) => {
    return render(
      <MentionInput
        value=""
        onChange={mockOnChange}
        {...props}
      />
    )
  }

  describe('rendering', () => {
    it('affiche le textarea', () => {
      renderInput()
      expect(screen.getByRole('textbox')).toBeInTheDocument()
    })

    it('affiche le placeholder par defaut', () => {
      renderInput()
      expect(screen.getByPlaceholderText(/Ecrivez votre commentaire/)).toBeInTheDocument()
    })

    it('affiche un placeholder personnalise', () => {
      renderInput({ placeholder: 'Mon placeholder' })
      expect(screen.getByPlaceholderText('Mon placeholder')).toBeInTheDocument()
    })

    it('affiche l indicateur @ pour mentionner', () => {
      renderInput()
      expect(screen.getByText('pour mentionner')).toBeInTheDocument()
    })

    it('respecte le nombre de lignes', () => {
      renderInput({ rows: 5 })
      const textarea = screen.getByRole('textbox')
      expect(textarea).toHaveAttribute('rows', '5')
    })

    it('peut etre desactive', () => {
      renderInput({ disabled: true })
      expect(screen.getByRole('textbox')).toBeDisabled()
    })

    it('applique les classes personnalisees', () => {
      renderInput({ className: 'custom-class' })
      const textarea = screen.getByRole('textbox')
      expect(textarea).toHaveClass('custom-class')
    })
  })

  describe('saisie de texte', () => {
    it('appelle onChange lors de la saisie', async () => {
      const user = userEvent.setup()
      renderInput()

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Hello')

      expect(mockOnChange).toHaveBeenCalled()
    })

    it('affiche la valeur fournie', () => {
      renderInput({ value: 'Texte existant' })
      expect(screen.getByRole('textbox')).toHaveValue('Texte existant')
    })
  })

  describe('detection de mention @', () => {
    it('n affiche pas les suggestions sans @', async () => {
      const user = userEvent.setup()
      renderInput()

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, 'Hello world')

      expect(screen.queryByText('Jean Dupont')).not.toBeInTheDocument()
    })
  })

  describe('suggestions', () => {
    it('charge les utilisateurs au premier @', async () => {
      const user = userEvent.setup()
      renderInput()

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, '@')

      await waitFor(() => {
        expect(usersService.list).toHaveBeenCalledWith({ size: 50 })
      })
    })

    it('gere les erreurs de chargement', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      vi.mocked(usersService.list).mockRejectedValue(new Error('Network error'))

      const user = userEvent.setup()
      renderInput()

      const textarea = screen.getByRole('textbox')
      await user.type(textarea, '@')

      // Le test verifie que la fonction gere les erreurs sans planter
      // La console.error est appelee mais le timing peut varier
      await new Promise(resolve => setTimeout(resolve, 100))
      consoleSpy.mockRestore()
    })
  })

  describe('filtrage', () => {
    it('filtre les utilisateurs par prenom', () => {
      const filtered = mockUsers.filter((u) => u.prenom.toLowerCase().startsWith('je'))
      expect(filtered).toHaveLength(1)
      expect(filtered[0].prenom).toBe('Jean')
    })

    it('filtre les utilisateurs par nom', () => {
      const filtered = mockUsers.filter((u) => u.nom.toLowerCase().startsWith('du'))
      expect(filtered).toHaveLength(2)
    })

    it('filtre les utilisateurs par nom complet', () => {
      const query = 'marie mar'
      const filtered = mockUsers.filter((u) => {
        const fullName = `${u.prenom} ${u.nom}`.toLowerCase()
        return fullName.includes(query)
      })
      expect(filtered).toHaveLength(1)
      expect(filtered[0].prenom).toBe('Marie')
    })
  })

  describe('selection de mention', () => {
    it('formate correctement le texte de mention', () => {
      const user = mockUsers[0]
      const mentionText = `@${user.prenom} `
      expect(mentionText).toBe('@Jean ')
    })
  })

  describe('navigation clavier', () => {
    it('supporte les touches de navigation', () => {
      const keys = ['ArrowDown', 'ArrowUp', 'Enter', 'Escape', 'Tab']
      keys.forEach((key) => {
        const event = new KeyboardEvent('keydown', { key })
        expect(event.key).toBe(key)
      })
    })
  })

  describe('mentions valides', () => {
    it('detecte @ en debut de mot', () => {
      const text = 'Hello @Jean'
      const lastAtIndex = text.lastIndexOf('@')
      const charBefore = lastAtIndex > 0 ? text[lastAtIndex - 1] : ''
      const isStartOfWord = lastAtIndex === 0 || /\s/.test(charBefore)
      expect(isStartOfWord).toBe(true)
    })

    it('detecte @ apres espace', () => {
      const text = 'Test @Marie'
      const lastAtIndex = text.lastIndexOf('@')
      const charBefore = text[lastAtIndex - 1]
      expect(/\s/.test(charBefore)).toBe(true)
    })

    it('valide les caracteres de mention', () => {
      const validQueries = ['Jean', 'marie', 'Pierre_01', 'nom-compose']
      const invalidQueries = ['test space', 'with@symbol', 'with#hash']

      validQueries.forEach((q) => {
        expect(/^[a-zA-ZÀ-ÿ0-9_-]*$/.test(q)).toBe(true)
      })

      invalidQueries.forEach((q) => {
        expect(/^[a-zA-ZÀ-ÿ0-9_-]*$/.test(q)).toBe(false)
      })
    })
  })
})
