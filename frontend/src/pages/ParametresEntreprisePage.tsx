/**
 * Page Parametres Entreprise - Configuration financiere.
 * Accessible uniquement aux administrateurs.
 * Permet de modifier les coefficients financiers de l'entreprise.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { useParametresEntreprise } from '../hooks/useParametresEntreprise';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import Layout from '../components/Layout';
import { Breadcrumb } from '../components/ui/Breadcrumb';

export function ParametresEntreprisePage(): React.ReactElement {
  useDocumentTitle('Paramètres entreprise');
  const { user } = useAuth();
  const { addToast } = useToast();
  const isAdmin = user?.role === 'admin';

  const {
    config,
    isLoading,
    isSaving,
    currentYear: CURRENT_YEAR,
    saveConfig,
  } = useParametresEntreprise();

  // Champs du formulaire
  const [coutsFixesAnnuels, setCoutsFixesAnnuels] = useState('');
  const [coeffFraisGeneraux, setCoeffFraisGeneraux] = useState('');
  const [coeffChargesPatronales, setCoeffChargesPatronales] = useState('');
  const [coeffHeuresSup, setCoeffHeuresSup] = useState('');
  const [coeffHeuresSup2, setCoeffHeuresSup2] = useState('');
  const [coeffProductivite, setCoeffProductivite] = useState('');
  const [coeffChargesOuvrier, setCoeffChargesOuvrier] = useState('');
  const [coeffChargesEtam, setCoeffChargesEtam] = useState('');
  const [coeffChargesCadre, setCoeffChargesCadre] = useState('');
  const [seuilAlerteBudget, setSeuilAlerteBudget] = useState('');
  const [seuilAlerteBudgetCritique, setSeuilAlerteBudgetCritique] = useState('');
  const [notes, setNotes] = useState('');

  // Synchroniser les champs du formulaire quand la config est chargee
  useEffect(() => {
    if (config) {
      setCoutsFixesAnnuels(config.couts_fixes_annuels);
      setCoeffFraisGeneraux(config.coeff_frais_generaux);
      setCoeffChargesPatronales(config.coeff_charges_patronales);
      setCoeffHeuresSup(config.coeff_heures_sup);
      setCoeffHeuresSup2(config.coeff_heures_sup_2);
      setCoeffProductivite(config.coeff_productivite);
      setCoeffChargesOuvrier(config.coeff_charges_ouvrier || '');
      setCoeffChargesEtam(config.coeff_charges_etam || '');
      setCoeffChargesCadre(config.coeff_charges_cadre || '');
      setSeuilAlerteBudget(config.seuil_alerte_budget_pct);
      setSeuilAlerteBudgetCritique(config.seuil_alerte_budget_critique_pct);
      setNotes(config.notes || '');
      if (config.is_default) {
        addToast({
          message: `Aucune configuration enregistree pour ${CURRENT_YEAR}. Valeurs par defaut affichees.`,
          type: 'info'
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [config]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isAdmin) return;

    const result = await saveConfig({
      coutsFixesAnnuels,
      coeffFraisGeneraux,
      coeffChargesPatronales,
      coeffHeuresSup,
      coeffHeuresSup2,
      coeffProductivite,
      coeffChargesOuvrier,
      coeffChargesEtam,
      coeffChargesCadre,
      seuilAlerteBudget,
      seuilAlerteBudgetCritique,
      notes,
    });

    if (result.success && result.data) {
      // EDGE-001: notifier si creation d'une nouvelle config
      if (result.data.created) {
        addToast({ message: `Configuration creee pour l'annee ${CURRENT_YEAR}`, type: 'success' });
      } else {
        addToast({ message: 'Configuration sauvegardee avec succes', type: 'success' });
      }
      // VAL-002 + EDGE-002: afficher les warnings
      if (result.data.warnings && result.data.warnings.length > 0) {
        for (const w of result.data.warnings) {
          addToast({ message: w, type: 'warning' });
        }
      }
    } else if (result.errorStatus === 422) {
      addToast({
        message: result.errorDetail || 'Valeurs invalides',
        type: 'error'
      });
    } else if (result.errorStatus === 403) {
      addToast({ message: 'Acces reserve aux administrateurs', type: 'error' });
    } else if (!result.success) {
      addToast({ message: 'Erreur lors de la sauvegarde', type: 'error' });
    }
  };

  if (!isAdmin) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-800">
              Cette page est reservee aux administrateurs.
            </p>
          </div>
        </div>
      </Layout>
    );
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Breadcrumb items={[{ label: 'Accueil', href: '/' }, { label: 'Paramètres entreprise' }]} />
      <div className="mt-6 md:grid md:grid-cols-3 md:gap-6">
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

              {/* Coefficient de productivite */}
              <div className="bg-gray-50 px-4 py-5 sm:p-6 border-t border-gray-200">
                <h4 className="text-base font-medium text-gray-900 mb-4">
                  Coefficient de productivite
                </h4>
                <div>
                  <label htmlFor="coeffProd" className="block text-sm font-medium text-gray-700">
                    Multiplicateur sur le cout de main-d'oeuvre
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <input
                      type="number"
                      id="coeffProd"
                      min="0.5"
                      max="2.0"
                      step="0.05"
                      required
                      aria-required="true"
                      value={coeffProductivite}
                      onChange={(e) => setCoeffProductivite(e.target.value)}
                      className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                      <span className="text-gray-500 sm:text-sm">x</span>
                    </div>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    1.0 = productivite normale. &lt; 1.0 = intemperies/difficulte acces. &gt; 1.0 = conditions optimales.
                  </p>
                </div>
              </div>

              {/* Charges patronales par categorie */}
              <div className="bg-white px-4 py-5 sm:p-6 border-t border-gray-200">
                <h4 className="text-base font-medium text-gray-900 mb-4">
                  Charges patronales par categorie
                </h4>
                <p className="text-xs text-gray-500 mb-4">
                  Optionnel. Si non renseigne, le coefficient global ({coeffChargesPatronales}x) s'applique a toutes les categories.
                </p>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <label htmlFor="coeffOuvrier" className="block text-sm font-medium text-gray-700">
                      Ouvrier
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <input
                        type="number"
                        id="coeffOuvrier"
                        min="1"
                        step="0.01"
                        value={coeffChargesOuvrier}
                        onChange={(e) => setCoeffChargesOuvrier(e.target.value)}
                        placeholder={coeffChargesPatronales}
                        className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">x</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <label htmlFor="coeffEtam" className="block text-sm font-medium text-gray-700">
                      ETAM
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <input
                        type="number"
                        id="coeffEtam"
                        min="1"
                        step="0.01"
                        value={coeffChargesEtam}
                        onChange={(e) => setCoeffChargesEtam(e.target.value)}
                        placeholder={coeffChargesPatronales}
                        className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">x</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <label htmlFor="coeffCadre" className="block text-sm font-medium text-gray-700">
                      Cadre
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <input
                        type="number"
                        id="coeffCadre"
                        min="1"
                        step="0.01"
                        value={coeffChargesCadre}
                        onChange={(e) => setCoeffChargesCadre(e.target.value)}
                        placeholder={coeffChargesPatronales}
                        className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">x</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Seuils alertes budget */}
              <div className="bg-white px-4 py-5 sm:p-6 border-t border-gray-200">
                <h4 className="text-base font-medium text-gray-900 mb-4">
                  Seuils d'alertes budget
                </h4>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="seuilAlerte" className="block text-sm font-medium text-gray-700">
                      Seuil d'alerte (%) <span className="text-red-500">*</span>
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <input
                        type="number"
                        id="seuilAlerte"
                        min="0"
                        max="100"
                        step="1"
                        required
                        aria-required="true"
                        value={seuilAlerteBudget}
                        onChange={(e) => setSeuilAlerteBudget(e.target.value)}
                        className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">%</span>
                      </div>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      Declenche un avertissement quand le budget consomme depasse ce seuil.
                    </p>
                  </div>
                  <div>
                    <label htmlFor="seuilCritique" className="block text-sm font-medium text-gray-700">
                      Seuil critique (%) <span className="text-red-500">*</span>
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <input
                        type="number"
                        id="seuilCritique"
                        min="0"
                        max="100"
                        step="1"
                        required
                        aria-required="true"
                        value={seuilAlerteBudgetCritique}
                        onChange={(e) => setSeuilAlerteBudgetCritique(e.target.value)}
                        className="block w-full pr-8 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">%</span>
                      </div>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      Declenche une alerte critique. Doit etre superieur au seuil d'alerte.
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
    </Layout>
  );
}

export default ParametresEntreprisePage;
