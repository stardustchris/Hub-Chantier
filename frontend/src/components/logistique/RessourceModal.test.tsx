/**
 * Tests unitaires pour RessourceModal
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { RessourceModal } from './RessourceModal'

const mockCreateRessource = vi.fn()
const mockUpdateRessource = vi.fn()

vi.mock('../../api/logistique', () => ({
  createRessource: (...args: any[]) => mockCreateRessource(...args),
  updateRessource: (...args: any[]) => mockUpdateRessource(...args),
}))

vi.mock('../../services/logger', () => ({
  logger: { info: vi.fn(), error: vi.fn(), warn: vi.fn() },
}))

vi.mock('../../types/logistique', async () => {
  const actual = await vi.importActual('../../types/logistique')
  return actual
})

const mockRessource: any = {
  id: 1,
  nom: 'Grue mobile',
  code: 'GRUE01',
  categorie: 'engin_levage',
  categorie_label: 'Engin de levage',
  couleur: '#E74C3C',
  heure_debut_defaut: '08:00',
  heure_fin_defaut: '17:00',
  validation_requise: true,
  actif: true,
  description: 'Grue 50T',
}

describe('RessourceModal', () => {
  const defaultProps = {
    onClose: vi.fn(),
    onSuccess: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockCreateRessource.mockResolvedValue({})
    mockUpdateRessource.mockResolvedValue({})
  })

  it('affiche le titre "Nouvelle ressource" en mode creation', () => {
    // Arrange & Act
    render(<RessourceModal {...defaultProps} />)

    // Assert
    expect(screen.getByText('Nouvelle ressource')).toBeInTheDocument()
  })

  it('affiche le titre "Modifier la ressource" en mode edition', () => {
    // Arrange & Act
    render(<RessourceModal {...defaultProps} ressource={mockRessource} />)

    // Assert
    expect(screen.getByText('Modifier la ressource')).toBeInTheDocument()
  })

  it('affiche les champs du formulaire (nom, code, categorie, description, horaires, couleur)', () => {
    // Arrange & Act
    render(<RessourceModal {...defaultProps} />)

    // Assert
    expect(screen.getByLabelText(/Nom de la ressource/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Code/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Catégorie/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Description/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Heure début/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Heure fin/)).toBeInTheDocument()
    expect(screen.getByText("Couleur d'affichage")).toBeInTheDocument()
  })

  it('le code est auto-genere a partir du nom', async () => {
    // Arrange
    render(<RessourceModal {...defaultProps} />)
    const user = userEvent.setup()

    // Act
    const nomInput = screen.getByLabelText(/Nom de la ressource/)
    await user.type(nomInput, 'Grue mobile')

    // Assert
    await waitFor(() => {
      const codeInput = screen.getByLabelText(/Code/) as HTMLInputElement
      expect(codeInput.value).not.toBe('')
    })
  })

  it('affiche les couleurs predefinies', () => {
    // Arrange & Act
    const { container } = render(<RessourceModal {...defaultProps} />)

    // Assert
    const colorButtons = container.querySelectorAll('button[title]')
    expect(colorButtons.length).toBeGreaterThanOrEqual(8)
  })

  it('appelle createRessource a la soumission en mode creation', async () => {
    // Arrange
    render(<RessourceModal {...defaultProps} />)
    const user = userEvent.setup()

    // Act
    await user.type(screen.getByLabelText(/Nom de la ressource/), 'Nouvelle Grue')
    await user.clear(screen.getByLabelText(/Code/))
    await user.type(screen.getByLabelText(/Code/), 'NGRUE01')

    const submitButton = screen.getByText('Créer')
    await user.click(submitButton)

    // Assert
    await waitFor(() => {
      expect(mockCreateRessource).toHaveBeenCalled()
    })
  })

  it('appelle updateRessource a la soumission en mode edition', async () => {
    // Arrange
    render(<RessourceModal {...defaultProps} ressource={mockRessource} />)
    const user = userEvent.setup()

    // Act
    const submitButton = screen.getByText('Mettre à jour')
    await user.click(submitButton)

    // Assert
    await waitFor(() => {
      expect(mockUpdateRessource).toHaveBeenCalledWith(1, expect.any(Object))
    })
  })

  it('appelle onClose au clic sur Annuler', async () => {
    // Arrange
    const onClose = vi.fn()
    render(<RessourceModal {...defaultProps} onClose={onClose} />)
    const user = userEvent.setup()

    // Act
    await user.click(screen.getByText('Annuler'))

    // Assert
    expect(onClose).toHaveBeenCalled()
  })

  it('affiche "Enregistrement..." pendant le chargement', async () => {
    // Arrange - make createRessource hang
    mockCreateRessource.mockReturnValue(new Promise(() => {}))
    render(<RessourceModal {...defaultProps} />)
    const user = userEvent.setup()

    // Act
    await user.type(screen.getByLabelText(/Nom de la ressource/), 'Grue Test')
    await user.clear(screen.getByLabelText(/Code/))
    await user.type(screen.getByLabelText(/Code/), 'GTEST')

    const submitButton = screen.getByText('Créer')
    await user.click(submitButton)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Enregistrement...')).toBeInTheDocument()
    })
  })

  it('affiche le message d\'erreur en cas d\'echec', async () => {
    // Arrange
    mockCreateRessource.mockRejectedValue(new Error('Erreur serveur'))
    render(<RessourceModal {...defaultProps} />)
    const user = userEvent.setup()

    // Act
    await user.type(screen.getByLabelText(/Nom de la ressource/), 'Grue Test')
    await user.clear(screen.getByLabelText(/Code/))
    await user.type(screen.getByLabelText(/Code/), 'GTEST')

    const submitButton = screen.getByText('Créer')
    await user.click(submitButton)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Erreur serveur')).toBeInTheDocument()
    })
  })
})
