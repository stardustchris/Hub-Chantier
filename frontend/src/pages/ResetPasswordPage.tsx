/**
 * Page de réinitialisation de mot de passe.
 * Permet de définir un nouveau mot de passe après avoir reçu un lien par email.
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useToast } from '../contexts/ToastContext';
import api from '../services/api';
import type { ApiError } from '../types/api';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export function ResetPasswordPage(): React.ReactElement {
  useDocumentTitle('Réinitialiser le mot de passe');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [token, setToken] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{ password?: string; confirm?: string }>({});

  useEffect(() => {
    // Récupérer le token depuis l'URL
    const tokenParam = searchParams.get('token');
    if (!tokenParam) {
      addToast({ message: 'Lien invalide. Veuillez demander un nouveau lien de réinitialisation.', type: 'error' });
      navigate('/forgot-password');
      return;
    }
    setToken(tokenParam);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, navigate]);

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) {
      return 'Le mot de passe doit contenir au moins 8 caractères';
    }
    if (!/[A-Z]/.test(pwd)) {
      return 'Le mot de passe doit contenir au moins une majuscule';
    }
    if (!/[a-z]/.test(pwd)) {
      return 'Le mot de passe doit contenir au moins une minuscule';
    }
    if (!/[0-9]/.test(pwd)) {
      return 'Le mot de passe doit contenir au moins un chiffre';
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) {
      return 'Le mot de passe doit contenir au moins un caractère spécial';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    const newErrors: { password?: string; confirm?: string } = {};

    const passwordError = validatePassword(password);
    if (passwordError) {
      newErrors.password = passwordError;
    }

    if (password !== confirmPassword) {
      newErrors.confirm = 'Les mots de passe ne correspondent pas';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      await api.post('/auth/reset-password', {
        token,
        new_password: password,
      });

      addToast({ message: 'Mot de passe réinitialisé avec succès !', type: 'success' });
      navigate('/login');
    } catch (err) {
      const error = err as ApiError;
      if (error.response?.status === 400) {
        addToast({ message: 'Le lien de réinitialisation est invalide ou expiré', type: 'error' });
      } else {
        addToast({ message: 'Une erreur est survenue. Veuillez réessayer.', type: 'error' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getPasswordStrength = (pwd: string): { strength: number; label: string; color: string } => {
    if (pwd.length === 0) return { strength: 0, label: '', color: '' };

    let strength = 0;
    if (pwd.length >= 8) strength += 1;
    if (pwd.length >= 12) strength += 1;
    if (/[A-Z]/.test(pwd)) strength += 1;
    if (/[a-z]/.test(pwd)) strength += 1;
    if (/[0-9]/.test(pwd)) strength += 1;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) strength += 1;

    if (strength <= 2) return { strength: 1, label: 'Faible', color: 'bg-red-500' };
    if (strength <= 4) return { strength: 2, label: 'Moyen', color: 'bg-yellow-500' };
    return { strength: 3, label: 'Fort', color: 'bg-green-500' };
  };

  const passwordStrength = getPasswordStrength(password);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Réinitialiser votre mot de passe
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Choisissez un nouveau mot de passe sécurisé
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <p className="text-sm text-gray-500">Les champs marques <span className="text-red-500">*</span> sont obligatoires</p>
            {/* Nouveau mot de passe */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Nouveau mot de passe <span className="text-red-500">*</span>
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  aria-required="true"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`appearance-none block w-full px-3 py-2 border ${
                    errors.password ? 'border-red-300' : 'border-gray-300'
                  } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm`}
                />
              </div>
              {errors.password && (
                <p className="mt-2 text-sm text-red-600">{errors.password}</p>
              )}

              {/* Indicateur de force */}
              {password && (
                <div className="mt-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-600">Force du mot de passe :</span>
                    <span className={`text-xs font-medium ${
                      passwordStrength.strength === 1 ? 'text-red-600' :
                      passwordStrength.strength === 2 ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {passwordStrength.label}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${passwordStrength.color}`}
                      style={{ width: `${(passwordStrength.strength / 3) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Confirmation */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirmer le mot de passe <span className="text-red-500">*</span>
              </label>
              <div className="mt-1">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  aria-required="true"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`appearance-none block w-full px-3 py-2 border ${
                    errors.confirm ? 'border-red-300' : 'border-gray-300'
                  } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm`}
                />
              </div>
              {errors.confirm && (
                <p className="mt-2 text-sm text-red-600">{errors.confirm}</p>
              )}
            </div>

            {/* Exigences */}
            <div className="bg-gray-50 p-4 rounded-md">
              <p className="text-xs font-medium text-gray-700 mb-2">Exigences du mot de passe :</p>
              <ul className="text-xs text-gray-600 space-y-1">
                <li className="flex items-center">
                  <span className={password.length >= 8 ? 'text-green-600' : ''}>
                    • Au moins 8 caractères
                  </span>
                </li>
                <li className="flex items-center">
                  <span className={/[A-Z]/.test(password) ? 'text-green-600' : ''}>
                    • Une majuscule
                  </span>
                </li>
                <li className="flex items-center">
                  <span className={/[a-z]/.test(password) ? 'text-green-600' : ''}>
                    • Une minuscule
                  </span>
                </li>
                <li className="flex items-center">
                  <span className={/[0-9]/.test(password) ? 'text-green-600' : ''}>
                    • Un chiffre
                  </span>
                </li>
                <li className="flex items-center">
                  <span className={/[!@#$%^&*(),.?":{}|<>]/.test(password) ? 'text-green-600' : ''}>
                    • Un caractère spécial
                  </span>
                </li>
              </ul>
            </div>

            {/* Bouton */}
            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Réinitialisation...' : 'Réinitialiser le mot de passe'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-600">Ou</span>
              </div>
            </div>

            <div className="mt-6">
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Retour à la connexion
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default ResetPasswordPage
