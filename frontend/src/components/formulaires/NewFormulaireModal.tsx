/**
 * NewFormulaireModal - Modal de sélection de template pour nouveau formulaire
 * Extrait de FormulairesPage pour réduction de taille
 */

import { X, FileText } from 'lucide-react'
import type { TemplateFormulaire, Chantier } from '../../types'
import { CATEGORIES_FORMULAIRES } from '../../types'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface NewFormulaireModalProps {
  isOpen: boolean
  onClose: () => void
  onCreateFormulaire: (templateId: number) => Promise<void>
  templates: TemplateFormulaire[]
  chantiers: Chantier[]
  selectedChantierId: string | null
  onChantierChange: (chantierId: string | null) => void
}

export function NewFormulaireModal({
  isOpen,
  onClose,
  onCreateFormulaire,
  templates,
  chantiers,
  selectedChantierId,
  onChantierChange,
}: NewFormulaireModalProps) {
  const handleClose = () => {
    onChantierChange(null)
    onClose()
  }
  const focusTrapRef = useFocusTrap({ enabled: isOpen, onClose: handleClose })

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="fixed inset-0 bg-black/50"
        onClick={handleClose}
      />
      <div ref={focusTrapRef} role="dialog" aria-modal="true" aria-labelledby="modal-title" className="relative bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[80vh] overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 id="modal-title" className="text-lg font-semibold">Nouveau formulaire</h2>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-4 space-y-4 overflow-y-auto max-h-[60vh]">
          {/* Selecteur de chantier */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chantier <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedChantierId || ''}
              onChange={(e) => onChantierChange(e.target.value || null)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">Selectionnez un chantier...</option>
              {chantiers.map((chantier) => (
                <option key={chantier.id} value={chantier.id}>
                  {chantier.code} - {chantier.nom}
                </option>
              ))}
            </select>
          </div>

          {/* Liste des templates */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Template
            </label>
            {templates.filter((t) => t.is_active).length === 0 ? (
              <p className="text-center text-gray-500 py-8">
                Aucun template disponible
              </p>
            ) : (
              <div className="space-y-2">
                {templates
                  .filter((t) => t.is_active)
                  .map((template) => {
                    const categorieInfo = CATEGORIES_FORMULAIRES[template.categorie]
                    return (
                      <button
                        key={template.id}
                        onClick={() => onCreateFormulaire(template.id)}
                        disabled={!selectedChantierId}
                        className="w-full flex items-center gap-3 p-3 rounded-lg border hover:border-primary-500 hover:bg-primary-50 transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:border-gray-200 disabled:hover:bg-white"
                      >
                        <div
                          className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                          style={{ backgroundColor: categorieInfo?.color + '20' }}
                        >
                          <FileText
                            className="w-5 h-5"
                            style={{ color: categorieInfo?.color }}
                          />
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">{template.nom}</h3>
                          <p className="text-sm text-gray-500">
                            {template.nombre_champs} champs
                            {template.a_photo && ' · Photos'}
                            {template.a_signature && ' · Signature'}
                          </p>
                        </div>
                      </button>
                    )
                  })}
              </div>
            )}
          </div>

          {!selectedChantierId && (
            <p className="text-sm text-amber-600 bg-amber-50 px-3 py-2 rounded-lg">
              Selectionnez un chantier pour pouvoir choisir un template
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
