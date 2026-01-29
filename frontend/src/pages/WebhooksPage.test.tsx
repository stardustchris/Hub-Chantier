// @vitest-environment jsdom
/**
 * Tests pour WebhooksPage
 * Page de gestion des webhooks (composant presentationnel)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import WebhooksPage from './WebhooksPage'

// Mock du hook useWebhooks
const mockSetShowCreateModal = vi.fn()
const mockCopySecret = vi.fn()
const mockDeleteWebhook = vi.fn()
const mockTestWebhook = vi.fn()
const mockViewDeliveries = vi.fn()
const mockOnWebhookCreated = vi.fn()
const mockCloseSecretModal = vi.fn()
const mockCloseDeliveryModal = vi.fn()
const mockFormatDate = vi.fn((d: string | null | undefined) => d ? '1 janv. 2025, 10:00' : 'Jamais')
const mockTruncateUrl = vi.fn((url: string) => url.length > 50 ? url.substring(0, 50) + '...' : url)

const defaultHookReturn = {
  webhooks: [] as any[],
  isLoading: false,
  showCreateModal: false,
  showSecretModal: false,
  showDeliveryModal: false,
  selectedWebhook: null,
  newSecret: '',
  newWebhook: null,
  secretCopied: false,
  setShowCreateModal: mockSetShowCreateModal,
  copySecret: mockCopySecret,
  deleteWebhook: mockDeleteWebhook,
  testWebhook: mockTestWebhook,
  viewDeliveries: mockViewDeliveries,
  onWebhookCreated: mockOnWebhookCreated,
  closeSecretModal: mockCloseSecretModal,
  closeDeliveryModal: mockCloseDeliveryModal,
  formatDate: mockFormatDate,
  truncateUrl: mockTruncateUrl,
}

let hookReturn = { ...defaultHookReturn }

vi.mock('../hooks/useWebhooks', () => ({
  useWebhooks: () => hookReturn,
}))

// Mock Layout pour simplifier
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock des modals webhook
vi.mock('../components/webhooks', () => ({
  CreateWebhookModal: ({ onClose, onCreated }: any) => (
    <div data-testid="create-webhook-modal">
      <button onClick={onClose}>Fermer creation</button>
      <button onClick={() => onCreated('secret123', { id: 'new' })}>Creer</button>
    </div>
  ),
  SecretModal: ({ secret, onCopy, onClose }: any) => (
    <div data-testid="secret-modal">
      <span>{secret}</span>
      <button onClick={onCopy}>Copier</button>
      <button onClick={onClose}>Fermer secret</button>
    </div>
  ),
  DeliveryHistoryModal: ({ webhook, onClose }: any) => (
    <div data-testid="delivery-modal">
      <span>{webhook?.url}</span>
      <button onClick={onClose}>Fermer historique</button>
    </div>
  ),
}))

// Mock AuthContext pour Layout
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', email: 'test@test.com', nom: 'Test', prenom: 'User', role: 'admin', is_active: true, couleur: '#333', created_at: '', updated_at: '' },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}))

const sampleWebhook = {
  id: 'wh-1',
  url: 'https://example.com/webhook',
  events: ['chantier.created', 'chantier.updated'],
  is_active: true,
  description: 'Webhook de test',
  consecutive_failures: 0,
  created_at: '2025-01-15T10:00:00Z',
  last_triggered_at: '2025-01-20T14:30:00Z',
}

const inactiveWebhook = {
  id: 'wh-2',
  url: 'https://example.com/inactive',
  events: ['user.created'],
  is_active: false,
  description: '',
  consecutive_failures: 0,
  created_at: '2025-01-10T08:00:00Z',
  last_triggered_at: null,
}

const failingWebhook = {
  id: 'wh-3',
  url: 'https://example.com/failing',
  events: ['document.uploaded'],
  is_active: true,
  description: 'Webhook avec echecs',
  consecutive_failures: 3,
  created_at: '2025-01-12T09:00:00Z',
  last_triggered_at: '2025-01-18T16:00:00Z',
}

function renderPage() {
  return render(
    <MemoryRouter>
      <WebhooksPage />
    </MemoryRouter>
  )
}

describe('WebhooksPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    hookReturn = { ...defaultHookReturn }
  })

  describe('Header', () => {
    it('affiche le titre de la page', () => {
      renderPage()
      expect(screen.getByText('Gestion des Webhooks')).toBeInTheDocument()
    })

    it('affiche la description', () => {
      renderPage()
      expect(screen.getByText(/Recevez des notifications en temps réel/)).toBeInTheDocument()
    })

    it('affiche le bouton de creation', () => {
      renderPage()
      expect(screen.getByText('Créer un Webhook')).toBeInTheDocument()
    })

    it('ouvre le modal de creation au clic', () => {
      renderPage()
      fireEvent.click(screen.getByText('Créer un Webhook'))
      expect(mockSetShowCreateModal).toHaveBeenCalledWith(true)
    })
  })

  describe('Etat de chargement', () => {
    it('affiche le loader quand isLoading est true', () => {
      hookReturn = { ...defaultHookReturn, isLoading: true }
      const { container } = renderPage()
      // Loader2 renders an svg with animate-spin class
      const spinner = container.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })

    it('ne affiche pas la liste quand isLoading est true', () => {
      hookReturn = { ...defaultHookReturn, isLoading: true }
      renderPage()
      expect(screen.queryByText('Aucun webhook configuré')).not.toBeInTheDocument()
    })
  })

  describe('Etat vide', () => {
    it('affiche le message quand aucun webhook', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [], isLoading: false }
      renderPage()
      expect(screen.getByText('Aucun webhook configuré')).toBeInTheDocument()
    })

    it('affiche le message d\'aide', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [], isLoading: false }
      renderPage()
      expect(screen.getByText(/Créez votre premier webhook/)).toBeInTheDocument()
    })
  })

  describe('Liste des webhooks', () => {
    it('affiche les webhooks', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [sampleWebhook] }
      renderPage()
      expect(mockTruncateUrl).toHaveBeenCalledWith('https://example.com/webhook')
    })

    it('affiche la description du webhook', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [sampleWebhook] }
      renderPage()
      expect(screen.getByText('Webhook de test')).toBeInTheDocument()
    })

    it('affiche les evenements du webhook', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [sampleWebhook] }
      renderPage()
      expect(screen.getByText('chantier.created')).toBeInTheDocument()
      expect(screen.getByText('chantier.updated')).toBeInTheDocument()
    })

    it('affiche le statut actif', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [sampleWebhook] }
      renderPage()
      expect(screen.getByText('Actif')).toBeInTheDocument()
    })

    it('affiche le statut inactif', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [inactiveWebhook] }
      renderPage()
      expect(screen.getByText('Inactif')).toBeInTheDocument()
    })

    it('affiche le badge d\'echecs consecutifs', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [failingWebhook] }
      renderPage()
      expect(screen.getByText(/3 échec\(s\)/)).toBeInTheDocument()
    })

    it('ne affiche pas la description si vide', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [inactiveWebhook] }
      renderPage()
      // inactiveWebhook has empty description
      expect(screen.queryByText('Webhook de test')).not.toBeInTheDocument()
    })

    it('appelle formatDate pour les dates', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [sampleWebhook] }
      renderPage()
      expect(mockFormatDate).toHaveBeenCalledWith('2025-01-15T10:00:00Z')
      expect(mockFormatDate).toHaveBeenCalledWith('2025-01-20T14:30:00Z')
    })
  })

  describe('Actions sur un webhook', () => {
    it('appelle viewDeliveries au clic sur historique', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [sampleWebhook] }
      renderPage()
      const historyButton = screen.getByTitle('Voir l\'historique')
      fireEvent.click(historyButton)
      expect(mockViewDeliveries).toHaveBeenCalledWith(sampleWebhook)
    })

    it('appelle testWebhook au clic sur tester', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [sampleWebhook] }
      renderPage()
      const testButton = screen.getByTitle('Tester')
      fireEvent.click(testButton)
      expect(mockTestWebhook).toHaveBeenCalledWith(sampleWebhook)
    })

    it('appelle deleteWebhook au clic sur supprimer', () => {
      hookReturn = { ...defaultHookReturn, webhooks: [sampleWebhook] }
      renderPage()
      const deleteButton = screen.getByTitle('Supprimer')
      fireEvent.click(deleteButton)
      expect(mockDeleteWebhook).toHaveBeenCalledWith(sampleWebhook)
    })
  })

  describe('Modals', () => {
    it('affiche le modal de creation quand showCreateModal est true', () => {
      hookReturn = { ...defaultHookReturn, showCreateModal: true }
      renderPage()
      expect(screen.getByTestId('create-webhook-modal')).toBeInTheDocument()
    })

    it('ne affiche pas le modal de creation quand showCreateModal est false', () => {
      hookReturn = { ...defaultHookReturn, showCreateModal: false }
      renderPage()
      expect(screen.queryByTestId('create-webhook-modal')).not.toBeInTheDocument()
    })

    it('affiche le modal secret quand showSecretModal est true avec newWebhook', () => {
      hookReturn = {
        ...defaultHookReturn,
        showSecretModal: true,
        newSecret: 'whsec_abc123',
        newWebhook: sampleWebhook as any,
      }
      renderPage()
      expect(screen.getByTestId('secret-modal')).toBeInTheDocument()
      expect(screen.getByText('whsec_abc123')).toBeInTheDocument()
    })

    it('ne affiche pas le modal secret sans newWebhook', () => {
      hookReturn = {
        ...defaultHookReturn,
        showSecretModal: true,
        newWebhook: null,
      }
      renderPage()
      expect(screen.queryByTestId('secret-modal')).not.toBeInTheDocument()
    })

    it('affiche le modal delivery quand showDeliveryModal et selectedWebhook', () => {
      hookReturn = {
        ...defaultHookReturn,
        showDeliveryModal: true,
        selectedWebhook: sampleWebhook as any,
      }
      renderPage()
      expect(screen.getByTestId('delivery-modal')).toBeInTheDocument()
    })

    it('ne affiche pas le modal delivery sans selectedWebhook', () => {
      hookReturn = {
        ...defaultHookReturn,
        showDeliveryModal: true,
        selectedWebhook: null,
      }
      renderPage()
      expect(screen.queryByTestId('delivery-modal')).not.toBeInTheDocument()
    })

    it('appelle closeSecretModal depuis le modal secret', () => {
      hookReturn = {
        ...defaultHookReturn,
        showSecretModal: true,
        newSecret: 'whsec_test',
        newWebhook: sampleWebhook as any,
      }
      renderPage()
      fireEvent.click(screen.getByText('Fermer secret'))
      expect(mockCloseSecretModal).toHaveBeenCalled()
    })

    it('appelle closeDeliveryModal depuis le modal delivery', () => {
      hookReturn = {
        ...defaultHookReturn,
        showDeliveryModal: true,
        selectedWebhook: sampleWebhook as any,
      }
      renderPage()
      fireEvent.click(screen.getByText('Fermer historique'))
      expect(mockCloseDeliveryModal).toHaveBeenCalled()
    })
  })

  describe('Affichage de plusieurs webhooks', () => {
    it('affiche tous les webhooks de la liste', () => {
      hookReturn = {
        ...defaultHookReturn,
        webhooks: [sampleWebhook, inactiveWebhook, failingWebhook],
      }
      renderPage()
      // Each webhook has its events rendered
      expect(screen.getByText('chantier.created')).toBeInTheDocument()
      expect(screen.getByText('user.created')).toBeInTheDocument()
      expect(screen.getByText('document.uploaded')).toBeInTheDocument()
    })
  })
})
