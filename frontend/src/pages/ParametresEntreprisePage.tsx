/**
 * Page Parametres Entreprise - Configuration financiere.
 * Accessible uniquement aux administrateurs.
 * Permet de modifier les coefficients financiers de l'entreprise.
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import api from '../services/api';
import type { ApiError } from '../types/api';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

interface ConfigurationEntreprise {
  id: number;
  couts_fixes_annuels: string;
  annee: number;
  coeff_frais_generaux: string;
  coeff_charges_patronales: string;
  coeff_heures_sup: string;
  coeff_heures_sup_2: string;
  notes: string | null;
  updated_at: string | null;
  updated_by: number | null;
  is_default?: boolean;
  stale_warning?: string | null;
}

interface ConfigurationUpdateResponse extends ConfigurationEntreprise {
  created?: boolean;
  warnings?: string[];
}

const CURRENT_YEAR = new Date().getFullYear();

export function ParametresEntreprisePage(): JSX.Element {
  useDocumentTitle('Paramètres entreprise');
  const { user } = useAuth();
  const { showToast } = useToast();
  const isAdmin = user?.role === 'admin';

  const [config, setConfig] = useState<ConfigurationEntreprise | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Champs du formulaire
  const [coutsFixesAnnuels, setCoutsFixesAnnuels] = useState('');
  const [coeffFraisGeneraux, setCoeffFraisGeneraux] = useState('');
  const [coeffChargesPatronales, setCoeffChargesPatronales] = useState('');
  const [coeffHeuresSup, setCoeffHeuresSup] = useState('');
  const [coeffHeuresSup2, setCoeffHeuresSup2] = useState('');
  const [notes, setNotes] = useState('');

  const loadConfig = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.get<ConfigurationEntreprise>(
        `/api/financier/configuration/${CURRENT_YEAR}`
      );
      const data = response.data;
      setConfig(data);
      setCoutsFixesAnnuels(data.couts_fixes_annuels);
      setCoeffFraisGeneraux(data.coeff_frais_generaux);
      setCoeffChargesPatronales(data.coeff_charges_patronales);
      setCoeffHeuresSup(data.coeff_heures_sup);
      setCoeffHeuresSup2(data.coeff_heures_sup_2);
      setNotes(data.notes || '');
      if (data.is_default) {
        showToast(
          `Aucune configuration enregistree pour ${CURRENT_YEAR}. Valeurs par defaut affichees.`,
          'info'
        );
      }
    } catch {
      showToast('Erreur lors du chargement de la configuration', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    if (isAdmin) {
      loadConfig();
    }
  }, [isAdmin, loadConfig]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isAdmin) return;

    setIsSaving(true);
    try {
      const response = await api.put<ConfigurationUpdateResponse>(
        `/api/financier/configuration/${CURRENT_YEAR}`,
        {
          couts_fixes_annuels: parseFloat(coutsFixesAnnuels),
          coeff_frais_generaux: parseFloat(coeffFraisGeneraux),
          coeff_charges_patronales: parseFloat(coeffChargesPatronales),
          coeff_heures_sup: parseFloat(coeffHeuresSup),
          coeff_heures_sup_2: parseFloat(coeffHeuresSup2),
          notes: notes || null,
        }
      );
      setConfig(response.data);
      // EDGE-001: notifier si creation d'une nouvelle config
      if (response.data.created) {
        showToast(`Configuration creee pour l'annee ${CURRENT_YEAR}`, 'success');
      } else {
        showToast('Configuration sauvegardee avec succes', 'success');
      }
      // VAL-002 + EDGE-002: afficher les warnings
      if (response.data.warnings && response.data.warnings.length > 0) {
        for (const w of response.data.warnings) {
          showToast(w, 'warning');
        }
      }
    } catch (err) {
      const error = err as ApiError;
      if (error.response?.status === 422) {
        showToast(
          error.response?.data?.detail || 'Valeurs invalides',
          'error'
        );
      } else if (error.response?.status === 403) {
        showToast('Acces reserve aux administrateurs', 'error');
      } else {
        showToast('Erreur lors de la sauvegarde', 'error');
      }
    } finally {
      setIsSaving(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-sm text-red-800">
            Cette page est reservee aux administrateurs.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="md:grid md:grid-cols-3 md:gap-6">
        <div className="md:col-span-1">
          <div className="px-4 sm:px-0">
            <h3 className="text-lg font-medium leading-6 text-gray-900">
              Parametres entreprise
            </h3>
            <p className="mt-1 text-sm text-gray-600">
              Configuration des coefficients financiers de Greg Construction.
              Ces valeurs impactent tous les calculs de marge, frais generaux
              et couts de main-d'oeuvre.
            </p>
            <div className="mt-4 bg-blue-50 border border-blue-200 rounded-md p-3">
              <p className="text-xs text-blue-800">
                Ces coefficients sont la source unique de verite pour tous les
                calculs financiers (dashboard, P&amp;L, bilan, devis, cout MO)
                de l'annee {CURRENT_YEAR}.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-5 md:mt-0 md:col-span-2">
          <form onSubmit={handleSave}>
            <div className="shadow sm:rounded-md sm:overflow-hidden">
              {/* Alerte revalidation 180 jours */}
              {config?.stale_warning && (
                <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-3">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 6a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 6zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-yellow-800">{config.stale_warning}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Couts fixes */}
              <div className="bg-white px-4 py-5 sm:p-6">
                <h4 className="text-base font-medium text-gray-900 mb-4">
                  Couts fixes annuels
                </h4>
                <div>
                  <label
                    htmlFor="coutsFixesAnnuels"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Montant annuel (EUR HT)
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <input
                      type="number"
                      id="coutsFixesAnnuels"
                      min="0"
                      step="0.01"
                      required
                      value={coutsFixesAnnuels}
                      onChange={(e) => setCoutsFixesAnnuels(e.target.value)}
                      className="block w-full pr-12 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                      <span className="text-gray-500 sm:text-sm">EUR</span>
                    </div>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    Frais generaux hors salaires : loyer, assurances,
                    vehicules, comptabilite, etc.
                  </p>
                </div>
              </div>

              {/* Coefficient frais generaux */}
              <div className="bg-gray-50 px-4 py-5 sm:p-6 border-t border-gray-200">
                <h4 className="text-base font-medium text-gray-900 mb-4">
                  Coefficient de frais generaux
                </h4>
                <div>
                  <label
                    htmlFor="coeffFG"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Pourcentage du debourse sec
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <input
                      type="number"
                      id="coeffFG"
                      min="0"
                      max="100"
                      step="0.01"
                      required
                      value={coeffFraisGeneraux}
                      onChange={(e) => setCoeffFraisGeneraux(e.target.value)}
                      className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                      <span className="text-gray-500 sm:text-sm">%</span>
                    </div>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    Applique sur le debourse sec (achats + MO + materiel) pour
                    calculer la quote-part frais generaux. Actuellement ~19%
                    (600k EUR / 3.16M EUR).
                  </p>
                </div>
              </div>

              {/* Charges patronales */}
              <div className="bg-white px-4 py-5 sm:p-6 border-t border-gray-200">
                <h4 className="text-base font-medium text-gray-900 mb-4">
                  Charges patronales
                </h4>
                <div>
                  <label
                    htmlFor="coeffCP"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Coefficient multiplicateur (brut &rarr; cout employeur)
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <input
                      type="number"
                      id="coeffCP"
                      min="1"
                      step="0.01"
                      required
                      value={coeffChargesPatronales}
                      onChange={(e) =>
                        setCoeffChargesPatronales(e.target.value)
                      }
                      className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                      <span className="text-gray-500 sm:text-sm">x</span>
                    </div>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    1.45 = 45% de charges patronales BTP (URSSAF, PROBTP,
                    prevoyance, conges payes caisse BTP).
                  </p>
                </div>
              </div>

              {/* Heures supplementaires */}
              <div className="bg-gray-50 px-4 py-5 sm:p-6 border-t border-gray-200">
                <h4 className="text-base font-medium text-gray-900 mb-4">
                  Heures supplementaires
                </h4>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label
                      htmlFor="coeffHS1"
                      className="block text-sm font-medium text-gray-700"
                    >
                      1er palier (36e-43e heure) <span className="text-red-500">*</span>
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <input
                        type="number"
                        id="coeffHS1"
                        min="1"
                        step="0.01"
                        required
                        aria-required="true"
                        value={coeffHeuresSup}
                        onChange={(e) => setCoeffHeuresSup(e.target.value)}
                        className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">x</span>
                      </div>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      Code du travail art. L3121-36 : +25% soit x1.25
                    </p>
                  </div>
                  <div>
                    <label
                      htmlFor="coeffHS2"
                      className="block text-sm font-medium text-gray-700"
                    >
                      2e palier (au-dela de 43h) <span className="text-red-500">*</span>
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <input
                        type="number"
                        id="coeffHS2"
                        min="1"
                        step="0.01"
                        required
                        aria-required="true"
                        value={coeffHeuresSup2}
                        onChange={(e) => setCoeffHeuresSup2(e.target.value)}
                        className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">x</span>
                      </div>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      Code du travail art. L3121-36 : +50% soit x1.50
                    </p>
                  </div>
                </div>
              </div>

              {/* Notes */}
              <div className="bg-white px-4 py-5 sm:p-6 border-t border-gray-200">
                <div>
                  <label
                    htmlFor="notes"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Notes
                  </label>
                  <div className="mt-1">
                    <textarea
                      id="notes"
                      rows={3}
                      maxLength={1000}
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      placeholder="Notes internes sur la configuration..."
                    />
                  </div>
                </div>
              </div>

              {/* Derniere modification */}
              {config?.updated_at && (
                <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    Derniere modification :{' '}
                    {new Date(config.updated_at).toLocaleDateString('fr-FR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              )}

              {/* Bouton */}
              <div className="bg-gray-50 px-4 py-3 text-right sm:px-6 border-t border-gray-200">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSaving ? 'Sauvegarde...' : 'Sauvegarder'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ParametresEntreprisePage;
