/**
 * Composant DocumentList - Liste des documents d'un dossier (GED-03)
 * Avec sélection multiple et téléchargement ZIP (GED-16)
 * Et prévisualisation (GED-17)
 */

import React, { useState, useCallback } from 'react';
import type { Document, TypeDocument } from '../../types/documents';
import { TYPE_DOCUMENT_LABELS } from '../../types/documents';
import { getDocumentIcon, downloadAndSaveZip } from '../../services/documents';

interface DocumentListProps {
  documents: Document[];
  loading?: boolean;
  onDocumentClick?: (document: Document) => void;
  onDocumentDownload?: (document: Document) => void;
  onDocumentEdit?: (document: Document) => void;
  onDocumentDelete?: (document: Document) => void;
  onDocumentPreview?: (document: Document) => void;
  selectedDocumentId?: number | null;
  selectionEnabled?: boolean;
}

const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  loading = false,
  onDocumentClick,
  onDocumentDownload,
  onDocumentEdit,
  onDocumentDelete,
  onDocumentPreview,
  selectedDocumentId,
  selectionEnabled = true,
}) => {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [isDownloadingZip, setIsDownloadingZip] = useState(false);

  const toggleSelection = useCallback((docId: number, event: React.MouseEvent) => {
    event.stopPropagation();
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(docId)) {
        next.delete(docId);
      } else {
        next.add(docId);
      }
      return next;
    });
  }, []);

  const toggleSelectAll = useCallback(() => {
    if (selectedIds.size === documents.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(documents.map((d) => d.id)));
    }
  }, [documents, selectedIds.size]);

  const handleDownloadZip = useCallback(async () => {
    if (selectedIds.size === 0) return;

    setIsDownloadingZip(true);
    try {
      await downloadAndSaveZip(Array.from(selectedIds));
      setSelectedIds(new Set());
    } catch (error) {
      console.error('Erreur lors du téléchargement ZIP:', error);
    } finally {
      setIsDownloadingZip(false);
    }
  }, [selectedIds]);

  const canPreview = (doc: Document): boolean => {
    const previewableTypes = ['pdf', 'image', 'video'];
    return previewableTypes.includes(doc.type_document) && doc.taille < 10 * 1024 * 1024;
  };
  const getTypeColor = (type: TypeDocument): string => {
    const colors: Record<TypeDocument, string> = {
      pdf: 'text-red-500',
      image: 'text-green-500',
      excel: 'text-emerald-600',
      word: 'text-blue-500',
      video: 'text-purple-500',
      autre: 'text-gray-500',
    };
    return colors[type] || 'text-gray-500';
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <span className="text-4xl mb-4 block">📂</span>
        <p>Aucun document dans ce dossier</p>
        <p className="text-sm mt-2">Glissez-déposez des fichiers ou cliquez sur "Ajouter"</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      {/* Barre d'actions pour la sélection (GED-16) */}
      {selectionEnabled && selectedIds.size > 0 && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-3 flex items-center justify-between">
          <span className="text-sm text-blue-700">
            {selectedIds.size} document{selectedIds.size > 1 ? 's' : ''} sélectionné{selectedIds.size > 1 ? 's' : ''}
          </span>
          <div className="flex gap-2">
            <button
              onClick={handleDownloadZip}
              disabled={isDownloadingZip}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50"
            >
              {isDownloadingZip ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Téléchargement...
                </>
              ) : (
                <>
                  📦 Télécharger en ZIP
                </>
              )}
            </button>
            <button
              onClick={() => setSelectedIds(new Set())}
              className="px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-800"
            >
              Annuler
            </button>
          </div>
        </div>
      )}

      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {selectionEnabled && (
              <th className="px-4 py-3 w-10">
                <input
                  type="checkbox"
                  checked={documents.length > 0 && selectedIds.size === documents.length}
                  onChange={toggleSelectAll}
                  className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                />
              </th>
            )}
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Nom
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Taille
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Ajouté par
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {documents.map((doc) => (
            <tr
              key={doc.id}
              className={`hover:bg-gray-50 cursor-pointer ${
                selectedDocumentId === doc.id ? 'bg-blue-50' : ''
              } ${selectedIds.has(doc.id) ? 'bg-blue-50' : ''}`}
              onClick={() => onDocumentClick?.(doc)}
            >
              {selectionEnabled && (
                <td className="px-4 py-3 whitespace-nowrap w-10">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(doc.id)}
                    onChange={() => {}}
                    onClick={(e) => toggleSelection(doc.id, e)}
                    className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />
                </td>
              )}
              <td className="px-4 py-3 whitespace-nowrap">
                <div className="flex items-center">
                  <span className={`text-xl mr-3 ${getTypeColor(doc.type_document)}`}>
                    {getDocumentIcon(doc.type_document)}
                  </span>
                  <div>
                    <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                      {doc.nom}
                    </div>
                    {doc.description && (
                      <div className="text-xs text-gray-500 truncate max-w-xs">
                        {doc.description}
                      </div>
                    )}
                  </div>
                </div>
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <span
                  className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    doc.type_document === 'pdf'
                      ? 'bg-red-100 text-red-800'
                      : doc.type_document === 'image'
                      ? 'bg-green-100 text-green-800'
                      : doc.type_document === 'excel'
                      ? 'bg-emerald-100 text-emerald-800'
                      : doc.type_document === 'word'
                      ? 'bg-blue-100 text-blue-800'
                      : doc.type_document === 'video'
                      ? 'bg-purple-100 text-purple-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {TYPE_DOCUMENT_LABELS[doc.type_document] || doc.type_document}
                </span>
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {doc.taille_formatee}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {doc.uploaded_by_nom || `Utilisateur #${doc.uploaded_by}`}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {formatDate(doc.uploaded_at)}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-right text-sm">
                <div className="flex justify-end gap-2">
                  {/* Prévisualisation (GED-17) */}
                  {onDocumentPreview && canPreview(doc) && (
                    <button
                      className="text-purple-600 hover:text-purple-800"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDocumentPreview(doc);
                      }}
                      title="Prévisualiser"
                    >
                      👁️
                    </button>
                  )}
                  {onDocumentDownload && (
                    <button
                      className="text-blue-600 hover:text-blue-800"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDocumentDownload(doc);
                      }}
                      title="Télécharger"
                    >
                      ⬇️
                    </button>
                  )}
                  {onDocumentEdit && (
                    <button
                      className="text-gray-600 hover:text-gray-800"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDocumentEdit(doc);
                      }}
                      title="Modifier"
                    >
                      ✏️
                    </button>
                  )}
                  {onDocumentDelete && (
                    <button
                      className="text-red-600 hover:text-red-800"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDocumentDelete(doc);
                      }}
                      title="Supprimer"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DocumentList;
