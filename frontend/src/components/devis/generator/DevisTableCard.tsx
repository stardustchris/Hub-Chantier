import { useState, useCallback } from 'react'
import { Plus, ChevronDown, ChevronRight, Type, Minus, FileText, Trash2 } from 'lucide-react'
import { devisService } from '../../../services/devis'
import ArticleAutocomplete from './ArticleAutocomplete'
import LineKebabMenu from './LineKebabMenu'
import type { DevisDetail, LotDevis, LigneDevis, Article } from '../../../types'

const formatEUR = (val: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val || 0)

interface Props {
  devis: DevisDetail
  isEditable: boolean
  onChanged: () => void
}

export default function DevisTableCard({ devis, isEditable, onChanged }: Props) {
  const [modeExpert, setModeExpert] = useState(false)
  const [collapsedLots, setCollapsedLots] = useState<Set<number>>(new Set())
  const [editingLine, setEditingLine] = useState<number | null>(null)
  const [editValues, setEditValues] = useState<Record<string, string | number>>({})

  const toggleLot = (lotId: number) => {
    setCollapsedLots(prev => {
      const next = new Set(prev)
      if (next.has(lotId)) next.delete(lotId)
      else next.add(lotId)
      return next
    })
  }

  // Line editing
  const startEdit = (ligne: LigneDevis) => {
    setEditingLine(ligne.id)
    setEditValues({
      designation: ligne.designation,
      quantite: ligne.quantite,
      unite: ligne.unite,
      prix_unitaire_ht: ligne.prix_unitaire_ht,
      taux_tva: ligne.taux_tva,
    })
  }

  const saveEdit = async (ligneId: number) => {
    try {
      await devisService.updateLigne(ligneId, {
        designation: String(editValues.designation),
        quantite: Number(editValues.quantite),
        unite: String(editValues.unite),
        prix_unitaire_ht: Number(editValues.prix_unitaire_ht),
        taux_tva: Number(editValues.taux_tva),
      })
      setEditingLine(null)
      onChanged()
    } catch { /* toast error */ }
  }

  const cancelEdit = () => setEditingLine(null)

  // CRUD operations
  const handleAddLot = async () => {
    const ordre = devis.lots.length + 1
    await devisService.createLot({
      devis_id: devis.id,
      titre: `Nouveau lot ${ordre}`,
      numero: String(ordre),
      ordre,
    })
    onChanged()
  }

  const handleAddLigne = async (lotId: number) => {
    await devisService.createLigne({
      lot_devis_id: lotId,
      designation: 'Nouvelle ligne',
      unite: 'u',
      quantite: 1,
      prix_unitaire_ht: 0,
      taux_tva: devis.taux_tva_defaut || 20,
    })
    onChanged()
  }

  const handleDeleteLigne = async (ligneId: number) => {
    await devisService.deleteLigne(ligneId)
    onChanged()
  }

  const handleDuplicateLigne = async (ligne: LigneDevis) => {
    await devisService.createLigne({
      lot_devis_id: ligne.lot_devis_id,
      designation: ligne.designation + ' (copie)',
      unite: ligne.unite,
      quantite: ligne.quantite,
      prix_unitaire_ht: ligne.prix_unitaire_ht,
      taux_tva: ligne.taux_tva,
      marge_ligne_pct: ligne.marge_ligne_pct,
    })
    onChanged()
  }

  const handleSelectArticle = useCallback(async (article: Article, lotId: number) => {
    await devisService.createLigne({
      lot_devis_id: lotId,
      designation: article.designation,
      unite: article.unite,
      prix_unitaire_ht: article.prix_unitaire_ht,
      taux_tva: devis.taux_tva_defaut || 20,
      quantite: 1,
      article_id: article.id,
    })
    onChanged()
  }, [devis.taux_tva_defaut, onChanged])

  const handleDeleteLot = async (lotId: number) => {
    await devisService.deleteLot(lotId)
    onChanged()
  }

  const tvaBadgeColor = (taux: number) => {
    if (taux <= 5.5) return 'bg-green-100 text-green-700'
    if (taux <= 10) return 'bg-amber-100 text-amber-700'
    return 'bg-gray-100 text-gray-600'
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Header bar */}
      <div className="p-4 border-b border-gray-100 flex items-center justify-between">
        <h2 className="font-semibold text-gray-900">Detail du devis</h2>
        <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
          <input
            type="checkbox"
            checked={modeExpert}
            onChange={e => setModeExpert(e.target.checked)}
            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          Mode expert (debourses)
        </label>
      </div>

      {/* Table */}
      <table className="w-full">
        <thead>
          <tr className="bg-indigo-600 text-white text-sm font-medium">
            <th className="px-4 py-3 text-left w-12">N</th>
            <th className="px-4 py-3 text-left">DESIGNATION</th>
            <th className="px-4 py-3 text-right w-20">QTE</th>
            <th className="px-4 py-3 text-center w-20">UNITE</th>
            <th className="px-4 py-3 text-right w-24">P.U. HT</th>
            <th className="px-4 py-3 text-center w-20">TVA</th>
            {modeExpert && (
              <>
                <th className="px-4 py-3 text-right w-24">D.S.</th>
                <th className="px-4 py-3 text-right w-20">Marge</th>
              </>
            )}
            <th className="px-4 py-3 text-right w-28">TOTAL HT</th>
            <th className="px-4 py-3 w-10"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {devis.lots.map((lot: LotDevis) => (
            <LotSection
              key={lot.id}
              lot={lot}
              collapsed={collapsedLots.has(lot.id)}
              onToggle={() => toggleLot(lot.id)}
              modeExpert={modeExpert}
              isEditable={isEditable}
              editingLine={editingLine}
              editValues={editValues}
              onStartEdit={startEdit}
              onSaveEdit={saveEdit}
              onCancelEdit={cancelEdit}
              onEditValueChange={(k, v) => setEditValues(prev => ({ ...prev, [k]: v }))}
              onAddLigne={() => handleAddLigne(lot.id)}
              onDeleteLigne={handleDeleteLigne}
              onDuplicateLigne={handleDuplicateLigne}
              onDeleteLot={() => handleDeleteLot(lot.id)}
              onSelectArticle={(a) => handleSelectArticle(a, lot.id)}
              tvaBadgeColor={tvaBadgeColor}
              tvaDefaut={devis.taux_tva_defaut || 20}
            />
          ))}
        </tbody>
      </table>

      {/* Add buttons */}
      {isEditable && (
        <div className="p-4 border-t border-gray-100 flex flex-wrap gap-2">
          <button
            onClick={() => handleAddLigne(devis.lots[devis.lots.length - 1]?.id)}
            disabled={devis.lots.length === 0}
            className="flex items-center gap-2 px-3 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            <Plus className="w-4 h-4" /> Nouvelle ligne
          </button>
          <button
            onClick={handleAddLot}
            className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200"
          >
            <Plus className="w-4 h-4" /> Section
          </button>
          <button className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">
            <Type className="w-4 h-4" /> Texte
          </button>
          <button className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">
            <Minus className="w-4 h-4" /> Saut de ligne
          </button>
          <button className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">
            <FileText className="w-4 h-4" /> Saut de page
          </button>
        </div>
      )}
    </div>
  )
}

// --- Lot section sub-component ---

interface LotSectionProps {
  lot: LotDevis
  collapsed: boolean
  onToggle: () => void
  modeExpert: boolean
  isEditable: boolean
  editingLine: number | null
  editValues: Record<string, string | number>
  onStartEdit: (ligne: LigneDevis) => void
  onSaveEdit: (ligneId: number) => void
  onCancelEdit: () => void
  onEditValueChange: (key: string, value: string | number) => void
  onAddLigne: () => void
  onDeleteLigne: (id: number) => void
  onDuplicateLigne: (ligne: LigneDevis) => void
  onDeleteLot: () => void
  onSelectArticle: (article: Article) => void
  tvaBadgeColor: (taux: number) => string
  tvaDefaut: number
}

function LotSection({
  lot, collapsed, onToggle, modeExpert, isEditable,
  editingLine, editValues, onStartEdit, onSaveEdit, onCancelEdit, onEditValueChange,
  onAddLigne, onDeleteLigne, onDuplicateLigne, onDeleteLot,
  onSelectArticle, tvaBadgeColor,
}: LotSectionProps) {
  const [showAutocomplete, setShowAutocomplete] = useState(false)
  const CollapseIcon = collapsed ? ChevronRight : ChevronDown

  const colSpan = modeExpert ? 10 : 8

  return (
    <>
      {/* Lot header row */}
      <tr className="bg-indigo-50 group">
        <td
          className="px-4 py-3 font-semibold text-indigo-900 cursor-pointer"
          colSpan={colSpan - 2}
          onClick={onToggle}
        >
          <span className="flex items-center gap-2">
            <CollapseIcon className="w-4 h-4" />
            {lot.numero}. {lot.titre}
          </span>
        </td>
        <td className="px-4 py-3 text-right font-semibold text-indigo-900 cursor-pointer" onClick={onToggle}>
          {formatEUR(lot.total_ht)}
        </td>
        <td className="px-4 py-3 text-right">
          {isEditable && (
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={onAddLigne}
                title="Ajouter une ligne"
                className="p-1 text-indigo-600 hover:bg-indigo-100 rounded"
              >
                <Plus className="w-4 h-4" />
              </button>
              <button
                onClick={onDeleteLot}
                title="Supprimer ce lot"
                className="p-1 text-red-400 hover:bg-red-50 hover:text-red-600 rounded"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          )}
        </td>
      </tr>

      {/* Lines */}
      {!collapsed && lot.lignes.map((ligne: LigneDevis) => {
        const isEditing = editingLine === ligne.id

        if (isEditing) {
          return (
            <tr key={ligne.id} className="bg-amber-50 border-2 border-amber-300">
              <td className="px-4 py-3 text-gray-500">{lot.numero}.{ligne.ordre}</td>
              <td className="px-4 py-3">
                <input
                  value={editValues.designation || ''}
                  onChange={e => onEditValueChange('designation', e.target.value)}
                  className="w-full px-2 py-1 border border-amber-400 rounded text-sm focus:ring-2 focus:ring-amber-500 outline-none"
                  autoFocus
                />
              </td>
              <td className="px-4 py-3">
                <input
                  type="number"
                  value={editValues.quantite || 0}
                  onChange={e => onEditValueChange('quantite', e.target.value)}
                  className="w-16 px-2 py-1 border border-gray-200 rounded text-right text-sm"
                />
              </td>
              <td className="px-4 py-3">
                <input
                  value={editValues.unite || ''}
                  onChange={e => onEditValueChange('unite', e.target.value)}
                  className="w-14 px-2 py-1 border border-gray-200 rounded text-center text-sm"
                />
              </td>
              <td className="px-4 py-3">
                <input
                  type="number"
                  step="0.01"
                  value={editValues.prix_unitaire_ht || 0}
                  onChange={e => onEditValueChange('prix_unitaire_ht', e.target.value)}
                  className="w-20 px-2 py-1 border border-gray-200 rounded text-right text-sm"
                />
              </td>
              <td className="px-4 py-3 text-center">
                <select
                  value={editValues.taux_tva || 20}
                  onChange={e => onEditValueChange('taux_tva', Number(e.target.value))}
                  className="px-1 py-1 border border-gray-200 rounded text-xs"
                >
                  <option value={5.5}>5,5%</option>
                  <option value={10}>10%</option>
                  <option value={20}>20%</option>
                </select>
              </td>
              {modeExpert && (
                <>
                  <td className="px-4 py-3 text-right text-sm text-gray-400">-</td>
                  <td className="px-4 py-3 text-right text-sm text-gray-400">-</td>
                </>
              )}
              <td className="px-4 py-3 text-right text-sm text-gray-400">
                {formatEUR(Number(editValues.quantite || 0) * Number(editValues.prix_unitaire_ht || 0))}
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-1">
                  <button onClick={() => onSaveEdit(ligne.id)} className="text-green-600 hover:text-green-700 text-xs font-medium">OK</button>
                  <button onClick={onCancelEdit} className="text-gray-400 hover:text-gray-600 text-xs">X</button>
                </div>
              </td>
            </tr>
          )
        }

        return (
          <tr
            key={ligne.id}
            className="hover:bg-gray-50"
            onDoubleClick={() => isEditable && onStartEdit(ligne)}
          >
            <td className="px-4 py-3 text-gray-500 text-sm">{lot.numero}.{ligne.ordre}</td>
            <td className="px-4 py-3 text-sm">{ligne.designation}</td>
            <td className="px-4 py-3 text-right text-sm">{ligne.quantite}</td>
            <td className="px-4 py-3 text-center text-gray-500 text-sm">{ligne.unite}</td>
            <td className="px-4 py-3 text-right text-sm">{formatEUR(ligne.prix_unitaire_ht)}</td>
            <td className="px-4 py-3 text-center">
              <span className={`text-xs px-1.5 py-0.5 rounded ${tvaBadgeColor(ligne.taux_tva)}`}>
                {ligne.taux_tva}%
              </span>
            </td>
            {modeExpert && (
              <>
                <td className="px-4 py-3 text-right text-sm text-gray-500">{formatEUR(ligne.debourse_sec)}</td>
                <td className="px-4 py-3 text-right text-sm text-gray-500">{ligne.marge_ligne_pct ?? '-'}%</td>
              </>
            )}
            <td className="px-4 py-3 text-right font-medium text-sm">{formatEUR(ligne.montant_ht)}</td>
            <td className="px-4 py-3">
              {isEditable && (
                <LineKebabMenu
                  onEdit={() => onStartEdit(ligne)}
                  onDelete={() => onDeleteLigne(ligne.id)}
                  onDuplicate={() => onDuplicateLigne(ligne)}
                />
              )}
            </td>
          </tr>
        )
      })}

      {/* Autocomplete row for adding new article to this lot */}
      {!collapsed && isEditable && (
        <tr className="bg-gray-50/50">
          <td className="px-4 py-2"></td>
          <td className="px-4 py-2" colSpan={colSpan - 1}>
            {showAutocomplete ? (
              <ArticleAutocomplete
                value=""
                onChange={() => {}}
                onSelectArticle={(article) => {
                  onSelectArticle(article)
                  setShowAutocomplete(false)
                }}
                placeholder="Rechercher un ouvrage dans la bibliotheque..."
              />
            ) : (
              <button
                onClick={() => setShowAutocomplete(true)}
                className="text-indigo-600 hover:text-indigo-700 text-sm flex items-center gap-1"
              >
                <Plus className="w-3 h-3" /> Ajouter depuis la bibliotheque
              </button>
            )}
          </td>
        </tr>
      )}
    </>
  )
}
