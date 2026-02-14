/**
 * Composant TaskList - Liste des taches d'un chantier (TAC-01)
 * Avec recherche (TAC-14), drag & drop (TAC-15), et statistiques (TAC-20)
 */

import { useState, useEffect, useCallback } from 'react'
import {
  Search,
  Plus,
  FileText,
  Loader2,
  ChevronDown,
  Filter,
  Download,
  BookTemplate,
} from 'lucide-react'
import { tachesService } from '../../services/taches'
import { logger } from '../../services/logger'
import { TasksProvider } from '../../contexts/TasksContext'
import type { Tache, TacheStats, TacheCreate, TacheUpdate } from '../../types'
import { COULEURS_PROGRESSION } from '../../types'
import TaskItem from './TaskItem'
import TaskModal from './TaskModal'
import TemplateImportModal from './TemplateImportModal'

interface TaskListProps {
  chantierId: number
  chantierNom: string
}

export default function TaskList({ chantierId, chantierNom }: TaskListProps) {
  const [taches, setTaches] = useState<Tache[]>([])
  const [stats, setStats] = useState<TacheStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatut, setFilterStatut] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)

  // Modals
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [editingTache, setEditingTache] = useState<Tache | null>(null)
  const [parentIdForNew, setParentIdForNew] = useState<number | null>(null)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Chargement des statistiques (stable car ne depend que de chantierId)
  const loadStats = useCallback(async () => {
    try {
      const statsData = await tachesService.getStats(chantierId)
      setStats(statsData)
    } catch (err) {
      logger.error('Erreur chargement stats', err, { context: 'TaskList' })
      // Stats non critiques, pas d'affichage d'erreur
    }
  }, [chantierId])

  // Chargement des taches (depend de chantierId, searchQuery, filterStatut)
  const loadTaches = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await tachesService.listByChantier(chantierId, {
        query: searchQuery || undefined,
        statut: filterStatut || undefined,
        include_sous_taches: true,
      })
      setTaches(response.items)
    } catch (err: any) {
      logger.error('Erreur chargement taches', err, { context: 'TaskList' })
      // Ne pas afficher d'erreur si c'est juste une liste vide (404 ou pas de données)
      // Seulement afficher l'erreur pour les vraies erreurs réseau/serveur
      if (err?.response?.status && err.response.status !== 404) {
        setError('Impossible de charger les taches. Verifiez votre connexion.')
      } else {
        // 404 ou pas de données : liste vide, pas d'erreur à afficher
        setTaches([])
      }
    } finally {
      setIsLoading(false)
    }
  }, [chantierId, searchQuery, filterStatut])

  // Chargement initial
  useEffect(() => {
    loadTaches()
    loadStats()
  }, [loadTaches, loadStats])

  // Recherche avec debounce (TAC-14)
  useEffect(() => {
    const timeout = setTimeout(() => {
      loadTaches()
    }, 300)
    return () => clearTimeout(timeout)
  }, [loadTaches])

  // P1-7: Memoize handlers pour éviter re-renders
  const handleToggleComplete = useCallback(async (tacheId: number, terminer: boolean) => {
    try {
      setError(null)
      await tachesService.complete(tacheId, terminer)
      loadTaches()
      loadStats()
    } catch (err) {
      logger.error('Erreur completion tache', err, { context: 'TaskList' })
      setError('Impossible de modifier le statut de la tache.')
    }
  }, [loadTaches, loadStats])

  const handleSaveTache = useCallback(async (data: TacheCreate | TacheUpdate) => {
    try {
      setError(null)
      if (editingTache) {
        await tachesService.update(editingTache.id, data as TacheUpdate)
      } else {
        const createData = data as Omit<TacheCreate, 'chantier_id'>
        await tachesService.create({
          ...createData,
          chantier_id: chantierId,
          parent_id: parentIdForNew || undefined,
        })
      }
      setShowTaskModal(false)
      setEditingTache(null)
      setParentIdForNew(null)
      loadTaches()
      loadStats()
    } catch (err) {
      logger.error('Erreur sauvegarde tache', err, { context: 'TaskList' })
      setError('Impossible de sauvegarder la tache. Verifiez les donnees.')
    }
  }, [chantierId, editingTache, parentIdForNew, loadTaches, loadStats])

  const handleDeleteTache = useCallback(async (tacheId: number) => {
    if (!confirm('Supprimer cette tache et ses sous-taches ?')) return

    try {
      setError(null)
      await tachesService.delete(tacheId)
      loadTaches()
      loadStats()
    } catch (err) {
      logger.error('Erreur suppression tache', err, { context: 'TaskList' })
      setError('Impossible de supprimer la tache.')
    }
  }, [loadTaches, loadStats])

  const handleImportTemplate = useCallback(async (templateId: number) => {
    try {
      setError(null)
      await tachesService.importTemplate(templateId, chantierId)
      setShowTemplateModal(false)
      loadTaches()
      loadStats()
    } catch (err) {
      logger.error('Erreur import template', err, { context: 'TaskList' })
      setError('Impossible d\'importer le modele.')
    }
  }, [chantierId, loadTaches, loadStats])

  // Export PDF (TAC-16)
  const handleExportPDF = async () => {
    try {
      setIsExporting(true)
      setError(null)
      const blob = await tachesService.exportPDF(chantierId)
      tachesService.downloadPDF(blob, `taches-${chantierNom}.pdf`)
    } catch (err) {
      logger.error('Erreur export PDF', err, { context: 'TaskList' })
      setError('Export PDF non disponible pour le moment.')
    } finally {
      setIsExporting(false)
    }
  }

  const openNewTaskModal = useCallback((parentId?: number) => {
    setEditingTache(null)
    setParentIdForNew(parentId || null)
    setShowTaskModal(true)
  }, [])

  const openEditTaskModal = useCallback((tache: Tache) => {
    setEditingTache(tache)
    setParentIdForNew(null)
    setShowTaskModal(true)
  }, [])

  // Calcul couleur progression globale
  const progressionCouleur = stats
    ? stats.progression_globale <= 0
      ? 'gris'
      : stats.progression_globale <= 80
      ? 'vert'
      : stats.progression_globale <= 100
      ? 'jaune'
      : 'rouge'
    : 'gris'

  return (
    <div className="space-y-4">
      {/* Banniere d'erreur */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center justify-between">
          <p className="text-red-700 text-sm">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-red-500 hover:text-red-700 text-sm font-medium"
          >
            Fermer
          </button>
        </div>
      )}

      {/* Stats header (TAC-20) */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white rounded-lg p-3 border">
            <p className="text-xs text-gray-500">Total taches</p>
            <p className="text-xl font-bold">{stats.total_taches}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border">
            <p className="text-xs text-gray-500">Terminees</p>
            <p className="text-xl font-bold text-green-600">{stats.taches_terminees}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border">
            <p className="text-xs text-gray-500">En retard</p>
            <p className="text-xl font-bold text-red-600">{stats.taches_en_retard}</p>
          </div>
          <div className="bg-white rounded-lg p-3 border">
            <p className="text-xs text-gray-500">Progression</p>
            <div className="flex items-center gap-2">
              <p className="text-xl font-bold">{stats.progression_globale.toFixed(0)}%</p>
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: COULEURS_PROGRESSION[progressionCouleur].color }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Barre de recherche et actions (TAC-07, TAC-14) */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Recherche */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
          <input
            type="text"
            placeholder="Rechercher une tache..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-9 w-full"
          />
        </div>

        {/* Filtres */}
        <div className="flex gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn btn-outline flex items-center gap-2 ${
              filterStatut ? 'border-primary-500 text-primary-600' : ''
            }`}
          >
            <Filter className="w-4 h-4" />
            <span className="hidden sm:inline">Filtrer</span>
            <ChevronDown className="w-4 h-4" />
          </button>

          {/* Import template (TAC-05) */}
          <button
            onClick={() => setShowTemplateModal(true)}
            className="btn btn-outline flex items-center gap-2"
            title="Importer un modele"
          >
            <BookTemplate className="w-4 h-4" />
            <span className="hidden sm:inline">Modele</span>
          </button>

          {/* Export PDF (TAC-16) */}
          <button
            onClick={handleExportPDF}
            disabled={isExporting}
            className="btn btn-outline flex items-center gap-2"
            title="Exporter en PDF"
          >
            {isExporting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            <span className="hidden sm:inline">PDF</span>
          </button>

          {/* Ajouter tache (TAC-07) */}
          <button
            onClick={() => openNewTaskModal()}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Ajouter</span>
          </button>
        </div>
      </div>

      {/* Panneau filtres */}
      {showFilters && (
        <div className="bg-gray-50 rounded-lg p-3 flex flex-wrap gap-2">
          <button
            onClick={() => setFilterStatut('')}
            className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
              !filterStatut
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            Toutes
          </button>
          <button
            onClick={() => setFilterStatut('a_faire')}
            className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
              filterStatut === 'a_faire'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            A faire
          </button>
          <button
            onClick={() => setFilterStatut('termine')}
            className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
              filterStatut === 'termine'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            Terminees
          </button>
        </div>
      )}

      {/* Liste des taches */}
      <div className="bg-white rounded-lg border">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
          </div>
        ) : taches.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-500 mb-3">
              {searchQuery
                ? 'Aucune tache trouvee'
                : 'Aucune tache pour ce chantier'}
            </p>
            <button
              onClick={() => openNewTaskModal()}
              className="btn btn-primary inline-flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Creer une tache
            </button>
          </div>
        ) : (
          <TasksProvider
            onToggleComplete={handleToggleComplete}
            onEdit={openEditTaskModal}
            onDelete={handleDeleteTache}
            onAddSubtask={openNewTaskModal}
          >
            <div className="divide-y">
              {taches.map((tache) => (
                <TaskItem key={tache.id} tache={tache} />
              ))}
            </div>
          </TasksProvider>
        )}
      </div>

      {/* Modal creation/edition tache */}
      {showTaskModal && (
        <TaskModal
          tache={editingTache}
          parentId={parentIdForNew}
          onClose={() => {
            setShowTaskModal(false)
            setEditingTache(null)
            setParentIdForNew(null)
          }}
          onSave={handleSaveTache}
        />
      )}

      {/* Modal import template */}
      {showTemplateModal && (
        <TemplateImportModal
          onClose={() => setShowTemplateModal(false)}
          onImport={handleImportTemplate}
        />
      )}
    </div>
  )
}
