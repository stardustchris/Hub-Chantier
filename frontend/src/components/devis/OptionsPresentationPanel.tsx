/**
 * OptionsPresentationPanel - Personnalisation de la presentation du devis PDF
 * Module Devis (Module 20) - DEV-11
 */

import { useState, useEffect, useCallback } from 'react'
import { devisService } from '../../services/devis'
import type { OptionsPresentation, TemplatePresentation } from '../../types'
import {
  Loader2,
  AlertCircle,
  CheckCircle2,
  FileText,
  FileSpreadsheet,
  FileBarChart,
  File,
  Save,
  Eye,
  EyeOff,
  Info,
} from 'lucide-react'

interface OptionsPresentationPanelProps {
  devisId: number
}

/** Icone pour chaque template */
const TEMPLATE_ICONS: Record<string, typeof FileText> = {
  standard: FileText,
  simplifie: File,
  detaille: FileSpreadsheet,
  minimaliste: FileBarChart,
}

/** Labels des options pour les toggles */
const OPTIONS_LABELS: { key: keyof Omit<OptionsPresentation, 'template_nom' | 'afficher_debourses'>; label: string }[] = [
  { key: 'afficher_quantites', label: 'Afficher les quantites' },
  { key: 'afficher_prix_unitaires', label: 'Afficher les prix unitaires' },
  { key: 'afficher_tva_detaillee', label: 'Afficher le detail de la TVA' },
  { key: 'afficher_conditions_generales', label: 'Afficher les conditions generales' },
  { key: 'afficher_logo', label: 'Afficher le logo entreprise' },
  { key: 'afficher_coordonnees_entreprise', label: 'Afficher les coordonnees entreprise' },
  { key: 'afficher_retenue_garantie', label: 'Afficher la retenue de garantie' },
  { key: 'afficher_frais_chantier_detail', label: 'Afficher le detail des frais de chantier' },
  { key: 'afficher_composants', label: 'Afficher les composants des articles' },
]

function ToggleSwitch({
  checked,
  onChange,
  label,
}: {
  checked: boolean
  onChange: (value: boolean) => void
  label: string
}) {
  return (
    <label className="flex items-center justify-between gap-3 py-2 cursor-pointer group">
      <span className="text-sm text-gray-700 group-hover:text-gray-900 transition-colors">
        {label}
      </span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={label}
        onClick={() => onChange(!checked)}
        className={`
          relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent
          transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          ${checked ? 'bg-blue-600' : 'bg-gray-200'}
        `}
      >
        <span
          className={`
            pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0
            transition duration-200 ease-in-out
            ${checked ? 'translate-x-5' : 'translate-x-0'}
          `}
        />
      </button>
    </label>
  )
}

/** Mini-maquette de previsualisation */
function MiniPreview({ options }: { options: OptionsPresentation }) {
  return (
    <div className="border border-gray-300 rounded-lg bg-white p-3 text-[10px] leading-relaxed text-gray-500 space-y-1.5 max-w-xs">
      {/* En-tete */}
      <div className="flex items-start justify-between gap-2">
        {options.afficher_logo && (
          <div className="w-8 h-8 bg-gray-200 rounded flex items-center justify-center text-[8px] text-gray-600 flex-shrink-0">
            Logo
          </div>
        )}
        <div className="text-right flex-1">
          {options.afficher_coordonnees_entreprise && (
            <div className="text-gray-600">
              <div className="h-1.5 bg-gray-200 rounded w-16 ml-auto mb-0.5" />
              <div className="h-1.5 bg-gray-200 rounded w-20 ml-auto" />
            </div>
          )}
        </div>
      </div>

      {/* Titre devis */}
      <div className="border-b border-gray-200 pb-1">
        <div className="h-2 bg-gray-300 rounded w-24 mb-0.5" />
        <div className="h-1.5 bg-gray-100 rounded w-32" />
      </div>

      {/* Tableau */}
      <div className="space-y-0.5">
        <div className="flex gap-1 text-[8px] font-medium text-gray-600 border-b border-gray-100 pb-0.5">
          <span className="flex-1">Designation</span>
          {options.afficher_quantites && <span className="w-6 text-center">Qte</span>}
          {options.afficher_prix_unitaires && <span className="w-10 text-right">P.U.</span>}
          <span className="w-10 text-right">Total</span>
        </div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-1 items-center">
            <div className="flex-1 h-1.5 bg-gray-100 rounded" />
            {options.afficher_quantites && <div className="w-6 h-1.5 bg-gray-100 rounded" />}
            {options.afficher_prix_unitaires && <div className="w-10 h-1.5 bg-gray-100 rounded" />}
            <div className="w-10 h-1.5 bg-gray-200 rounded" />
          </div>
        ))}
        {options.afficher_composants && (
          <div className="pl-3 space-y-0.5">
            {[1, 2].map((i) => (
              <div key={i} className="flex gap-1 items-center">
                <div className="flex-1 h-1 bg-blue-50 rounded" />
                <div className="w-6 h-1 bg-blue-50 rounded" />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Totaux */}
      <div className="border-t border-gray-200 pt-1 space-y-0.5">
        <div className="flex justify-between">
          <span>Total HT</span>
          <div className="h-1.5 bg-gray-300 rounded w-12" />
        </div>
        {options.afficher_tva_detaillee && (
          <div className="flex justify-between text-gray-600">
            <span>TVA 20%</span>
            <div className="h-1.5 bg-gray-100 rounded w-10" />
          </div>
        )}
        <div className="flex justify-between font-medium">
          <span>Total TTC</span>
          <div className="h-1.5 bg-gray-400 rounded w-14" />
        </div>
        {options.afficher_retenue_garantie && (
          <div className="flex justify-between text-gray-600">
            <span>Retenue garantie</span>
            <div className="h-1.5 bg-gray-100 rounded w-10" />
          </div>
        )}
        {options.afficher_frais_chantier_detail && (
          <div className="flex justify-between text-gray-600">
            <span>Frais chantier</span>
            <div className="h-1.5 bg-gray-100 rounded w-8" />
          </div>
        )}
      </div>

      {/* Pied de page */}
      {options.afficher_conditions_generales && (
        <div className="border-t border-gray-200 pt-1">
          <div className="h-1 bg-gray-100 rounded w-full mb-0.5" />
          <div className="h-1 bg-gray-100 rounded w-3/4" />
        </div>
      )}
    </div>
  )
}

export default function OptionsPresentationPanel({ devisId }: OptionsPresentationPanelProps) {
  const [templates, setTemplates] = useState<TemplatePresentation[]>([])
  const [options, setOptions] = useState<OptionsPresentation | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [showPreview, setShowPreview] = useState(false)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const [tpls, opts] = await Promise.all([
        devisService.getTemplatesPresentation(),
        devisService.getOptionsPresentation(devisId),
      ])
      setTemplates(tpls)
      setOptions(opts)
    } catch {
      setError('Erreur lors du chargement des options de presentation')
    } finally {
      setLoading(false)
    }
  }, [devisId])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleSelectTemplate = (tpl: TemplatePresentation) => {
    setOptions({
      ...tpl.options,
      template_nom: tpl.nom,
    })
    setSuccess(false)
  }

  const handleToggleOption = (key: keyof OptionsPresentation, value: boolean) => {
    if (!options) return
    setOptions({ ...options, [key]: value })
    setSuccess(false)
  }

  const handleSave = async () => {
    if (!options) return
    try {
      setSaving(true)
      setError(null)
      setSuccess(false)
      const updated = await devisService.updateOptionsPresentation(devisId, options)
      setOptions(updated)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch {
      setError('Erreur lors de la sauvegarde des options')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error && !options) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
        <div>
          <p>{error}</p>
          <button onClick={loadData} className="text-sm underline mt-1">Reessayer</button>
        </div>
      </div>
    )
  }

  if (!options) return null

  return (
    <div className="space-y-6">
      {/* Selecteur de template */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Modele de presentation</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {templates.map((tpl) => {
            const isSelected = options.template_nom === tpl.nom
            const IconComponent = TEMPLATE_ICONS[tpl.nom.toLowerCase()] || FileText
            return (
              <button
                key={tpl.nom}
                type="button"
                onClick={() => handleSelectTemplate(tpl)}
                className={`
                  flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all text-center
                  ${isSelected
                    ? 'border-blue-500 bg-blue-50 shadow-sm'
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                  }
                `}
              >
                <IconComponent
                  className={`w-8 h-8 ${isSelected ? 'text-blue-600' : 'text-gray-600'}`}
                />
                <div>
                  <p className={`text-sm font-medium ${isSelected ? 'text-blue-700' : 'text-gray-900'}`}>
                    {tpl.nom}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">{tpl.description}</p>
                </div>
                {isSelected && (
                  <CheckCircle2 className="w-4 h-4 text-blue-600" />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Personnalisation fine */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Personnalisation fine</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-0 bg-gray-50 rounded-lg p-4 border border-gray-200">
          {OPTIONS_LABELS.map(({ key, label }) => (
            <ToggleSwitch
              key={key}
              checked={options[key] as boolean}
              onChange={(val) => handleToggleOption(key, val)}
              label={label}
            />
          ))}
        </div>

        {/* Note debourses */}
        <div className="flex items-start gap-2 mt-3 px-1">
          <Info className="w-4 h-4 text-gray-600 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-gray-600 italic">
            Les debourses ne sont jamais affiches au client
          </p>
        </div>
      </div>

      {/* Previsualisation et actions */}
      <div className="flex flex-col sm:flex-row items-start gap-4">
        {/* Bouton previsualisation */}
        <button
          type="button"
          onClick={() => setShowPreview(!showPreview)}
          className="inline-flex items-center gap-2 px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          {showPreview ? (
            <>
              <EyeOff className="w-4 h-4" />
              Masquer la previsualisation
            </>
          ) : (
            <>
              <Eye className="w-4 h-4" />
              Previsualiser le rendu
            </>
          )}
        </button>

        {/* Bouton enregistrer */}
        <button
          type="button"
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {saving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          Enregistrer les preferences
        </button>

        {/* Feedback */}
        {success && (
          <span className="inline-flex items-center gap-1.5 text-sm text-green-600">
            <CheckCircle2 className="w-4 h-4" />
            Preferences enregistrees
          </span>
        )}
      </div>

      {/* Erreur sauvegarde */}
      {error && options && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
          <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Mini-maquette previsualisation */}
      {showPreview && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">
            Apercu du rendu client
          </h3>
          <MiniPreview options={options} />
        </div>
      )}
    </div>
  )
}
