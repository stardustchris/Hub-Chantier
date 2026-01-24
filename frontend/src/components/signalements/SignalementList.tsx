/**
 * Composant SignalementList - Liste des signalements d'un chantier (SIG-03)
 */

import React, { useState, useEffect, useCallback } from 'react';
import type { Signalement, Priorite, StatutSignalement } from '../../types/signalements';
import { listSignalementsByChantier, searchSignalements } from '../../services/signalements';
import SignalementCard from './SignalementCard';
import SignalementFilters from './SignalementFilters';

interface SignalementListProps {
  chantierId?: number;
  onSignalementClick?: (signalement: Signalement) => void;
  onTraiter?: (signalement: Signalement) => void;
  onCloturer?: (signalement: Signalement) => void;
  showFilters?: boolean;
  compact?: boolean;
  limit?: number;
  showGlobalView?: boolean;
}

const SignalementList: React.FC<SignalementListProps> = ({
  chantierId,
  onSignalementClick,
  onTraiter,
  onCloturer,
  showFilters = true,
  compact = false,
  limit = 100,
  showGlobalView = false,
}) => {
  const [signalements, setSignalements] = useState<Signalement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);

  // Filtres
  const [statut, setStatut] = useState<StatutSignalement | ''>('');
  const [priorite, setPriorite] = useState<Priorite | ''>('');
  const [query, setQuery] = useState('');
  const [enRetardOnly, setEnRetardOnly] = useState(false);

  const loadSignalements = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      let response;

      if (showGlobalView || !chantierId) {
        // Vue globale avec filtres avancés
        response = await searchSignalements({
          query: query || undefined,
          chantier_id: chantierId,
          statut: statut || undefined,
          priorite: priorite || undefined,
          en_retard_only: enRetardOnly,
          skip,
          limit,
        });
      } else {
        // Vue par chantier
        response = await listSignalementsByChantier(
          chantierId,
          skip,
          limit,
          statut || undefined,
          priorite || undefined
        );
      }

      setSignalements(response.signalements);
      setTotal(response.total);
    } catch (err) {
      console.error('Erreur lors du chargement des signalements:', err);
      setError('Impossible de charger les signalements');
    } finally {
      setLoading(false);
    }
  }, [chantierId, showGlobalView, query, statut, priorite, enRetardOnly, skip, limit]);

  useEffect(() => {
    loadSignalements();
  }, [loadSignalements]);

  const handleFilterChange = (filters: {
    statut?: StatutSignalement | '';
    priorite?: Priorite | '';
    query?: string;
    enRetardOnly?: boolean;
  }) => {
    if (filters.statut !== undefined) setStatut(filters.statut);
    if (filters.priorite !== undefined) setPriorite(filters.priorite);
    if (filters.query !== undefined) setQuery(filters.query);
    if (filters.enRetardOnly !== undefined) setEnRetardOnly(filters.enRetardOnly);
    setSkip(0);
  };

  const handlePageChange = (newSkip: number) => {
    setSkip(newSkip);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-500">
        <p>{error}</p>
        <button
          onClick={loadSignalements}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Réessayer
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Filtres */}
      {showFilters && (
        <SignalementFilters
          statut={statut}
          priorite={priorite}
          query={query}
          enRetardOnly={enRetardOnly}
          onFilterChange={handleFilterChange}
          showSearchBar={showGlobalView}
        />
      )}

      {/* Liste */}
      {signalements.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <span className="text-4xl mb-4 block">📋</span>
          <p>Aucun signalement</p>
          {(statut || priorite || query || enRetardOnly) && (
            <p className="text-sm mt-2">Essayez de modifier vos filtres</p>
          )}
        </div>
      ) : (
        <>
          <div className={compact ? 'space-y-2' : 'grid gap-4 md:grid-cols-2 lg:grid-cols-3'}>
            {signalements.map((signalement) => (
              <SignalementCard
                key={signalement.id}
                signalement={signalement}
                onClick={onSignalementClick}
                onTraiter={onTraiter}
                onCloturer={onCloturer}
                compact={compact}
              />
            ))}
          </div>

          {/* Pagination */}
          {total > limit && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t">
              <span className="text-sm text-gray-600">
                {skip + 1} - {Math.min(skip + limit, total)} sur {total}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => handlePageChange(Math.max(0, skip - limit))}
                  disabled={skip === 0}
                  className="px-3 py-1 text-sm border rounded disabled:opacity-50 hover:bg-gray-50"
                >
                  Précédent
                </button>
                <button
                  onClick={() => handlePageChange(skip + limit)}
                  disabled={skip + limit >= total}
                  className="px-3 py-1 text-sm border rounded disabled:opacity-50 hover:bg-gray-50"
                >
                  Suivant
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SignalementList;
