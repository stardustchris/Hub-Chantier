/**
 * Tests pour le service upload
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { uploadService, UploadValidationError } from './upload'
import api from './api'

vi.mock('./api')

describe('uploadService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ===== VALIDATION =====

  describe('validation', () => {
    it('rejette les types de fichiers non supportés', async () => {
      const file = new File(['content'], 'test.txt', { type: 'text/plain' })

      await expect(uploadService.uploadProfilePhoto(file)).rejects.toThrow(UploadValidationError)
      await expect(uploadService.uploadProfilePhoto(file)).rejects.toThrow(
        'Type de fichier non supporté'
      )
    })

    it('rejette les fichiers trop volumineux', async () => {
      // Créer un fichier de 3 Mo (au-dessus de la limite de 2 Mo)
      const largeContent = new Array(3 * 1024 * 1024).fill('a').join('')
      const file = new File([largeContent], 'large.jpg', { type: 'image/jpeg' })

      await expect(uploadService.uploadProfilePhoto(file)).rejects.toThrow(UploadValidationError)
      await expect(uploadService.uploadProfilePhoto(file)).rejects.toThrow(
        'Fichier trop volumineux'
      )
    })

    it('accepte les images JPEG valides', async () => {
      const mockResponse = { url: 'https://example.com/photo.jpg' }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const file = new File(['content'], 'photo.jpg', { type: 'image/jpeg' })
      const result = await uploadService.uploadProfilePhoto(file)

      expect(result).toEqual(mockResponse)
    })

    it('accepte les images PNG valides', async () => {
      const mockResponse = { url: 'https://example.com/photo.png' }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const file = new File(['content'], 'photo.png', { type: 'image/png' })
      const result = await uploadService.uploadProfilePhoto(file)

      expect(result).toEqual(mockResponse)
    })

    it('accepte les images GIF valides', async () => {
      const mockResponse = { url: 'https://example.com/photo.gif' }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const file = new File(['content'], 'photo.gif', { type: 'image/gif' })
      const result = await uploadService.uploadProfilePhoto(file)

      expect(result).toEqual(mockResponse)
    })

    it('accepte les images WebP valides', async () => {
      const mockResponse = { url: 'https://example.com/photo.webp' }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const file = new File(['content'], 'photo.webp', { type: 'image/webp' })
      const result = await uploadService.uploadProfilePhoto(file)

      expect(result).toEqual(mockResponse)
    })
  })

  // ===== UPLOAD PROFILE PHOTO =====

  describe('uploadProfilePhoto', () => {
    it('upload une photo de profil', async () => {
      const mockResponse = { url: 'https://example.com/profile.jpg', thumbnail_url: 'https://example.com/profile_thumb.jpg' }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const file = new File(['content'], 'profile.jpg', { type: 'image/jpeg' })
      const result = await uploadService.uploadProfilePhoto(file)

      expect(api.post).toHaveBeenCalledWith(
        '/api/uploads/profile',
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      expect(result).toEqual(mockResponse)
    })
  })

  // ===== UPLOAD POST MEDIA =====

  describe('uploadPostMedia', () => {
    it('upload des médias pour un post', async () => {
      const mockResponse = { files: [{ url: 'https://example.com/1.jpg' }, { url: 'https://example.com/2.jpg' }] }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const files = [
        new File(['content1'], 'photo1.jpg', { type: 'image/jpeg' }),
        new File(['content2'], 'photo2.jpg', { type: 'image/jpeg' }),
      ]
      const result = await uploadService.uploadPostMedia('post-123', files)

      expect(api.post).toHaveBeenCalledWith(
        '/api/uploads/posts/post-123',
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      expect(result).toEqual(mockResponse)
    })

    it('rejette si un fichier est invalide', async () => {
      const files = [
        new File(['content'], 'photo.jpg', { type: 'image/jpeg' }),
        new File(['content'], 'doc.pdf', { type: 'application/pdf' }),
      ]

      await expect(uploadService.uploadPostMedia('post-123', files)).rejects.toThrow(
        UploadValidationError
      )
    })
  })

  // ===== UPLOAD CHANTIER PHOTO =====

  describe('uploadChantierPhoto', () => {
    it('upload une photo de chantier', async () => {
      const mockResponse = { url: 'https://example.com/chantier.jpg' }
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse })

      const file = new File(['content'], 'chantier.jpg', { type: 'image/jpeg' })
      const result = await uploadService.uploadChantierPhoto('chantier-123', file)

      expect(api.post).toHaveBeenCalledWith(
        '/api/uploads/chantiers/chantier-123',
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      expect(result).toEqual(mockResponse)
    })

    it('rejette les fichiers non-image', async () => {
      const file = new File(['content'], 'doc.pdf', { type: 'application/pdf' })

      await expect(uploadService.uploadChantierPhoto('chantier-123', file)).rejects.toThrow(
        UploadValidationError
      )
    })
  })

  // ===== COMPRESS IMAGE =====

  describe('compressImage', () => {
    // Note: compressImage utilise canvas qui n'est pas disponible dans jsdom
    // Ces tests vérifient le comportement de base

    it('existe comme méthode du service', () => {
      expect(uploadService.compressImage).toBeDefined()
      expect(typeof uploadService.compressImage).toBe('function')
    })
  })
})

describe('UploadValidationError', () => {
  it('est une instance de Error', () => {
    const error = new UploadValidationError('Test error')
    expect(error).toBeInstanceOf(Error)
  })

  it('a le bon nom', () => {
    const error = new UploadValidationError('Test error')
    expect(error.name).toBe('UploadValidationError')
  })

  it('contient le message', () => {
    const error = new UploadValidationError('Test error message')
    expect(error.message).toBe('Test error message')
  })
})
