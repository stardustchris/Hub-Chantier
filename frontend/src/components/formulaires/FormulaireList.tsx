/**
 * FormulaireList - Liste des formulaires remplis (FOR-10)
 * Affiche les formulaires avec leur statut et actions disponibles
 */

import { formatDateDayMonthYear, formatDateTimeShort } from '../../utils/dates'
import {
  FileText,
  Eye,
  Download,
  CheckCircle,
  Clock,
  Edit,
  Building2,
  User,
  Calendar,
} from 'lucide-react'
import type { FormulaireRempli, CategorieFormulaire, StatutFormulaire } from '../../types'
import { CATEGORIES_FORMULAIRES, STATUTS_FORMULAIRE } from '../../types'

interface FormulaireListProps {
  formulaires: FormulaireRempli[]
  onView: (formulaire: FormulaireRempli) => void
  onEdit: (formulaire: FormulaireRempli) => void
  onExportPDF: (formulaire: FormulaireRempli) => void
  onValidate?: (formulaire: FormulaireRempli) => void
  loading?: boolean
  showChantier?: boolean
}

export default function FormulaireList({
  formulaires,
  onView,
  onEdit,
  onExportPDF,
  onValidate,
  loading = false,
  showChantier = true,
}: FormulaireListProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-xl border p-4 animate-pulse">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gray-200 rounded-lg" />
              <div className="flex-1">
                <div className="h-5 bg-gray-200 rounded w-1/3 mb-2" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (formulaires.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-xl border">
        <FileText className="w-12 h-12 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-1">Aucun formulaire</h3>
        <p className="text-gray-500">Creez un formulaire depuis un template</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {formulaires.map((formulaire) => {
        const categorieInfo = CATEGORIES_FORMULAIRES[formulaire.template_categorie as CategorieFormulaire]
        const statutInfo = STATUTS_FORMULAIRE[formulaire.statut as StatutFormulaire]
        const isEditable = formulaire.statut === 'brouillon'

        return (
          <div
            key={formulaire.id}
            className="bg-white rounded-xl border p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start gap-4">
              {/* Icon */}
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: categorieInfo?.color + '20' }}
              >
                <FileText
                  className="w-6 h-6"
                  style={{ color: categorieInfo?.color }}
                />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {formulaire.template_nom || `Formulaire #${formulaire.id}`}
                  </h3>
                  <span
                    className="flex-shrink-0 text-xs px-2 py-1 rounded-full font-medium"
                    style={{
                      backgroundColor: statutInfo?.bgColor,
                      color: statutInfo?.color,
                    }}
                  >
                    {statutInfo?.label || formulaire.statut}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-500 mb-3">
                  {showChantier && formulaire.chantier_nom && (
                    <span className="flex items-center gap-1">
                      <Building2 className="w-4 h-4" />
                      {formulaire.chantier_nom}
                    </span>
                  )}
                  {formulaire.user_nom && (
                    <span className="flex items-center gap-1">
                      <User className="w-4 h-4" />
                      {formulaire.user_nom}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {formatDateDayMonthYear(formulaire.created_at)}
                  </span>
                </div>

                {/* Indicateurs */}
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  {formulaire.est_signe && (
                    <span className="flex items-center gap-1 text-green-600 bg-green-50 px-2 py-1 rounded">
                      <CheckCircle className="w-3.5 h-3.5" />
                      Signe
                    </span>
                  )}
                  {formulaire.photos.length > 0 && (
                    <span className="text-blue-600 bg-blue-50 px-2 py-1 rounded">
                      {formulaire.photos.length} photo{formulaire.photos.length > 1 ? 's' : ''}
                    </span>
                  )}
                  {formulaire.soumis_at && (
                    <span className="flex items-center gap-1 text-gray-500">
                      <Clock className="w-3.5 h-3.5" />
                      Soumis le {formatDateTimeShort(formulaire.soumis_at)}
                    </span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1 flex-shrink-0">
                <button
                  onClick={() => onView(formulaire)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Voir"
                >
                  <Eye className="w-5 h-5" />
                </button>
                {isEditable && (
                  <button
                    onClick={() => onEdit(formulaire)}
                    className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="Modifier"
                  >
                    <Edit className="w-5 h-5" />
                  </button>
                )}
                {formulaire.statut === 'soumis' && onValidate && (
                  <button
                    onClick={() => onValidate(formulaire)}
                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Valider"
                  >
                    <CheckCircle className="w-5 h-5" />
                  </button>
                )}
                <button
                  onClick={() => onExportPDF(formulaire)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Telecharger PDF"
                >
                  <Download className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
