/**
 * Modal pour créer/éditer un dossier ou document
 */

import React, { useState, useEffect } from 'react';
import type {
  Dossier,
  Document,
  DossierCreateDTO,
  DossierUpdateDTO,
  DocumentUpdateDTO,
  NiveauAcces,
  TypeDossier,
} from '../../types/documents';
import {
  NIVEAU_ACCES_LABELS,
  TYPE_DOSSIER_LABELS,
} from '../../types/documents';
import { useFocusTrap } from '../../hooks/useFocusTrap';

interface DossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: DossierCreateDTO | DossierUpdateDTO) => void;
  dossier?: Dossier | null;
  chantierId: number;
  parentId?: number | null;
  loading?: boolean;
}

export const DossierModal: React.FC<DossierModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  dossier,
  chantierId,
  parentId = null,
  loading = false,
}) => {
  const focusTrapRef = useFocusTrap({ enabled: isOpen, onClose });
  const [nom, setNom] = useState('');
  const [typeDossier, setTypeDossier] = useState<TypeDossier>('custom');
  const [niveauAcces, setNiveauAcces] = useState<NiveauAcces>('compagnon');

  const isEditing = !!dossier;

  useEffect(() => {
    if (dossier) {
      setNom(dossier.nom);
      setTypeDossier(dossier.type_dossier);
      setNiveauAcces(dossier.niveau_acces);
    } else {
      setNom('');
      setTypeDossier('custom');
      setNiveauAcces('compagnon');
    }
  }, [dossier, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (isEditing) {
      const data: DossierUpdateDTO = {
        nom: nom !== dossier?.nom ? nom : undefined,
        niveau_acces: niveauAcces !== dossier?.niveau_acces ? niveauAcces : undefined,
      };
      onSubmit(data);
    } else {
      const data: DossierCreateDTO = {
        chantier_id: chantierId,
        nom,
        type_dossier: typeDossier,
        niveau_acces: niveauAcces,
        parent_id: parentId,
      };
      onSubmit(data);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div
        ref={focusTrapRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className="bg-white rounded-lg shadow-xl w-full max-w-md p-6"
      >
        <h2 id="modal-title" className="text-xl font-semibold mb-4">
          {isEditing ? 'Modifier le dossier' : 'Nouveau dossier'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom du dossier
            </label>
            <input
              type="text"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
              autoFocus
            />
          </div>

          {!isEditing && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type de dossier
              </label>
              <select
                value={typeDossier}
                onChange={(e) => setTypeDossier(e.target.value as TypeDossier)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {Object.entries(TYPE_DOSSIER_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Niveau d'accès minimum (GED-04)
            </label>
            <select
              value={niveauAcces}
              onChange={(e) => setNiveauAcces(e.target.value as NiveauAcces)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {Object.entries(NIVEAU_ACCES_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              disabled={loading}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
              disabled={loading || !nom.trim()}
            >
              {loading ? 'Enregistrement...' : isEditing ? 'Modifier' : 'Créer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

interface DocumentEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: DocumentUpdateDTO) => void;
  document: Document | null;
  loading?: boolean;
}

export const DocumentEditModal: React.FC<DocumentEditModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  document,
  loading = false,
}) => {
  const focusTrapRef = useFocusTrap({ enabled: isOpen, onClose });
  const [nom, setNom] = useState('');
  const [description, setDescription] = useState('');
  const [niveauAcces, setNiveauAcces] = useState<NiveauAcces | ''>('');

  useEffect(() => {
    if (document) {
      setNom(document.nom);
      setDescription(document.description || '');
      setNiveauAcces(document.niveau_acces || '');
    }
  }, [document, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const data: DocumentUpdateDTO = {};
    if (nom !== document?.nom) data.nom = nom;
    if (description !== (document?.description || '')) data.description = description;
    if (niveauAcces !== (document?.niveau_acces || '')) {
      data.niveau_acces = niveauAcces || null;
    }

    onSubmit(data);
  };

  if (!isOpen || !document) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div
        ref={focusTrapRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title-doc"
        className="bg-white rounded-lg shadow-xl w-full max-w-md p-6"
      >
        <h2 id="modal-title-doc" className="text-xl font-semibold mb-4">Modifier le document</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom du fichier
            </label>
            <input
              type="text"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Niveau d'accès spécifique
            </label>
            <select
              value={niveauAcces}
              onChange={(e) => setNiveauAcces(e.target.value as NiveauAcces | '')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Hériter du dossier</option>
              {Object.entries(NIVEAU_ACCES_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              disabled={loading}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
              disabled={loading || !nom.trim()}
            >
              {loading ? 'Enregistrement...' : 'Modifier'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DossierModal;
