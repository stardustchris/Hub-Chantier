/**
 * Tests unitaires pour sanitize.ts
 */

import { describe, it, expect } from 'vitest'
import { sanitizeHTML, sanitizeText, sanitizeURL, escapeHTML } from './sanitize'

describe('sanitize', () => {
  describe('sanitizeHTML', () => {
    it('autorise les balises de formatage basique', () => {
      const input = '<b>bold</b> <i>italic</i> <em>emphasis</em> <strong>strong</strong>'
      const result = sanitizeHTML(input)
      expect(result).toContain('<b>bold</b>')
      expect(result).toContain('<i>italic</i>')
      expect(result).toContain('<em>emphasis</em>')
      expect(result).toContain('<strong>strong</strong>')
    })

    it('autorise les liens avec href et target', () => {
      const input = '<a href="https://example.com" target="_blank">link</a>'
      const result = sanitizeHTML(input)
      expect(result).toContain('href="https://example.com"')
      expect(result).toContain('target="_blank"')
    })

    it('autorise les listes', () => {
      const input = '<ul><li>item 1</li><li>item 2</li></ul>'
      const result = sanitizeHTML(input)
      expect(result).toContain('<ul>')
      expect(result).toContain('<li>item 1</li>')
    })

    it('supprime les scripts', () => {
      const input = '<script>alert("xss")</script>text'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('<script>')
      expect(result).not.toContain('alert')
      expect(result).toContain('text')
    })

    it('supprime les iframes', () => {
      const input = '<iframe src="https://evil.com"></iframe>'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('<iframe')
      expect(result).not.toContain('evil.com')
    })

    it('supprime les attributs onerror', () => {
      const input = '<img src="x" onerror="alert(1)">'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('onerror')
      expect(result).not.toContain('alert')
    })

    it('supprime les attributs onclick', () => {
      const input = '<div onclick="alert(1)">click me</div>'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('onclick')
    })

    it('supprime les balises style', () => {
      const input = '<style>body{display:none}</style>'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('<style>')
    })

    it('supprime les formulaires', () => {
      const input = '<form action="/steal"><input type="text"></form>'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('<form')
      expect(result).not.toContain('<input')
    })

    it('gere les chaines vides', () => {
      expect(sanitizeHTML('')).toBe('')
    })

    it('accepte une config personnalisee', () => {
      const input = '<div class="test">content</div>'
      const result = sanitizeHTML(input, { ALLOWED_TAGS: ['div'], ALLOWED_ATTR: ['class'] })
      expect(result).toContain('<div')
      expect(result).toContain('class="test"')
    })
  })

  describe('sanitizeText', () => {
    it('supprime toutes les balises HTML', () => {
      const input = '<b>bold</b> <script>evil</script> <p>paragraph</p>'
      const result = sanitizeText(input)
      expect(result).toBe('bold  paragraph')
    })

    it('conserve le texte simple', () => {
      const input = 'Hello World'
      expect(sanitizeText(input)).toBe('Hello World')
    })

    it('gere les chaines vides', () => {
      expect(sanitizeText('')).toBe('')
    })

    it('supprime les attributs', () => {
      const input = '<a href="javascript:alert(1)">link</a>'
      const result = sanitizeText(input)
      expect(result).toBe('link')
    })
  })

  describe('sanitizeURL', () => {
    it('autorise les URLs https', () => {
      const url = 'https://example.com/path'
      expect(sanitizeURL(url)).toBe(url)
    })

    it('autorise les URLs http', () => {
      const url = 'http://example.com/path'
      expect(sanitizeURL(url)).toBe(url)
    })

    it('autorise les chemins relatifs', () => {
      const url = '/path/to/resource'
      expect(sanitizeURL(url)).toBe(url)
    })

    it('bloque javascript:', () => {
      expect(sanitizeURL('javascript:alert(1)')).toBe('')
      expect(sanitizeURL('JAVASCRIPT:alert(1)')).toBe('')
      expect(sanitizeURL('  javascript:alert(1)')).toBe('')
    })

    it('bloque data:', () => {
      expect(sanitizeURL('data:text/html,<script>alert(1)</script>')).toBe('')
      expect(sanitizeURL('DATA:text/html,<script>alert(1)</script>')).toBe('')
    })

    it('bloque vbscript:', () => {
      expect(sanitizeURL('vbscript:msgbox(1)')).toBe('')
    })

    it('gere les URLs vides', () => {
      expect(sanitizeURL('')).toBe('')
    })

    it('preserve les URLs avec query params', () => {
      const url = 'https://example.com/search?q=test&page=1'
      expect(sanitizeURL(url)).toBe(url)
    })
  })

  describe('escapeHTML', () => {
    it('echappe les chevrons', () => {
      expect(escapeHTML('<div>')).toBe('&lt;div&gt;')
    })

    it('echappe les ampersands', () => {
      expect(escapeHTML('a & b')).toBe('a &amp; b')
    })

    it('echappe les guillemets doubles', () => {
      expect(escapeHTML('"quoted"')).toBe('&quot;quoted&quot;')
    })

    it('echappe les guillemets simples', () => {
      expect(escapeHTML("it's")).toBe('it&#039;s')
    })

    it('echappe plusieurs caracteres speciaux', () => {
      const input = '<script>alert("xss")</script>'
      const expected = '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
      expect(escapeHTML(input)).toBe(expected)
    })

    it('conserve le texte normal', () => {
      expect(escapeHTML('Hello World 123')).toBe('Hello World 123')
    })

    it('gere les chaines vides', () => {
      expect(escapeHTML('')).toBe('')
    })
  })
})
