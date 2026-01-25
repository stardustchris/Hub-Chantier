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
