/**
 * Composant SignalementStats - Tableau de bord des statistiques (SIG-18)
 */

import React, { useState, useEffect, useCallback } from 'react';
import type { SignalementStatsResponse } from '../../types/signalements';
import {
  PRIORITE_LABELS,
  PRIORITE_BG_COLORS,
  STATUT_LABELS,
  STATUT_BG_COLORS,
} from '../../types/signalements';
import { getStatistiques } from '../../api/signalements';

interface SignalementStatsProps {
  chantierId?: number;
  dateDebut?: string;
  dateFin?: string;
  refreshTrigger?: number;
}

interface StatCardProps {
  label: string;
  value: string | number;
  icon: string;
  color: string;
  subtext?: string;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon, color, subtext }) => (
  <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 ${color}`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
      </div>
      <span className="text-3xl">{icon}</span>
    </div>
  </div>
);

const SignalementStats: React.FC<SignalementStatsProps> = ({
  chantierId,
  dateDebut,
  dateFin,
  refreshTrigger,
}) => {
  const [stats, setStats] = useState<SignalementStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getStatistiques(chantierId, dateDebut, dateFin);
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement');
    } finally {
      setLoading(false);
    }
  }, [chantierId, dateDebut, dateFin]);

  useEffect(() => {
    loadStats();
  }, [loadStats, refreshTrigger]);

  const formatDuration = (hours: number | null): string => {
    if (hours === null) return '-';
    if (hours < 1) return `${Math.round(hours * 60)} min`;
    if (hours < 24) return `${hours.toFixed(1)}h`;
    const days = Math.floor(hours / 24);
    const remainingHours = Math.round(hours % 24);
    return `${days}j ${remainingHours}h`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Chargement des statistiques...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded text-red-700">
        {error}
        <button
          onClick={loadStats}
          className="ml-2 text-red-600 underline hover:no-underline"
        >
          Réessayer
        </button>
      </div>
    );
  }

  if (!stats) return null;

  const prioriteKeys = Object.keys(PRIORITE_LABELS) as Array<keyof typeof PRIORITE_LABELS>;
  const statutKeys = Object.keys(STATUT_LABELS) as Array<keyof typeof STATUT_LABELS>;

  return (
    <div className="space-y-6">
      {/* Indicateurs principaux */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total signalements"
          value={stats.total}
          icon="📋"
          color=""
        />
        <StatCard
          label="En retard"
          value={stats.en_retard}
          icon="⚠️"
          color={stats.en_retard > 0 ? 'border-l-4 border-l-red-500' : ''}
        />
        <StatCard
          label="Traités cette semaine"
          value={stats.traites_cette_semaine}
          icon="✅"
          color="border-l-4 border-l-green-500"
        />
        <StatCard
          label="Taux de résolution"
          value={`${stats.taux_resolution.toFixed(0)}%`}
          icon="📈"
          color="border-l-4 border-l-blue-500"
          subtext={`Temps moyen: ${formatDuration(stats.temps_moyen_resolution)}`}
        />
      </div>

      {/* Répartition par statut et priorité */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Par statut */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Par statut</h3>
          <div className="space-y-3">
            {statutKeys.map((statut) => {
              const count = stats.par_statut[statut] || 0;
              const percentage = stats.total > 0 ? (count / stats.total) * 100 : 0;
              const bgClass = STATUT_BG_COLORS[statut] || 'bg-gray-100 text-gray-800';

              return (
                <div key={statut} className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${bgClass} min-w-20 text-center`}>
                    {STATUT_LABELS[statut]}
                  </span>
                  <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        statut === 'cloture'
                          ? 'bg-green-500'
                          : statut === 'traite'
                          ? 'bg-blue-500'
                          : statut === 'en_cours'
                          ? 'bg-orange-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-700 min-w-12 text-right">
                    {count}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Par priorité */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Par priorité</h3>
          <div className="space-y-3">
            {prioriteKeys.map((priorite) => {
              const count = stats.par_priorite[priorite] || 0;
              const percentage = stats.total > 0 ? (count / stats.total) * 100 : 0;
              const bgClass = PRIORITE_BG_COLORS[priorite] || 'bg-gray-100 text-gray-800';

              return (
                <div key={priorite} className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${bgClass} min-w-28 text-center`}>
                    {PRIORITE_LABELS[priorite]}
                  </span>
                  <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        priorite === 'critique'
                          ? 'bg-red-500'
                          : priorite === 'haute'
                          ? 'bg-orange-500'
                          : priorite === 'moyenne'
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-700 min-w-12 text-right">
                    {count}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Alertes */}
      {stats.en_retard > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🚨</span>
            <div>
              <h4 className="font-semibold text-red-800">
                {stats.en_retard} signalement{stats.en_retard > 1 ? 's' : ''} en retard
              </h4>
              <p className="text-sm text-red-600">
                Ces signalements ont dépassé leur délai de résolution et nécessitent une attention immédiate.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Performance résumé */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Résumé performance</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Ouverts:</span>{' '}
            <span className="font-medium">{stats.par_statut['ouvert'] || 0}</span>
          </div>
          <div>
            <span className="text-gray-500">En cours:</span>{' '}
            <span className="font-medium">{stats.par_statut['en_cours'] || 0}</span>
          </div>
          <div>
            <span className="text-gray-500">Traités:</span>{' '}
            <span className="font-medium">{stats.par_statut['traite'] || 0}</span>
          </div>
          <div>
            <span className="text-gray-500">Clôturés:</span>{' '}
            <span className="font-medium">{stats.par_statut['cloture'] || 0}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignalementStats;
