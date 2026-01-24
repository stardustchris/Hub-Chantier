/**
 * Composant DocumentPreviewModal - Prévisualisation intégrée (GED-17)
 * Supporte PDF, images et vidéos
 */

import React, { useState, useEffect } from 'react';
import type { Document } from '../../types/documents';
import { getDocumentPreviewUrl, getDocumentPreview, type DocumentPreview } from '../../services/documents';

interface DocumentPreviewModalProps {
  document: Document | null;
  isOpen: boolean;
  onClose: () => void;
  onDownload?: (document: Document) => void;
}

const DocumentPreviewModal: React.FC<DocumentPreviewModalProps> = ({
  document,
  isOpen,
  onClose,
  onDownload,
}) => {
  const [previewInfo, setPreviewInfo] = useState<DocumentPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (document && isOpen) {
      setLoading(true);
      setError(null);
      getDocumentPreview(document.id)
        .then(setPreviewInfo)
        .catch(() => setError('Impossible de charger la prévisualisation'))
        .finally(() => setLoading(false));
    } else {
      setPreviewInfo(null);
    }
  }, [document, isOpen]);

  if (!isOpen || !document) return null;

  const previewUrl = getDocumentPreviewUrl(document.id);

  const renderPreview = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      );
    }

    if (error || !previewInfo?.can_preview) {
      return (
        <div className="flex flex-col items-center justify-center h-96 text-gray-500">
          <span className="text-6xl mb-4">📄</span>
          <p className="text-lg">{error || 'Prévisualisation non disponible'}</p>
          <p className="text-sm mt-2">
            {document.taille > 10 * 1024 * 1024
              ? 'Le fichier est trop volumineux (max 10 Mo)'
              : 'Ce type de fichier ne peut pas être prévisualisé'}
          </p>
          {onDownload && (
            <button
              onClick={() => onDownload(document)}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Télécharger le fichier
            </button>
          )}
        </div>
      );
    }

    // Prévisualisation selon le type
    switch (document.type_document) {
      case 'pdf':
        return (
          <iframe
            src={previewUrl}
            className="w-full h-[70vh] border-0"
            title={document.nom}
          />
        );

      case 'image':
        return (
          <div className="flex items-center justify-center p-4 bg-gray-100">
            <img
              src={previewUrl}
              alt={document.nom}
              className="max-w-full max-h-[70vh] object-contain"
            />
          </div>
        );

      case 'video':
        return (
          <div className="flex items-center justify-center p-4 bg-black">
            <video
              src={previewUrl}
              controls
              className="max-w-full max-h-[70vh]"
            >
              Votre navigateur ne supporte pas la lecture de vidéos.
            </video>
          </div>
        );

      default:
        return (
          <div className="flex flex-col items-center justify-center h-96 text-gray-500">
            <span className="text-6xl mb-4">📄</span>
            <p>Prévisualisation non disponible pour ce type de fichier</p>
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        {/* Overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative inline-block w-full max-w-5xl p-0 overflow-hidden text-left align-middle transition-all transform bg-white rounded-lg shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center gap-3">
              <span className="text-2xl">
                {document.type_document === 'pdf' && '📄'}
                {document.type_document === 'image' && '🖼️'}
                {document.type_document === 'video' && '🎬'}
              </span>
              <div>
                <h3 className="text-lg font-medium text-gray-900 truncate max-w-md">
                  {document.nom}
                </h3>
                <p className="text-sm text-gray-500">
                  {document.taille_formatee} • {document.type_document.toUpperCase()}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {onDownload && (
                <button
                  onClick={() => onDownload(document)}
                  className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md"
                >
                  ⬇️ Télécharger
                </button>
              )}
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="bg-white">{renderPreview()}</div>
        </div>
      </div>
    </div>
  );
};

export default DocumentPreviewModal;
