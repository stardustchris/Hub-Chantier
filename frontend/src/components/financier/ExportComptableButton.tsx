/**
 * ExportComptableButton - Bouton d'export comptable (FIN-13)
 *
 * Bouton deroulant permettant d'exporter les donnees comptables
 * au format CSV ou Excel (xlsx). Telecharge via blob + URL.createObjectURL.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { Download, ChevronDown, Loader2 } from 'lucide-react'
import { financierService } from '../../services/financier'
import { logger } from '../../services/logger'

interface ExportComptableButtonProps {
  chantierId: number
}

type ExportFormat = 'csv' | 'xlsx'

interface FormatOption {
  format: ExportFormat
  label: string
  extension: string
}

const FORMAT_OPTIONS: FormatOption[] = [
  { format: 'csv', label: 'Export CSV', extension: 'csv' },
  { format: 'xlsx', label: 'Export Excel', extension: 'xlsx' },
]

export default function ExportComptableButton({
  chantierId,
}: ExportComptableButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState<ExportFormat | null>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Fermer le dropdown au clic exterieur
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleExport = useCallback(
    async (format: ExportFormat, extension: string) => {
      try {
        setLoading(format)
        setIsOpen(false)
        const blob = await financierService.exportComptable(chantierId, format)

        const now = new Date()
        const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
        const fileName = `export-comptable-${chantierId}-${dateStr}.${extension}`

        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = fileName
        document.body.appendChild(link)
        link.click()

        // Nettoyage
        setTimeout(() => {
          URL.revokeObjectURL(url)
          document.body.removeChild(link)
        }, 100)
      } catch (err) {
        logger.error('Erreur export comptable', err, {
          context: 'ExportComptableButton',
          metadata: { format },
        })
      } finally {
        setLoading(null)
      }
    },
    [chantierId]
  )

  const isExporting = loading !== null

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isExporting}
        className="flex items-center justify-center gap-2 px-3 py-2 border border-green-300 text-green-600 rounded-lg hover:bg-green-50 transition-colors text-sm font-medium disabled:opacity-50"
        aria-label="Exporter les donnees comptables"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        {isExporting ? (
          <Loader2 size={16} className="animate-spin" />
        ) : (
          <Download size={16} />
        )}
        {isExporting ? 'Export...' : 'Export Comptable'}
        <ChevronDown size={14} />
      </button>

      {isOpen && (
        <div
          className="absolute right-0 mt-1 w-44 bg-white border border-gray-200 rounded-lg shadow-lg z-10 overflow-hidden"
          role="menu"
          aria-label="Formats d'export disponibles"
        >
          {FORMAT_OPTIONS.map((option) => (
            <button
              key={option.format}
              onClick={() => handleExport(option.format, option.extension)}
              className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2"
              role="menuitem"
              aria-label={option.label}
            >
              <Download size={14} className="text-gray-400" />
              {option.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
