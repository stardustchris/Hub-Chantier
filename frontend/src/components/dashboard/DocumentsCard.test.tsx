/**
 * Tests pour DocumentsCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import DocumentsCard from './DocumentsCard'

describe('DocumentsCard', () => {
  it('affiche le titre Mes documents', () => {
    render(<DocumentsCard />)

    expect(screen.getByText('Mes documents')).toBeInTheDocument()
  })

  it('affiche les documents par defaut', () => {
    render(<DocumentsCard />)

    expect(screen.getByText(/Plan étage 1/)).toBeInTheDocument()
    expect(screen.getByText(/Consignes de sécurité/)).toBeInTheDocument()
    expect(screen.getByText(/Checklist qualité/)).toBeInTheDocument()
  })

  it('affiche des documents personnalises', () => {
    const customDocs = [
      { id: '1', name: 'Document A.pdf', type: 'pdf' as const },
      { id: '2', name: 'Image B.jpg', type: 'image' as const },
    ]

    render(<DocumentsCard documents={customDocs} />)

    expect(screen.getByText('Document A.pdf')).toBeInTheDocument()
    expect(screen.getByText('Image B.jpg')).toBeInTheDocument()
  })

  it('affiche le nom du chantier si defini', () => {
    const docs = [
      { id: '1', name: 'Test.pdf', siteName: 'Chantier ABC', type: 'pdf' as const },
    ]

    render(<DocumentsCard documents={docs} />)

    expect(screen.getByText('Chantier ABC')).toBeInTheDocument()
  })

  it('n\'affiche pas le nom du chantier si non defini', () => {
    const docs = [
      { id: '1', name: 'Test.pdf', type: 'pdf' as const },
    ]

    render(<DocumentsCard documents={docs} />)

    expect(screen.getByText('Test.pdf')).toBeInTheDocument()
    expect(screen.queryByText('Chantier')).not.toBeInTheDocument()
  })

  it('affiche le bouton Voir tout', () => {
    render(<DocumentsCard />)

    expect(screen.getByText('Voir tout')).toBeInTheDocument()
  })

  it('appelle onViewAll au clic sur Voir tout', () => {
    const onViewAll = vi.fn()
    render(<DocumentsCard onViewAll={onViewAll} />)

    fireEvent.click(screen.getByText('Voir tout'))

    expect(onViewAll).toHaveBeenCalled()
  })

  it('appelle onDocumentClick au clic sur un document', () => {
    const onDocumentClick = vi.fn()
    const docs = [
      { id: 'doc-123', name: 'Mon Document.pdf', type: 'pdf' as const },
    ]

    render(<DocumentsCard documents={docs} onDocumentClick={onDocumentClick} />)

    fireEvent.click(screen.getByText('Mon Document.pdf'))

    expect(onDocumentClick).toHaveBeenCalledWith('doc-123')
  })

  it('gere les differents types de documents', () => {
    const docs = [
      { id: '1', name: 'PDF Doc', type: 'pdf' as const },
      { id: '2', name: 'Word Doc', type: 'doc' as const },
      { id: '3', name: 'Image Doc', type: 'image' as const },
      { id: '4', name: 'Other Doc', type: 'other' as const },
    ]

    render(<DocumentsCard documents={docs} />)

    expect(screen.getByText('PDF Doc')).toBeInTheDocument()
    expect(screen.getByText('Word Doc')).toBeInTheDocument()
    expect(screen.getByText('Image Doc')).toBeInTheDocument()
    expect(screen.getByText('Other Doc')).toBeInTheDocument()
  })

  it('gere une liste vide de documents', () => {
    render(<DocumentsCard documents={[]} />)

    expect(screen.getByText('Mes documents')).toBeInTheDocument()
    expect(screen.getByText('Voir tout')).toBeInTheDocument()
  })

  it('rend les documents cliquables', () => {
    const docs = [
      { id: '1', name: 'Clickable.pdf', type: 'pdf' as const },
    ]

    const { container } = render(<DocumentsCard documents={docs} />)

    const button = container.querySelector('button')
    expect(button).toBeInTheDocument()
  })

  it('applique les couleurs correctes pour les types de fichiers', () => {
    const docs = [
      { id: '1', name: 'PDF', type: 'pdf' as const },
    ]

    const { container } = render(<DocumentsCard documents={docs} />)

    // PDF devrait avoir la couleur rouge
    const pdfIcon = container.querySelector('.bg-red-100')
    expect(pdfIcon).toBeInTheDocument()
  })

  it('affiche plusieurs documents du meme chantier', () => {
    const docs = [
      { id: '1', name: 'Doc 1.pdf', siteName: 'Villa Moderne', type: 'pdf' as const },
      { id: '2', name: 'Doc 2.pdf', siteName: 'Villa Moderne', type: 'pdf' as const },
    ]

    render(<DocumentsCard documents={docs} />)

    expect(screen.getAllByText('Villa Moderne')).toHaveLength(2)
  })
})
