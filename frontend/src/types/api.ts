/**
 * Types API partagés entre frontend et backend.
 * Ces types doivent correspondre aux modèles Pydantic du backend.
 */

export type UserRole = 'admin' | 'chef_chantier' | 'employe';

export interface User {
  id: number;
  email: string;
  nom: string;
  prenom: string;
  role: UserRole;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  email_verified?: boolean;
  email_verified_at?: string | null;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  nom: string;
  prenom: string;
  role?: UserRole;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

export interface InviteUserRequest {
  email: string;
  nom: string;
  prenom: string;
  role: UserRole;
}

export interface AcceptInvitationRequest {
  token: string;
  password: string;
}

export interface InvitationInfo {
  email: string;
  nom: string;
  prenom: string;
  role: UserRole;
}

export interface MessageResponse {
  message: string;
}

export interface ErrorResponse {
  detail: string;
}

// Types utilitaires
export type ApiResponse<T> = {
  data: T;
  status: 'success';
} | {
  error: string;
  status: 'error';
};

export interface ApiError {
  response?: {
    status: number;
    data?: {
      detail?: string;
    };
  };
  message?: string;
}
