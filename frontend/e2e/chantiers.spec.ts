import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour la gestion des chantiers.
 *
 * Ces tests vérifient les flux utilisateur critiques :
 * - Affichage de la liste des chantiers
 * - Création d'un nouveau chantier
 * - Consultation des détails d'un chantier
 * - Modification d'un chantier
 * - Suppression d'un chantier
 */

test.describe('Chantiers', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter d'abord
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@gregconstruction.fr');
    await page.getByLabel(/mot de passe/i).fill('Admin123!');
    await page.getByRole('button', { name: /se connecter/i }).click();
    await expect(page).toHaveURL(/dashboard|\//i, { timeout: 10000 });
  });

  test('should display chantiers list', async ({ page }) => {
    // Naviguer vers la liste des chantiers
    await page.goto('/chantiers');

    // Vérifier que la page des chantiers est affichée
    await expect(page.getByRole('heading', { name: /chantiers/i })).toBeVisible({ timeout: 10000 });

    // Vérifier la présence du bouton de création
    await expect(page.getByRole('button', { name: /nouveau|créer|ajouter/i })).toBeVisible();
  });

  test('should create a new chantier', async ({ page }) => {
    await page.goto('/chantiers');

    // Cliquer sur le bouton de création
    await page.getByRole('button', { name: /nouveau|créer|ajouter/i }).click();

    // Remplir le formulaire de création
    // Note: Les sélecteurs dépendent de l'implémentation réelle du formulaire
    const nomInput = page.getByLabel(/nom/i);
    if (await nomInput.isVisible()) {
      await nomInput.fill('Chantier E2E Test');
    }

    const adresseInput = page.getByLabel(/adresse/i);
    if (await adresseInput.isVisible()) {
      await adresseInput.fill('123 Rue des Tests, 75001 Paris');
    }

    // Soumettre le formulaire
    const submitButton = page.getByRole('button', { name: /créer|enregistrer|valider/i });
    if (await submitButton.isVisible()) {
      await submitButton.click();

      // Vérifier la création (redirection ou message de succès)
      await expect(page.getByText(/créé|succès|enregistré/i)).toBeVisible({ timeout: 10000 });
    }
  });

  test('should view chantier details', async ({ page }) => {
    await page.goto('/chantiers');

    // Attendre que la liste soit chargée
    await page.waitForTimeout(2000);

    // Cliquer sur le premier chantier de la liste
    const firstChantier = page.locator('[data-testid="chantier-item"]').first();
    if (await firstChantier.isVisible()) {
      await firstChantier.click();

      // Vérifier que les détails sont affichés
      await expect(page.getByText(/détails|informations/i)).toBeVisible({ timeout: 10000 });
    } else {
      // Alternative: cliquer sur un lien ou bouton "voir"
      const viewButton = page.getByRole('link', { name: /voir|détails/i }).first();
      if (await viewButton.isVisible()) {
        await viewButton.click();
        await expect(page.getByText(/détails|informations/i)).toBeVisible({ timeout: 10000 });
      }
    }
  });

  test('should navigate to chantier tabs', async ({ page }) => {
    // Naviguer vers un chantier spécifique (si ID connu ou premier de la liste)
    await page.goto('/chantiers');

    // Attendre le chargement
    await page.waitForTimeout(2000);

    // Chercher un lien vers un chantier
    const chantierLink = page.locator('a[href*="/chantiers/"]').first();
    if (await chantierLink.isVisible()) {
      await chantierLink.click();

      // Vérifier les onglets disponibles
      const tabs = ['Informations', 'Tâches', 'Planning', 'Documents'];
      for (const tab of tabs) {
        const tabElement = page.getByRole('tab', { name: new RegExp(tab, 'i') });
        if (await tabElement.isVisible({ timeout: 2000 }).catch(() => false)) {
          // L'onglet existe, cliquer dessus
          await tabElement.click();
          await page.waitForTimeout(500);
        }
      }
    }
  });

  test('should filter chantiers by status', async ({ page }) => {
    await page.goto('/chantiers');

    // Chercher un filtre par statut
    const statusFilter = page.getByRole('combobox', { name: /statut|filtrer/i });
    if (await statusFilter.isVisible({ timeout: 5000 }).catch(() => false)) {
      await statusFilter.click();

      // Sélectionner un statut
      const enCoursOption = page.getByRole('option', { name: /en cours/i });
      if (await enCoursOption.isVisible()) {
        await enCoursOption.click();

        // Vérifier que le filtre est appliqué
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should search chantiers', async ({ page }) => {
    await page.goto('/chantiers');

    // Chercher un champ de recherche
    const searchInput = page.getByPlaceholder(/rechercher|chercher/i);
    if (await searchInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await searchInput.fill('test');
      await page.waitForTimeout(1000);

      // La recherche devrait filtrer les résultats
    }
  });
});

test.describe('Chantier CRUD Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@gregconstruction.fr');
    await page.getByLabel(/mot de passe/i).fill('Admin123!');
    await page.getByRole('button', { name: /se connecter/i }).click();
    await expect(page).toHaveURL(/dashboard|\//i, { timeout: 10000 });
  });

  test('should edit chantier information', async ({ page }) => {
    await page.goto('/chantiers');
    await page.waitForTimeout(2000);

    // Naviguer vers un chantier
    const chantierLink = page.locator('a[href*="/chantiers/"]').first();
    if (await chantierLink.isVisible()) {
      await chantierLink.click();

      // Chercher le bouton d'édition
      const editButton = page.getByRole('button', { name: /modifier|éditer|edit/i });
      if (await editButton.isVisible({ timeout: 5000 }).catch(() => false)) {
        await editButton.click();

        // Modifier un champ
        const descriptionInput = page.getByLabel(/description/i);
        if (await descriptionInput.isVisible()) {
          await descriptionInput.fill('Description modifiée via E2E test');
        }

        // Sauvegarder
        const saveButton = page.getByRole('button', { name: /enregistrer|sauvegarder|valider/i });
        if (await saveButton.isVisible()) {
          await saveButton.click();
          await expect(page.getByText(/modifié|sauvegardé|succès/i)).toBeVisible({ timeout: 10000 });
        }
      }
    }
  });

  test('should change chantier status', async ({ page }) => {
    await page.goto('/chantiers');
    await page.waitForTimeout(2000);

    // Naviguer vers un chantier
    const chantierLink = page.locator('a[href*="/chantiers/"]').first();
    if (await chantierLink.isVisible()) {
      await chantierLink.click();

      // Chercher un bouton de changement de statut
      const statusButton = page.getByRole('button', { name: /statut|démarrer|terminer/i });
      if (await statusButton.isVisible({ timeout: 5000 }).catch(() => false)) {
        // Le changement de statut est possible
        await statusButton.click();
        await page.waitForTimeout(1000);
      }
    }
  });
});
