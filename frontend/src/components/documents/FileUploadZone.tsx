/**
 * Composant FileUploadZone - Zone de drag & drop pour upload (GED-06, GED-08, GED-09)
 */

import React, { useState, useCallback, useRef } from 'react';
import { MAX_FILE_SIZE, MAX_FILES_UPLOAD, ACCEPTED_EXTENSIONS } from '../../types/documents';
import { formatFileSize } from '../../services/documents';

interface FileUploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  uploading?: boolean;
  uploadProgress?: number;
  disabled?: boolean;
  maxFiles?: number;
  accept?: string;
}

const FileUploadZone: React.FC<FileUploadZoneProps> = ({
  onFilesSelected,
  uploading = false,
  uploadProgress = 0,
  disabled = false,
  maxFiles = MAX_FILES_UPLOAD,
  accept = ACCEPTED_EXTENSIONS.join(','),
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFiles = (files: FileList | File[]): File[] => {
    const validFiles: File[] = [];
    const errors: string[] = [];

    const fileArray = Array.from(files);

    if (fileArray.length > maxFiles) {
      errors.push(`Maximum ${maxFiles} fichiers simultanés (GED-06)`);
      return [];
    }

    for (const file of fileArray) {
      // Vérifier la taille (GED-07)
      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name}: dépasse la limite de 10 Go`);
        continue;
      }

      // Vérifier l'extension (GED-12)
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!ACCEPTED_EXTENSIONS.includes(extension)) {
        errors.push(`${file.name}: type de fichier non supporté`);
        continue;
      }

      validFiles.push(file);
    }

    if (errors.length > 0) {
      setError(errors.join('\n'));
    } else {
      setError(null);
    }

    return validFiles;
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled && !uploading) {
      setIsDragging(true);
    }
  }, [disabled, uploading]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (disabled || uploading) return;

      const files = e.dataTransfer.files;
      const validFiles = validateFiles(files);
      if (validFiles.length > 0) {
        onFilesSelected(validFiles);
      }
    },
    [disabled, uploading, onFilesSelected, validateFiles]
  );

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files) {
        const validFiles = validateFiles(files);
        if (validFiles.length > 0) {
          onFilesSelected(validFiles);
        }
      }
      // Reset input pour permettre re-sélection du même fichier
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    [onFilesSelected, validateFiles]
  );

  const handleClick = () => {
    if (!disabled && !uploading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="w-full">
      {/* Zone de drop */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : disabled || uploading
            ? 'border-gray-200 bg-gray-50 cursor-not-allowed'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          multiple
          accept={accept}
          onChange={handleFileInputChange}
          disabled={disabled || uploading}
        />

        {uploading ? (
          <div className="space-y-3">
            <div className="animate-spin text-4xl">⏳</div>
            <p className="text-gray-600">Upload en cours...</p>
            {/* Barre de progression (GED-09) */}
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500">{Math.round(uploadProgress)}%</p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-4xl">
              {isDragging ? '📥' : '📤'}
            </div>
            <p className="text-gray-600">
              {isDragging ? (
                'Déposez les fichiers ici'
              ) : (
                <>
                  <span className="font-medium text-blue-600">Cliquez pour sélectionner</span>
                  {' '}ou glissez-déposez vos fichiers
                </>
              )}
            </p>
            <p className="text-sm text-gray-500">
              Max {maxFiles} fichiers, {formatFileSize(MAX_FILE_SIZE)} par fichier
            </p>
            <p className="text-xs text-gray-600">
              Formats: PDF, Images, Excel, Word, Vidéos
            </p>
          </div>
        )}
      </div>

      {/* Message d'erreur */}
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600 whitespace-pre-line">{error}</p>
        </div>
      )}
    </div>
  );
};

export default FileUploadZone;
