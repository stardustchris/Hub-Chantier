import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CommandPalette from './CommandPalette'
import { useCommandPalette } from '../../hooks/useCommandPalette'

// Mock the hook
vi.mock('../../hooks/useCommandPalette')

describe('CommandPalette', () => {
  const mockOpen = vi.fn()
  const mockClose = vi.fn()
  const mockSetQuery = vi.fn()
  const mockSelectResult = vi.fn()
  const mockSetSelectedIndex = vi.fn()

  const defaultHookReturn = {
    isOpen: false,
    query: '',
    setQuery: mockSetQuery,
    results: [],
    selectedIndex: 0,
    setSelectedIndex: mockSetSelectedIndex,
    recentSearches: [],
    open: mockOpen,
    close: mockClose,
    selectResult: mockSelectResult,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useCommandPalette).mockReturnValue(defaultHookReturn)
    HTMLElement.prototype.scrollIntoView = vi.fn()
  })

  it('should not render when closed', () => {
    render(<CommandPalette />)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('should render when open', () => {
    vi.mocked(useCommandPalette).mockReturnValue({
      ...defaultHookReturn,
      isOpen: true,
    })

    render(<CommandPalette />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('should display search input when open', () => {
    vi.mocked(useCommandPalette).mockReturnValue({
      ...defaultHookReturn,
      isOpen: true,
    })

    render(<CommandPalette />)
    const input = screen.getByPlaceholderText(/rechercher/i)
    expect(input).toBeInTheDocument()
  })

  it('should call setQuery when typing', async () => {
    const user = userEvent.setup()
    vi.mocked(useCommandPalette).mockReturnValue({
      ...defaultHookReturn,
      isOpen: true,
    })

    render(<CommandPalette />)
    const input = screen.getByPlaceholderText(/rechercher/i)

    await user.type(input, 't')

    expect(mockSetQuery).toHaveBeenCalled()
  })

  it('should display search results with categories', () => {
    vi.mocked(useCommandPalette).mockReturnValue({
      ...defaultHookReturn,
      isOpen: true,
      query: 'test',
      results: [
        {
          id: '1',
          type: 'chantier',
          title: 'Chantier Test',
          icon: 'Building2',
          url: '/chantiers/1',
        },
      ],
    })

    render(<CommandPalette />)

    expect(screen.getByText('Chantier Test')).toBeInTheDocument()
    expect(screen.getByText('Chantiers')).toBeInTheDocument()
  })

  it('should display empty state when no results', () => {
    vi.mocked(useCommandPalette).mockReturnValue({
      ...defaultHookReturn,
      isOpen: true,
      query: 'xyz123',
      results: [],
      recentSearches: [],
    })

    render(<CommandPalette />)

    expect(screen.getByText(/aucun resultat/i)).toBeInTheDocument()
  })

  it('should call close when clicking overlay', async () => {
    const user = userEvent.setup()
    vi.mocked(useCommandPalette).mockReturnValue({
      ...defaultHookReturn,
      isOpen: true,
    })

    render(<CommandPalette />)

    const dialog = screen.getByRole('dialog')
    await user.click(dialog)

    expect(mockClose).toHaveBeenCalled()
  })

  it('should have proper accessibility attributes', () => {
    vi.mocked(useCommandPalette).mockReturnValue({
      ...defaultHookReturn,
      isOpen: true,
      results: [
        {
          id: '1',
          type: 'chantier',
          title: 'Chantier Test',
          icon: 'Building2',
          url: '/chantiers/1',
        },
      ],
    })

    render(<CommandPalette />)

    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-label', 'Recherche globale')
    expect(dialog).toHaveAttribute('aria-modal', 'true')

    const listbox = screen.getByRole('listbox')
    expect(listbox).toBeInTheDocument()

    const input = screen.getByPlaceholderText(/rechercher/i)
    expect(input).toHaveAttribute('aria-autocomplete', 'list')
  })
})
