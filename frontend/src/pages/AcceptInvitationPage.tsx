/**
 * Page d'acceptation d'invitation.
 * Permet à un utilisateur invité de créer son compte et définir son mot de passe.
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useToast } from '../contexts/ToastContext';
import { api } from '../services/api';

export function AcceptInvitationPage(): JSX.Element {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [token, setToken] = useState<string>('');
  const [invitationInfo, setInvitationInfo] = useState<{
    email: string;
    nom: string;
    prenom: string;
    role: string;
  } | null>(null);
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingInfo, setIsLoadingInfo] = useState(true);
  const [errors, setErrors] = useState<{ password?: string; confirm?: string }>({});

  useEffect(() => {
    // Récupérer le token depuis l'URL
    const tokenParam = searchParams.get('token');
    if (!tokenParam) {
      showToast('Lien d\'invitation invalide.', 'error');
      navigate('/login');
      return;
    }
    setToken(tokenParam);

    // Récupérer les informations de l'invitation
    fetchInvitationInfo(tokenParam);
  }, [searchParams, navigate, showToast]);

  const fetchInvitationInfo = async (invitationToken: string) => {
    setIsLoadingInfo(true);
    try {
      const response = await api.get(`/auth/invitation/${invitationToken}`);
      setInvitationInfo(response.data);
    } catch (error: any) {
      if (error.response?.status === 404 || error.response?.status === 400) {
        showToast('Cette invitation est invalide ou a expiré.', 'error');
        navigate('/login');
      } else {
        showToast('Impossible de charger l\'invitation.', 'error');
      }
    } finally {
      setIsLoadingInfo(false);
    }
  };

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
      await api.post('/auth/accept-invitation', {
        token,
        password,
      });

      showToast('Compte créé avec succès ! Bienvenue à Hub Chantier.', 'success');
      navigate('/login');
    } catch (error: any) {
      if (error.response?.status === 400) {
        showToast('L\'invitation est invalide ou a expiré', 'error');
      } else if (error.response?.status === 409) {
        showToast('Cette invitation a déjà été acceptée', 'error');
      } else {
        showToast('Une erreur est survenue. Veuillez réessayer.', 'error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getRoleLabel = (role: string): string => {
    const labels: { [key: string]: string } = {
      admin: 'Administrateur',
      chef_chantier: 'Chef de Chantier',
      employe: 'Employé',
    };
    return labels[role] || role;
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

  if (isLoadingInfo) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <div className="flex justify-center items-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
            <p className="mt-4 text-center text-gray-600">Chargement de votre invitation...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!invitationInfo) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Bienvenue à Hub Chantier !
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Vous avez été invité à rejoindre la plateforme
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {/* Informations de l'invitation */}
          <div className="mb-6 p-4 bg-primary-50 rounded-md">
            <h3 className="text-sm font-medium text-primary-800 mb-2">Vos informations</h3>
            <dl className="space-y-1">
              <div>
                <dt className="text-xs text-primary-600">Email</dt>
                <dd className="text-sm font-medium text-primary-900">{invitationInfo.email}</dd>
              </div>
              <div>
                <dt className="text-xs text-primary-600">Nom</dt>
                <dd className="text-sm font-medium text-primary-900">
                  {invitationInfo.prenom} {invitationInfo.nom}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-primary-600">Rôle</dt>
                <dd className="text-sm font-medium text-primary-900">
                  {getRoleLabel(invitationInfo.role)}
                </dd>
              </div>
            </dl>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Mot de passe */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Créer votre mot de passe
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
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
                Confirmer le mot de passe
              </label>
              <div className="mt-1">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
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
                <li className={password.length >= 8 ? 'text-green-600' : ''}>
                  • Au moins 8 caractères
                </li>
                <li className={/[A-Z]/.test(password) ? 'text-green-600' : ''}>
                  • Une majuscule
                </li>
                <li className={/[a-z]/.test(password) ? 'text-green-600' : ''}>
                  • Une minuscule
                </li>
                <li className={/[0-9]/.test(password) ? 'text-green-600' : ''}>
                  • Un chiffre
                </li>
                <li className={/[!@#$%^&*(),.?":{}|<>]/.test(password) ? 'text-green-600' : ''}>
                  • Un caractère spécial
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
                {isLoading ? 'Création du compte...' : 'Créer mon compte'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
