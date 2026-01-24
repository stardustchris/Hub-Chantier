/**
 * DocumentsCard - Carte mes documents
 * CDC Section 9 - GED avec acces rapide
 */

import { FileText } from 'lucide-react'

interface Document {
  id: string
  name: string
  siteName?: string
  type: 'pdf' | 'doc' | 'image' | 'other'
  url?: string
}

interface DocumentsCardProps {
  documents?: Document[]
  onViewAll?: () => void
  onDocumentClick?: (docId: string) => void
}

const defaultDocuments: Document[] = [
  { id: '1', name: 'Plan etage 1.pdf', siteName: 'Villa Lyon', type: 'pdf' },
  { id: '2', name: 'Consignes securite', siteName: 'General', type: 'doc' },
  { id: '3', name: 'Checklist qualite', siteName: 'Villa Lyon', type: 'doc' },
]

const typeColors = {
  pdf: { bg: 'bg-red-100', text: 'text-red-600' },
  doc: { bg: 'bg-blue-100', text: 'text-blue-600' },
  image: { bg: 'bg-green-100', text: 'text-green-600' },
  other: { bg: 'bg-gray-100', text: 'text-gray-600' },
}

export default function DocumentsCard({
  documents = defaultDocuments,
  onViewAll,
  onDocumentClick,
}: DocumentsCardProps) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <FileText className="w-5 h-5 text-purple-600" />
          Mes documents
        </h2>
        <button
          onClick={onViewAll}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          Voir tout
        </button>
      </div>
      <div className="space-y-3">
        {documents.map((doc) => {
          const colors = typeColors[doc.type]
          return (
            <button
              key={doc.id}
              onClick={() => onDocumentClick?.(doc.id)}
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
    </div>
  )
}
