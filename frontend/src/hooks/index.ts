/**
 * Custom hooks pour Hub Chantier.
 *
 * @module hooks
 */

export { useListPage } from './useListPage'
export type {
  PaginatedResponse,
  ListParams,
  UseListPageOptions,
  UseListPageReturn,
} from './useListPage'

export { useReservationModal } from './useReservationModal'
export type {
  UseReservationModalOptions,
  UseReservationModalReturn,
} from './useReservationModal'

export { useClockCard } from './useClockCard'
export type { ClockState, UseClockCardReturn } from './useClockCard'

export { useDashboardFeed } from './useDashboardFeed'
export type { UseDashboardFeedReturn } from './useDashboardFeed'

export { useChantierDetail } from './useChantierDetail'
export { useLogistique } from './useLogistique'
export { useFormulaires } from './useFormulaires'
export { useTodayPlanning } from './useTodayPlanning'
export type { UseTodayPlanningReturn } from './useTodayPlanning'

export { useWeeklyStats } from './useWeeklyStats'

export { useRecentDocuments } from './useRecentDocuments'
export type { RecentDocument } from './useRecentDocuments'

export { useChantierLogistique } from './useChantierLogistique'

export { useTodayTeam } from './useTodayTeam'
export type { TeamMember, UseTodayTeamReturn } from './useTodayTeam'

export { useWeather } from './useWeather'
export type { UseWeatherReturn, WeatherData, WeatherAlert } from './useWeather'

export { useMultiSelect } from './useMultiSelect'

// Devis hooks
export { useDevisKanban } from './useDevisKanban'
export type { UseDevisKanbanReturn, KanbanFilters } from './useDevisKanban'

export { useDevisFilters } from './useDevisFilters'
export type { DevisFilters, UseDevisFiltersReturn } from './useDevisFilters'

export { useDevisMediaUpload } from './useDevisMediaUpload'
export type { UseDevisMediaUploadOptions, UseDevisMediaUploadReturn } from './useDevisMediaUpload'

export { useDevisList } from './useDevisList'
export type { UseDevisListParams, UseDevisListReturn } from './useDevisList'

export { useDevisDetail } from './useDevisDetail'
export type { UseDevisDetailReturn } from './useDevisDetail'

export { useDevisDashboard } from './useDevisDashboard'
export type { UseDevisDashboardReturn } from './useDevisDashboard'

export { useArticles } from './useArticles'
export type { UseArticlesParams, UseArticlesReturn } from './useArticles'

export { useDocumentTitle } from './useDocumentTitle'
export { useRouteChangeReset } from './useRouteChangeReset'

export { useKeyboardShortcuts } from './useKeyboardShortcuts'
export type { UseKeyboardShortcutsOptions, UseKeyboardShortcutsReturn } from './useKeyboardShortcuts'

export { usePointageStreak } from './usePointageStreak'
export type { UsePointageStreakReturn } from './usePointageStreak'

export { useProgressiveHint } from './useProgressiveHint'

// Financial hooks
export { useAchats } from './useAchats'
export type { UseAchatsReturn } from './useAchats'

export { useBudgets } from './useBudgets'
export type { BudgetKPI, BudgetChantier, UseBudgetsReturn } from './useBudgets'

export { useDashboardFinancier } from './useDashboardFinancier'
export type { AnalyseIADisplay, UseDashboardFinancierReturn } from './useDashboardFinancier'

// Chantiers hooks
export { useCreateChantier } from './useCreateChantier'

// Users/Auth hooks
export { useUsersList } from './useUsersList'
export { useUserDetail } from './useUserDetail'
export { useForgotPassword } from './useForgotPassword'
export { useResetPassword } from './useResetPassword'
export { useAcceptInvitation } from './useAcceptInvitation'
export { useSecuritySettings } from './useSecuritySettings'
export { useParametresEntreprise } from './useParametresEntreprise'
export type { ConfigurationEntreprise, ConfigurationUpdateResponse, SaveConfigPayload } from './useParametresEntreprise'

// Dashboard hooks
export { useAllUsers } from './useAllUsers'
export { useWeatherNotifications } from './useWeatherNotifications'

// Upload hooks
export { useImageUpload, useImageCompress } from './useImageUpload'
