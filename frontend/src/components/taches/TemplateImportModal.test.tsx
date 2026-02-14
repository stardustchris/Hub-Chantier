/**
 * Tests unitaires pour TemplateImportModal
 * Modal d'import de modeles de taches
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import TemplateImportModal from './TemplateImportModal'
import { ToastProvider } from '../../contexts/ToastContext'

vi.mock('../../services/taches', () => ({
  tachesService: {
    listTemplates: vi.fn(),
  },
}))

vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

import { tachesService } from '../../services/taches'

const mockedTachesService = tachesService as { listTemplates: ReturnType<typeof vi.fn> }

const mockTemplate: any = {
  id: 1,
  nom: 'Fondations',
  description: 'Template fondations',
  categorie: 'gros_oeuvre',
  nombre_sous_taches: 5,
  unite_mesure: null,
  heures_estimees_defaut: 40,
  sous_taches: [
    { titre: 'Fouilles' },
    { titre: 'Ferraillage' },
  ],
}

const mockTemplate2: any = {
  id: 2,
  nom: 'Electricite',
  description: 'Template electricite',
  categorie: 'second_oeuvre',
  nombre_sous_taches: 3,
  unite_mesure: null,
  heures_estimees_defaut: null,
  sous_taches: [],
}

describe('TemplateImportModal', () => {
  const defaultProps = {
    onClose: vi.fn(),
    onImport: vi.fn().mockResolvedValue(undefined),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockedTachesService.listTemplates.mockResolvedValue({
      items: [mockTemplate, mockTemplate2],
      categories: ['gros_oeuvre', 'second_oeuvre'],
    })
  })

  const renderWithToast = (props = defaultProps) => {
    return render(
      <ToastProvider>
        <TemplateImportModal {...props} />
      </ToastProvider>
    )
  }

  it('affiche le titre "Importer un modele"', async () => {
    // Act
    renderWithToast()

    // Assert
    expect(screen.getByText('Importer un modele de taches')).toBeInTheDocument()
  })

  it('affiche le champ de recherche', () => {
    // Act
    renderWithToast()

    // Assert
    expect(screen.getByPlaceholderText('Rechercher un modele...')).toBeInTheDocument()
  })

  it('affiche les templates charges', async () => {
    // Act
    renderWithToast()

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Fondations')).toBeInTheDocument()
      expect(screen.getByText('Electricite')).toBeInTheDocument()
    })
  })

  it('filtre les templates par recherche', async () => {
    // Arrange
    renderWithToast()

    await waitFor(() => {
      expect(screen.getByText('Fondations')).toBeInTheDocument()
    })

    // Act - le changement de searchQuery declenche un reload via useEffect
    const searchInput = screen.getByPlaceholderText('Rechercher un modele...')
    fireEvent.change(searchInput, { target: { value: 'elec' } })

    // Assert - le service est rappele avec la query
    await waitFor(() => {
      expect(mockedTachesService.listTemplates).toHaveBeenCalledWith(
        expect.objectContaining({ query: 'elec' })
      )
    })
  })

  it('appelle onImport au clic sur un template puis Importer', async () => {
    // Arrange
    const onImport = vi.fn().mockResolvedValue(undefined)
    renderWithToast({ ...defaultProps, onImport })

    await waitFor(() => {
      expect(screen.getByText('Fondations')).toBeInTheDocument()
    })

    // Act - selectionner le template
    fireEvent.click(screen.getByText('Fondations'))
    // Cliquer sur Importer
    fireEvent.click(screen.getByText('Importer'))

    // Assert
    await waitFor(() => {
      expect(onImport).toHaveBeenCalledWith(1)
    })
  })

  it('appelle onClose au clic sur Annuler', () => {
    // Arrange
    const onClose = vi.fn()

    // Act
    renderWithToast({ ...defaultProps, onClose })
    fireEvent.click(screen.getByText('Annuler'))

    // Assert
    expect(onClose).toHaveBeenCalled()
  })

  it('affiche le loader pendant le chargement', () => {
    // Arrange - mock qui ne resout jamais
    mockedTachesService.listTemplates.mockReturnValue(new Promise(() => {}))

    // Act
    const { container } = renderWithToast()

    // Assert
    expect(container.querySelector('.animate-spin')).toBeInTheDocument()
  })
})
