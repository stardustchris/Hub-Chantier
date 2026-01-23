/**
 * Composant SignalementCard - Carte individuelle pour un signalement
 */

import React from 'react';
import type { Signalement } from '../../types/signalements';
import { PRIORITE_BG_COLORS, STATUT_BG_COLORS } from '../../types/signalements';
import { getPrioriteIcon, getStatutIcon } from '../../api/signalements';

interface SignalementCardProps {
  signalement: Signalement;
  onClick?: (signalement: Signalement) => void;
  onTraiter?: (signalement: Signalement) => void;
  onCloturer?: (signalement: Signalement) => void;
  compact?: boolean;
}

const SignalementCard: React.FC<SignalementCardProps> = ({
  signalement,
  onClick,
  onTraiter,
  onCloturer,
  compact = false,
}) => {
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

  const prioriteClass = PRIORITE_BG_COLORS[signalement.priorite] || 'bg-gray-100 text-gray-800';
  const statutClass = STATUT_BG_COLORS[signalement.statut] || 'bg-gray-100 text-gray-800';

  if (compact) {
    return (
      <div
        className={`p-3 border rounded-lg cursor-pointer hover:bg-gray-50 ${
          signalement.est_en_retard ? 'border-red-300 bg-red-50' : 'border-gray-200'
        }`}
        onClick={() => onClick?.(signalement)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>{getPrioriteIcon(signalement.priorite)}</span>
            <span className="font-medium text-sm truncate max-w-xs">{signalement.titre}</span>
          </div>
          <span className={`px-2 py-0.5 text-xs rounded-full ${statutClass}`}>
            {signalement.statut_label}
          </span>
        </div>
        {signalement.est_en_retard && (
          <div className="text-xs text-red-600 mt-1">En retard</div>
        )}
      </div>
    );
  }

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border p-4 cursor-pointer hover:shadow-md transition-shadow ${
        signalement.est_en_retard ? 'border-red-300' : 'border-gray-200'
      }`}
      onClick={() => onClick?.(signalement)}
    >
      {/* En-tête */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xl">{getPrioriteIcon(signalement.priorite)}</span>
            <h3 className="font-semibold text-gray-900">{signalement.titre}</h3>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${prioriteClass}`}>
              {signalement.priorite_label}
            </span>
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${statutClass}`}>
              {getStatutIcon(signalement.statut)} {signalement.statut_label}
            </span>
          </div>
        </div>
        {signalement.est_en_retard && (
          <span className="px-2 py-1 text-xs font-bold text-white bg-red-500 rounded">
            EN RETARD
          </span>
        )}
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-3 line-clamp-2">{signalement.description}</p>

      {/* Métadonnées */}
      <div className="grid grid-cols-2 gap-2 text-xs text-gray-500 mb-3">
        <div>
          <span className="font-medium">Créé par:</span> {signalement.cree_par_nom || `#${signalement.cree_par}`}
        </div>
        <div>
          <span className="font-medium">Assigné à:</span>{' '}
          {signalement.assigne_a_nom || (signalement.assigne_a ? `#${signalement.assigne_a}` : 'Non assigné')}
        </div>
        {signalement.localisation && (
          <div>
            <span className="font-medium">Localisation:</span> {signalement.localisation}
          </div>
        )}
        <div>
          <span className="font-medium">Créé le:</span> {formatDate(signalement.created_at)}
        </div>
      </div>

      {/* Temps restant et progression */}
      {signalement.statut !== 'cloture' && (
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Temps écoulé: {signalement.pourcentage_temps.toFixed(0)}%</span>
            <span>{signalement.temps_restant || 'Délai dépassé'}</span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
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

      {/* Compteurs et actions */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span>💬 {signalement.nb_reponses} réponse{signalement.nb_reponses > 1 ? 's' : ''}</span>
          {signalement.nb_escalades > 0 && (
            <span className="text-orange-600">🔔 {signalement.nb_escalades} escalade{signalement.nb_escalades > 1 ? 's' : ''}</span>
          )}
        </div>
        <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
          {signalement.statut === 'ouvert' || signalement.statut === 'en_cours' ? (
            <button
              onClick={() => onTraiter?.(signalement)}
              className="px-3 py-1 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded"
            >
              Traiter
            </button>
          ) : null}
          {signalement.statut === 'traite' && (
            <button
              onClick={() => onCloturer?.(signalement)}
              className="px-3 py-1 text-xs font-medium text-green-600 hover:bg-green-50 rounded"
            >
              Clôturer
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default SignalementCard;
