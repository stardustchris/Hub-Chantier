/**
 * Composant SignalementModal - Modale de création/édition d'un signalement
 */

import React, { useState, useEffect } from 'react';
import type {
  Signalement,
  SignalementCreateDTO,
  SignalementUpdateDTO,
  Priorite,
} from '../../types/signalements';
import { PRIORITE_OPTIONS } from '../../types/signalements';
import { createSignalement, updateSignalement } from '../../services/signalements';

interface SignalementModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (signalement: Signalement) => void;
  chantierId: number;
  signalement?: Signalement | null;
  users?: Array<{ id: number; nom: string }>;
}

const SignalementModal: React.FC<SignalementModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  chantierId,
  signalement,
  users = [],
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<{
    titre: string;
    description: string;
    priorite: Priorite;
    assigne_a: number | null;
    date_resolution_souhaitee: string;
    localisation: string;
    photo_url: string;
  }>({
    titre: '',
    description: '',
    priorite: 'moyenne',
    assigne_a: null,
    date_resolution_souhaitee: '',
    localisation: '',
    photo_url: '',
  });

  const isEdit = !!signalement;

  useEffect(() => {
    if (signalement) {
      setFormData({
        titre: signalement.titre,
        description: signalement.description,
        priorite: signalement.priorite,
        assigne_a: signalement.assigne_a,
        date_resolution_souhaitee: signalement.date_resolution_souhaitee?.split('T')[0] || '',
        localisation: signalement.localisation || '',
        photo_url: signalement.photo_url || '',
      });
    } else {
      setFormData({
        titre: '',
        description: '',
        priorite: 'moyenne',
        assigne_a: null,
        date_resolution_souhaitee: '',
        localisation: '',
        photo_url: '',
      });
    }
    setError(null);
  }, [signalement, isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'assigne_a' ? (value ? parseInt(value, 10) : null) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let result: Signalement;

      if (isEdit && signalement) {
        const updateData: SignalementUpdateDTO = {
          titre: formData.titre,
          description: formData.description,
          priorite: formData.priorite,
          assigne_a: formData.assigne_a,
          date_resolution_souhaitee: formData.date_resolution_souhaitee || null,
          localisation: formData.localisation || null,
          photo_url: formData.photo_url || null,
        };
        result = await updateSignalement(signalement.id, updateData);
      } else {
        const createData: SignalementCreateDTO = {
          chantier_id: chantierId,
          titre: formData.titre,
          description: formData.description,
          priorite: formData.priorite,
          assigne_a: formData.assigne_a,
          date_resolution_souhaitee: formData.date_resolution_souhaitee || null,
          localisation: formData.localisation || null,
          photo_url: formData.photo_url || null,
        };
        result = await createSignalement(createData);
      }

      onSuccess(result);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="inline-block w-full max-w-lg p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {isEdit ? 'Modifier le signalement' : 'Nouveau signalement'}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-600 hover:text-gray-600"
              aria-label="Fermer"
            >
              ✕
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Titre */}
            <div>
              <label htmlFor="titre" className="block text-sm font-medium text-gray-700 mb-1">
                Titre *
              </label>
              <input
                type="text"
                id="titre"
                name="titre"
                value={formData.titre}
                onChange={handleChange}
                required
                maxLength={200}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="Titre du signalement"
              />
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                Description *
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="Décrivez le problème en détail..."
              />
            </div>

            {/* Priorité */}
            <div>
              <label htmlFor="priorite" className="block text-sm font-medium text-gray-700 mb-1">
                Priorité
              </label>
              <select
                id="priorite"
                name="priorite"
                value={formData.priorite}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                {PRIORITE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Assignation */}
            <div>
              <label htmlFor="assigne_a" className="block text-sm font-medium text-gray-700 mb-1">
                Assigner à
              </label>
              <select
                id="assigne_a"
                name="assigne_a"
                value={formData.assigne_a || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Non assigné</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.nom}
                  </option>
                ))}
              </select>
            </div>

            {/* Date de résolution souhaitée */}
            <div>
              <label
                htmlFor="date_resolution_souhaitee"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Date de résolution souhaitée
              </label>
              <input
                type="date"
                id="date_resolution_souhaitee"
                name="date_resolution_souhaitee"
                value={formData.date_resolution_souhaitee}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Localisation */}
            <div>
              <label htmlFor="localisation" className="block text-sm font-medium text-gray-700 mb-1">
                Localisation
              </label>
              <input
                type="text"
                id="localisation"
                name="localisation"
                value={formData.localisation}
                onChange={handleChange}
                maxLength={100}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ex: Étage 2, Salle B..."
              />
            </div>

            {/* URL Photo */}
            <div>
              <label htmlFor="photo_url" className="block text-sm font-medium text-gray-700 mb-1">
                URL de la photo
              </label>
              <input
                type="url"
                id="photo_url"
                name="photo_url"
                value={formData.photo_url}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="https://..."
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Enregistrement...' : isEdit ? 'Modifier' : 'Créer'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignalementModal;
