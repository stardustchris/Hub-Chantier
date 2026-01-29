/**
 * Tests unitaires pour mentionRenderer
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { renderContentWithMentions } from './mentionRenderer'

// Helper to render the result in a React tree
function renderMentions(content: string, authors: { id: string | number; prenom: string; nom: string }[]) {
  const result = renderContentWithMentions(content, authors)
  return render(
    <MemoryRouter>
      <div data-testid="container">{result}</div>
    </MemoryRouter>
  )
}

describe('renderContentWithMentions', () => {
  const authors = [
    { id: '1', prenom: 'Jean', nom: 'Dupont' },
    { id: 2, prenom: 'Marie', nom: 'Martin' },
    { id: '3', prenom: 'Pierre', nom: 'Durand' },
  ]

  it('retourne le contenu brut sans mentions', () => {
    const result = renderContentWithMentions('Bonjour tout le monde', authors)
    expect(result).toEqual(['Bonjour tout le monde'])
  })

  it('rend une mention reconnue comme lien cliquable', () => {
    renderMentions('Bonjour @Jean', authors)

    const link = screen.getByText('@Jean')
    expect(link.tagName).toBe('A')
    expect(link).toHaveAttribute('href', '/utilisateurs/1')
  })

  it('rend une mention non reconnue comme span sans lien', () => {
    renderMentions('Bonjour @Inconnu', authors)

    const mention = screen.getByText('@Inconnu')
    expect(mention.tagName).toBe('SPAN')
    expect(mention).toHaveClass('text-blue-500')
  })

  it('gere plusieurs mentions dans le meme texte', () => {
    renderMentions('CC @Jean et @Marie', authors)

    const jeanLink = screen.getByText('@Jean')
    expect(jeanLink.tagName).toBe('A')
    expect(jeanLink).toHaveAttribute('href', '/utilisateurs/1')

    const marieLink = screen.getByText('@Marie')
    expect(marieLink.tagName).toBe('A')
    expect(marieLink).toHaveAttribute('href', '/utilisateurs/2')
  })

  it('matche par nom de famille', () => {
    renderMentions('Salut @Dupont', authors)

    const link = screen.getByText('@Dupont')
    expect(link.tagName).toBe('A')
    expect(link).toHaveAttribute('href', '/utilisateurs/1')
  })

  it('matche par prenom+nom concatene', () => {
    renderMentions('Salut @JeanDupont', authors)

    const link = screen.getByText('@JeanDupont')
    expect(link.tagName).toBe('A')
    expect(link).toHaveAttribute('href', '/utilisateurs/1')
  })

  it('est insensible a la casse', () => {
    renderMentions('Salut @jean', authors)

    const link = screen.getByText('@jean')
    expect(link.tagName).toBe('A')
    expect(link).toHaveAttribute('href', '/utilisateurs/1')
  })

  it('preserve le texte avant et apres les mentions', () => {
    renderMentions('Debut @Jean fin', authors)

    const container = screen.getByTestId('container')
    expect(container.textContent).toBe('Debut @Jean fin')
  })

  it('gere le contenu vide', () => {
    const result = renderContentWithMentions('', authors)
    expect(result).toEqual([''])
  })

  it('gere une liste d auteurs vide', () => {
    renderMentions('Salut @Jean', [])

    const mention = screen.getByText('@Jean')
    // No matching author, should be a span
    expect(mention.tagName).toBe('SPAN')
  })

  it('gere les mentions avec tirets et underscores', () => {
    renderMentions('CC @Jean-Pierre', authors)

    const mention = screen.getByText('@Jean-Pierre')
    // Jean-Pierre doesn't match any author (Jean != Jean-Pierre), so it's a span
    expect(mention.tagName).toBe('SPAN')
  })

  it('applique les classes CSS correctes aux liens', () => {
    renderMentions('Hello @Jean', authors)

    const link = screen.getByText('@Jean')
    expect(link).toHaveClass('text-blue-600')
    expect(link).toHaveClass('font-semibold')
    expect(link).toHaveClass('hover:underline')
  })
})
