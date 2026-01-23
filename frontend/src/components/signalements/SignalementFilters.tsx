/**
 * Composant SignalementFilters - Filtres pour la liste des signalements (SIG-19, SIG-20)
 */

import React from 'react';
import type { Priorite, StatutSignalement } from '../../types/signalements';
import { PRIORITE_OPTIONS, STATUT_OPTIONS } from '../../types/signalements';

interface SignalementFiltersProps {
  statut: StatutSignalement | '';
  priorite: Priorite | '';
  query: string;
  enRetardOnly: boolean;
  onFilterChange: (filters: {
    statut?: StatutSignalement | '';
    priorite?: Priorite | '';
    query?: string;
    enRetardOnly?: boolean;
  }) => void;
  showSearchBar?: boolean;
}

const SignalementFilters: React.FC<SignalementFiltersProps> = ({
  statut,
  priorite,
  query,
  enRetardOnly,
  onFilterChange,
  showSearchBar = false,
}) => {
  return (
    <div className="mb-6 space-y-4">
      {/* Barre de recherche (vue globale) */}
      {showSearchBar && (
        <div className="relative">
          <input
            type="text"
            placeholder="Rechercher par titre, description, localisation..."
            value={query}
            onChange={(e) => onFilterChange({ query: e.target.value })}
            className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="absolute left-3 top-2.5 text-gray-400">🔍</span>
        </div>
      )}

      {/* Filtres en ligne */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Filtre par statut */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-600">Statut:</label>
          <select
            value={statut}
            onChange={(e) => onFilterChange({ statut: e.target.value as StatutSignalement | '' })}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tous</option>
            {STATUT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Filtre par priorité */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-600">Priorité:</label>
          <select
            value={priorite}
            onChange={(e) => onFilterChange({ priorite: e.target.value as Priorite | '' })}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Toutes</option>
            {PRIORITE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Filtre en retard */}
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={enRetardOnly}
            onChange={(e) => onFilterChange({ enRetardOnly: e.target.checked })}
            className="h-4 w-4 text-red-600 rounded border-gray-300 focus:ring-red-500"
          />
          <span className="text-sm font-medium text-red-600">En retard uniquement</span>
        </label>

        {/* Bouton de réinitialisation */}
        {(statut || priorite || query || enRetardOnly) && (
          <button
            onClick={() =>
              onFilterChange({ statut: '', priorite: '', query: '', enRetardOnly: false })
            }
            className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
          >
            ✕ Réinitialiser
          </button>
        )}
      </div>

      {/* Raccourcis rapides */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onFilterChange({ statut: 'ouvert', priorite: '', enRetardOnly: false })}
          className={`px-3 py-1 text-xs rounded-full border ${
            statut === 'ouvert' && !enRetardOnly
              ? 'bg-red-100 border-red-300 text-red-800'
              : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
          }`}
        >
          ⚠️ Ouverts
        </button>
        <button
          onClick={() => onFilterChange({ statut: 'en_cours', priorite: '', enRetardOnly: false })}
          className={`px-3 py-1 text-xs rounded-full border ${
            statut === 'en_cours' && !enRetardOnly
              ? 'bg-orange-100 border-orange-300 text-orange-800'
              : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
          }`}
        >
          🔄 En cours
        </button>
        <button
          onClick={() => onFilterChange({ statut: '', priorite: 'critique', enRetardOnly: false })}
          className={`px-3 py-1 text-xs rounded-full border ${
            priorite === 'critique' && !enRetardOnly
              ? 'bg-red-100 border-red-300 text-red-800'
              : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
          }`}
        >
          🔴 Critiques
        </button>
        <button
          onClick={() => onFilterChange({ statut: '', priorite: '', enRetardOnly: true })}
          className={`px-3 py-1 text-xs rounded-full border ${
            enRetardOnly
              ? 'bg-red-500 border-red-600 text-white'
              : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
          }`}
        >
          🚨 En retard
        </button>
      </div>
    </div>
  );
};

export default SignalementFilters;
