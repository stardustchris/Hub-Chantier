/**
 * Page d'acceptation d'une invitation.
 * Permet à un utilisateur invité de définir son mot de passe et activer son compte.
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useToast } from '../contexts/ToastContext';
import { useAcceptInvitation } from '../hooks/useAcceptInvitation';
import { useDocumentTitle } from '../hooks/useDocumentTitle';

export function AcceptInvitationPage(): React.ReactElement {
  useDocumentTitle('Accepter l\'invitation');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [token, setToken] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [errors, setErrors] = useState<{ password?: string; confirm?: string; token?: string }>({});

  const {
    invitationInfo,
    isLoadingInfo,
    isLoading,
    fetchInvitationInfo,
    acceptInvitation,
  } = useAcceptInvitation();

  useEffect(() => {
    const tokenParam = searchParams.get('token');
    if (!tokenParam) {
      addToast({ message: 'Lien d\'invitation invalide ou expiré', type: 'error' });
      navigate('/login');
      return;
    }
    setToken(tokenParam);

    fetchInvitationInfo(tokenParam).then(result => {
      if (!result.success) {
        if (result.errorStatus === 404 || result.errorStatus === 400) {
          setErrors({ token: 'Ce lien d\'invitation est invalide ou expiré' });
        } else {
          addToast({ message: 'Erreur lors du chargement de l\'invitation', type: 'error' });
        }
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, navigate]);

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) return 'Le mot de passe doit contenir au moins 8 caractères';
    if (!/[A-Z]/.test(pwd)) return 'Le mot de passe doit contenir au moins une majuscule';
    if (!/[a-z]/.test(pwd)) return 'Le mot de passe doit contenir au moins une minuscule';
    if (!/[0-9]/.test(pwd)) return 'Le mot de passe doit contenir au moins un chiffre';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: { password?: string; confirm?: string } = {};

    const passwordError = validatePassword(password);
    if (passwordError) newErrors.password = passwordError;

    if (password !== confirmPassword) {
      newErrors.confirm = 'Les mots de passe ne correspondent pas';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});

    const result = await acceptInvitation(token, password);

    if (result.success) {
      addToast({ message: 'Compte activé avec succès ! Vous pouvez maintenant vous connecter.', type: 'success' });
      navigate('/login');
    } else if (result.errorStatus === 400 || result.errorStatus === 404) {
      addToast({ message: 'Ce lien d\'invitation est invalide ou expiré', type: 'error' });
    } else {
      addToast({ message: 'Une erreur est survenue. Veuillez réessayer.', type: 'error' });
    }
  };

  // Loading state
  if (isLoadingInfo) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Vérification de l'invitation...</p>
        </div>
      </div>
    );
  }

  // Error state (invalid token)
  if (errors.token) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-red-800">Lien invalide</h3>
              <p className="mt-2 text-sm text-red-700">{errors.token}</p>
            </div>
            <button
              onClick={() => navigate('/login')}
              className="mt-6 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Aller à la connexion
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Bienvenue !
        </h2>
        {invitationInfo && (
          <p className="mt-2 text-center text-sm text-gray-600">
            Bonjour <strong>{invitationInfo.prenom} {invitationInfo.nom}</strong>,
            créez votre mot de passe pour activer votre compte.
          </p>
        )}
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {invitationInfo && (
            <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-700">
                <strong>Email :</strong> {invitationInfo.email}
              </p>
              <p className="text-sm text-blue-700 mt-1">
                <strong>Rôle :</strong> {invitationInfo.role}
              </p>
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <p className="text-sm text-gray-500">Les champs marques <span className="text-red-500">*</span> sont obligatoires</p>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Mot de passe <span className="text-red-500">*</span>
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
                  placeholder="Minimum 8 caractères"
                />
              </div>
              {errors.password && (
                <p className="mt-2 text-sm text-red-600">{errors.password}</p>
              )}
            </div>

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

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Activation...' : 'Activer mon compte'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default AcceptInvitationPage;
