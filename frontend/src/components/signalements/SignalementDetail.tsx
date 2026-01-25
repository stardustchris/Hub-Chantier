/**
 * Composant SignalementDetail - Vue détaillée d'un signalement avec réponses
 */

import React, { useState, useEffect, useCallback } from 'react';
import type {
  Signalement,
  Reponse,
  ReponseCreateDTO,
} from '../../types/signalements';
import {
  PRIORITE_BG_COLORS,
  STATUT_BG_COLORS,
} from '../../types/signalements';
import {
  getSignalement,
  listReponses,
  createReponse,
  marquerTraite,
  cloturerSignalement,
  reouvrirSignalement,
  getPrioriteIcon,
  getStatutIcon,
} from '../../services/signalements';
import { formatDateDayMonthYearTime } from '../../utils/dates';
import TraiterModal from './TraiterModal';
import ReponsesSection from './ReponsesSection';

interface SignalementDetailProps {
  signalementId: number;
  onClose?: () => void;
  onUpdate?: (signalement: Signalement) => void;
  onEdit?: (signalement: Signalement) => void;
  canEdit?: boolean;
  canTraiter?: boolean;
  canCloturer?: boolean;
}

const SignalementDetail: React.FC<SignalementDetailProps> = ({
  signalementId,
  onClose,
  onUpdate,
  onEdit,
  canEdit = true,
  canTraiter = true,
  canCloturer = true,
}) => {
  const [signalement, setSignalement] = useState<Signalement | null>(null);
  const [reponses, setReponses] = useState<Reponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTraiterModal, setShowTraiterModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [signalementData, reponsesData] = await Promise.all([
        getSignalement(signalementId),
        listReponses(signalementId),
      ]);
      setSignalement(signalementData);
      setReponses(reponsesData.reponses);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement');
    } finally {
      setLoading(false);
    }
  }, [signalementId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAddReponse = async (contenu: string) => {
    if (!signalement) return;

    try {
      const data: ReponseCreateDTO = { contenu };
      const reponse = await createReponse(signalement.id, data);
      setReponses((prev) => [...prev, reponse]);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'envoi');
    }
  };

  const handleTraiter = async (commentaire: string) => {
    if (!signalement) return;

    setActionLoading(true);
    try {
      const updated = await marquerTraite(signalement.id, commentaire);
      setSignalement(updated);
      setShowTraiterModal(false);
      onUpdate?.(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du traitement');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCloturer = async () => {
    if (!signalement) return;

    setActionLoading(true);
    try {
      const updated = await cloturerSignalement(signalement.id);
      setSignalement(updated);
      onUpdate?.(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la clôture');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReouvrir = async () => {
    if (!signalement) return;

    setActionLoading(true);
    try {
      const updated = await reouvrirSignalement(signalement.id);
      setSignalement(updated);
      onUpdate?.(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la réouverture');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Chargement...</div>
      </div>
    );
  }

  if (error && !signalement) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded text-red-700">
        {error}
      </div>
    );
  }

  if (!signalement) return null;

  const prioriteClass = PRIORITE_BG_COLORS[signalement.priorite] || 'bg-gray-100 text-gray-800';
  const statutClass = STATUT_BG_COLORS[signalement.statut] || 'bg-gray-100 text-gray-800';

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-3xl mx-auto">
      {/* En-tête */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">{getPrioriteIcon(signalement.priorite)}</span>
              <h2 className="text-xl font-semibold text-gray-900">{signalement.titre}</h2>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${prioriteClass}`}>
                {signalement.priorite_label}
              </span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${statutClass}`}>
                {getStatutIcon(signalement.statut)} {signalement.statut_label}
              </span>
              {signalement.est_en_retard && (
                <span className="px-2 py-1 text-xs font-bold text-white bg-red-500 rounded">
                  EN RETARD
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {canEdit && signalement.statut !== 'cloture' && (
              <button
                onClick={() => onEdit?.(signalement)}
                className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
              >
                Modifier
              </button>
            )}
            {onClose && (
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-xl"
                aria-label="Fermer"
              >
                ✕
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Contenu principal */}
      <div className="p-6">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Description */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Description</h3>
          <p className="text-gray-600 whitespace-pre-wrap">{signalement.description}</p>
        </div>

        {/* Photo */}
        {signalement.photo_url && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Photo</h3>
            <img
              src={signalement.photo_url}
              alt="Photo du signalement"
              className="max-w-full h-auto rounded-lg border border-gray-200"
            />
          </div>
        )}

        {/* Métadonnées */}
        <div className="mb-6 grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Créé par:</span>{' '}
            <span className="text-gray-900">{signalement.cree_par_nom || `#${signalement.cree_par}`}</span>
          </div>
          <div>
            <span className="text-gray-500">Assigné à:</span>{' '}
            <span className="text-gray-900">
              {signalement.assigne_a_nom || (signalement.assigne_a ? `#${signalement.assigne_a}` : 'Non assigné')}
            </span>
          </div>
          {signalement.localisation && (
            <div>
              <span className="text-gray-500">Localisation:</span>{' '}
              <span className="text-gray-900">{signalement.localisation}</span>
            </div>
          )}
          <div>
            <span className="text-gray-500">Créé le:</span>{' '}
            <span className="text-gray-900">{formatDateDayMonthYearTime(signalement.created_at)}</span>
          </div>
          {signalement.date_traitement && (
            <div>
              <span className="text-gray-500">Traité le:</span>{' '}
              <span className="text-gray-900">{formatDateDayMonthYearTime(signalement.date_traitement)}</span>
            </div>
          )}
          {signalement.date_cloture && (
            <div>
              <span className="text-gray-500">Clôturé le:</span>{' '}
              <span className="text-gray-900">{formatDateDayMonthYearTime(signalement.date_cloture)}</span>
            </div>
          )}
        </div>

        {/* Commentaire de traitement */}
        {signalement.commentaire_traitement && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
            <h3 className="text-sm font-medium text-blue-800 mb-1">Commentaire de traitement</h3>
            <p className="text-blue-900">{signalement.commentaire_traitement}</p>
          </div>
        )}

        {/* Temps restant */}
        {signalement.statut !== 'cloture' && (
          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Temps écoulé: {signalement.pourcentage_temps.toFixed(0)}%</span>
              <span>{signalement.temps_restant || 'Délai dépassé'}</span>
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  signalement.pourcentage_temps >= 100
                    ? 'bg-red-500'
                    : signalement.pourcentage_temps >= 50
                    ? 'bg-orange-500'
                    : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(signalement.pourcentage_temps, 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mb-6 flex flex-wrap gap-2">
          {canTraiter && (signalement.statut === 'ouvert' || signalement.statut === 'en_cours') && (
            <button
              onClick={() => setShowTraiterModal(true)}
              disabled={actionLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Marquer comme traité
            </button>
          )}
          {canCloturer && signalement.statut === 'traite' && (
            <button
              onClick={handleCloturer}
              disabled={actionLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded hover:bg-green-700 disabled:opacity-50"
            >
              Clôturer
            </button>
          )}
          {signalement.statut === 'cloture' && (
            <button
              onClick={handleReouvrir}
              disabled={actionLoading}
              className="px-4 py-2 text-sm font-medium text-orange-600 bg-orange-100 rounded hover:bg-orange-200 disabled:opacity-50"
            >
              Réouvrir
            </button>
          )}
        </div>

        {/* Réponses */}
        <ReponsesSection
          reponses={reponses}
          canReply={signalement.statut !== 'cloture'}
          onAddReponse={handleAddReponse}
        />
      </div>

      {/* Modal traitement */}
      <TraiterModal
        isOpen={showTraiterModal}
        onClose={() => setShowTraiterModal(false)}
        onConfirm={handleTraiter}
        isLoading={actionLoading}
      />
    </div>
  );
};

export default SignalementDetail;
