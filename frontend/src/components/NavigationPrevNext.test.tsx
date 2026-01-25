/**
 * Tests pour NavigationPrevNext
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import NavigationPrevNext from './NavigationPrevNext'

const renderWithRouter = (props: { prevId?: string | null; nextId?: string | null; baseUrl: string; entityLabel?: string }) => {
  return render(
    <MemoryRouter>
      <NavigationPrevNext {...props} />
    </MemoryRouter>
  )
}

describe('NavigationPrevNext', () => {
  it('affiche les deux boutons', () => {
    renderWithRouter({ baseUrl: '/users' })

    expect(screen.getAllByRole('button')).toHaveLength(2)
  })

  it('desactive le bouton precedent si prevId est null', () => {
    renderWithRouter({ baseUrl: '/users', prevId: null })

    const prevButton = screen.getByTitle('Pas de élément précédent')
    expect(prevButton).toBeDisabled()
  })

  it('desactive le bouton suivant si nextId est null', () => {
    renderWithRouter({ baseUrl: '/users', nextId: null })

    const nextButton = screen.getByTitle('Pas de élément suivant')
    expect(nextButton).toBeDisabled()
  })

  it('active le bouton precedent si prevId est defini', () => {
    renderWithRouter({ baseUrl: '/users', prevId: 'user-1' })

    const prevLink = screen.getByTitle('élément précédent')
    expect(prevLink).toBeInTheDocument()
    expect(prevLink.tagName).toBe('A')
  })

  it('active le bouton suivant si nextId est defini', () => {
    renderWithRouter({ baseUrl: '/users', nextId: 'user-2' })

    const nextLink = screen.getByTitle('élément suivant')
    expect(nextLink).toBeInTheDocument()
    expect(nextLink.tagName).toBe('A')
  })

  it('cree un lien correct pour le precedent', () => {
    renderWithRouter({ baseUrl: '/chantiers', prevId: 'ch-123' })

    const prevLink = screen.getByTitle('élément précédent')
    expect(prevLink).toHaveAttribute('href', '/chantiers/ch-123')
  })

  it('cree un lien correct pour le suivant', () => {
    renderWithRouter({ baseUrl: '/chantiers', nextId: 'ch-456' })

    const nextLink = screen.getByTitle('élément suivant')
    expect(nextLink).toHaveAttribute('href', '/chantiers/ch-456')
  })

  it('utilise le label personnalise pour le precedent', () => {
    renderWithRouter({ baseUrl: '/users', prevId: 'u-1', entityLabel: 'utilisateur' })

    expect(screen.getByTitle('utilisateur précédent')).toBeInTheDocument()
  })

  it('utilise le label personnalise pour le suivant', () => {
    renderWithRouter({ baseUrl: '/users', nextId: 'u-2', entityLabel: 'utilisateur' })

    expect(screen.getByTitle('utilisateur suivant')).toBeInTheDocument()
  })

  it('utilise le label personnalise pour le precedent desactive', () => {
    renderWithRouter({ baseUrl: '/users', prevId: null, entityLabel: 'chantier' })

    expect(screen.getByTitle('Pas de chantier précédent')).toBeInTheDocument()
  })

  it('utilise le label personnalise pour le suivant desactive', () => {
    renderWithRouter({ baseUrl: '/users', nextId: null, entityLabel: 'chantier' })

    expect(screen.getByTitle('Pas de chantier suivant')).toBeInTheDocument()
  })

  it('affiche les deux liens si les deux IDs sont definis', () => {
    renderWithRouter({ baseUrl: '/docs', prevId: 'doc-1', nextId: 'doc-2' })

    expect(screen.getByTitle('élément précédent')).toBeInTheDocument()
    expect(screen.getByTitle('élément suivant')).toBeInTheDocument()
  })

  it('desactive les deux boutons si aucun ID', () => {
    renderWithRouter({ baseUrl: '/items', prevId: null, nextId: null })

    expect(screen.getByTitle('Pas de élément précédent')).toBeDisabled()
    expect(screen.getByTitle('Pas de élément suivant')).toBeDisabled()
  })

  it('a l\'attribut aria-label pour le precedent actif', () => {
    renderWithRouter({ baseUrl: '/users', prevId: 'u-1' })

    const prevLink = screen.getByTitle('élément précédent')
    expect(prevLink).toHaveAttribute('aria-label', 'élément précédent')
  })

  it('a l\'attribut aria-label pour le suivant actif', () => {
    renderWithRouter({ baseUrl: '/users', nextId: 'u-2' })

    const nextLink = screen.getByTitle('élément suivant')
    expect(nextLink).toHaveAttribute('aria-label', 'élément suivant')
  })

  it('a l\'attribut aria-disabled pour le bouton desactive', () => {
    renderWithRouter({ baseUrl: '/users', prevId: null })

    const prevButton = screen.getByTitle('Pas de élément précédent')
    expect(prevButton).toHaveAttribute('aria-disabled', 'true')
  })

  it('gere undefined comme null pour prevId', () => {
    renderWithRouter({ baseUrl: '/users', prevId: undefined })

    const prevButton = screen.getByTitle('Pas de élément précédent')
    expect(prevButton).toBeDisabled()
  })

  it('gere undefined comme null pour nextId', () => {
    renderWithRouter({ baseUrl: '/users', nextId: undefined })

    const nextButton = screen.getByTitle('Pas de élément suivant')
    expect(nextButton).toBeDisabled()
  })
})
