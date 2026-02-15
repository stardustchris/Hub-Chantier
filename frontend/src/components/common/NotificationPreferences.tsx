/**
 * NotificationPreferences - Modal de préférences de notifications (5.1.5)
 *
 * Permet de configurer les préférences de notifications par catégorie:
 * - Mentions
 * - Validations FdH
 * - Signalements
 * - Météo
 * - Pointages
 * - Documents
 *
 * Chaque catégorie peut être configurée pour:
 * - Notifications push
 * - Notifications in-app
 * - Notifications email
 *
 * Les préférences sont sauvegardées dans localStorage.
 */

import { useState, useEffect } from 'react'
import { X, Settings, Bell, Mail, Smartphone } from 'lucide-react'

export interface NotificationCategoryPreferences {
  push: boolean
  inApp: boolean
  email: boolean
}

export interface NotificationPreferencesData {
  mentions: NotificationCategoryPreferences
  validations_fdh: NotificationCategoryPreferences
  signalements: NotificationCategoryPreferences
  meteo: NotificationCategoryPreferences
  pointages: NotificationCategoryPreferences
  documents: NotificationCategoryPreferences
}

const STORAGE_KEY = 'hub_notification_preferences'

const DEFAULT_PREFERENCES: NotificationPreferencesData = {
  mentions: { push: true, inApp: true, email: false },
  validations_fdh: { push: true, inApp: true, email: true },
  signalements: { push: true, inApp: true, email: false },
  meteo: { push: true, inApp: true, email: false },
  pointages: { push: false, inApp: true, email: false },
  documents: { push: true, inApp: true, email: false },
}

const CATEGORIES = [
  { id: 'mentions', label: 'Mentions (@)', description: 'Quand quelqu\'un vous mentionne' },
  { id: 'validations_fdh', label: 'Validations FdH', description: 'Validation de feuilles d\'heures' },
  { id: 'signalements', label: 'Signalements', description: 'Nouveaux signalements et résolutions' },
  { id: 'meteo', label: 'Météo', description: 'Alertes météo pour vos chantiers' },
  { id: 'pointages', label: 'Pointages', description: 'Pointages d\'équipe' },
  { id: 'documents', label: 'Documents', description: 'Nouveaux documents ajoutés' },
] as const

export function loadNotificationPreferences(): NotificationPreferencesData {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) }
    }
  } catch (error) {
    console.error('Erreur chargement préférences notifications', error)
  }
  return DEFAULT_PREFERENCES
}

function saveNotificationPreferences(prefs: NotificationPreferencesData): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs))
  } catch (error) {
    console.error('Erreur sauvegarde préférences notifications', error)
  }
}

interface NotificationPreferencesProps {
  isOpen: boolean
  onClose: () => void
}

export default function NotificationPreferences({ isOpen, onClose }: NotificationPreferencesProps) {
  const [preferences, setPreferences] = useState<NotificationPreferencesData>(DEFAULT_PREFERENCES)

  useEffect(() => {
    if (isOpen) {
      setPreferences(loadNotificationPreferences())
    }
  }, [isOpen])

  const handleToggle = (
    categoryId: keyof NotificationPreferencesData,
    channel: keyof NotificationCategoryPreferences
  ) => {
    setPreferences((prev) => ({
      ...prev,
      [categoryId]: {
        ...prev[categoryId],
        [channel]: !prev[categoryId][channel],
      },
    }))
  }

  const handleSave = () => {
    saveNotificationPreferences(preferences)
    onClose()
  }

  if (!isOpen) return null

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50" onClick={onClose} />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="px-6 py-4 border-b flex items-center justify-between sticky top-0 bg-white">
            <div className="flex items-center gap-3">
              <Settings className="w-6 h-6 text-gray-700" />
              <h2 className="text-xl font-semibold text-gray-900">Préférences de notifications</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full"
              aria-label="Fermer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4">
            <p className="text-sm text-gray-600 mb-6">
              Configurez comment vous souhaitez recevoir les notifications pour chaque catégorie.
            </p>

            {/* Table header */}
            <div className="grid grid-cols-[2fr_1fr_1fr_1fr] gap-4 mb-4 pb-3 border-b">
              <div className="text-sm font-medium text-gray-500 uppercase">Catégorie</div>
              <div className="text-center">
                <Smartphone className="w-5 h-5 text-gray-500 mx-auto mb-1" />
                <div className="text-xs font-medium text-gray-500 uppercase">Push</div>
              </div>
              <div className="text-center">
                <Bell className="w-5 h-5 text-gray-500 mx-auto mb-1" />
                <div className="text-xs font-medium text-gray-500 uppercase">In-app</div>
              </div>
              <div className="text-center">
                <Mail className="w-5 h-5 text-gray-500 mx-auto mb-1" />
                <div className="text-xs font-medium text-gray-500 uppercase">Email</div>
              </div>
            </div>

            {/* Categories */}
            <div className="space-y-4">
              {CATEGORIES.map((category) => {
                const categoryId = category.id as keyof NotificationPreferencesData
                const prefs = preferences[categoryId]

                return (
                  <div
                    key={category.id}
                    className="grid grid-cols-[2fr_1fr_1fr_1fr] gap-4 items-center py-3 border-b last:border-b-0"
                  >
                    <div>
                      <div className="font-medium text-gray-900">{category.label}</div>
                      <div className="text-sm text-gray-500">{category.description}</div>
                    </div>
                    <div className="flex justify-center">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={prefs.push}
                          onChange={() => handleToggle(categoryId, 'push')}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                    <div className="flex justify-center">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={prefs.inApp}
                          onChange={() => handleToggle(categoryId, 'inApp')}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                    <div className="flex justify-center">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={prefs.email}
                          onChange={() => handleToggle(categoryId, 'email')}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t bg-gray-50 flex gap-3 justify-end sticky bottom-0">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 font-medium"
            >
              Annuler
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
            >
              Enregistrer
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
