import { test, expect } from '@playwright/test'

test.describe('Equipment flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard first (bypass login)
    await page.goto('/dashboard')
  })

  test('user can view and filter equipment', async ({ page }) => {
    // When I click Equipment in the dock
    await page.locator('.dock-item').nth(4).click()

    // I see the equipment table
    await expect(page.locator('.equipment-table')).toBeVisible()
    await expect(page.locator('.equipment-table tbody tr')).toHaveCount(6)

    // When I filter by status "DOWN"
    await page.locator('.filter-bar select').first().selectOption('DOWN')

    // Only matching equipment rows are shown
    await expect(page.locator('.equipment-table tbody tr')).toHaveCount(1)
    await expect(page.locator('.equipment-table tbody tr').first()).toContainText('Wafer Prober Station')
  })

  test('user can search for equipment', async ({ page }) => {
    await page.goto('/equipment')

    // When I search for "Prober"
    await page.fill('.filter-bar input[type="text"]', 'Prober')

    // Only the Wafer Prober row is visible
    await expect(page.locator('.equipment-table tbody tr')).toHaveCount(1)
    await expect(page.locator('.equipment-table tbody tr').first()).toContainText('Wafer Prober Station')
  })
})
