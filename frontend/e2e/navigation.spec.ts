import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('SPA routing works via dock nav', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.locator('.dashboard h1')).toContainText('QCI Foundry Services')

    // Click Equipment in the dock
    await page.locator('.dock-item').nth(4).click()
    await expect(page.locator('.equipment-header h1')).toContainText('Equipment Status')

    // Click Foundry in the dock to go back
    await page.locator('.dock-item').first().click()
    await expect(page.locator('.dashboard h1')).toContainText('QCI Foundry Services')
  })

  test('direct URL access works (SPA fallback)', async ({ page }) => {
    // Navigate directly to /equipment
    await page.goto('/equipment')
    await expect(page.locator('.equipment-header h1')).toContainText('Equipment Status')

    // Refresh the page — SPA fallback should serve index.html
    await page.reload()
    await expect(page.locator('.equipment-header h1')).toContainText('Equipment Status')
  })

  test('dock toggle hides and shows navigation', async ({ page }) => {
    await page.goto('/dashboard')

    // Dock is visible
    await expect(page.locator('.dock')).toBeVisible()

    // Toggle dock hidden
    await page.click('.dock-toggle-tab')
    await expect(page.locator('.dock-wrapper')).toHaveClass(/dock-hidden/)

    // Toggle dock visible again
    await page.click('.dock-toggle-tab')
    await expect(page.locator('.dock-wrapper')).not.toHaveClass(/dock-hidden/)
  })
})
