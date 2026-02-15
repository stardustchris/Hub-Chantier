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
