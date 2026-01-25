/**
 * PayrollMacrosConfig - Interface de configuration des macros de paie
 * FDH-18: Calculs automatises parametrables
 */

import { useState, useCallback, memo } from 'react'
import { X, Save, Plus, Trash2, Calculator, AlertCircle, Info } from 'lucide-react'

// Types pour les macros de paie
export interface PayrollMacro {
  id: string
  nom: string
  type: 'multiplicateur' | 'fixe' | 'conditionnel'
  variable: string
  valeur: number
  condition?: {
    operateur: '>' | '<' | '>=' | '<=' | '=='
    seuil: number
    variable: string
  }
  actif: boolean
  description?: string
}

export interface PayrollConfig {
  heures_sup_seuil: number // Seuil heures sup (ex: 35h)
  heures_sup_majoration: number // % majoration (ex: 25)
  heures_sup_majoration_2: number // % majoration 2e tranche
  heures_sup_seuil_2: number // Seuil 2e tranche
  panier_repas: number // Montant fixe
  transport_zone_1: number
  transport_zone_2: number
  transport_zone_3: number
  prime_intemperies: number
  macros: PayrollMacro[]
}

const defaultConfig: PayrollConfig = {
  heures_sup_seuil: 35,
  heures_sup_majoration: 25,
  heures_sup_majoration_2: 50,
  heures_sup_seuil_2: 43,
  panier_repas: 10.30,
  transport_zone_1: 3.50,
  transport_zone_2: 7.00,
  transport_zone_3: 10.50,
  prime_intemperies: 15.00,
  macros: [],
}

interface PayrollMacrosConfigProps {
  isOpen: boolean
  onClose: () => void
  config?: PayrollConfig
  onSave: (config: PayrollConfig) => void
}

const MacroRow = memo(function MacroRow({
  macro,
  onUpdate,
  onDelete,
}: {
  macro: PayrollMacro
  onUpdate: (macro: PayrollMacro) => void
  onDelete: () => void
}) {
  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <input
        type="checkbox"
        checked={macro.actif}
        onChange={(e) => onUpdate({ ...macro, actif: e.target.checked })}
        className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
        aria-label={`Activer ${macro.nom}`}
      />

      <div className="flex-1 grid grid-cols-2 sm:grid-cols-4 gap-2">
        <input
          type="text"
          value={macro.nom}
          onChange={(e) => onUpdate({ ...macro, nom: e.target.value })}
          placeholder="Nom"
          className="px-2 py-1 border rounded text-sm"
          aria-label="Nom de la macro"
        />

        <select
          value={macro.type}
          onChange={(e) => onUpdate({ ...macro, type: e.target.value as PayrollMacro['type'] })}
          className="px-2 py-1 border rounded text-sm"
          aria-label="Type de macro"
        >
          <option value="multiplicateur">Multiplicateur</option>
          <option value="fixe">Montant fixe</option>
          <option value="conditionnel">Conditionnel</option>
        </select>

        <select
          value={macro.variable}
          onChange={(e) => onUpdate({ ...macro, variable: e.target.value })}
          className="px-2 py-1 border rounded text-sm"
          aria-label="Variable cible"
        >
          <option value="heures_normales">Heures normales</option>
          <option value="heures_sup">Heures sup.</option>
          <option value="panier">Panier repas</option>
          <option value="transport">Transport</option>
          <option value="prime">Prime</option>
          <option value="total">Total</option>
        </select>

        <div className="flex items-center gap-2">
          <input
            type="number"
            value={macro.valeur}
            onChange={(e) => onUpdate({ ...macro, valeur: parseFloat(e.target.value) || 0 })}
            step={macro.type === 'multiplicateur' ? 0.01 : 0.1}
            className="w-20 px-2 py-1 border rounded text-sm"
            aria-label="Valeur"
          />
          <span className="text-sm text-gray-500">
            {macro.type === 'multiplicateur' ? 'x' : '\u20ac'}
          </span>
        </div>
      </div>

      <button
        onClick={onDelete}
        className="p-1 text-red-500 hover:text-red-700"
        aria-label={`Supprimer ${macro.nom}`}
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </div>
  )
})

function PayrollMacrosConfig({
  isOpen,
  onClose,
  config = defaultConfig,
  onSave,
}: PayrollMacrosConfigProps) {
  const [localConfig, setLocalConfig] = useState<PayrollConfig>(config)
  const [activeTab, setActiveTab] = useState<'heures' | 'indemnites' | 'macros'>('heures')
  const [hasChanges, setHasChanges] = useState(false)

  const updateConfig = useCallback(<K extends keyof PayrollConfig>(
    key: K,
    value: PayrollConfig[K]
  ) => {
    setLocalConfig((prev) => ({ ...prev, [key]: value }))
    setHasChanges(true)
  }, [])

  const addMacro = useCallback(() => {
    const newMacro: PayrollMacro = {
      id: `macro-${Date.now()}`,
      nom: 'Nouvelle macro',
      type: 'fixe',
      variable: 'total',
      valeur: 0,
      actif: true,
    }
    updateConfig('macros', [...localConfig.macros, newMacro])
  }, [localConfig.macros, updateConfig])

  const updateMacro = useCallback((id: string, updated: PayrollMacro) => {
    updateConfig(
      'macros',
      localConfig.macros.map((m) => (m.id === id ? updated : m))
    )
  }, [localConfig.macros, updateConfig])

  const deleteMacro = useCallback((id: string) => {
    updateConfig(
      'macros',
      localConfig.macros.filter((m) => m.id !== id)
    )
  }, [localConfig.macros, updateConfig])

  const handleSave = useCallback(() => {
    onSave(localConfig)
    setHasChanges(false)
    onClose()
  }, [localConfig, onSave, onClose])

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="macros-title"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-hidden bg-white rounded-xl shadow-xl mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <div className="flex items-center gap-3">
            <Calculator className="w-6 h-6 text-primary-600" />
            <h2 id="macros-title" className="text-xl font-semibold text-gray-900">
              Configuration des macros de paie
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
            aria-label="Fermer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b px-6">
          <button
            onClick={() => setActiveTab('heures')}
            className={`px-4 py-3 text-sm font-medium border-b-2 -mb-px ${
              activeTab === 'heures'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Heures supplementaires
          </button>
          <button
            onClick={() => setActiveTab('indemnites')}
            className={`px-4 py-3 text-sm font-medium border-b-2 -mb-px ${
              activeTab === 'indemnites'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Indemnites
          </button>
          <button
            onClick={() => setActiveTab('macros')}
            className={`px-4 py-3 text-sm font-medium border-b-2 -mb-px ${
              activeTab === 'macros'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Macros personnalisees
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(90vh - 200px)' }}>
          {/* Tab: Heures supplementaires */}
          {activeTab === 'heures' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
                <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-blue-700">
                  Les heures supplementaires sont calculees automatiquement au-dela du seuil defini.
                  Deux tranches de majoration peuvent etre configurees.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Seuil heures normales (h/semaine)
                  </label>
                  <input
                    type="number"
                    value={localConfig.heures_sup_seuil}
                    onChange={(e) =>
                      updateConfig('heures_sup_seuil', parseFloat(e.target.value) || 0)
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                    aria-label="Seuil heures normales"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Majoration 1ere tranche (%)
                  </label>
                  <input
                    type="number"
                    value={localConfig.heures_sup_majoration}
                    onChange={(e) =>
                      updateConfig('heures_sup_majoration', parseFloat(e.target.value) || 0)
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                    aria-label="Majoration premiere tranche"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Seuil 2eme tranche (h/semaine)
                  </label>
                  <input
                    type="number"
                    value={localConfig.heures_sup_seuil_2}
                    onChange={(e) =>
                      updateConfig('heures_sup_seuil_2', parseFloat(e.target.value) || 0)
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                    aria-label="Seuil deuxieme tranche"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Majoration 2eme tranche (%)
                  </label>
                  <input
                    type="number"
                    value={localConfig.heures_sup_majoration_2}
                    onChange={(e) =>
                      updateConfig('heures_sup_majoration_2', parseFloat(e.target.value) || 0)
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                    aria-label="Majoration deuxieme tranche"
                  />
                </div>
              </div>

              {/* Preview */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Apercu du calcul</h4>
                <div className="text-sm text-gray-600 space-y-1">
                  <p>0 - {localConfig.heures_sup_seuil}h : taux normal</p>
                  <p>
                    {localConfig.heures_sup_seuil}h - {localConfig.heures_sup_seuil_2}h :{' '}
                    +{localConfig.heures_sup_majoration}%
                  </p>
                  <p>
                    Au-dela de {localConfig.heures_sup_seuil_2}h :{' '}
                    +{localConfig.heures_sup_majoration_2}%
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Tab: Indemnites */}
          {activeTab === 'indemnites' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Panier repas
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={localConfig.panier_repas}
                      onChange={(e) =>
                        updateConfig('panier_repas', parseFloat(e.target.value) || 0)
                      }
                      step="0.10"
                      className="w-full px-3 py-2 pr-8 border rounded-lg"
                      aria-label="Montant panier repas"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                      &euro;
                    </span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prime intemperies
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={localConfig.prime_intemperies}
                      onChange={(e) =>
                        updateConfig('prime_intemperies', parseFloat(e.target.value) || 0)
                      }
                      step="0.10"
                      className="w-full px-3 py-2 pr-8 border rounded-lg"
                      aria-label="Montant prime intemperies"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                      &euro;
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">Indemnites de transport par zone</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Zone 1 (0-10km)</label>
                    <div className="relative">
                      <input
                        type="number"
                        value={localConfig.transport_zone_1}
                        onChange={(e) =>
                          updateConfig('transport_zone_1', parseFloat(e.target.value) || 0)
                        }
                        step="0.10"
                        className="w-full px-3 py-2 pr-8 border rounded-lg"
                        aria-label="Transport zone 1"
                      />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                        &euro;
                      </span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Zone 2 (10-30km)</label>
                    <div className="relative">
                      <input
                        type="number"
                        value={localConfig.transport_zone_2}
                        onChange={(e) =>
                          updateConfig('transport_zone_2', parseFloat(e.target.value) || 0)
                        }
                        step="0.10"
                        className="w-full px-3 py-2 pr-8 border rounded-lg"
                        aria-label="Transport zone 2"
                      />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                        &euro;
                      </span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Zone 3 (30km+)</label>
                    <div className="relative">
                      <input
                        type="number"
                        value={localConfig.transport_zone_3}
                        onChange={(e) =>
                          updateConfig('transport_zone_3', parseFloat(e.target.value) || 0)
                        }
                        step="0.10"
                        className="w-full px-3 py-2 pr-8 border rounded-lg"
                        aria-label="Transport zone 3"
                      />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                        &euro;
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab: Macros personnalisees */}
          {activeTab === 'macros' && (
            <div className="space-y-6">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-yellow-700">
                  Les macros personnalisees permettent d'ajouter des regles de calcul specifiques
                  a votre entreprise. Utilisez avec precaution.
                </p>
              </div>

              <div className="space-y-3">
                {localConfig.macros.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Calculator className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>Aucune macro personnalisee</p>
                    <p className="text-sm">Cliquez sur le bouton ci-dessous pour en creer une</p>
                  </div>
                ) : (
                  localConfig.macros.map((macro) => (
                    <MacroRow
                      key={macro.id}
                      macro={macro}
                      onUpdate={(updated) => updateMacro(macro.id, updated)}
                      onDelete={() => deleteMacro(macro.id)}
                    />
                  ))
                )}
              </div>

              <button
                onClick={addMacro}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg border border-primary-200"
              >
                <Plus className="w-4 h-4" />
                Ajouter une macro
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t bg-gray-50">
          <div>
            {hasChanges && (
              <span className="text-sm text-amber-600 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                Modifications non enregistrees
              </span>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border rounded-lg hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700"
            >
              <Save className="w-4 h-4" />
              Enregistrer
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default memo(PayrollMacrosConfig)
