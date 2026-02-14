/**
 * MobileTimePicker - Composant de saisie d'heure style roulette pour mobile
 * FDH-11: Saisie mobile roulette HH:MM
 */

import { useState, useRef, useEffect, useCallback, memo } from 'react'
import { X, Check, Clock } from 'lucide-react'

interface MobileTimePickerProps {
  value: string // Format "HH:MM"
  onChange: (value: string) => void
  label?: string
  disabled?: boolean
  className?: string
  minTime?: string
  maxTime?: string
  step?: number // Minutes step (default 5)
}

interface WheelColumnProps {
  items: string[]
  selectedIndex: number
  onSelect: (index: number) => void
  itemHeight: number
}

const WheelColumn = memo(function WheelColumn({
  items,
  selectedIndex,
  onSelect,
  itemHeight,
}: WheelColumnProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const isScrollingRef = useRef(false)
  const scrollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Scroll to selected item on mount and when selection changes externally
  useEffect(() => {
    if (containerRef.current && !isScrollingRef.current) {
      containerRef.current.scrollTop = selectedIndex * itemHeight
    }
  }, [selectedIndex, itemHeight])

  const handleScroll = useCallback(() => {
    if (!containerRef.current) return

    isScrollingRef.current = true

    // Clear existing timeout
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current)
    }

    // Debounce the selection
    scrollTimeoutRef.current = setTimeout(() => {
      if (!containerRef.current) return

      const scrollTop = containerRef.current.scrollTop
      const newIndex = Math.round(scrollTop / itemHeight)
      const clampedIndex = Math.max(0, Math.min(items.length - 1, newIndex))

      // Snap to closest item
      containerRef.current.scrollTo({
        top: clampedIndex * itemHeight,
        behavior: 'smooth',
      })

      if (clampedIndex !== selectedIndex) {
        onSelect(clampedIndex)
      }

      isScrollingRef.current = false
    }, 100)
  }, [items.length, itemHeight, onSelect, selectedIndex])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current)
      }
    }
  }, [])

  const visibleItems = 5 // Number of visible items
  const paddingItems = Math.floor(visibleItems / 2)

  return (
    <div
      ref={containerRef}
      className="relative h-full overflow-y-auto scrollbar-hide snap-y snap-mandatory"
      style={{
        scrollSnapType: 'y mandatory',
        WebkitOverflowScrolling: 'touch',
      }}
      onScroll={handleScroll}
    >
      {/* Padding at top */}
      <div style={{ height: `${paddingItems * itemHeight}px` }} />

      {items.map((item, index) => {
        const isSelected = index === selectedIndex
        const distance = Math.abs(index - selectedIndex)
        const opacity = distance === 0 ? 1 : distance === 1 ? 0.6 : 0.3
        const scale = distance === 0 ? 1 : distance === 1 ? 0.9 : 0.8

        return (
          <div
            key={index}
            className="flex items-center justify-center snap-center transition-all duration-150"
            style={{
              height: `${itemHeight}px`,
              opacity,
              transform: `scale(${scale})`,
            }}
            onClick={() => {
              onSelect(index)
              if (containerRef.current) {
                containerRef.current.scrollTo({
                  top: index * itemHeight,
                  behavior: 'smooth',
                })
              }
            }}
          >
            <span
              className={`text-2xl font-medium tabular-nums ${
                isSelected ? 'text-primary-600' : 'text-gray-500'
              }`}
            >
              {item}
            </span>
          </div>
        )
      })}

      {/* Padding at bottom */}
      <div style={{ height: `${paddingItems * itemHeight}px` }} />
    </div>
  )
})

function MobileTimePicker({
  value,
  onChange,
  label,
  disabled = false,
  className = '',
  minTime: _minTime,
  maxTime: _maxTime,
  step = 5,
}: MobileTimePickerProps) {
  // Reserved for future validation
  void _minTime
  void _maxTime
  const [isOpen, setIsOpen] = useState(false)
  const [tempHour, setTempHour] = useState(0)
  const [tempMinute, setTempMinute] = useState(0)

  // Parse value
  const parseTime = useCallback((timeStr: string): [number, number] => {
    const parts = timeStr.split(':')
    if (parts.length >= 2) {
      return [parseInt(parts[0], 10) || 0, parseInt(parts[1], 10) || 0]
    }
    return [0, 0]
  }, [])

  // Generate hours array (0-23)
  const hours = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'))

  // Generate minutes array based on step
  const minutes = Array.from(
    { length: Math.ceil(60 / step) },
    (_, i) => (i * step).toString().padStart(2, '0')
  )

  // Open picker
  const handleOpen = useCallback(() => {
    if (disabled) return
    const [h, m] = parseTime(value)
    setTempHour(h)
    // Round minute to nearest step
    const roundedMinute = Math.round(m / step) * step
    setTempMinute(Math.min(roundedMinute, 55))
    setIsOpen(true)
  }, [disabled, value, parseTime, step])

  // Confirm selection
  const handleConfirm = useCallback(() => {
    const newValue = `${hours[tempHour]}:${minutes[Math.floor(tempMinute / step)]}`
    onChange(newValue)
    setIsOpen(false)
  }, [tempHour, tempMinute, hours, minutes, step, onChange])

  // Cancel selection
  const handleCancel = useCallback(() => {
    setIsOpen(false)
  }, [])

  // Close on escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleCancel()
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, handleCancel])

  // Prevent body scroll when picker is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  const displayValue = value || '--:--'
  const itemHeight = 48

  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}

      {/* Trigger button */}
      <button
        type="button"
        onClick={handleOpen}
        disabled={disabled}
        className={`
          w-full px-3 py-2 text-left border rounded-lg
          flex items-center gap-2
          ${disabled
            ? 'bg-gray-100 cursor-not-allowed text-gray-500'
            : 'bg-white hover:border-primary-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
          }
          transition-colors
        `}
        aria-label={label ? `${label}: ${displayValue}` : `Heure: ${displayValue}`}
      >
        <Clock className="w-4 h-4 text-gray-600" />
        <span className={value ? 'text-gray-900' : 'text-gray-600'}>
          {displayValue}
        </span>
      </button>

      {/* Modal */}
      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center"
          role="dialog"
          aria-modal="true"
          aria-label="Sélecteur d'heure"
        >
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50"
            onClick={handleCancel}
          />

          {/* Picker container */}
          <div className="relative w-full sm:max-w-sm bg-white rounded-t-2xl sm:rounded-2xl shadow-xl animate-slide-up sm:animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b">
              <button
                type="button"
                onClick={handleCancel}
                className="p-2 -m-2 text-gray-500 hover:text-gray-700"
                aria-label="Annuler"
              >
                <X className="w-5 h-5" />
              </button>
              <span className="font-medium text-gray-900">
                {label || 'Sélectionner l\'heure'}
              </span>
              <button
                type="button"
                onClick={handleConfirm}
                className="p-2 -m-2 text-primary-600 hover:text-primary-700"
                aria-label="Confirmer"
              >
                <Check className="w-5 h-5" />
              </button>
            </div>

            {/* Wheel picker */}
            <div
              className="relative flex justify-center items-center px-4"
              style={{ height: `${itemHeight * 5}px` }}
            >
              {/* Selection indicator */}
              <div
                className="absolute left-4 right-4 bg-primary-50 border-y border-primary-200 rounded-lg pointer-events-none"
                style={{
                  height: `${itemHeight}px`,
                  top: '50%',
                  transform: 'translateY(-50%)',
                }}
              />

              {/* Hours column */}
              <div className="flex-1 h-full">
                <WheelColumn
                  items={hours}
                  selectedIndex={tempHour}
                  onSelect={setTempHour}
                  itemHeight={itemHeight}
                />
              </div>

              {/* Separator */}
              <div className="text-2xl font-bold text-gray-900 mx-2">:</div>

              {/* Minutes column */}
              <div className="flex-1 h-full">
                <WheelColumn
                  items={minutes}
                  selectedIndex={Math.floor(tempMinute / step)}
                  onSelect={(index) => setTempMinute(index * step)}
                  itemHeight={itemHeight}
                />
              </div>
            </div>

            {/* Quick buttons */}
            <div className="flex gap-2 px-4 py-3 border-t bg-gray-50 rounded-b-2xl">
              <button
                type="button"
                onClick={() => {
                  const now = new Date()
                  setTempHour(now.getHours())
                  setTempMinute(Math.floor(now.getMinutes() / step) * step)
                }}
                className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-white border rounded-lg hover:bg-gray-50"
              >
                Maintenant
              </button>
              <button
                type="button"
                onClick={() => {
                  setTempHour(7)
                  setTempMinute(0)
                }}
                className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border rounded-lg hover:bg-gray-50"
              >
                07:00
              </button>
              <button
                type="button"
                onClick={() => {
                  setTempHour(12)
                  setTempMinute(0)
                }}
                className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border rounded-lg hover:bg-gray-50"
              >
                12:00
              </button>
              <button
                type="button"
                onClick={() => {
                  setTempHour(17)
                  setTempMinute(0)
                }}
                className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border rounded-lg hover:bg-gray-50"
              >
                17:00
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default memo(MobileTimePicker)
