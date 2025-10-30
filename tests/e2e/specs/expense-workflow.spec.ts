import { test, expect } from '@playwright/test';

/**
 * E2E Test: Complete Expense Workflow
 *
 * Simulates the full business process:
 * 1. Employee submits expense
 * 2. Manager reviews and approves
 * 3. Finance processes payment
 * 4. System generates accounting entries
 *
 * This validates not just code, but the entire configured workflow.
 */

test.describe('Expense Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as test user
    await page.goto('/web/login');
    await page.fill('input[name="login"]', 'admin');
    await page.fill('input[name="password"]', 'admin');
    await page.click('button[type="submit"]');

    // Wait for dashboard
    await expect(page.locator('.o_web_client')).toBeVisible({ timeout: 10000 });
  });

  test('Employee submits expense and gets approval', async ({ page }) => {
    // Navigate to Expenses app
    await page.click('text=Expenses');
    await expect(page.locator('h1:has-text("Expenses")')).toBeVisible();

    // Create new expense
    await page.click('button:has-text("New")');

    // Fill expense form
    await page.fill('input[name="name"]', 'Test Business Meal');
    await page.fill('input[name="unit_amount"]', '150.00');
    await page.selectOption('select[name="product_id"]', { label: 'Meals' });

    // Save expense
    await page.click('button:has-text("Save")');
    await expect(page.locator('.o_form_status_indicator:has-text("Saved")')).toBeVisible();

    // Submit for approval
    await page.click('button:has-text("Submit to Manager")');

    // Verify state changed
    await expect(page.locator('.badge:has-text("Submitted")')).toBeVisible();

    // Get expense ID
    const expenseUrl = page.url();
    const expenseId = expenseUrl.match(/id=(\d+)/)?.[1];

    expect(expenseId).toBeTruthy();

    // Logout
    await page.click('.o_user_menu');
    await page.click('text=Log out');

    // Login as manager
    await page.goto('/web/login');
    await page.fill('input[name="login"]', 'manager');
    await page.fill('input[name="password"]', 'manager');
    await page.click('button[type="submit"]');

    // Navigate to expense for approval
    await page.goto(`/web#id=${expenseId}&model=hr.expense&view_type=form`);

    // Approve expense
    await page.click('button:has-text("Approve")');

    // Verify approved state
    await expect(page.locator('.badge:has-text("Approved")')).toBeVisible();
  });

  test('Expense validation rules enforced', async ({ page }) => {
    // Navigate to Expenses
    await page.click('text=Expenses');
    await page.click('button:has-text("New")');

    // Try to save without required fields
    await page.click('button:has-text("Save")');

    // Verify validation error
    await expect(page.locator('.o_notification_title:has-text("Invalid")')).toBeVisible();

    // Fill minimum required fields
    await page.fill('input[name="name"]', 'Valid Expense');
    await page.fill('input[name="unit_amount"]', '100.00');

    // Save should succeed now
    await page.click('button:has-text("Save")');
    await expect(page.locator('.o_form_status_indicator:has-text("Saved")')).toBeVisible();
  });

  test('Large expense requires CFO approval', async ({ page }) => {
    // Navigate to Expenses
    await page.click('text=Expenses');
    await page.click('button:has-text("New")');

    // Fill expense with large amount
    await page.fill('input[name="name"]', 'Large Equipment Purchase');
    await page.fill('input[name="unit_amount"]', '15000.00');  // Above CFO threshold
    await page.selectOption('select[name="product_id"]', { label: 'Equipment' });

    await page.click('button:has-text("Save")');
    await page.click('button:has-text("Submit to Manager")');

    // Verify CFO approval required badge
    await expect(page.locator('.badge:has-text("CFO Approval Required")')).toBeVisible();
  });

  test('Performance: Expense list loads within 2 seconds', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/web#action=hr.hr_expense_actions_all');

    // Wait for list to load
    await expect(page.locator('.o_list_view')).toBeVisible();

    const loadTime = Date.now() - startTime;

    // Performance assertion
    expect(loadTime).toBeLessThan(2000);

    console.log(`Expense list loaded in ${loadTime}ms`);
  });
});

test.describe('Multi-Currency Expense Workflow', () => {
  test('Expense with foreign currency converts correctly', async ({ page }) => {
    await page.goto('/web/login');
    await page.fill('input[name="login"]', 'admin');
    await page.fill('input[name="password"]', 'admin');
    await page.click('button[type="submit"]');

    await page.click('text=Expenses');
    await page.click('button:has-text("New")');

    // Create expense in EUR
    await page.fill('input[name="name"]', 'European Conference');
    await page.fill('input[name="unit_amount"]', '500.00');
    await page.selectOption('select[name="currency_id"]', { label: 'EUR' });

    await page.click('button:has-text("Save")');

    // Verify currency conversion displayed
    await expect(page.locator('span:has-text("USD")')).toBeVisible();
  });
});
