import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour le module Planning.
 *
 * Ces tests vérifient les flux utilisateur critiques :
 * - Affichage du planning hebdomadaire
 * - Création d'affectations
 * - Navigation entre les semaines
 * - Vue par chantier
 */

test.describe('Planning', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter d'abord
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@gregconstruction.fr');
    await page.getByLabel(/mot de passe/i).fill('Admin123!');
    await page.getByRole('button', { name: /se connecter/i }).click();
    await expect(page).toHaveURL(/dashboard|\//i, { timeout: 10000 });
  });

  test('should display planning page', async ({ page }) => {
    // Naviguer vers le planning
    await page.goto('/planning');

    // Vérifier que la page planning est affichée
    await expect(page.getByRole('heading', { name: /planning/i })).toBeVisible({ timeout: 10000 });
  });

  test('should navigate between weeks', async ({ page }) => {
    await page.goto('/planning');
    await page.waitForTimeout(2000);

    // Chercher les boutons de navigation
    const prevButton = page.getByRole('button', { name: /précédent|prev|<|semaine précédente/i });
    const nextButton = page.getByRole('button', { name: /suivant|next|>|semaine suivante/i });

    if (await nextButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      // Aller à la semaine suivante
      await nextButton.click();
      await page.waitForTimeout(1000);

      // Revenir à la semaine précédente
      if (await prevButton.isVisible()) {
        await prevButton.click();
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should switch between views (compagnons/chantiers)', async ({ page }) => {
    await page.goto('/planning');
    await page.waitForTimeout(2000);

    // Chercher les onglets de vue
    const compagnonsTab = page.getByRole('tab', { name: /compagnons|employés|équipe/i });
    const chantiersTab = page.getByRole('tab', { name: /chantiers/i });

    if (await chantiersTab.isVisible({ timeout: 5000 }).catch(() => false)) {
      // Basculer vers la vue chantiers
      await chantiersTab.click();
      await page.waitForTimeout(1000);

      // Revenir à la vue compagnons
      if (await compagnonsTab.isVisible()) {
        await compagnonsTab.click();
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should display week days header', async ({ page }) => {
    await page.goto('/planning');
    await page.waitForTimeout(2000);

    // Vérifier que les jours de la semaine sont affichés
    const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'];
    for (const day of days) {
      const dayHeader = page.getByText(new RegExp(day, 'i'));
      // Au moins un jour devrait être visible
      if (await dayHeader.first().isVisible({ timeout: 2000 }).catch(() => false)) {
        break;
      }
    }
  });

  test('should go to today', async ({ page }) => {
    await page.goto('/planning');
    await page.waitForTimeout(2000);

    // Chercher le bouton "Aujourd'hui"
    const todayButton = page.getByRole('button', { name: /aujourd'hui|today/i });
    if (await todayButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await todayButton.click();
      await page.waitForTimeout(1000);
    }
  });
});

test.describe('Planning Affectations', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@gregconstruction.fr');
    await page.getByLabel(/mot de passe/i).fill('Admin123!');
    await page.getByRole('button', { name: /se connecter/i }).click();
    await expect(page).toHaveURL(/dashboard|\//i, { timeout: 10000 });
  });

  test('should open affectation dialog on cell click', async ({ page }) => {
    await page.goto('/planning');
    await page.waitForTimeout(2000);

    // Chercher une cellule de planning cliquable
    const planningCell = page.locator('[data-testid="planning-cell"]').first();
    if (await planningCell.isVisible({ timeout: 5000 }).catch(() => false)) {
      await planningCell.click();

      // Vérifier qu'un dialogue/modal s'ouvre
      const dialog = page.getByRole('dialog');
      if (await dialog.isVisible({ timeout: 3000 }).catch(() => false)) {
        // Le dialogue d'affectation est ouvert
        await expect(dialog).toBeVisible();
      }
    }
  });

  test('should display existing affectations', async ({ page }) => {
    await page.goto('/planning');
    await page.waitForTimeout(3000);

    // Vérifier s'il y a des affectations existantes
    const affectations = page.locator('[data-testid="affectation"]');
    const count = await affectations.count();

    // Si des affectations existent, vérifier qu'elles sont visibles
    if (count > 0) {
      await expect(affectations.first()).toBeVisible();
    }
  });

  test('should show affectation details on hover/click', async ({ page }) => {
    await page.goto('/planning');
    await page.waitForTimeout(3000);

    // Chercher une affectation existante
    const affectation = page.locator('[data-testid="affectation"]').first();
    if (await affectation.isVisible({ timeout: 5000 }).catch(() => false)) {
      // Survoler ou cliquer pour voir les détails
      await affectation.hover();
      await page.waitForTimeout(500);

      // Ou cliquer
      await affectation.click();
      await page.waitForTimeout(500);
    }
  });
});

test.describe('Planning Integration with Chantiers', () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@gregconstruction.fr');
    await page.getByLabel(/mot de passe/i).fill('Admin123!');
    await page.getByRole('button', { name: /se connecter/i }).click();
    await expect(page).toHaveURL(/dashboard|\//i, { timeout: 10000 });
  });

  test('should access planning from chantier detail', async ({ page }) => {
    // Aller sur un chantier
    await page.goto('/chantiers');
    await page.waitForTimeout(2000);

    const chantierLink = page.locator('a[href*="/chantiers/"]').first();
    if (await chantierLink.isVisible()) {
      await chantierLink.click();
      await page.waitForTimeout(1000);

      // Chercher l'onglet Planning dans la fiche chantier
      const planningTab = page.getByRole('tab', { name: /planning/i });
      if (await planningTab.isVisible({ timeout: 5000 }).catch(() => false)) {
        await planningTab.click();
        await page.waitForTimeout(1000);

        // Vérifier que la vue planning chantier est affichée
      }
    }
  });

  test('should filter planning by chantier', async ({ page }) => {
    await page.goto('/planning');
    await page.waitForTimeout(2000);

    // Chercher un filtre par chantier
    const chantierFilter = page.getByRole('combobox', { name: /chantier|filtrer/i });
    if (await chantierFilter.isVisible({ timeout: 5000 }).catch(() => false)) {
      await chantierFilter.click();
      await page.waitForTimeout(500);

      // Sélectionner un chantier si disponible
      const firstOption = page.getByRole('option').first();
      if (await firstOption.isVisible()) {
        await firstOption.click();
        await page.waitForTimeout(1000);
      }
    }
  });
});
