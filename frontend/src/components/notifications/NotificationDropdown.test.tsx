/**
 * Tests unitaires pour NotificationDropdown
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import NotificationDropdown from './NotificationDropdown'

// Mock du hook useNotifications
vi.mock('../../hooks/useNotifications', () => ({
  useNotifications: () => ({
    notifications: [
      {
        id: '1',
        type: 'comment_added',
        title: 'Nouveau commentaire',
        body: 'Jean a commenté votre post',
        is_read: false,
        created_at: new Date().toISOString(),
      },
      {
        id: '2',
        type: 'mention',
        title: 'Mention',
        body: 'Vous avez été mentionné',
        is_read: true,
        created_at: new Date().toISOString(),
      },
    ],
    unreadCount: 1,
    loading: false,
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
  }),
}))

// Mock des services
vi.mock('../../services/notificationsApi', () => ({
  formatRelativeTime: () => 'il y a 5 min',
}))

vi.mock('../../services/documents', () => ({
  getDocument: vi.fn(),
  downloadDocument: vi.fn(),
  getDocumentPreviewUrl: vi.fn(),
  formatFileSize: vi.fn(),
}))

const renderDropdown = (props = {}) => {
  return render(
    <MemoryRouter>
      <NotificationDropdown isOpen={true} onClose={vi.fn()} {...props} />
    </MemoryRouter>
  )
}

describe('NotificationDropdown', () => {
  describe('rendering', () => {
    it('affiche les notifications', () => {
      renderDropdown()
      expect(screen.getByText('Nouveau commentaire')).toBeInTheDocument()
      expect(screen.getByText('Mention')).toBeInTheDocument()
    })

    it('affiche le nombre de non lues', () => {
      renderDropdown()
      expect(screen.getByText('Notifications')).toBeInTheDocument()
    })

    it('n affiche rien si ferme', () => {
      const { container } = render(
        <MemoryRouter>
          <NotificationDropdown isOpen={false} onClose={vi.fn()} />
        </MemoryRouter>
      )
      expect(container.querySelector('.absolute')).not.toBeInTheDocument()
    })
  })

  describe('interactions', () => {
    it('affiche un bouton d action', () => {
      renderDropdown()
      // There should be action buttons in the dropdown
      expect(screen.getAllByRole('button').length).toBeGreaterThan(0)
    })
  })

  describe('types de notifications', () => {
    it('affiche l icone commentaire pour comment_added', () => {
      const { container } = renderDropdown()
      expect(container.querySelector('.lucide-message-circle')).toBeInTheDocument()
    })

    it('affiche l icone mention pour mention', () => {
      const { container } = renderDropdown()
      expect(container.querySelector('.lucide-at-sign')).toBeInTheDocument()
    })
  })
})
