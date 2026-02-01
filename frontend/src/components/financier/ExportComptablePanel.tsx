/**
 * ExportComptablePanel - Export comptable CSV/Excel (FIN-13)
 *
 * Formulaire d'export avec :
 * - Date debut / Date fin
 * - Chantier (select optionnel)
 * - Format (radio: CSV / Excel)
 * - Bouton Exporter -> telecharge le fichier
 */

import { useState, useEffect, useCallback } from 'react'
import { Download, Loader2, AlertCircle, FileSpreadsheet } from 'lucide-react'
import { financierService } from '../../services/financier'
import { chantiersService } from '../../services/chantiers'
import { logger } from '../../services/logger'
import type { Chantier } from '../../types'

type ExportFormat = 'csv' | 'excel'

// Dates par defaut: 1er du mois courant -> aujourd'hui
const getDefaultDates = () => {
  const now = new Date()
  const debut = new Date(now.getFullYear(), now.getMonth(), 1)
  return {
    date_debut: debut.toISOString().split('T')[0],
    date_fin: now.toISOString().split('T')[0],
  }
}

export default function ExportComptablePanel() {
  const defaults = getDefaultDates()
  const [dateDebut, setDateDebut] = useState(defaults.date_debut)
  const [dateFin, setDateFin] = useState(defaults.date_fin)
  const [chantierId, setChantierId] = useState<string>('')
  const [format, setFormat] = useState<ExportFormat>('csv')
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingChantiers, setLoadingChantiers] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadChantiers = useCallback(async () => {
    try {
      setLoadingChantiers(true)
      const response = await chantiersService.list({ size: 200 })
      setChantiers(response.items)
    } catch (err) {
      logger.error('Erreur chargement chantiers pour export', err, { context: 'ExportComptablePanel' })
    } finally {
      setLoadingChantiers(false)
    }
  }, [])

  useEffect(() => {
    loadChantiers()
  }, [loadChantiers])

  const handleExport = async () => {
    if (!dateDebut || !dateFin) {
      setError('Les dates de debut et fin sont obligatoires')
      return
    }

    if (new Date(dateDebut) > new Date(dateFin)) {
      setError('La date de debut doit etre anterieure a la date de fin')
      return
    }

    try {
      setLoading(true)
      setError(null)

      const params: {
        date_debut: string
        date_fin: string
        format: ExportFormat
        chantier_id?: number
      } = {
        date_debut: dateDebut,
        date_fin: dateFin,
        format,
      }

      if (chantierId) {
        params.chantier_id = parseInt(chantierId)
      }

      const blob = await financierService.exportComptable(params)

      // Declencher le telechargement
      const extension = format === 'csv' ? 'csv' : 'xlsx'
      const filename = `export-comptable_${dateDebut}_${dateFin}.${extension}`
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      setError('Erreur lors de l\'export comptable')
      logger.error('Erreur export comptable', err, { context: 'ExportComptablePanel' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white border rounded-xl">
      <div className="flex items-center gap-2 p-4 border-b">
        <FileSpreadsheet size={18} className="text-green-600" />
        <h3 className="font-semibold text-gray-900">Export comptable</h3>
      </div>

      <div className="p-4 space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg flex items-start gap-2 text-sm">
            <AlertCircle className="flex-shrink-0 mt-0.5" size={16} />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date debut *</label>
            <input
              type="date"
              value={dateDebut}
              onChange={(e) => setDateDebut(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date fin *</label>
            <input
              type="date"
              value={dateFin}
              onChange={(e) => setDateFin(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Chantier (optionnel)
          </label>
          {loadingChantiers ? (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="w-4 h-4 animate-spin" />
              Chargement des chantiers...
            </div>
          ) : (
            <select
              value={chantierId}
              onChange={(e) => setChantierId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            >
              <option value="">Tous les chantiers</option>
              {chantiers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} - {c.nom}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Format</label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="export-format"
                value="csv"
                checked={format === 'csv'}
                onChange={() => setFormat('csv')}
                className="w-4 h-4 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">CSV</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="export-format"
                value="excel"
                checked={format === 'excel'}
                onChange={() => setFormat('excel')}
                className="w-4 h-4 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Excel (.xlsx)</span>
            </label>
          </div>
        </div>

        <div className="pt-2">
          <button
            onClick={handleExport}
            disabled={loading || !dateDebut || !dateFin}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors text-sm font-medium"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Export en cours...
              </>
            ) : (
              <>
                <Download size={16} />
                Exporter
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
