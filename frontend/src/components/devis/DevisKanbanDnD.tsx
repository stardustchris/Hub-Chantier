/**
 * DevisKanbanDnD - Kanban avec drag & drop pour les devis
 * DEV-17: Tableau de bord devis (vue kanban)
 *
 * Accessibility:
 * - Keyboard navigation (Tab, Enter, Space)
 * - Screen reader announcements
 * - Touch targets 44px minimum
 * - ARIA labels et roles
 */

import { useState, useCallback } from 'react'
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { useNavigate } from 'react-router-dom'
import { User, Euro, Loader2 } from 'lucide-react'
import type { DevisRecent, StatutDevis } from '../../types'
import { STATUT_DEVIS_CONFIG } from '../../types'
import { formatEUR } from '../../utils/format'
import KanbanColumn from './KanbanColumn'
import KanbanCard from './KanbanCard'

const KANBAN_COLUMNS: StatutDevis[] = [
  'brouillon',
  'en_validation',
  'envoye',
  'vu',
  'en_negociation',
  'accepte',
  'refuse',
]

interface DevisKanbanDnDProps {
  devis: DevisRecent[]
  devisParStatut: Record<StatutDevis, number>
  onMoveDevis: (devisId: number, newStatut: StatutDevis) => Promise<boolean>
  loading?: boolean
}

export default function DevisKanbanDnD({
  devis,
  devisParStatut,
  onMoveDevis,
  loading = false,
}: DevisKanbanDnDProps) {
  const navigate = useNavigate()
  const [activeId, setActiveId] = useState<number | null>(null)
  const [isMoving, setIsMoving] = useState(false)

  // Configurer les sensors pour le drag & drop
  // Touch sensor avec delay pour éviter les conflits avec le scroll
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px de mouvement avant d'activer le drag
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 200, // 200ms de pression avant d'activer le drag
        tolerance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const getDevisByStatut = useCallback((statut: StatutDevis): DevisRecent[] => {
    return devis.filter((d) => d.statut === statut)
  }, [devis])

  const getActiveDevis = useCallback((): DevisRecent | null => {
    if (!activeId) return null
    return devis.find(d => d.id === activeId) || null
  }, [activeId, devis])

  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id as number)
  }, [])

  const handleDragEnd = useCallback(async (event: DragEndEvent) => {
    const { active, over } = event

    if (!over) {
      setActiveId(null)
      return
    }

    const devisId = active.id as number
    const newStatut = over.id as StatutDevis

    // Si pas de changement de statut, annuler
    const currentDevis = devis.find(d => d.id === devisId)
    if (currentDevis && currentDevis.statut === newStatut) {
      setActiveId(null)
      return
    }

    // Appeler le handler de déplacement
    setIsMoving(true)
    const success = await onMoveDevis(devisId, newStatut)

    if (success) {
      // Annoncer le changement aux lecteurs d'écran
      const announcement = `Devis déplacé vers ${STATUT_DEVIS_CONFIG[newStatut].label}`
      announceToScreenReader(announcement)
    }

    setIsMoving(false)
    setActiveId(null)
  }, [devis, onMoveDevis])

  const handleCardClick = useCallback((devisId: number) => {
    if (!isMoving && !activeId) {
      navigate(`/devis/${devisId}`)
    }
  }, [navigate, isMoving, activeId])

  return (
    <div
      className="relative"
      role="region"
      aria-label="Kanban des devis"
      aria-busy={loading || isMoving}
    >
      {(loading || isMoving) && (
        <div className="absolute inset-0 bg-white/50 z-10 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      )}

      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="overflow-x-auto pb-4">
          <div className="flex gap-4 min-w-max">
            {KANBAN_COLUMNS.map((statut) => {
              const config = STATUT_DEVIS_CONFIG[statut]
              const items = getDevisByStatut(statut)
              const count = devisParStatut[statut] || 0

              return (
                <KanbanColumn
                  key={statut}
                  id={statut}
                  title={config.label}
                  count={count}
                  color={config.couleur}
                >
                  <SortableContext
                    items={items.map(d => d.id)}
                    strategy={verticalListSortingStrategy}
                  >
                    {items.map((d) => (
                      <KanbanCard
                        key={d.id}
                        devis={d}
                        onClick={() => handleCardClick(d.id)}
                        isDragging={activeId === d.id}
                      />
                    ))}
                  </SortableContext>

                  {items.length === 0 && (
                    <div className="text-center py-4 text-gray-600 text-xs">
                      Aucun devis
                    </div>
                  )}
                </KanbanColumn>
              )
            })}
          </div>
        </div>

        <DragOverlay>
          {activeId ? (
            <KanbanCardOverlay devis={getActiveDevis()} />
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Live region pour les annonces aux lecteurs d'écran */}
      <div role="status" aria-live="polite" aria-atomic="true" className="sr-only" />
    </div>
  )
}

// Carte en overlay pendant le drag
function KanbanCardOverlay({ devis }: { devis: DevisRecent | null }) {
  if (!devis) return null

  return (
    <div className="bg-white rounded-lg p-3 border-2 border-blue-500 shadow-xl w-72 opacity-90">
      <div className="flex items-start justify-between mb-2">
        <span className="text-xs font-mono text-gray-600">{devis.numero}</span>
      </div>
      <p className="text-sm font-medium text-gray-900 line-clamp-2 mb-2">
        {devis.objet}
      </p>
      <div className="space-y-1.5 text-xs text-gray-500">
        <div className="flex items-center gap-1.5">
          <User className="w-3.5 h-3.5" />
          <span className="truncate">{devis.client_nom}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Euro className="w-3.5 h-3.5" />
          <span className="font-medium text-gray-700">
            {formatEUR(Number(devis.montant_total_ht))}
          </span>
        </div>
      </div>
    </div>
  )
}

// Helper pour annoncer aux lecteurs d'écran
function announceToScreenReader(message: string) {
  const liveRegion = document.querySelector('[role="status"][aria-live="polite"]')
  if (liveRegion) {
    liveRegion.textContent = message
    setTimeout(() => {
      liveRegion.textContent = ''
    }, 1000)
  }
}
