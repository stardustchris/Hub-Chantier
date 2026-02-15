/**
 * Configuration des tours guidés par rôle
 * Chaque step cible un élément via data-tour attribute
 */

import type { UserRole } from '../../types'

export interface TourStep {
  target: string // Sélecteur data-tour
  title: string
  content: string
  placement?: 'top' | 'bottom' | 'left' | 'right'
}

export const TOURS: Record<UserRole, TourStep[]> = {
  compagnon: [
    {
      target: 'clock-card',
      title: 'Pointage',
      content: 'Pointez ici chaque matin en arrivant et le soir en partant.',
      placement: 'bottom',
    },
    {
      target: 'nav-planning',
      title: 'Votre planning',
      content: 'Consultez vos affectations de la semaine ici.',
      placement: 'right',
    },
    {
      target: 'nav-feuilles-heures',
      title: 'Vos heures',
      content: 'Vérifiez vos heures travaillées et validées.',
      placement: 'right',
    },
    {
      target: 'dashboard-feed',
      title: 'Actualités',
      content: 'Suivez les infos du chantier et échangez avec l\'équipe.',
      placement: 'top',
    },
  ],

  chef_chantier: [
    {
      target: 'dashboard-feed',
      title: 'Fil d\'actualité',
      content: 'Publiez des infos urgentes et signalez les problèmes terrain.',
      placement: 'top',
    },
    {
      target: 'nav-planning',
      title: 'Planning équipe',
      content: 'Consultez qui travaille sur vos chantiers cette semaine.',
      placement: 'right',
    },
    {
      target: 'nav-feuilles-heures',
      title: 'Validation heures',
      content: 'Validez les heures travaillées par votre équipe.',
      placement: 'right',
    },
    {
      target: 'nav-chantiers',
      title: 'Vos chantiers',
      content: 'Accédez aux fiches chantiers dont vous êtes responsable.',
      placement: 'right',
    },
  ],

  conducteur: [
    {
      target: 'dashboard-stats',
      title: 'Statistiques',
      content: 'Suivez les heures et la charge de travail en temps réel.',
      placement: 'bottom',
    },
    {
      target: 'nav-chantiers',
      title: 'Gestion chantiers',
      content: 'Créez et gérez tous les chantiers de l\'entreprise.',
      placement: 'right',
    },
    {
      target: 'nav-planning',
      title: 'Planning global',
      content: 'Affectez les équipes sur les chantiers pour la semaine.',
      placement: 'right',
    },
    {
      target: 'nav-finances',
      title: 'Suivi financier',
      content: 'Budgets, achats et synchronisation Pennylane.',
      placement: 'right',
    },
    {
      target: 'nav-devis',
      title: 'Pipeline devis',
      content: 'Gérez vos devis et suivez les opportunités commerciales.',
      placement: 'right',
    },
  ],

  admin: [
    {
      target: 'dashboard-stats',
      title: 'Vue d\'ensemble',
      content: 'Pilotez l\'activité : heures, chantiers, devis en cours.',
      placement: 'bottom',
    },
    {
      target: 'nav-utilisateurs',
      title: 'Gestion utilisateurs',
      content: 'Invitez des compagnons, chefs et conducteurs.',
      placement: 'right',
    },
    {
      target: 'nav-chantiers',
      title: 'Tous les chantiers',
      content: 'Accédez à tous les chantiers de l\'entreprise.',
      placement: 'right',
    },
    {
      target: 'nav-finances',
      title: 'Finance & achats',
      content: 'Budgets, achats, fournisseurs et synchronisation comptable.',
      placement: 'right',
    },
    {
      target: 'nav-webhooks',
      title: 'Intégrations',
      content: 'Configurez Pennylane, Silae et autres connecteurs.',
      placement: 'right',
    },
  ],
}
