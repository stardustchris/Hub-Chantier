/**
 * Tests pour le composant ResponsiveImage (P2-5).
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ResponsiveImage } from './ResponsiveImage'

describe('ResponsiveImage', () => {
  // ===== SANS WEBP =====

  describe('sans variantes WebP', () => {
    it('rend une img simple sans webpVariants', () => {
      render(<ResponsiveImage src="/photo.jpg" alt="Photo test" />)
      const img = screen.getByRole('img')
      expect(img).toHaveAttribute('src', '/photo.jpg')
      expect(img).toHaveAttribute('alt', 'Photo test')
    })

    it('rend une img simple avec webpVariants vide', () => {
      render(<ResponsiveImage src="/photo.jpg" alt="Photo test" webpVariants={{}} />)
      const img = screen.getByRole('img')
      expect(img).toHaveAttribute('src', '/photo.jpg')
    })

    it('ajoute loading=lazy par défaut', () => {
      render(<ResponsiveImage src="/photo.jpg" alt="Photo" />)
      expect(screen.getByRole('img')).toHaveAttribute('loading', 'lazy')
    })

    it('ajoute decoding=async par défaut', () => {
      render(<ResponsiveImage src="/photo.jpg" alt="Photo" />)
      expect(screen.getByRole('img')).toHaveAttribute('decoding', 'async')
    })

    it('transmet les props HTML additionnelles', () => {
      render(
        <ResponsiveImage src="/photo.jpg" alt="Photo" className="w-full rounded" />
      )
      expect(screen.getByRole('img')).toHaveAttribute('class', 'w-full rounded')
    })
  })

  // ===== AVEC WEBP =====

  describe('avec variantes WebP', () => {
    const webpVariants = {
      webp_thumbnail_url: '/uploads/webp/photo_thumbnail.webp',
      webp_medium_url: '/uploads/webp/photo_medium.webp',
      webp_large_url: '/uploads/webp/photo_large.webp',
    }

    it('rend un élément picture', () => {
      const { container } = render(
        <ResponsiveImage src="/photo.jpg" alt="Photo" webpVariants={webpVariants} />
      )
      expect(container.querySelector('picture')).not.toBeNull()
    })

    it('contient une source WebP avec srcSet', () => {
      const { container } = render(
        <ResponsiveImage src="/photo.jpg" alt="Photo" webpVariants={webpVariants} />
      )
      const source = container.querySelector('source')
      expect(source).not.toBeNull()
      expect(source!.getAttribute('type')).toBe('image/webp')
      expect(source!.getAttribute('srcset')).toContain('photo_thumbnail.webp 300w')
      expect(source!.getAttribute('srcset')).toContain('photo_medium.webp 800w')
      expect(source!.getAttribute('srcset')).toContain('photo_large.webp 1200w')
    })

    it('contient un fallback img avec src original', () => {
      render(
        <ResponsiveImage src="/photo.jpg" alt="Photo" webpVariants={webpVariants} />
      )
      const img = screen.getByRole('img')
      expect(img).toHaveAttribute('src', '/photo.jpg')
    })

    it('ajoute sizes responsive', () => {
      const { container } = render(
        <ResponsiveImage src="/photo.jpg" alt="Photo" webpVariants={webpVariants} />
      )
      const source = container.querySelector('source')
      expect(source!.getAttribute('sizes')).toContain('max-width: 640px')
      expect(source!.getAttribute('sizes')).toContain('max-width: 1024px')
    })

    it('gère uniquement thumbnail disponible', () => {
      const { container } = render(
        <ResponsiveImage
          src="/photo.jpg"
          alt="Photo"
          webpVariants={{ webp_thumbnail_url: '/thumb.webp' }}
        />
      )
      const source = container.querySelector('source')
      expect(source).not.toBeNull()
      expect(source!.getAttribute('srcset')).toBe('/thumb.webp 300w')
    })

    it('transmet les props HTML au fallback img', () => {
      render(
        <ResponsiveImage
          src="/photo.jpg"
          alt="Photo"
          webpVariants={webpVariants}
          className="object-cover"
        />
      )
      expect(screen.getByRole('img')).toHaveAttribute('class', 'object-cover')
    })
  })
})
