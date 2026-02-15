/**
 * PageHelp component - Aide contextuelle par page
 * Affiche un bouton d'aide avec badge pulsant pour les nouvelles visites
 * Ouvre un panneau latéral avec le contenu d'aide adapté à la page
 */

import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { createPortal } from 'react-dom'
import { HelpCircle, X } from 'lucide-react'
import { useProgressiveHint } from '../../hooks/useProgressiveHint'
import Tooltip from '../ui/Tooltip'

interface HelpSection {
  title: string
  content: string
}

interface HelpContent {
  title: string
  sections: HelpSection[]
}

// Dictionnaire de contenu d'aide par route
const HELP_CONTENT: Record<string, HelpContent> = {
  '/': {
    title: 'Tableau de bord',
    sections: [
      {
        title: "Vue d'ensemble",
        content: 'Le tableau de bord affiche vos chantiers actifs, la météo, et les dernières actualités.',
      },
      {
        title: 'Pointer',
        content: 'Utilisez la carte en haut pour pointer votre arrivée et votre départ.',
      },
    ],
  },
  '/planning': {
    title: 'Planning',
    sections: [
      {
        title: 'Affectations',
        content: 'Glissez-déposez pour créer ou déplacer des affectations.',
      },
      {
        title: 'Vue',
        content: 'Basculez entre vue semaine et vue mois.',
      },
    ],
  },
  '/feuilles-heures': {
    title: "Feuilles d'heures",
    sections: [
      {
        title: 'Saisie',
        content: 'Cliquez sur une cellule pour saisir les heures.',
      },
      {
        title: 'Validation',
        content: "Les chefs d'équipe valident les heures de leurs compagnons.",
      },
    ],
  },
  '/chantiers': {
    title: 'Chantiers',
    sections: [
      {
        title: 'Liste',
        content: 'Vue de tous vos chantiers avec filtres par statut.',
      },
    ],
  },
  '/documents': {
    title: 'Documents',
    sections: [
      {
        title: 'GED',
        content: 'Gérez vos documents par chantier. Uploadez et classez facilement.',
      },
    ],
  },
  '/formulaires': {
    title: 'Formulaires',
    sections: [
      {
        title: 'Templates',
        content: 'Créez des templates réutilisables pour vos rapports terrain.',
      },
    ],
  },
  '/logistique': {
    title: 'Logistique',
    sections: [
      {
        title: 'Ressources',
        content: 'Gérez vos matériels et véhicules. Réservez par chantier et date.',
      },
    ],
  },
  '/finances': {
    title: 'Finances',
    sections: [
      {
        title: 'Vue consolidée',
        content: 'Vue financière globale de tous vos chantiers.',
      },
    ],
  },
  '/budgets': {
    title: 'Budgets',
    sections: [
      {
        title: 'Gestion budgétaire',
        content: 'Suivez et gérez les budgets de vos chantiers.',
      },
    ],
  },
  '/achats': {
    title: 'Achats',
    sections: [
      {
        title: 'Commandes',
        content: 'Gérez vos bons de commande et achats matériels.',
      },
    ],
  },
  '/fournisseurs': {
    title: 'Fournisseurs',
    sections: [
      {
        title: 'Annuaire',
        content: 'Centralisez vos contacts fournisseurs et leurs tarifs.',
      },
    ],
  },
  '/devis': {
    title: 'Devis',
    sections: [
      {
        title: 'Gestion',
        content: 'Créez, suivez et convertissez vos devis en chantiers.',
      },
    ],
  },
  '/devis/dashboard': {
    title: 'Pipeline devis',
    sections: [
      {
        title: 'Suivi',
        content: 'Visualisez votre pipeline commercial et vos taux de conversion.',
      },
    ],
  },
  '/devis/articles': {
    title: 'Articles',
    sections: [
      {
        title: 'Catalogue',
        content: 'Gérez votre catalogue d\'articles pour construire vos devis rapidement.',
      },
    ],
  },
  '/utilisateurs': {
    title: 'Utilisateurs',
    sections: [
      {
        title: 'Gestion équipe',
        content: 'Gérez les accès et permissions de votre équipe.',
      },
    ],
  },
  '/webhooks': {
    title: 'Webhooks',
    sections: [
      {
        title: 'Intégrations',
        content: 'Configurez des webhooks pour intégrer Hub Chantier avec vos outils.',
      },
    ],
  },
}

const PageHelp = () => {
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)
  const { shouldShowHint, recordVisit } = useProgressiveHint()

  // Obtenir le contenu d'aide pour la page actuelle
  const helpContent = HELP_CONTENT[location.pathname] || {
    title: 'Aide',
    sections: [
      {
        title: 'Assistance',
        content: 'Utilisez la navigation pour accéder aux différentes sections de l\'application.',
      },
    ],
  }

  // Enregistrer la visite de la page
  useEffect(() => {
    recordVisit(location.pathname)
  }, [location.pathname, recordVisit])

  // Déterminer si le hint doit être affiché
  const showHint = shouldShowHint(location.pathname)

  // Bloquer le scroll du body quand le panneau est ouvert
  useEffect(() => {
    if (isOpen) {
      const originalStyle = window.getComputedStyle(document.body).overflow
      document.body.style.overflow = 'hidden'
      return () => {
        document.body.style.overflow = originalStyle
      }
    }
  }, [isOpen])

  const handleClose = () => {
    setIsOpen(false)
  }

  // Gestion du clic sur le backdrop
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      handleClose()
    }
  }

  const panelContent = (
    <div
      className="fixed inset-0 z-50 bg-black/30 motion-reduce:transition-none"
      onClick={handleBackdropClick}
      style={{
        animation: 'fadeIn 200ms ease-out',
      }}
    >
      <div
        role="complementary"
        aria-label="Aide contextuelle"
        className="fixed right-0 top-0 h-full w-80 bg-white shadow-2xl flex flex-col motion-reduce:transition-none"
        style={{
          animation: 'slideInFromRight 300ms ease-out',
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4 bg-primary-50">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              {helpContent.title}
            </h2>
          </div>
          <button
            type="button"
            onClick={handleClose}
            className="rounded-lg p-1.5 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2"
            aria-label="Fermer l'aide"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
          {helpContent.sections.map((section, index) => (
            <div key={index}>
              <h3 className="text-base font-semibold text-gray-900 mb-2">
                {section.title}
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {section.content}
              </p>
            </div>
          ))}

          {/* Aide supplémentaire */}
          <div className="pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Besoin d&apos;aide supplémentaire ? Contactez votre administrateur ou consultez la documentation complète.
            </p>
          </div>
        </div>
      </div>

      {/* Animations CSS injectées */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes slideInFromRight {
          from {
            transform: translateX(100%);
          }
          to {
            transform: translateX(0);
          }
        }

        @media (prefers-reduced-motion: reduce) {
          @keyframes fadeIn {
            from, to {
              opacity: 1;
            }
          }

          @keyframes slideInFromRight {
            from, to {
              transform: translateX(0);
            }
          }
        }
      `}</style>
    </div>
  )

  return (
    <>
      <Tooltip content="Aide sur cette page">
        <button
          onClick={() => setIsOpen(true)}
          className="relative min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-600 transition-colors"
          aria-label="Ouvrir l'aide contextuelle"
          aria-expanded={isOpen}
        >
          <HelpCircle className="w-5 h-5" />
          {showHint && (
            <span
              className="absolute -top-1 -right-1 w-3 h-3 bg-primary-600 rounded-full"
              style={{
                animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
              }}
              aria-hidden="true"
            >
              <style>{`
                @keyframes pulse {
                  0%, 100% {
                    opacity: 1;
                  }
                  50% {
                    opacity: 0.5;
                  }
                }

                @media (prefers-reduced-motion: reduce) {
                  @keyframes pulse {
                    0%, 100% {
                      opacity: 1;
                    }
                  }
                }
              `}</style>
            </span>
          )}
        </button>
      </Tooltip>

      {isOpen && createPortal(panelContent, document.body)}
    </>
  )
}

PageHelp.displayName = 'PageHelp'

export default PageHelp
