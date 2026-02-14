/**
 * DocumentsCard - Carte mes documents
 * CDC Section 9 - GED avec acces rapide
 * Charge les vrais documents depuis l'API et les ouvre sur toutes les plateformes
 */

import { FileText, Loader2, FolderOpen, ChevronDown } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useRecentDocuments, type RecentDocument } from '../../hooks'

const typeColors = {
  pdf: { bg: 'bg-red-100', text: 'text-red-600' },
  doc: { bg: 'bg-blue-100', text: 'text-blue-600' },
  image: { bg: 'bg-green-100', text: 'text-green-600' },
  other: { bg: 'bg-gray-100', text: 'text-gray-600' },
}

export default function DocumentsCard() {
  const navigate = useNavigate()
  const { documents, isLoading, hasMore, openDocument, loadMore } = useRecentDocuments()

  const handleViewAll = () => {
    navigate('/documents')
  }

  const handleDocumentClick = (doc: RecentDocument) => {
    openDocument(doc)
  }

  return (
    <div className="bg-white rounded-2xl p-5 shadow-lg hover-lift">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <FileText className="w-5 h-5 text-purple-600" />
          Mes documents
        </h2>
        <button
          onClick={handleViewAll}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          Voir tout
        </button>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-purple-600" />
        </div>
      )}

      {/* Empty state */}
      {!isLoading && documents.length === 0 && (
        <div className="text-center py-8">
          <FolderOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">Aucun document récent</p>
          <p className="text-gray-400 text-xs mt-1">Les documents de vos chantiers apparaîtront ici</p>
          <button
            onClick={handleViewAll}
            className="mt-3 text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            Accéder à la GED
          </button>
        </div>
      )}

      {/* Documents list */}
      {!isLoading && documents.length > 0 && (
        <div className="space-y-3">
          <div className="space-y-2 max-h-[240px] overflow-y-auto">
            {documents.map((doc) => {
              const colors = typeColors[doc.type]
              return (
                <button
                  key={doc.id}
                  onClick={() => handleDocumentClick(doc)}
                  className="w-full flex items-center gap-3 p-2 rounded-xl hover:bg-gray-50 transition-colors text-left"
                >
                  <div className={`w-10 h-10 rounded-lg ${colors.bg} flex items-center justify-center shrink-0`}>
                    <FileText className={`w-5 h-5 ${colors.text}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 text-sm truncate">{doc.name}</p>
                    {doc.siteName && <p className="text-xs text-gray-500">{doc.siteName}</p>}
                  </div>
                </button>
              )
            })}
          </div>

          {/* Bouton Voir plus */}
          {hasMore && (
            <button
              onClick={loadMore}
              className="w-full flex items-center justify-center gap-1 py-2 text-sm text-purple-600 hover:text-purple-700 font-medium hover:bg-purple-50 rounded-lg transition-colors"
            >
              <ChevronDown className="w-4 h-4" />
              Voir plus
            </button>
          )}
        </div>
      )}
    </div>
  )
}
