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

  // ===== UPLOAD POST MEDIA - edge cases =====

  describe('uploadPostMedia edge cases', () => {
    it('gere un tableau vide de fichiers', async () => {
      vi.mocked(api.post).mockResolvedValue({ data: { files: [] } })
      const result = await uploadService.uploadPostMedia('post-1', [])
      expect(result.files).toEqual([])
    })

    it('rejette si un fichier du lot est trop volumineux', async () => {
      const largeContent = new Array(3 * 1024 * 1024).fill('a').join('')
      const files = [
        new File(['content'], 'ok.jpg', { type: 'image/jpeg' }),
        new File([largeContent], 'big.jpg', { type: 'image/jpeg' }),
      ]
      await expect(uploadService.uploadPostMedia('post-1', files)).rejects.toThrow(
        UploadValidationError
      )
      expect(api.post).not.toHaveBeenCalled()
    })
  })

  // ===== UPLOAD CHANTIER PHOTO - edge cases =====

  describe('uploadChantierPhoto edge cases', () => {
    it('rejette un fichier trop volumineux', async () => {
      const largeContent = new Array(5 * 1024 * 1024).fill('a').join('')
      const file = new File([largeContent], 'huge.png', { type: 'image/png' })
      await expect(uploadService.uploadChantierPhoto('chantier-1', file)).rejects.toThrow(
        'trop volumineux'
      )
    })

    it('retourne la thumbnail_url si presente', async () => {
      vi.mocked(api.post).mockResolvedValue({
        data: { url: '/uploads/chantier.jpg', thumbnail_url: '/uploads/thumb.jpg' },
      })
      const file = new File(['content'], 'chantier.jpg', { type: 'image/jpeg' })
      const result = await uploadService.uploadChantierPhoto('c1', file)
      expect(result.thumbnail_url).toBe('/uploads/thumb.jpg')
    })
  })

  // ===== BOUNDARY VALIDATION =====

  describe('file size boundary', () => {
    it('accepte un fichier exactement a la limite (2Mo)', async () => {
      vi.mocked(api.post).mockResolvedValue({ data: { url: 'test.jpg' } })
      const buffer = new ArrayBuffer(2 * 1024 * 1024)
      const file = new File([buffer], 'exact.jpg', { type: 'image/jpeg' })
      const result = await uploadService.uploadProfilePhoto(file)
      expect(result).toEqual({ url: 'test.jpg' })
    })

    it('rejette un fichier juste au-dessus de la limite', async () => {
      const buffer = new ArrayBuffer(2 * 1024 * 1024 + 1)
      const file = new File([buffer], 'over.jpg', { type: 'image/jpeg' })
      await expect(uploadService.uploadProfilePhoto(file)).rejects.toThrow(UploadValidationError)
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

    it('accepte un parametre maxSizeMB optionnel', () => {
      expect(uploadService.compressImage.length).toBeLessThanOrEqual(2)
    })
  })

  // ===== ERROR HANDLING =====

  describe('error handling', () => {
    it('gere les erreurs API sur uploadProfilePhoto', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Network error'))
      const file = new File(['content'], 'photo.jpg', { type: 'image/jpeg' })
      await expect(uploadService.uploadProfilePhoto(file)).rejects.toThrow('Network error')
    })

    it('gere les erreurs API sur uploadPostMedia', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Server error'))
      const files = [new File(['content'], 'photo.jpg', { type: 'image/jpeg' })]
      await expect(uploadService.uploadPostMedia('post-1', files)).rejects.toThrow('Server error')
    })

    it('gere les erreurs API sur uploadChantierPhoto', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Upload failed'))
      const file = new File(['content'], 'photo.jpg', { type: 'image/jpeg' })
      await expect(uploadService.uploadChantierPhoto('chantier-1', file)).rejects.toThrow('Upload failed')
    })
  })

  // ===== FORMDATA =====

  describe('FormData construction', () => {
    it('ajoute le fichier au FormData pour uploadProfilePhoto', async () => {
      vi.mocked(api.post).mockResolvedValue({ data: { url: 'test.jpg' } })
      const appendSpy = vi.spyOn(FormData.prototype, 'append')
      const file = new File(['content'], 'profile.jpg', { type: 'image/jpeg' })
      await uploadService.uploadProfilePhoto(file)
      expect(appendSpy).toHaveBeenCalledWith('file', file)
      appendSpy.mockRestore()
    })

    it('ajoute les fichiers au FormData pour uploadPostMedia', async () => {
      vi.mocked(api.post).mockResolvedValue({ data: { files: [] } })
      const appendSpy = vi.spyOn(FormData.prototype, 'append')
      const files = [
        new File(['content1'], 'photo1.jpg', { type: 'image/jpeg' }),
        new File(['content2'], 'photo2.jpg', { type: 'image/jpeg' }),
      ]
      await uploadService.uploadPostMedia('post-1', files)
      expect(appendSpy).toHaveBeenCalledWith('files', files[0])
      expect(appendSpy).toHaveBeenCalledWith('files', files[1])
      appendSpy.mockRestore()
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
