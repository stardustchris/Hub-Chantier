// @vitest-environment jsdom
/**
 * Tests pour APIKeysPage
 * Page de gestion des cles API (composant presentationnel)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import APIKeysPage from './APIKeysPage'

// Mock des fonctions du hook
const mockSetShowCreateModal = vi.fn()
const mockCopySecret = vi.fn()
const mockRevokeKey = vi.fn()
const mockOnKeyCreated = vi.fn()
const mockCloseSecretModal = vi.fn()

const defaultHookReturn = {
  apiKeys: [] as any[],
  isLoading: false,
  showCreateModal: false,
  setShowCreateModal: mockSetShowCreateModal,
  showSecretModal: false,
  newSecret: '',
  newKeyInfo: null as any,
  secretCopied: false,
  copySecret: mockCopySecret,
  revokeKey: mockRevokeKey,
  onKeyCreated: mockOnKeyCreated,
  closeSecretModal: mockCloseSecretModal,
}

let hookReturn = { ...defaultHookReturn }

vi.mock('../hooks/useAPIKeys', () => ({
  useAPIKeys: () => hookReturn,
  formatDate: (d: string | null) => d ? '1 janv. 2025, 10:00' : 'Jamais',
  isExpiringSoon: (d: string | null) => {
    if (!d) return false
    return d === '2025-02-01T00:00:00Z' // convention for test: this date = expiring soon
  },
  isExpired: (d: string | null) => {
    if (!d) return false
    return d === '2024-01-01T00:00:00Z' // convention for test: this date = expired
  },
}))

// Mock Layout
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock des modals apikeys
vi.mock('../components/apikeys', () => ({
  CreateAPIKeyModal: ({ onClose, onCreated }: any) => (
    <div data-testid="create-apikey-modal">
      <button onClick={onClose}>Fermer creation</button>
      <button onClick={() => onCreated('secret_xyz', { key_prefix: 'hc_', nom: 'Test', expires_at: null })}>Creer</button>
    </div>
  ),
  APIKeySecretModal: ({ secret, onCopy, onClose }: any) => (
    <div data-testid="secret-modal">
      <span>{secret}</span>
      <button onClick={onCopy}>Copier</button>
      <button onClick={onClose}>Fermer secret</button>
    </div>
  ),
}))

// Mock AuthContext
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', email: 'test@test.com', nom: 'Test', prenom: 'User', role: 'admin', is_active: true, couleur: '#333', created_at: '', updated_at: '' },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}))

const activeKey = {
  id: 'key-1',
  nom: 'Cle Production',
  description: 'Cle pour l\'API de production',
  key_prefix: 'hc_prod_abc',
  scopes: ['read:chantiers', 'write:chantiers'],
  is_active: true,
  expires_at: '2026-06-15T00:00:00Z',
  created_at: '2025-01-10T08:00:00Z',
  last_used_at: '2025-01-25T14:30:00Z',
}

const revokedKey = {
  id: 'key-2',
  nom: 'Cle Revoquee',
  description: '',
  key_prefix: 'hc_old_xyz',
  scopes: ['read:chantiers'],
  is_active: false,
  expires_at: null,
  created_at: '2025-01-05T08:00:00Z',
  last_used_at: null,
}

const expiredKey = {
  id: 'key-3',
  nom: 'Cle Expiree',
  description: 'Cette cle a expire',
  key_prefix: 'hc_exp_def',
  scopes: ['read:documents'],
  is_active: true,
  expires_at: '2024-01-01T00:00:00Z', // matches isExpired mock
  created_at: '2024-06-01T08:00:00Z',
  last_used_at: '2024-12-20T10:00:00Z',
}

const expiringSoonKey = {
  id: 'key-4',
  nom: 'Cle Bientot Expiree',
  description: 'Expire dans quelques jours',
  key_prefix: 'hc_soon_ghi',
  scopes: ['read:users'],
  is_active: true,
  expires_at: '2025-02-01T00:00:00Z', // matches isExpiringSoon mock
  created_at: '2025-01-01T08:00:00Z',
  last_used_at: '2025-01-28T09:00:00Z',
}

function renderPage() {
  return render(
    <MemoryRouter>
      <APIKeysPage />
    </MemoryRouter>
  )
}

describe('APIKeysPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    hookReturn = { ...defaultHookReturn }
  })

  describe('Header', () => {
    it('affiche le titre de la page', () => {
      renderPage()
      expect(screen.getByText('Clés API')).toBeInTheDocument()
    })

    it('affiche la description', () => {
      renderPage()
      expect(screen.getByText(/Gérez vos clés d'authentification/)).toBeInTheDocument()
    })

    it('affiche le bouton de creation', () => {
      renderPage()
      expect(screen.getByText('Créer une clé')).toBeInTheDocument()
    })

    it('ouvre le modal de creation au clic', () => {
      renderPage()
      fireEvent.click(screen.getByText('Créer une clé'))
      expect(mockSetShowCreateModal).toHaveBeenCalledWith(true)
    })
  })

  describe('Etat de chargement', () => {
    it('affiche le loader quand isLoading est true', () => {
      hookReturn = { ...defaultHookReturn, isLoading: true }
      const { container } = renderPage()
      const spinner = container.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })

    it('ne affiche pas la liste ou l\'etat vide en chargement', () => {
      hookReturn = { ...defaultHookReturn, isLoading: true }
      renderPage()
      expect(screen.queryByText('Aucune clé API')).not.toBeInTheDocument()
    })
  })

  describe('Etat vide', () => {
    it('affiche le message quand aucune cle', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [], isLoading: false }
      renderPage()
      expect(screen.getByText('Aucune clé API')).toBeInTheDocument()
    })

    it('affiche le message d\'aide', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [], isLoading: false }
      renderPage()
      expect(screen.getByText(/Créez votre première clé pour commencer/)).toBeInTheDocument()
    })
  })

  describe('Liste des cles API', () => {
    it('affiche le nom de la cle', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [activeKey] }
      renderPage()
      expect(screen.getByText('Cle Production')).toBeInTheDocument()
    })

    it('affiche la description de la cle', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [activeKey] }
      renderPage()
      expect(screen.getByText("Cle pour l'API de production")).toBeInTheDocument()
    })

    it('affiche le prefix de la cle', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [activeKey] }
      renderPage()
      expect(screen.getByText('hc_prod_abc...')).toBeInTheDocument()
    })

    it('affiche les scopes de la cle', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [activeKey] }
      renderPage()
      expect(screen.getByText('read:chantiers')).toBeInTheDocument()
      expect(screen.getByText('write:chantiers')).toBeInTheDocument()
    })

    it('affiche le badge revoquee pour une cle inactive', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [revokedKey] }
      renderPage()
      expect(screen.getByText('Révoquée')).toBeInTheDocument()
    })

    it('affiche le badge expiree', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [expiredKey] }
      renderPage()
      expect(screen.getByText('Expirée')).toBeInTheDocument()
    })

    it('affiche le badge expire bientot', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [expiringSoonKey] }
      renderPage()
      expect(screen.getByText('Expire bientôt')).toBeInTheDocument()
    })

    it('ne affiche pas la description si vide', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [revokedKey] }
      renderPage()
      // revokedKey has empty description
      const descriptions = screen.queryByText("Cle pour l'API de production")
      expect(descriptions).not.toBeInTheDocument()
    })

    it('affiche les dates formatees', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [activeKey] }
      renderPage()
      // formatDate mock returns '1 janv. 2025, 10:00' for any non-null date
      const dateElements = screen.getAllByText('1 janv. 2025, 10:00')
      expect(dateElements.length).toBeGreaterThanOrEqual(3) // created_at, last_used_at, expires_at
    })
  })

  describe('Actions sur une cle', () => {
    it('affiche le bouton revoquer pour une cle active', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [activeKey] }
      renderPage()
      expect(screen.getByTitle('Révoquer cette clé')).toBeInTheDocument()
    })

    it('appelle revokeKey au clic sur revoquer', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [activeKey] }
      renderPage()
      fireEvent.click(screen.getByTitle('Révoquer cette clé'))
      expect(mockRevokeKey).toHaveBeenCalledWith('key-1', 'Cle Production')
    })

    it('ne affiche pas le bouton revoquer pour une cle inactive', () => {
      hookReturn = { ...defaultHookReturn, apiKeys: [revokedKey] }
      renderPage()
      expect(screen.queryByTitle('Révoquer cette clé')).not.toBeInTheDocument()
    })
  })

  describe('Modals', () => {
    it('affiche le modal de creation quand showCreateModal est true', () => {
      hookReturn = { ...defaultHookReturn, showCreateModal: true }
      renderPage()
      expect(screen.getByTestId('create-apikey-modal')).toBeInTheDocument()
    })

    it('ne affiche pas le modal de creation quand showCreateModal est false', () => {
      hookReturn = { ...defaultHookReturn, showCreateModal: false }
      renderPage()
      expect(screen.queryByTestId('create-apikey-modal')).not.toBeInTheDocument()
    })

    it('affiche le modal secret quand showSecretModal est true avec newKeyInfo', () => {
      hookReturn = {
        ...defaultHookReturn,
        showSecretModal: true,
        newSecret: 'hc_secret_abc123',
        newKeyInfo: { key_prefix: 'hc_abc', nom: 'Nouvelle Cle', expires_at: null },
      }
      renderPage()
      expect(screen.getByTestId('secret-modal')).toBeInTheDocument()
      expect(screen.getByText('hc_secret_abc123')).toBeInTheDocument()
    })

    it('ne affiche pas le modal secret sans newKeyInfo', () => {
      hookReturn = {
        ...defaultHookReturn,
        showSecretModal: true,
        newKeyInfo: null as any,
      }
      renderPage()
      expect(screen.queryByTestId('secret-modal')).not.toBeInTheDocument()
    })

    it('appelle closeSecretModal depuis le modal secret', () => {
      hookReturn = {
        ...defaultHookReturn,
        showSecretModal: true,
        newSecret: 'hc_test_secret',
        newKeyInfo: { key_prefix: 'hc_test', nom: 'Test', expires_at: null },
      }
      renderPage()
      fireEvent.click(screen.getByText('Fermer secret'))
      expect(mockCloseSecretModal).toHaveBeenCalled()
    })

    it('appelle copySecret depuis le modal secret', () => {
      hookReturn = {
        ...defaultHookReturn,
        showSecretModal: true,
        newSecret: 'hc_test_secret',
        newKeyInfo: { key_prefix: 'hc_test', nom: 'Test', expires_at: null },
      }
      renderPage()
      fireEvent.click(screen.getByText('Copier'))
      expect(mockCopySecret).toHaveBeenCalled()
    })
  })

  describe('Affichage de plusieurs cles', () => {
    it('affiche toutes les cles de la liste', () => {
      hookReturn = {
        ...defaultHookReturn,
        apiKeys: [activeKey, revokedKey, expiredKey, expiringSoonKey],
      }
      renderPage()
      expect(screen.getByText('Cle Production')).toBeInTheDocument()
      expect(screen.getByText('Cle Revoquee')).toBeInTheDocument()
      expect(screen.getByText('Cle Expiree')).toBeInTheDocument()
      expect(screen.getByText('Cle Bientot Expiree')).toBeInTheDocument()
    })

    it('affiche le bouton revoquer uniquement pour les cles actives', () => {
      hookReturn = {
        ...defaultHookReturn,
        apiKeys: [activeKey, revokedKey, expiredKey],
      }
      renderPage()
      // activeKey and expiredKey are is_active: true, revokedKey is is_active: false
      const revokeButtons = screen.getAllByTitle('Révoquer cette clé')
      expect(revokeButtons).toHaveLength(2)
    })
  })
})
