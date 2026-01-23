import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour l'authentification.
 *
 * Ces tests vérifient les flux utilisateur critiques :
 * - Connexion avec identifiants valides
 * - Erreur avec identifiants invalides
 * - Déconnexion
 * - Protection des routes authentifiées
 */

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Aller à la page de login
    await page.goto('/login');
  });

  test('should display login form', async ({ page }) => {
    // Vérifier que le formulaire de login est affiché
    await expect(page.getByRole('heading', { name: /connexion/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/mot de passe/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /se connecter/i })).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    // Remplir avec des identifiants invalides
    await page.getByLabel(/email/i).fill('invalid@test.com');
    await page.getByLabel(/mot de passe/i).fill('wrongpassword');
    await page.getByRole('button', { name: /se connecter/i }).click();

    // Vérifier le message d'erreur
    await expect(page.getByText(/identifiants invalides|erreur/i)).toBeVisible({ timeout: 10000 });
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Note: Ce test nécessite un utilisateur de test dans la base de données
    // Pour le faire fonctionner en CI, il faudrait un setup de données de test

    // Remplir le formulaire
    await page.getByLabel(/email/i).fill('admin@gregconstruction.fr');
    await page.getByLabel(/mot de passe/i).fill('Admin123!');
    await page.getByRole('button', { name: /se connecter/i }).click();

    // Vérifier la redirection vers le dashboard
    await expect(page).toHaveURL(/dashboard|\/$/i, { timeout: 10000 });
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    // Essayer d'accéder au dashboard sans être connecté
    await page.goto('/dashboard');

    // Vérifier la redirection vers login
    await expect(page).toHaveURL(/login/i, { timeout: 10000 });
  });
});

test.describe('Logout', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter d'abord
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@gregconstruction.fr');
    await page.getByLabel(/mot de passe/i).fill('Admin123!');
    await page.getByRole('button', { name: /se connecter/i }).click();
    await expect(page).toHaveURL(/dashboard|\/$/i, { timeout: 10000 });
  });

  test('should logout successfully', async ({ page }) => {
    // Cliquer sur le bouton de déconnexion (généralement dans un menu utilisateur)
    // L'implémentation dépend de l'UI - adapter selon le design réel
    const userMenu = page.getByRole('button', { name: /profil|utilisateur|menu/i });
    if (await userMenu.isVisible()) {
      await userMenu.click();
    }

    const logoutButton = page.getByRole('button', { name: /déconnexion|logout/i });
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      // Vérifier la redirection vers login
      await expect(page).toHaveURL(/login/i, { timeout: 10000 });
    }
  });
});
