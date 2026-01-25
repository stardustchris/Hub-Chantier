/**
 * Tests unitaires pour MiniMap
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MiniMap, { MiniMapStatic, MapPlaceholder } from './MiniMap'

describe('MiniMap', () => {
  const defaultProps = {
    latitude: 48.8566,
    longitude: 2.3522,
  }

  describe('rendering', () => {
    it('rend une iframe avec la bonne URL', () => {
      render(<MiniMap {...defaultProps} />)

      const iframe = screen.getByTitle('Localisation')
      expect(iframe).toBeInTheDocument()
      expect(iframe).toHaveAttribute('src')
      expect(iframe.getAttribute('src')).toContain('openstreetmap.org')
      expect(iframe.getAttribute('src')).toContain('48.8566')
      expect(iframe.getAttribute('src')).toContain('2.3522')
    })

    it('utilise le locationName comme title', () => {
      render(<MiniMap {...defaultProps} locationName="Paris" />)

      expect(screen.getByTitle('Paris')).toBeInTheDocument()
    })

    it('applique la hauteur par defaut', () => {
      const { container } = render(<MiniMap {...defaultProps} />)

      const wrapper = container.firstChild
      expect(wrapper).toHaveClass('h-40')
    })

    it('applique une hauteur personnalisee', () => {
      const { container } = render(<MiniMap {...defaultProps} height="h-64" />)

      const wrapper = container.firstChild
      expect(wrapper).toHaveClass('h-64')
    })

    it('a les attributs de securite corrects', () => {
      render(<MiniMap {...defaultProps} />)

      const iframe = screen.getByTitle('Localisation')
      expect(iframe).toHaveAttribute('loading', 'lazy')
      expect(iframe).toHaveAttribute('referrerPolicy', 'no-referrer')
    })
  })

  describe('bbox calculation', () => {
    it('calcule correctement les limites de la carte', () => {
      render(<MiniMap latitude={48.8566} longitude={2.3522} />)

      const iframe = screen.getByTitle('Localisation')
      const src = iframe.getAttribute('src') || ''

      // bbox should include latitude/longitude with offset
      expect(src).toContain('bbox=')
      expect(src).toContain('marker=48.8566')
    })
  })
})

describe('MiniMapStatic', () => {
  const defaultProps = {
    latitude: 48.8566,
    longitude: 2.3522,
  }

  describe('rendering', () => {
    it('rend une image avec la bonne URL', () => {
      render(<MiniMapStatic {...defaultProps} />)

      const img = screen.getByRole('img', { name: 'Localisation' })
      expect(img).toBeInTheDocument()
      expect(img).toHaveAttribute('src')
      expect(img.getAttribute('src')).toContain('staticmap')
      expect(img.getAttribute('src')).toContain('48.8566')
      expect(img.getAttribute('src')).toContain('2.3522')
    })

    it('utilise le locationName comme alt', () => {
      render(<MiniMapStatic {...defaultProps} locationName="Chantier ABC" />)

      expect(screen.getByRole('img', { name: 'Chantier ABC' })).toBeInTheDocument()
    })

    it('applique la hauteur personnalisee', () => {
      const { container } = render(<MiniMapStatic {...defaultProps} height="h-32" />)

      const wrapper = container.firstChild
      expect(wrapper).toHaveClass('h-32')
    })

    it('charge en lazy', () => {
      render(<MiniMapStatic {...defaultProps} />)

      const img = screen.getByRole('img', { name: 'Localisation' })
      expect(img).toHaveAttribute('loading', 'lazy')
    })
  })
})

describe('MapPlaceholder', () => {
  describe('rendering', () => {
    it('rend un placeholder', () => {
      const { container } = render(<MapPlaceholder />)

      expect(container.firstChild).toBeInTheDocument()
      expect(container.firstChild).toHaveClass('h-40')
    })

    it('applique une hauteur personnalisee', () => {
      const { container } = render(<MapPlaceholder height="h-24" />)

      expect(container.firstChild).toHaveClass('h-24')
    })

    it('a le style de base', () => {
      const { container } = render(<MapPlaceholder />)

      expect(container.firstChild).toHaveClass('rounded-lg')
      expect(container.firstChild).toHaveClass('bg-gray-100')
    })
  })
})
